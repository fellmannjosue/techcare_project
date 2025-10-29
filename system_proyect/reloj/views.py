# ─────────────────────────────────────────────────────────────
# VIEWS · RELOJ (Asistencia)
# ─────────────────────────────────────────────────────────────
from django.shortcuts import render, get_object_or_404, redirect
from django.db import connections
from django.urls import reverse
from django import forms
from datetime import datetime, time
# REEMPLAZA cualquier import de make_naive por este:
from django.utils import timezone


from .models import EmployeeSchedule
from .forms import EmployeeScheduleForm

# arriba de tu archivo
from django.http import JsonResponse

def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


FMT_HHMM = "%H:%M"

def _to_hhmm(val):
    """
    Normaliza distintos tipos (None/time/datetime/str) a 'HH:MM'.
    - Si es datetime aware -> lo paso a hora local y formateo.
    - Si es datetime naive  -> formateo directo (sin make_naive).
    """
    if val is None:
        return None

    # time -> HH:MM
    if isinstance(val, time):
        return val.strftime(FMT_HHMM)

    # datetime (aware o naive)
    if isinstance(val, datetime):
        dt = val
        try:
            if timezone.is_aware(dt):
                dt = timezone.localtime(dt)  # convierte a tz local conservando awareness
            # ahora formateamos (funciona para aware o naive)
            return dt.strftime(FMT_HHMM)
        except Exception:
            # fallback muy seguro por si llega un tipo raro
            return dt.replace(tzinfo=None).strftime(FMT_HHMM)

    # str -> intenta normalizar a HH:MM
    if isinstance(val, str):
        s = val.strip()
        if len(s) >= 5 and s[2] == ':':  # 'HH:MM...' -> corta a HH:MM
            return s[:5]
        for pat in ("%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(s, pat).strftime(FMT_HHMM)
            except Exception:
                continue
        return s  # último recurso: deja la cadena como venga

    # otros tipos
    try:
        return str(val)
    except Exception:
        return None


def _parse_hhmm_to_dt(hhmm):
    """
    Convierte 'HH:MM' a datetime (fecha dummy de hoy) para poder restar/comparar.
    """
    if not hhmm:
        return None
    try:
        return datetime.strptime(hhmm, FMT_HHMM)
    except Exception:
        return None


def _mins_between(a_dt, b_dt):
    """Minutos entre dos datetime (entero)."""
    return int((b_dt - a_dt).total_seconds() // 60)


def _sum_sched_minutes(segments):
    """
    Suma total de minutos programados en una lista de segmentos:
    segments = [(in_hhmm, out_hhmm), ...]
    Soporta turno partido (ej. mañana y tarde).
    """
    total = 0
    for hh_in, hh_out in segments:
        t_in = _parse_hhmm_to_dt(hh_in)
        t_out = _parse_hhmm_to_dt(hh_out)
        if t_in and t_out and t_out > t_in:
            total += _mins_between(t_in, t_out)
    return total


def _first_in_last_out(segments):
    """
    A partir de los segmentos programados, retorna:
    - primer_inicio (para color de llegada)
    - ultimo_fin    (para color de salida)
    Ambos como 'HH:MM'. Si no hay datos, (None, None).
    """
    starts = [_parse_hhmm_to_dt(s[0]) for s in segments if s and s[0]]
    ends   = [_parse_hhmm_to_dt(s[1]) for s in segments if s and s[1]]
    starts = [s for s in starts if s]
    ends   = [e for e in ends if e]
    if not starts or not ends:
        return (None, None)
    return (min(starts).strftime(FMT_HHMM), max(ends).strftime(FMT_HHMM))


# ─────────────────────────────────────────────────────────────
# Utilidad: obtener lista de empleados desde ZKBioTime (para combos)
# ─────────────────────────────────────────────────────────────
def get_empleados_zkbiotime():
    """
    Devuelve lista [(emp_code, 'Nombre Apellido')] para llenar dropdowns.
    """
    with connections['zkbio_sqlserver'].cursor() as cursor:
        cursor.execute("""
            SELECT emp_code, first_name + ' ' + last_name AS nombre
            FROM dbo.personnel_employee
            ORDER BY first_name, last_name
        """)
        return cursor.fetchall()


# ─────────────────────────────────────────────────────────────
# Dashboard principal y vistas base
# ─────────────────────────────────────────────────────────────
def dashboard(request):
    """Renderiza el panel principal del módulo Reloj."""
    return render(request, 'reloj/dashboard.html')

def grafica_detalle(request):
    """
    Devuelve en JSON el detalle de empleados/días para un estado dado:
    - estado: 'PRESENTE' o 'AUSENTE'
    - fecha_inicio, fecha_fin (YYYY-MM-DD)
    Respuesta: {"success": bool, "error": str|None, "rows": [{emp_code, empleado, fecha, marcas}, ...]}
    """
    estado = (request.GET.get('estado') or 'PRESENTE').upper()
    hoy = datetime.today()
    fi_def = hoy.replace(day=1).strftime('%Y-%m-%d')
    ff_def = hoy.strftime('%Y-%m-%d')
    fecha_inicio = request.GET.get('fecha_inicio', fi_def)
    fecha_fin    = request.GET.get('fecha_fin', ff_def)

    rows_out, error = [], None

    if estado == 'PRESENTE':
        # Un registro por empleado/día, con TODAS las marcas ordenadas
        query = f"""
        DECLARE @fechaInicio DATE = '{fecha_inicio}';
        DECLARE @fechaFin    DATE = '{fecha_fin}';

        SELECT
            e.emp_code                                   AS emp_code,
            (e.first_name + ' ' + e.last_name)           AS empleado,
            CONVERT(DATE, t.punch_time)                  AS fecha,
            STRING_AGG(CONVERT(VARCHAR(5), CAST(t.punch_time AS TIME), 108), ', ')
                WITHIN GROUP (ORDER BY t.punch_time)     AS marcas
        FROM dbo.iclock_transaction t
        INNER JOIN dbo.personnel_employee e ON e.emp_code = t.emp_code
        WHERE t.punch_time >= @fechaInicio
          AND t.punch_time <  DATEADD(DAY, 1, @fechaFin)
        GROUP BY e.emp_code, e.first_name, e.last_name, CONVERT(DATE, t.punch_time)
        ORDER BY fecha, e.emp_code;
        """
        try:
            with connections['zkbio_sqlserver'].cursor() as cursor:
                cursor.execute(query)
                for emp_code, empleado, fecha, marcas in cursor.fetchall():
                    rows_out.append({
                        "emp_code": str(emp_code),
                        "empleado": empleado,
                        "fecha": fecha.strftime("%Y-%m-%d"),
                        "marcas": marcas or ""
                    })
        except Exception as e:
            error = str(e)

    else:  # AUSENTE
        # Universo de empleados x fechas MENOS los que marcaron
        query = f"""
        DECLARE @fechaInicio DATE = '{fecha_inicio}';
        DECLARE @fechaFin    DATE = '{fecha_fin}';

        ;WITH fechas AS (
            SELECT @fechaInicio AS f
            UNION ALL
            SELECT DATEADD(DAY, 1, f) FROM fechas WHERE f < @fechaFin
        ),
        presentes AS (
            SELECT DISTINCT t.emp_code, CONVERT(DATE, t.punch_time) AS fecha
            FROM dbo.iclock_transaction t
            WHERE t.punch_time >= @fechaInicio
              AND t.punch_time <  DATEADD(DAY, 1, @fechaFin)
        )
        SELECT
            e.emp_code                         AS emp_code,
            (e.first_name + ' ' + e.last_name) AS empleado,
            f.f                                AS fecha
        FROM dbo.personnel_employee e
        CROSS JOIN fechas f
        LEFT JOIN presentes p
               ON p.emp_code = e.emp_code AND p.fecha = f.f
        WHERE p.emp_code IS NULL
        ORDER BY f.f, e.emp_code
        OPTION (MAXRECURSION 0);
        """
        try:
            with connections['zkbio_sqlserver'].cursor() as cursor:
                cursor.execute(query)
                for emp_code, empleado, fecha in cursor.fetchall():
                    rows_out.append({
                        "emp_code": str(emp_code),
                        "empleado": empleado,
                        "fecha": fecha.strftime("%Y-%m-%d"),
                        "marcas": ""  # ausentes no tienen marcas
                    })
        except Exception as e:
            error = str(e)

    return JsonResponse({"success": error is None, "error": error, "rows": rows_out})

def grafica(request):
    """
    Pie chart: Asistencias vs Ausencias en el rango indicado.
    Cuenta, por cada empleado y día, si tuvo al menos una marca (PRESENTE) o ninguna (AUSENTE),
    y resume los totales para el gráfico.
    """
    hoy = datetime.today()
    fecha_inicio_default = hoy.replace(day=1).strftime('%Y-%m-%d')
    fecha_fin_default    = hoy.strftime('%Y-%m-%d')

    fecha_inicio = request.GET.get('fecha_inicio', fecha_inicio_default)
    fecha_fin    = request.GET.get('fecha_fin', fecha_fin_default)

    presentes = 0
    ausentes  = 0
    error     = None

    query = f"""
    DECLARE @fechaInicio DATE = '{fecha_inicio}';
    DECLARE @fechaFin    DATE = '{fecha_fin}';

    ;WITH fechas AS (
        SELECT @fechaInicio AS Fecha
        UNION ALL
        SELECT DATEADD(DAY, 1, Fecha)
        FROM fechas
        WHERE Fecha < @fechaFin
    ),
    estado_dia AS (
        SELECT
            e.emp_code,
            f.Fecha,
            CASE 
                WHEN EXISTS (
                    SELECT 1
                    FROM dbo.iclock_transaction t
                    WHERE t.emp_code = e.emp_code
                      AND CONVERT(DATE, t.punch_time) = f.Fecha
                )
                THEN 'PRESENTE' ELSE 'AUSENTE'
            END AS Estado
        FROM fechas f
        CROSS JOIN dbo.personnel_employee e
    )
    SELECT Estado, COUNT(*) AS Total
    FROM estado_dia
    GROUP BY Estado
    OPTION (MAXRECURSION 0);
    """

    try:
        with connections['zkbio_sqlserver'].cursor() as cursor:
            cursor.execute(query)
            for estado, total in cursor.fetchall():
                est = (estado or '').upper()
                if est == 'PRESENTE':
                    presentes = int(total or 0)
                elif est == 'AUSENTE':
                    ausentes = int(total or 0)
    except Exception as e:
        error = f"Error al consultar la base de datos: {str(e)}"

    contexto = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'presentes': presentes,
        'ausentes': ausentes,
        'error': error,
    }
    return render(request, 'reloj/grafica.html', contexto)

def exportar_pdf(request):
    """
    Renderiza el template de reporte con flag 'pdf' (si lo usas para exportación).
    """
    return render(request, 'reloj/reporte.html', {'pdf': True})


# ─────────────────────────────────────────────────────────────
# REPORTE: listado de marcas por día/empleado (SQL EXACTO)
# ─────────────────────────────────────────────────────────────

def get_empleado_options():
    """
    Devuelve [(emp_code, "emp_code - Nombre Apellido"), ...] para el dropdown.
    """
    opciones = []
    with connections['zkbio_sqlserver'].cursor() as cursor:
        cursor.execute("""
            SELECT CAST(emp_code AS VARCHAR(20)) AS code,
                   (first_name + ' ' + last_name) AS nombre
            FROM dbo.personnel_employee
            ORDER BY first_name, last_name
        """)
        for code, nombre in cursor.fetchall():
            code = (code or "").strip()
            nombre = (nombre or "").strip()
            opciones.append((code, f"{code} - {nombre}"))
    return opciones


def reporte(request):
    """
    Reporte principal de marcas (string_agg de horas por día/empleado).
    - Filtros: fecha_inicio / fecha_fin.
    - Filtro opcional: emp_code (dropdown).
    """
    hoy = datetime.today()
    fecha_inicio_default = hoy.replace(day=1).strftime('%Y-%m-%d')
    fecha_fin_default    = hoy.strftime('%Y-%m-%d')

    fecha_inicio = request.GET.get('fecha_inicio', fecha_inicio_default)
    fecha_fin    = request.GET.get('fecha_fin', fecha_fin_default)
    emp_code_f   = (request.GET.get('emp_code') or "").strip()  # ← NUEVO: filtro por empleado

    datos = []
    error = None

    if request.GET.get('fecha_inicio') and request.GET.get('fecha_fin'):
        query = f"""
DECLARE @fechaInicio DATE = '{fecha_inicio}';
DECLARE @fechaFin    DATE = '{fecha_fin}';

;WITH fechas AS (
    SELECT @fechaInicio AS Fecha
    UNION ALL
    SELECT DATEADD(DAY, 1, Fecha)
    FROM fechas
    WHERE Fecha < @fechaFin
),
marcas AS (
    SELECT
        CAST(emp_code AS VARCHAR(20)) AS emp_code,
        CONVERT(DATE, punch_time)     AS fecha,
        CONVERT(VARCHAR(5), CAST(punch_time AS TIME), 108) AS hora
    FROM dbo.iclock_transaction
    WHERE punch_time IS NOT NULL
)
SELECT 
    e.emp_code                               AS ID_Empleado,
    e.first_name + ' ' + e.last_name         AS Empleado,
    p.position_name                          AS Cargo,
    f.Fecha,
    ISNULL((
        SELECT STRING_AGG(m.hora, ',') WITHIN GROUP (ORDER BY m.hora)
        FROM marcas m
        WHERE m.emp_code = CAST(e.emp_code AS VARCHAR(20))
          AND m.fecha    = f.Fecha
    ), '')                                    AS Marcas,
    COUNT(m.hora)                             AS Cantidad_Marcas,
    CASE WHEN COUNT(m.hora) = 0 THEN 'AUSENTE' ELSE 'PRESENTE' END AS Estado
FROM fechas f
CROSS JOIN dbo.personnel_employee e
LEFT JOIN dbo.personnel_position p ON p.id = TRY_CONVERT(INT, e.position_id)
LEFT JOIN marcas m
       ON m.emp_code = CAST(e.emp_code AS VARCHAR(20))
      AND m.fecha    = f.Fecha
GROUP BY e.emp_code, e.first_name, e.last_name, p.position_name, f.Fecha
ORDER BY e.emp_code, f.Fecha
OPTION (MAXRECURSION 0);
"""
        try:
            with connections['zkbio_sqlserver'].cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columnas = [col[0] for col in cursor.description]

                for r in rows:
                    row = dict(zip(columnas, r))

                    # ← NUEVO: si se eligió un empleado, filtra aquí
                    if emp_code_f and str(row.get('ID_Empleado') or "").strip() != emp_code_f:
                        continue

                    datos.append(row)

        except Exception as e:
            error = f"Error al consultar la base de datos: {str(e)}"

    contexto = {
        'datos': datos,
        'error': error,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'empleados_opts': get_empleado_options(),  # ← NUEVO: opciones para el select
        'emp_code_f': emp_code_f,                  # ← NUEVO: mantener seleccionado
    }
    return render(request, 'reloj/reporte.html', contexto)


# ─────────────────────────────────────────────────────────────
# CRUD de Horarios (con dropdown de empleados reales)
# ─────────────────────────────────────────────────────────────
def horarios_list(request):
    # Listado para la tabla
    horarios = EmployeeSchedule.objects.all().order_by('nombre', 'emp_code')

    # Opciones: value=emp_code, label="emp_code - Nombre"
    empleados = get_empleados_zkbiotime()
    EMPLEADOS_CHOICES = [('', '--- Selecciona ---')] + [
        (str(e[0]), f"{e[0]} - {e[1]}")
    for e in empleados]

    # Form para el modal (crear desde la lista)
    class EmployeeScheduleCustomForm(EmployeeScheduleForm):
        nombre = forms.ChoiceField(
            choices=EMPLEADOS_CHOICES,
            label="Empleado",
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_nombre_dropdown'})
        )
        emp_code = forms.CharField(
            label="ID Empleado",
            widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control', 'id': 'id_emp_code'})
        )

    form = EmployeeScheduleCustomForm()
    form.fields['emp_code'].initial = ""  # vacío al abrir modal

    return render(request, 'reloj/horarios_list.html', {
        'horarios': horarios,
        'form': form,
    })

def horarios_add(request):
    """
    Alta de horario:
    - Dropdown con empleados (emp_code – Nombre)
    - Copia emp_code al campo readonly automáticamente
    - Responde JSON si el request es AJAX (modal)
    """
    empleados = get_empleados_zkbiotime()
    EMPLEADOS_CHOICES = [('', '--- Selecciona ---')] + [
        (str(e[0]), f"{e[0]} - {e[1]}")
        for e in empleados
    ]

    class EmployeeScheduleCustomForm(EmployeeScheduleForm):
        nombre = forms.ChoiceField(
            choices=EMPLEADOS_CHOICES,
            label="Empleado",
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_nombre_dropdown'})
        )
        emp_code = forms.CharField(
            label="ID Empleado",
            widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control', 'id': 'id_emp_code'})
        )

    if request.method == 'POST':
        form = EmployeeScheduleCustomForm(request.POST)
        if form.is_valid():
            emp_code = form.cleaned_data['nombre']  # value del select = emp_code
            instance = form.save(commit=False)
            instance.emp_code = emp_code

            # nombre limpio desde etiqueta "CODE - Nombre"
            label = dict(form.fields['nombre'].choices).get(emp_code, emp_code)
            instance.nombre = label.split(' - ', 1)[1].strip() if ' - ' in label else label

            instance.save()

            if _is_ajax(request):
                return JsonResponse({'success': True})
            return redirect('horarios_list')
        else:
            if _is_ajax(request):
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EmployeeScheduleCustomForm()
        form.fields['emp_code'].initial = ""  # vacío al empezar

    # Render de página completa (no modal)
    return render(request, 'reloj/horario_form.html', {'form': form, 'modo': 'Agregar'})


def horarios_edit(request, pk):
    """
    Edición de horario (modal):
    - Preselecciona el empleado actual
    - Devuelve JSON en POST por AJAX (success / errors)
    - En GET devuelve el fragmento HTML del formulario y pasa 'horario' para el action
    """
    horario = get_object_or_404(EmployeeSchedule, pk=pk)
    empleados = get_empleados_zkbiotime()
    EMPLEADOS_CHOICES = [('', '--- Selecciona ---')] + [
        (str(e[0]), f"{e[0]} - {e[1]}")
        for e in empleados
    ]

    class EmployeeScheduleCustomForm(EmployeeScheduleForm):
        nombre = forms.ChoiceField(
            choices=EMPLEADOS_CHOICES,
            label="Empleado",
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_nombre_dropdown'})
        )
        emp_code = forms.CharField(
            label="ID Empleado",
            widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control', 'id': 'id_emp_code'})
        )

    if request.method == 'POST':
        form = EmployeeScheduleCustomForm(request.POST, instance=horario)
        if form.is_valid():
            emp_code = form.cleaned_data['nombre']
            instance = form.save(commit=False)
            instance.emp_code = emp_code

            label = dict(form.fields['nombre'].choices).get(emp_code, emp_code)
            instance.nombre = label.split(' - ', 1)[1].strip() if ' - ' in label else label

            instance.save()

            if _is_ajax(request):
                return JsonResponse({'success': True})
            return redirect('horarios_list')
        else:
            if _is_ajax(request):
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EmployeeScheduleCustomForm(instance=horario)
        form.fields['nombre'].initial = str(horario.emp_code)
        form.fields['emp_code'].initial = str(horario.emp_code)

    # IMPORTANTE: pasar 'horario' para que el template construya action con pk
    return render(request, 'reloj/horario_form.html', {
        'form': form,
        'modo': 'Editar',
        'horario': horario,
    })


# ─────────────────────────────────────────────────────────────
# Test de conexión a SQL Server (útil cuando falla el ODBC)
# ─────────────────────────────────────────────────────────────
def test_sqlserver_connection(request):
    """Realiza una consulta mínima a ZKBioTime para validar la conexión."""
    try:
        with connections['zkbio_sqlserver'].cursor() as cursor:
            cursor.execute("SELECT TOP 1 * FROM dbo.personnel_employee")
            row = cursor.fetchone()
            msg = f"Conexión OK: {row}"
    except Exception as e:
        msg = f"ERROR de conexión: {e}"
    return render(request, 'reloj/test_sql.html', {'mensaje': msg})


# ─────────────────────────────────────────────────────────────
# TIEMPO POR HORA (Jornada/Extras/Faltantes) · SQL EXACTO + horarios reales
# ─────────────────────────────────────────────────────────────
def tiempo_por_hora(request):
    """
    Calcula para cada empleado/día:
    - Hora de entrada/salida reales (del SQL original).
    - Colores de llegada/salida (comparado contra horario real).
    - Tiempo extra / faltante (comparando total real vs total programado).
    - Marcas del día (todas) separadas por coma, coloreando 1ª y última.
    NOTA: El SQL NO se modifica; los horarios vienen del ORM (formulario).
    """
    # 1) Filtros por fecha + búsqueda q (empleado, depto o código)
    hoy = datetime.today()
    fecha_inicio_default = hoy.replace(day=1).strftime('%Y-%m-%d')
    fecha_fin_default = hoy.strftime('%Y-%m-%d')

    fecha_inicio = request.GET.get('fecha_inicio', fecha_inicio_default)
    fecha_fin    = request.GET.get('fecha_fin', fecha_fin_default)
    q            = (request.GET.get('q') or "").strip()

    datos = []
    error = None

    # 2) Mapa de horarios por emp_code desde tu formulario (soporta turno partido)
    schedules_map = {}
    try:
        qs = EmployeeSchedule.objects.all().values(
            'emp_code',
            'entrada_manana', 'salida_manana',
            'entrada_tarde', 'salida_tarde',
        )
        for obj in qs:
            code = str(obj['emp_code']).strip()
            segs = []
            m_in  = _to_hhmm(obj.get('entrada_manana'))
            m_out = _to_hhmm(obj.get('salida_manana'))
            t_in  = _to_hhmm(obj.get('entrada_tarde'))
            t_out = _to_hhmm(obj.get('salida_tarde'))
            if m_in and m_out:
                segs.append((m_in, m_out))
            if t_in and t_out:
                segs.append((t_in, t_out))
            schedules_map[code] = segs
    except Exception as ex:
        print(f"[WARN] No fue posible cargar horarios del ORM: {ex}")

    # 3) SQL ORIGINAL (NO tocar)
    query = f"""
DECLARE @fechaInicio DATE = '{fecha_inicio}';
DECLARE @fechaFin DATE = '{fecha_fin}';

;WITH fechas AS (
    SELECT @fechaInicio AS Fecha
    UNION ALL
    SELECT DATEADD(DAY, 1, Fecha)
    FROM fechas
    WHERE Fecha < @fechaFin
)
SELECT 
    e.emp_code AS ID_Empleado,
    e.first_name + ' ' + e.last_name AS Empleado,
    p.position_code AS Cargo,
    f.Fecha,
    MIN(t.punch_time) AS Hora_Entrada,
    MAX(t.punch_time) AS Hora_Salida,
    COUNT(t.punch_time) AS Cantidad_Marcas,
    CASE 
        WHEN COUNT(t.punch_time) = 0 THEN 'AUSENTE'
        ELSE 'PRESENTE'
    END AS Estado
FROM fechas f
CROSS JOIN dbo.personnel_employee e
LEFT JOIN dbo.personnel_position p ON e.position_id = p.position_code
LEFT JOIN dbo.iclock_transaction t 
       ON t.emp_code = e.emp_code 
      AND CONVERT(DATE, t.punch_time) = f.Fecha
GROUP BY e.emp_code, e.first_name, e.last_name, p.position_code, f.Fecha
ORDER BY e.emp_code, f.Fecha
OPTION (MAXRECURSION 0);
"""


    try:
        with connections['zkbio_sqlserver'].cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columnas = [col[0] for col in cursor.description]

            # === NUEVO: mapa con TODAS las marcas por día (ordenadas) ===
            marcas_map = {}  # key: (emp_code_str, fecha_date) -> ["06:54","12:01","13:00","17:25"]
            try:
                with connections['zkbio_sqlserver'].cursor() as cur2:
                    cur2.execute(f"""
                        SELECT 
                            CAST(t.emp_code AS VARCHAR(10)) AS emp_code,
                            CONVERT(DATE, t.punch_time) AS fecha,
                            CONVERT(VARCHAR(5), CAST(t.punch_time AS TIME), 108) AS hhmm
                        FROM dbo.iclock_transaction t
                        WHERE CONVERT(DATE, t.punch_time) BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
                        ORDER BY CAST(t.punch_time AS TIME)
                    """)
                    rows_m = cur2.fetchall()
                    for emp_code_m, fecha_m, hhmm in rows_m:
                        key = (str(emp_code_m).strip(), fecha_m)
                        marcas_map.setdefault(key, []).append(hhmm)
            except Exception as ex:
                print(f"[WARN] Consulta de marcas por día falló: {ex}")
            # === FIN NUEVO ===

            # Depuración útil
            print("==[Tiempo por Hora]==")
            print(f"Rango: {fecha_inicio} -> {fecha_fin} | q='{q}'")
            print(f"Total filas recibidas (SQL): {len(rows)}")

            # Defaults si un empleado no tiene horario configurado
            DEF_IN, DEF_OUT = "07:00", "16:35"

            for i, r in enumerate(rows):
                row = dict(zip(columnas, r))

                # Campos básicos
                emp_code = str(row.get('ID_Empleado') or "").strip()
                empleado = (row.get('Empleado') or "").strip()
                depto    = (row.get('Departamento') or "").strip()

                # Normaliza horas reales a HH:MM
                h_in_real  = _to_hhmm(row.get('Hora_Entrada'))
                h_out_real = _to_hhmm(row.get('Hora_Salida'))

                # Segmentos programados del empleado (1 o 2 tramos)
                segs = schedules_map.get(emp_code) or [(DEF_IN, DEF_OUT)]

                # Para colores: comparamos contra primer_inicio y ultimo_fin
                prog_first_in, prog_last_out = _first_in_last_out(segs)
                # Para extra/faltante: suma de todos los tramos
                prog_total_mins = _sum_sched_minutes(segs)

                color_in_class  = ""
                color_out_class = ""
                t_extra = ""
                t_falt  = ""

                try:
                    if h_in_real and h_out_real and prog_first_in and prog_last_out:
                        tin_real  = _parse_hhmm_to_dt(h_in_real)
                        tin_prog  = _parse_hhmm_to_dt(prog_first_in)
                        tout_real = _parse_hhmm_to_dt(h_out_real)
                        tout_prog = _parse_hhmm_to_dt(prog_last_out)

                        # LLEGADA: Verde si llega antes/igual; Rojo si tarde
                        color_in_class = "hora-verde" if tin_real and tin_prog and tin_real <= tin_prog else "hora-rojo"

                        # SALIDA: Azul si se queda más; Verde si igual; Rojo si se va antes
                        if tout_real and tout_prog:
                            if tout_real > tout_prog:
                                color_out_class = "hora-azul"
                            elif tout_real == tout_prog:
                                color_out_class = "hora-verde"
                            else:
                                color_out_class = "hora-rojo"

                        # Extra/Faltante por minutos totales (real vs programado)
                        if tin_real and tout_real:
                            total_real_mins = _mins_between(tin_real, tout_real)
                            dif = total_real_mins - prog_total_mins
                            if dif > 0:
                                h, m = divmod(dif, 60)
                                t_extra = f"{h}h {m}m" if h else f"{m} min"
                            elif dif < 0:
                                dif = abs(dif)
                                h, m = divmod(dif, 60)
                                t_falt = f"{h}h {m}m" if h else f"{dif} min"
                except Exception as ex:
                    print(f"[WARN] Fila #{i} cálculo: {ex}")

                # Filtro de búsqueda 'q' (servidor): código, nombre o depto
                if q:
                    qlow = q.lower()
                    if not (qlow in emp_code.lower() or qlow in empleado.lower() or qlow in depto.lower()):
                        continue

                # --- NUEVO: Marcas del día y coloreado de 1ª y última ---
                key = (emp_code, row.get('Fecha'))
                marcas_list = marcas_map.get(key, [])  # lista de "HH:MM"
                marcas_coloreadas = []
                if marcas_list:
                    for idx, t in enumerate(marcas_list):
                        cls = ""
                        if idx == 0:
                            cls = color_in_class      # primera marca usa color de ENTRADA
                        elif idx == len(marcas_list) - 1:
                            cls = color_out_class     # última marca usa color de SALIDA
                        marcas_coloreadas.append({'t': t, 'cls': cls})
                row['Marcas_Dia_Texto'] = ", ".join(marcas_list) if marcas_list else ""
                row['Marcas_Dia'] = marcas_coloreadas
                # --- FIN NUEVO ---

                # Campos finales para el template
                row['Hora_Entrada']        = h_in_real  or "—"
                row['Hora_Salida']         = h_out_real or "—"
                row['Color_Entrada_Class'] = color_in_class
                row['Color_Salida_Class']  = color_out_class
                row['Tiempo_Extra']        = t_extra
                row['Tiempo_Faltante']     = t_falt

                # (Opcional) Exponer primer y último horario aplicado
                row['Horario_Primera_Entrada'] = prog_first_in or DEF_IN
                row['Horario_Ultima_Salida']   = prog_last_out or DEF_OUT

                datos.append(row)

            # Muestras a consola
            print(f"Total filas procesadas (vista): {len(datos)}")
            for j, r0 in enumerate(datos[:5]):
                print(f"[{j}] emp={r0.get('ID_Empleado')} fecha={r0.get('Fecha')} "
                      f"in={r0.get('Hora_Entrada')} out={r0.get('Hora_Salida')} "
                      f"extra={r0.get('Tiempo_Extra')} falt={r0.get('Tiempo_Faltante')} | "
                      f"prog_in={r0.get('Horario_Primera_Entrada')} prog_out={r0.get('Horario_Ultima_Salida')} | "
                      f"marcas={r0.get('Marcas_Dia_Texto')}")
            if not datos:
                print("⚠️ No llegaron registros (SQL vacío o filtros dejaron 0 filas).")

    except Exception as e:
        error = f"Error al consultar la base de datos: {str(e)}"
        print(f"[ERROR] tiempo_por_hora: {error}")

    contexto = {
        'datos': datos,
        'error': error,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'q': q,
        'total_filas': len(datos),
    }
    return render(request, 'reloj/tiempo_por_hora.html', contexto)
