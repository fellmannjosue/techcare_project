# ─────────────────────────────────────────────────────────────
# VIEWS · RELOJ (Asistencia con Plantillas de Horario)
# ─────────────────────────────────────────────────────────────
from django.shortcuts import render, get_object_or_404, redirect
import json
from django.db import connections, transaction
from django.urls import reverse
from django import forms
from datetime import datetime, time, date
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.dateparse import parse_date
from django.conf import settings
from django.views.decorators.http import require_GET

# Modelos (plantillas + reglas + asignaciones + extras)
from .models import (
    ScheduleTemplate,
    ScheduleRule,
    EmployeeScheduleAssignment,
    OvertimeRequest,
    Feriado,
    SabadoEspecial,
    TiempoCompensatorio,
    PermisoEmpleado,
)

# Formularios
from .forms import (
    ScheduleTemplateForm,
    ScheduleRuleForm,          # edición individual (un día)
    RuleBulkForm,              # creación/actualización en lote (checkbox días)
    EmployeeScheduleAssignmentForm,
    FeriadoForm,
    SabadoEspecialForm,
    TiempoCompensatorioForm,
    PermisoEmpleadoForm,
)

# ─────────────────────────────────────────────────────────────
# Utilidades generales
# ─────────────────────────────────────────────────────────────

def _is_ajax(request):
    """Devuelve True si la petición es AJAX (para respuestas JSON en modales)."""
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func))


FMT_HHMM = "%H:%M"  # formato estándar HH:MM

def _to_hhmm(val):
    """
    Normaliza varios tipos (None/time/datetime/str) a cadena 'HH:MM'.
    - datetime aware -> se convierte a tz local y se formatea.
    - datetime naive -> se formatea directo.
    - str -> intenta parsear a HH:MM; si no, se retorna como viene.
    """
    if val is None:
        return None

    if isinstance(val, time):
        return val.strftime(FMT_HHMM)

    if isinstance(val, datetime):
        dt = val
        try:
            if timezone.is_aware(dt):
                dt = timezone.localtime(dt)
            return dt.strftime(FMT_HHMM)
        except Exception:
            return dt.replace(tzinfo=None).strftime(FMT_HHMM)

    if isinstance(val, str):
        s = val.strip()
        if len(s) >= 5 and len(s.split(":")[0]) in (1, 2) and s[2] == ':':
            # ya parece 'HH:MM...' (y soporta 'H:MM')
            # normaliza a 5 caracteres si viene 'H:MM'
            parts = s.split(":")
            hh = parts[0].zfill(2)
            mm = parts[1][:2]
            return f"{hh}:{mm}"
        for pat in ("%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(s, pat).strftime(FMT_HHMM)
            except Exception:
                continue
        return s

    try:
        return str(val)
    except Exception:
        return None


def _parse_hhmm_to_dt(hhmm):
    """Convierte 'HH:MM' en datetime (con fecha dummy de hoy) para poder restas/comparaciones."""
    if not hhmm:
        return None
    try:
        # Asegura dos dígitos en horas
        h, m = hhmm.split(":")
        hhmm = f"{int(h):02d}:{int(m):02d}"
        return datetime.strptime(hhmm, FMT_HHMM)
    except Exception:
        return None


def _mins_between(a_dt, b_dt):
    """Retorna los minutos (int) entre dos datetime."""
    return int((b_dt - a_dt).total_seconds() // 60)


def _sum_sched_minutes(segments):
    """
    Suma minutos programados de una lista de segmentos [(in_hhmm, out_hhmm), ...].
    Soporta turno partido (p. ej. mañana y tarde).
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
    A partir de segmentos programados, devuelve:
    - primer_inicio ('HH:MM') para comparar llegadas
    - ultimo_fin    ('HH:MM') para comparar salidas
    Si no hay datos suficientes, retorna (None, None).
    """
    starts = [_parse_hhmm_to_dt(s[0]) for s in segments if s and s[0]]
    ends   = [_parse_hhmm_to_dt(s[1]) for s in segments if s and s[1]]
    starts = [s for s in starts if s]
    ends   = [e for e in ends if e]
    if not starts or not ends:
        return (None, None)
    return (min(starts).strftime(FMT_HHMM), max(ends).strftime(FMT_HHMM))


# ─────────────────────────────────────────────────────────────
# Helpers de PLANTILLAS/ASIGNACIONES para resolver horario del día
# ─────────────────────────────────────────────────────────────

def _plantilla_para_fecha(emp_code: str, fecha: date) -> int | None:
    """
    Devuelve el ID de la plantilla vigente para un empleado en 'fecha'.
    Reglas:
      - activo=True
      - fecha_inicio <= fecha <= fecha_fin (o fecha_fin es NULL)
    Si hay varias, prioriza la de fecha_inicio más reciente.
    """
    qs = (EmployeeScheduleAssignment.objects
          .filter(emp_code=emp_code, activo=True, fecha_inicio__lte=fecha)
          .order_by("-fecha_inicio"))
    for a in qs:
        if a.fecha_fin is None or a.fecha_fin >= fecha:
            return a.template_id
    return None


def _reglas_del_dia(template_id: int, weekday: int) -> ScheduleRule | None:
    """Devuelve la regla de la plantilla para un 'weekday' (0=Lunes ... 6=Domingo)."""
    try:
        return ScheduleRule.objects.get(template_id=template_id, weekday=weekday)
    except ScheduleRule.DoesNotExist:
        return None


def _segmentos_programados(emp_code: str, fecha: date):
    """
    Resuelve los segmentos programados para 'emp_code' en la 'fecha' dada.
    Retorna lista de tuplas [(entrada_hhmm, salida_hhmm), ...].
    Si el día no se trabaja o no hay plantilla, devuelve [].
    """
    tpl_id = _plantilla_para_fecha(emp_code, fecha)
    if not tpl_id:
        return []

    rule = _reglas_del_dia(tpl_id, fecha.weekday())
    if not rule or not rule.trabaja:
        return []

    segs = []
    if rule.entrada_manana and rule.salida_manana:
        segs.append((_to_hhmm(rule.entrada_manana), _to_hhmm(rule.salida_manana)))
    if rule.entrada_tarde and rule.salida_tarde:
        segs.append((_to_hhmm(rule.entrada_tarde), _to_hhmm(rule.salida_tarde)))
    return segs


# ─────────────────────────────────────────────────────────────
# Utilidad: obtener lista de empleados desde ZKBioTime (para combos)
# ─────────────────────────────────────────────────────────────

def get_empleados_zkbiotime():
    """
    Devuelve lista [(emp_code, 'Nombre Apellido')] para llenar dropdowns.
    Fuente: ZKBioTime (SQL Server).
    """
    with connections['zkbio_sqlserver'].cursor() as cursor:
        cursor.execute("""
            SELECT emp_code, first_name + ' ' + last_name AS nombre
            FROM dbo.personnel_employee
            ORDER BY first_name, last_name
        """)
        return cursor.fetchall()


# ─────────────────────────────────────────────────────────────
# Dashboard principal
# ─────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    """Renderiza el panel principal del módulo Reloj."""
    return render(request, 'reloj/dashboard.html')


# ─────────────────────────────────────────────────────────────
# Gráfica: detalle (modal) y totales (pastel)
# ─────────────────────────────────────────────────────────────

@login_required
def grafica_detalle(request):
    """
    (Modal) Devuelve JSON con filas por 'estado' entre fechas:
    - estado: 'PRESENTE' o 'AUSENTE'
    - fecha_inicio, fecha_fin: 'YYYY-MM-DD'
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
        # Un registro por empleado/día, agregando TODAS las marcas ordenadas
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
        # Universo de empleados × fechas MENOS los que marcaron
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


@login_required
def grafica(request):
    """
    (Vista) Renderiza la página de gráfico pastel:
    - Cuenta PRESENTE si hay al menos una marca por empleado/día en el rango,
      de lo contrario AUSENTE. Muestra totales en el pastel.
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


# ─────────────────────────────────────────────────────────────
# Exportar PDF (placeholder)
# ─────────────────────────────────────────────────────────────

@login_required
def exportar_pdf(request):
    """
    Placeholder: Renderiza el reporte como HTML con flag 'pdf'.
    Si luego activas ReportLab/WeasyPrint, reutiliza este contexto.
    """
    return render(request, 'reloj/reporte.html', {'pdf': True})


# ─────────────────────────────────────────────────────────────
# Reporte de marcas diarias por empleado (STRING_AGG)
# ─────────────────────────────────────────────────────────────

def get_empleado_options():
    """Genera opciones para el <select> de empleado [(emp_code, "emp_code - Nombre"), ...]."""
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


@login_required
def reporte(request):
    """
    (Vista) Reporte principal de marcas:
    - Filtros: fecha_inicio, fecha_fin, y (opcional) emp_code
    - Muestra por empleado/día: marcas (STRING_AGG) y estado (PRESENTE/AUSENTE)
    """
    hoy = datetime.today()
    fecha_inicio_default = hoy.replace(day=1).strftime('%Y-%m-%d')
    fecha_fin_default    = hoy.strftime('%Y-%m-%d')

    fecha_inicio = request.GET.get('fecha_inicio', fecha_inicio_default)
    fecha_fin    = request.GET.get('fecha_fin', fecha_fin_default)
    emp_code_f   = (request.GET.get('emp_code') or "").strip()

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
        CAST(t.emp_code AS VARCHAR(20)) AS emp_code,
        CONVERT(DATE, t.punch_time)     AS fecha,
        CONVERT(VARCHAR(5), CAST(t.punch_time AS TIME), 108) AS hora,
        t.punch_time
    FROM dbo.iclock_transaction t
    WHERE t.punch_time IS NOT NULL
)
SELECT 
    e.emp_code                               AS ID_Empleado,
    e.first_name + ' ' + e.last_name         AS Empleado,
    ISNULL(p.position_name, '-')             AS Cargo,
    f.Fecha,
    ISNULL((
        SELECT STRING_AGG(m2.hora, ', ') WITHIN GROUP (ORDER BY m2.punch_time)
        FROM marcas m2
        WHERE m2.emp_code = CAST(e.emp_code AS VARCHAR(20))
          AND m2.fecha    = f.Fecha
    ), '')                                   AS Marcas,
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
        'empleados_opts': get_empleado_options(),
        'emp_code_f': emp_code_f,
    }
    return render(request, 'reloj/reporte.html', contexto)


# ─────────────────────────────────────────────────────────────
# CRUD · Plantillas y Reglas (con creación en lote)
# ─────────────────────────────────────────────────────────────

@login_required
def plantilla_list(request):
    """Lista de plantillas de horario (con enlace para editar y agregar reglas)."""
    plantillas = ScheduleTemplate.objects.all().order_by("nombre")
    return render(request, "reloj/plantilla_list.html", {"plantillas": plantillas})


@login_required
def plantilla_edit(request, pk=None):
    """
    Crear/editar una plantilla. Si existe, muestra sus reglas.
    """
    plantilla = get_object_or_404(ScheduleTemplate, pk=pk) if pk else None
    if request.method == "POST":
        form = ScheduleTemplateForm(request.POST, instance=plantilla)
        if form.is_valid():
            obj = form.save()
            messages.success(request, "Plantilla guardada.")
            return redirect("reloj_plantilla_edit", pk=obj.pk)
    else:
        form = ScheduleTemplateForm(instance=plantilla)

    reglas = ScheduleRule.objects.filter(template=plantilla).order_by("weekday") if plantilla else []
    return render(request, "reloj/plantilla_form.html", {"form": form, "plantilla": plantilla, "reglas": reglas})


@login_required
def regla_add(request, template_pk):
    """
    Crea/actualiza reglas **en lote** para varios días a la vez con checkboxes.
    - Si ya existe la regla (template, weekday), se actualiza.
    - Si no existe, se crea.
    """
    plantilla = get_object_or_404(ScheduleTemplate, pk=template_pk)

    if request.method == "POST":
        form = RuleBulkForm(request.POST)
        if form.is_valid():
            weekdays = form.cleaned_data["weekdays"]      # lista de ints
            trabaja  = form.cleaned_data["trabaja"]
            em = form.cleaned_data["entrada_manana"]
            sm = form.cleaned_data["salida_manana"]
            et = form.cleaned_data["entrada_tarde"]
            st = form.cleaned_data["salida_tarde"]

            creadas, actualizadas = 0, 0
            with transaction.atomic():
                for wd in weekdays:
                    obj, created = ScheduleRule.objects.update_or_create(
                        template=plantilla,
                        weekday=wd,
                        defaults={
                            "trabaja": trabaja,
                            "entrada_manana": em if trabaja else None,
                            "salida_manana": sm if trabaja else None,
                            "entrada_tarde": et if trabaja else None,
                            "salida_tarde": st if trabaja else None,
                        }
                    )
                    if created:
                        creadas += 1
                    else:
                        actualizadas += 1

            messages.success(
                request,
                f"Reglas guardadas: Creadas {creadas}, Actualizadas {actualizadas}."
            )
            return redirect("reloj_plantilla_edit", plantilla.pk)
    else:
        # Por defecto marca L-V
        form = RuleBulkForm(initial={"weekdays": [0,1,2,3,4], "trabaja": True})

    return render(request, "reloj/regla_form.html", {
        "form": form,
        "plantilla": plantilla,
        "bulk": True,   # bandera para que el template muestre checkboxes
    })


@login_required
def regla_edit(request, pk):
    """
    Edición individual de una regla existente (un solo día).
    """
    regla = get_object_or_404(ScheduleRule, pk=pk)
    if request.method == "POST":
        form = ScheduleRuleForm(request.POST, instance=regla)
        if form.is_valid():
            form.save()
            messages.success(request, "Regla actualizada.")
            return redirect("reloj_plantilla_edit", pk=regla.template.pk)
    else:
        form = ScheduleRuleForm(instance=regla)
    return render(request, "reloj/regla_form.html", {"form": form, "plantilla": regla.template, "bulk": False})


# ─────────────────────────────────────────────────────────────
# CRUD · Asignaciones (esto reemplaza “horarios por empleado”)
# Mantengo nombres horarios_list/add/edit para no romper tus URLs
# ─────────────────────────────────────────────────────────────

@login_required
def horarios_list(request):
    """
    Lista de asignaciones de plantilla por empleado.
    (Sustituye a la antigua lista de 'EmployeeSchedule'). 
    """
    asignaciones = (EmployeeScheduleAssignment.objects
                    .select_related("template")
                    .order_by("-activo", "emp_code", "-fecha_inicio"))

    # Dropdown de empleados (ZKBioTime)
    empleados = get_empleados_zkbiotime()
    EMPLEADOS_CHOICES = [('', '--- Selecciona ---')] + [
        (str(e[0]), f"{e[0]} - {e[1]}") for e in empleados
    ]

    # Form para modal "crear"
    class _AsignacionCustomForm(EmployeeScheduleAssignmentForm):
        # 'nombre_empleado' lo llenamos desde la etiqueta del select
        emp_code = forms.ChoiceField(
            choices=EMPLEADOS_CHOICES,
            label="Empleado",
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_emp_dropdown'})
        )

    form = _AsignacionCustomForm()

    return render(request, 'reloj/horarios_list.html', {
        'asignaciones': asignaciones,
        'form': form,
    })


@login_required
def horarios_add(request):
    """
    Alta de asignación de plantilla a empleado (modal o página completa).
    """
    empleados = get_empleados_zkbiotime()
    EMPLEADOS_CHOICES = [('', '--- Selecciona ---')] + [
        (str(e[0]), f"{e[0]} - {e[1]}") for e in empleados
    ]

    class _AsignacionCustomForm(EmployeeScheduleAssignmentForm):
        emp_code = forms.ChoiceField(
            choices=EMPLEADOS_CHOICES,
            label="Empleado",
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_emp_dropdown'})
        )

    if request.method == 'POST':
        form = _AsignacionCustomForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)

            # Copia “nombre_empleado” desde la etiqueta del select
            emp_code_val = form.cleaned_data['emp_code']
            label = dict(form.fields['emp_code'].choices).get(emp_code_val, emp_code_val)
            instance.nombre_empleado = label.split(' - ', 1)[1].strip() if ' - ' in label else label

            instance.save()
            if _is_ajax(request):
                return JsonResponse({'success': True})
            messages.success(request, "Asignación creada.")
            return redirect('horarios_list')
        else:
            if _is_ajax(request):
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = _AsignacionCustomForm()

    return render(request, 'reloj/asignacion_form.html', {'form': form, 'modo': 'Agregar'})


@login_required
def horarios_edit(request, pk):
    """
    Edición de una asignación existente (modal o página completa).
    """
    asignacion = get_object_or_404(EmployeeScheduleAssignment, pk=pk)

    empleados = get_empleados_zkbiotime()
    EMPLEADOS_CHOICES = [('', '--- Selecciona ---')] + [
        (str(e[0]), f"{e[0]} - {e[1]}") for e in empleados
    ]

    class _AsignacionCustomForm(EmployeeScheduleAssignmentForm):
        emp_code = forms.ChoiceField(
            choices=EMPLEADOS_CHOICES,
            label="Empleado",
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_emp_dropdown'})
        )

    if request.method == 'POST':
        form = _AsignacionCustomForm(request.POST, instance=asignacion)
        if form.is_valid():
            instance = form.save(commit=False)

            emp_code_val = form.cleaned_data['emp_code']
            label = dict(form.fields['emp_code'].choices).get(emp_code_val, emp_code_val)
            instance.nombre_empleado = label.split(' - ', 1)[1].strip() if ' - ' in label else label

            instance.save()
            if _is_ajax(request):
                return JsonResponse({'success': True})
            messages.success(request, "Asignación actualizada.")
            return redirect('horarios_list')
        else:
            if _is_ajax(request):
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = _AsignacionCustomForm(instance=asignacion)
        # Preselección del empleado actual
        form.fields['emp_code'].initial = str(asignacion.emp_code)

    return render(request, 'reloj/asignacion_form.html', {
        'form': form,
        'modo': 'Editar',
        'asignacion': asignacion,
    })


# ─────────────────────────────────────────────────────────────
# Test de conexión a SQL Server (útil para validar ODBC)
# ─────────────────────────────────────────────────────────────

@login_required
def test_sqlserver_connection(request):
    """
    Ejecuta una consulta mínima en ZKBioTime para validar la conexión.
    Muestra un mensaje en pantalla sobre el estado (OK / ERROR).
    """
    try:
        with connections['zkbio_sqlserver'].cursor() as cursor:
            cursor.execute("SELECT TOP 1 emp_code, first_name FROM dbo.personnel_employee")
            row = cursor.fetchone()
            msg = f"Conexión OK: {row}"
    except Exception as e:
        msg = f"ERROR de conexión: {e}"
    return render(request, 'reloj/test_sql.html', {'mensaje': msg})


# ─────────────────────────────────────────────────────────────
# Tiempo por hora (comparación real vs programado por PLANTILLA)
# ─────────────────────────────────────────────────────────────

def _fmt_mins(m: int) -> str:
    """Devuelve 'Xh Ym' o 'M min' para mostrar minutos bonitos."""
    m = int(m or 0)
    if m <= 0:
        return "0 min"
    h, mm = divmod(m, 60)
    return f"{h}h {mm}m" if h else f"{mm} min"


@login_required
def tiempo_por_hora(request):
    """
    Calcula para cada empleado/día (en el rango):
      - Hora de entrada/salida reales (MIN/MAX de marcas del día).
      - Colores de llegada/salida vs horario programado (plantilla/segmentos).
      - Tiempo extra / faltante (real total vs total programado).
      - Marcas del día (todas) separadas por coma y con color en 1ª/última.
      - Sincroniza Tiempo Extra con OvertimeRequest (minutos calculados y autorizados).
    NOTA: el SQL obtiene las marcas; el horario se resuelve con ORMs (plantillas).
    """
    # Filtros básicos
    hoy = datetime.today()
    fecha_inicio_default = hoy.replace(day=1).strftime('%Y-%m-%d')
    fecha_fin_default    = hoy.strftime('%Y-%m-%d')

    fecha_inicio = request.GET.get('fecha_inicio', fecha_inicio_default)
    fecha_fin    = request.GET.get('fecha_fin', fecha_fin_default)
    q            = (request.GET.get('q') or "").strip()

    datos = []
    error = None

    # SQL: MIN/MAX y conteo por empleado/día (tu SQL intacto)
    query = f"""
DECLARE @fechaInicio DATE = '{fecha_inicio}';
DECLARE @fechaFin    DATE = '{fecha_fin}';

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
    ISNULL(p.position_name, '-') AS Cargo,
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
LEFT JOIN dbo.personnel_position p ON p.id = TRY_CONVERT(INT, e.position_id)
LEFT JOIN dbo.iclock_transaction t 
       ON t.emp_code = e.emp_code 
      AND CONVERT(DATE, t.punch_time) = f.Fecha
GROUP BY e.emp_code, e.first_name, e.last_name, p.position_name, f.Fecha
ORDER BY e.emp_code, f.Fecha
OPTION (MAXRECURSION 0);
"""
    try:
        with connections['zkbio_sqlserver'].cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columnas = [col[0] for col in cursor.description]

            # Consulta auxiliar: TODAS las marcas "HH:MM" por empleado/día
            marcas_map = {}  # key: (emp_code_str, fecha_date) -> ["06:54","12:01","13:00","17:25"]
            try:
                with connections['zkbio_sqlserver'].cursor() as cur2:
                    cur2.execute(f"""
                        SELECT 
                            CAST(t.emp_code AS VARCHAR(20)) AS emp_code,
                            CONVERT(DATE, t.punch_time) AS fecha,
                            CONVERT(VARCHAR(5), CAST(t.punch_time AS TIME), 108) AS hhmm
                        FROM dbo.iclock_transaction t
                        WHERE CONVERT(DATE, t.punch_time) BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
                        ORDER BY t.emp_code, t.punch_time
                    """)
                    for emp_code_m, fecha_m, hhmm in cur2.fetchall():
                        key = (str(emp_code_m).strip(), fecha_m)
                        marcas_map.setdefault(key, []).append(hhmm)
            except Exception as ex:
                print(f"[WARN] Consulta de marcas por día falló: {ex}")

            # Defaults si no hay plantilla vigente ese día
            DEF_IN, DEF_OUT = "07:00", "16:48"

            for i, r in enumerate(rows):
                row = dict(zip(columnas, r))

                # Campos base
                emp_code = str(row.get('ID_Empleado') or "").strip()
                empleado = (row.get('Empleado') or "").strip()
                cargo    = (row.get('Cargo') or "").strip()
                fecha_d  = row.get('Fecha')

                # Normaliza horas reales a HH:MM
                h_in_real  = _to_hhmm(row.get('Hora_Entrada'))
                h_out_real = _to_hhmm(row.get('Hora_Salida'))

                # Segmentos programados desde PLANTILLA/ASIGNACIÓN
                segs = _segmentos_programados(emp_code, fecha_d)
                if not segs:
                    segs = [(DEF_IN, DEF_OUT)]  # fallback
                    no_programado = True
                else:
                    no_programado = False

                prog_first_in, prog_last_out = _first_in_last_out(segs)
                prog_total_mins = _sum_sched_minutes(segs)  # minutos programados del día

                color_in_class  = ""
                color_out_class = ""

                # --- Cálculo robusto de trabajado/extra/faltante ---
                trabajado_min = 0
                total_real_mins = 0
                extra_calc_min = 0
                faltante_min = 0

                try:
                    if h_in_real and h_out_real and prog_first_in and prog_last_out:
                        tin_real  = _parse_hhmm_to_dt(h_in_real)
                        tin_prog  = _parse_hhmm_to_dt(prog_first_in)
                        tout_real = _parse_hhmm_to_dt(h_out_real)
                        tout_prog = _parse_hhmm_to_dt(prog_last_out)

                        # LLEGADA
                        color_in_class = "hora-verde" if tin_real and tin_prog and tin_real <= tin_prog else "hora-rojo"

                        # SALIDA
                        if tout_real and tout_prog:
                            if tout_real > tout_prog:
                                color_out_class = "hora-azul"
                            elif tout_real == tout_prog:
                                color_out_class = "hora-verde"
                            else:
                                color_out_class = "hora-rojo"

                        # Trabajado real
                        if tin_real and tout_real:
                            total_real_mins = _mins_between(tin_real, tout_real)
                            trabajado_min = total_real_mins

                    # Diferencias (independiente de colores)
                    extra_calc_min = max(0, total_real_mins - prog_total_mins)
                    faltante_min   = max(0, prog_total_mins - total_real_mins)

                except Exception as ex:
                    print(f"[WARN] Cálculo fila #{i}: {ex}")

                # Filtro de búsqueda 'q' (código, nombre, cargo)
                if q:
                    qlow = q.lower()
                    if not (qlow in emp_code.lower() or qlow in empleado.lower() or qlow in cargo.lower()):
                        continue

                # Marcas del día y coloreado de 1ª y última
                key = (emp_code, fecha_d)
                marcas_list = marcas_map.get(key, [])
                marcas_coloreadas = []
                if marcas_list:
                    for idx, tmark in enumerate(marcas_list):
                        cls = ""
                        if idx == 0:
                            cls = color_in_class
                        elif idx == len(marcas_list) - 1:
                            cls = color_out_class
                        marcas_coloreadas.append({'t': tmark, 'cls': cls})

                # --- Sincronizar con OvertimeRequest (minutos calculados) ---
                try:
                    ot, _ = OvertimeRequest.objects.get_or_create(
                        emp_code=emp_code, fecha=fecha_d,
                        defaults={"minutos_calculados": int(extra_calc_min)}
                    )
                    if ot.minutos_calculados != int(extra_calc_min):
                        ot.minutos_calculados = int(extra_calc_min)
                        ot.save(update_fields=["minutos_calculados"])
                    # Campos para UI
                    aprobado_por = ""
                    if ot.approved_by:
                        aprobado_por = (ot.approved_by.get_full_name() or ot.approved_by.username)
                    aprobado_en = ot.approved_at.strftime("%Y-%m-%d %H:%M") if ot.approved_at else ""
                    can_authorize = bool(getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False))
                except Exception as ex:
                    print(f"[WARN] Overtime sync #{i}: {ex}")
                    aprobado_por = ""
                    aprobado_en = ""
                    can_authorize = False
                    ot = None

                # Ensamble de salida (manteniendo tus claves + nuevas)
                row['Cargo']                    = cargo
                row['No_Programado']           = no_programado
                row['Hora_Entrada']            = h_in_real  or "—"
                row['Hora_Salida']             = h_out_real or "—"
                row['Color_Entrada_Class']     = color_in_class
                row['Color_Salida_Class']      = color_out_class

                # NUEVOS: números y string bonitos
                row['Programado_Min']          = int(prog_total_mins or 0)
                row['Trabajado_Min']           = int(trabajado_min or 0)
                row['Faltante_Min']            = int(faltante_min or 0)
                row['Extra_Min_Calculado']     = int(extra_calc_min or 0)
                row['Extra_Min_Autorizado']    = int((ot.minutos_autorizados if ot else 0) or 0)
                row['Extra_Status']            = (ot.status if ot else "PEND")
                row['Extra_Autorizado_Por']    = aprobado_por
                row['Extra_Autorizado_En']     = aprobado_en
                row['Can_Authorize']           = can_authorize

                # Compatibilidad con tus columnas de texto previas
                row['Tiempo_Extra']            = _fmt_mins(row['Extra_Min_Calculado'])
                row['Tiempo_Faltante']         = _fmt_mins(row['Faltante_Min'])

                row['Horario_Primera_Entrada'] = prog_first_in or DEF_IN
                row['Horario_Ultima_Salida']   = prog_last_out or DEF_OUT
                row['Marcas_Dia_Texto']        = ", ".join(marcas_list) if marcas_list else ""
                row['Marcas_Dia']              = marcas_coloreadas

                datos.append(row)

            # Logs de depuración
            print(f"Total filas procesadas (vista): {len(datos)}")
            for j, r0 in enumerate(datos[:5]):
                print(f"[{j}] emp={r0.get('ID_Empleado')} fecha={r0.get('Fecha')} "
                      f"in={r0.get('Hora_Entrada')} out={r0.get('Hora_Salida')} "
                      f"prog_min={r0.get('Programado_Min')} trab_min={r0.get('Trabajado_Min')} "
                      f"extra={r0.get('Tiempo_Extra')} falt={r0.get('Tiempo_Faltante')} | "
                      f"aut={r0.get('Extra_Min_Autorizado')} {r0.get('Extra_Status')} por={r0.get('Extra_Autorizado_Por')} | "
                      f"prog_in={r0.get('Horario_Primera_Entrada')} prog_out={r0.get('Horario_Ultima_Salida')} | "
                      f"marcas={r0.get('Marcas_Dia_Texto')}")

            if not datos:
                print("⚠️ SQL vacío o filtros dejaron 0 filas.")

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


# ─────────────────────────────────────────────────────────────
# AUTORIZAR TIEMPO EXTRA (JSON)
# ─────────────────────────────────────────────────────────────

@staff_required
@require_POST
def overtime_authorize(request):
    """
    Autoriza/Rechaza minutos de tiempo extra.
    Espera JSON:
      { "emp_code":"0001", "fecha":"YYYY-MM-DD", "minutos": 30, "status":"APPR"|"REJC", "comentario": "opc" }
    Devuelve JSON: { success, msg }
    """
    try:
        data = request.POST or {}
        # Soporta JSON en body
        if request.content_type.startswith("application/json"):
            import json
            data = json.loads(request.body.decode("utf-8"))
        emp_code = (data.get("emp_code") or "").strip()
        fecha = parse_date(data.get("fecha") or "")
        minutos = int(data.get("minutos") or 0)
        status = (data.get("status") or "APPR").upper()
        comentario = (data.get("comentario") or "").strip()

        if status not in ("APPR", "REJC"):
            return JsonResponse({"success": False, "msg": "Estado inválido."}, status=400)
        if not (emp_code and fecha is not None):
            return JsonResponse({"success": False, "msg": "Datos incompletos."}, status=400)
        if minutos < 0:
            minutos = 0

        ot, _ = OvertimeRequest.objects.get_or_create(emp_code=emp_code, fecha=fecha)
        ot.minutos_autorizados = minutos if status == "APPR" else 0
        ot.status = status
        ot.comentario = comentario
        ot.approved_by = request.user
        ot.approved_at = timezone.now()
        ot.save()
        return JsonResponse({"success": True, "msg": "Actualizado."})
    except Exception as e:
        return JsonResponse({"success": False, "msg": str(e)}, status=500)


# ─────────────────────────────────────────────────────────────
# GOOGLE FORMS HOOK · Tiempo compensatorio
# ─────────────────────────────────────────────────────────────

def _parse_date_flexible(s: str):
    """Acepta 'YYYY-MM-DD', 'DD/MM/YYYY' o 'MM/DD/YYYY' y retorna date (o None)."""
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    return None


@require_GET
def compensatorio_employees_list(request):
    # Auth por el mismo token compartido
    token = request.headers.get("X-Forms-Token") or request.headers.get("Authorization", "").replace("Bearer ", "")
    if token != getattr(settings, "GOOGLE_FORMS_SHARED_TOKEN", ""):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    rows = []
    try:
        with connections['zkbio_sqlserver'].cursor() as c:
            c.execute("""
                SELECT CAST(emp_code AS VARCHAR(20)) AS code,
                       (first_name + ' ' + last_name) AS nombre
                FROM dbo.personnel_employee
                ORDER BY first_name, last_name
            """)
            rows = c.fetchall()
    except Exception as ex:
        return JsonResponse({"ok": False, "error": f"SQL error: {ex}"}, status=500)

    choices = [{"code": (code or "").strip(),
                "label": f"{(code or '').strip()} — {(nombre or '').strip()}"} for code, nombre in rows]

    return JsonResponse({"ok": True, "choices": choices})

@csrf_exempt
@require_POST
def compensatorio_google_hook(request):
    """
    Endpoint para Google Forms (Apps Script).
    - Auth: Authorization: Bearer <TOKEN>  (y fallbacks X-Forms-Token, ?token=)
    - JSON: {emp_code, fecha, minutos_registrados, motivo, ...}
    - Resuelve nombre_empleado oficial desde ZKBioTime.
    """
    # --- Auth robusto por token compartido ---
    expected = getattr(settings, "GOOGLE_FORMS_SHARED_TOKEN", "")
    raw = (
        request.headers.get("Authorization")
        or request.META.get("HTTP_AUTHORIZATION")
        or request.headers.get("X-Forms-Token")
        or request.GET.get("token")
    )
    token = ""
    if raw:
        token = raw.split(" ", 1)[1].strip() if str(raw).startswith("Bearer ") else str(raw).strip()

    if not token:
        return JsonResponse({"success": False, "error": "Falta token"}, status=401)
    if token != expected:
        return JsonResponse({"success": False, "error": "Token inválido"}, status=403)

    # --- Parse body ---
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception as ex:
        return JsonResponse({"success": False, "error": f"JSON inválido: {ex}"}, status=400)

    emp_code = (data.get("emp_code") or "").strip()
    if not emp_code:
        return JsonResponse({"success": False, "error": "emp_code requerido"}, status=400)

    fecha = _parse_date_flexible((data.get("fecha") or "").strip())
    if not fecha:
        return JsonResponse({"success": False, "error": "fecha inválida"}, status=400)

    try:
        minutos = int(data.get("minutos_registrados") or 0)
        if minutos < 0:
            minutos = 0
    except Exception:
        return JsonResponse({"success": False, "error": "minutos_registrados inválido"}, status=400)

    motivo = (data.get("motivo") or "").strip()

    # --- Resolver nombre oficial desde ZKBioTime ---
    try:
        with connections["zkbio_sqlserver"].cursor() as c:
            c.execute(
                """
                SELECT (first_name + ' ' + last_name) AS nombre
                FROM dbo.personnel_employee
                WHERE CAST(emp_code AS VARCHAR(20)) = %s
                """,
                [emp_code],
            )
            row = c.fetchone()
    except Exception as ex:
        return JsonResponse({"success": False, "error": f"Error SQLServer: {ex}"}, status=500)

    if not row:
        return JsonResponse({"success": False, "error": "emp_code no existe en ZKBioTime"}, status=400)

    nombre_oficial = (row[0] or "").strip()

    # --- Crear/actualizar registro (clave emp_code+fecha) ---
    obj, created = TiempoCompensatorio.objects.update_or_create(
        emp_code=emp_code,
        fecha=fecha,
        defaults={
            "nombre_empleado": nombre_oficial,  # ignoramos el nombre del Form
            "minutos_registrados": minutos,
            "motivo": motivo,
        },
    )

    return JsonResponse({
        "success": True,
        "created": created,
        "id": obj.id,
        "emp_code": emp_code,
        "nombre": nombre_oficial,
        "fecha": fecha.isoformat(),
        "minutos": minutos,
    })

# ─────────────────────────────────────────────────────────────
# CRUD · Feriados
# ─────────────────────────────────────────────────────────────

@staff_required
def feriados_list(request):
    qs = Feriado.objects.all().order_by("-fecha")
    paginator = Paginator(qs, 20)
    page = request.GET.get("page")
    feriados = paginator.get_page(page)
    return render(request, "reloj/feriados_list.html", {"feriados": feriados})


@staff_required
def feriado_new(request):
    if request.method == "POST":
        form = FeriadoForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.creado_por = request.user
            obj.save()
            messages.success(request, "Feriado creado.")
            return redirect("reloj_feriados_list")
    else:
        form = FeriadoForm()
    return render(request, "reloj/feriado_form.html", {"form": form, "modo": "Agregar"})


@staff_required
def feriado_edit(request, pk):
    obj = get_object_or_404(Feriado, pk=pk)
    if request.method == "POST":
        form = FeriadoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Feriado actualizado.")
            return redirect("reloj_feriados_list")
    else:
        form = FeriadoForm(instance=obj)
    return render(request, "reloj/feriado_form.html", {"form": form, "modo": "Editar", "obj": obj})


@staff_required
def feriado_delete(request, pk):
    obj = get_object_or_404(Feriado, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Feriado eliminado.")
        return redirect("reloj_feriados_list")
    return render(request, "reloj/confirm_delete.html", {"obj": obj, "titulo": "Eliminar feriado"})


# ─────────────────────────────────────────────────────────────
# CRUD · Sábados especiales
# ─────────────────────────────────────────────────────────────

@staff_required
def sabados_list(request):
    qs = SabadoEspecial.objects.all().order_by("-fecha")
    paginator = Paginator(qs, 20)
    page = request.GET.get("page")
    sabados = paginator.get_page(page)
    return render(request, "reloj/sabados_list.html", {"sabados": sabados})


@staff_required
def sabado_new(request):
    if request.method == "POST":
        form = SabadoEspecialForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.creado_por = request.user
            obj.save()
            messages.success(request, "Sábado especial creado.")
            return redirect("reloj_sabados_list")
    else:
        form = SabadoEspecialForm()
    return render(request, "reloj/sabado_form.html", {"form": form, "modo": "Agregar"})


@staff_required
def sabado_edit(request, pk):
    obj = get_object_or_404(SabadoEspecial, pk=pk)
    if request.method == "POST":
        form = SabadoEspecialForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Sábado especial actualizado.")
            return redirect("reloj_sabados_list")
    else:
        form = SabadoEspecialForm(instance=obj)
    return render(request, "reloj/sabado_form.html", {"form": form, "modo": "Editar", "obj": obj})


@staff_required
def sabado_delete(request, pk):
    obj = get_object_or_404(SabadoEspecial, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Sábado especial eliminado.")
        return redirect("reloj_sabados_list")
    return render(request, "reloj/confirm_delete.html", {"obj": obj, "titulo": "Eliminar sábado especial"})


# ─────────────────────────────────────────────────────────────
# CRUD · Tiempo compensatorio (capturas)
# ─────────────────────────────────────────────────────────────

@login_required
def compensatorio_list(request):
    """
    Cualquiera autenticado puede ver su lista filtrada por emp_code si quieres;
    aquí mostramos todos (puedes filtrar por request.user.is_staff si lo prefieres).
    """
    qs = TiempoCompensatorio.objects.all().order_by("-fecha", "-creado_en")
    emp_code_f = (request.GET.get("emp_code") or "").strip()
    if emp_code_f:
        qs = qs.filter(emp_code__iexact=emp_code_f)

    paginator = Paginator(qs, 25)
    page = request.GET.get("page")
    items = paginator.get_page(page)
    return render(request, "reloj/compensatorio_list.html", {"items": items, "emp_code_f": emp_code_f})


@login_required
def compensatorio_new(request):
    if request.method == "POST":
        form = TiempoCompensatorioForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.registrado_por = request.user
            obj.estado = "PEND"
            obj.save()
            messages.success(request, "Tiempo compensatorio registrado (pendiente).")
            return redirect("reloj_compensatorio_list")
    else:
        form = TiempoCompensatorioForm()
    return render(request, "reloj/compensatorio_form.html", {"form": form, "modo": "Agregar"})


@staff_required
def compensatorio_edit(request, pk):
    obj = get_object_or_404(TiempoCompensatorio, pk=pk)
    if request.method == "POST":
        form = TiempoCompensatorioForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro actualizado.")
            return redirect("reloj_compensatorio_list")
    else:
        form = TiempoCompensatorioForm(instance=obj)
    return render(request, "reloj/compensatorio_form.html", {"form": form, "modo": "Editar", "obj": obj})


@staff_required
def compensatorio_delete(request, pk):
    obj = get_object_or_404(TiempoCompensatorio, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Registro eliminado.")
        return redirect("reloj_compensatorio_list")
    return render(request, "reloj/confirm_delete.html", {"obj": obj, "titulo": "Eliminar registro de tiempo compensatorio"})


# ─────────────────────────────────────────────────────────────
# CRUD · Permisos
# ─────────────────────────────────────────────────────────────

@login_required
def permisos_list(request):
    qs = PermisoEmpleado.objects.all().order_by("-fecha_inicio", "emp_code")
    emp_code_f = (request.GET.get("emp_code") or "").strip()
    if emp_code_f:
        qs = qs.filter(emp_code__iexact=emp_code_f)
    paginator = Paginator(qs, 25)
    page = request.GET.get("page")
    items = paginator.get_page(page)
    return render(request, "reloj/permisos_list.html", {"items": items, "emp_code_f": emp_code_f})


@login_required
def permiso_new(request):
    if request.method == "POST":
        form = PermisoEmpleadoForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.registrado_por = request.user
            obj.save()
            messages.success(request, "Permiso registrado (pendiente de aprobación).")
            return redirect("reloj_permisos_list")
    else:
        form = PermisoEmpleadoForm()
    return render(request, "reloj/permiso_form.html", {"form": form, "modo": "Agregar"})


@staff_required
def permiso_edit(request, pk):
    obj = get_object_or_404(PermisoEmpleado, pk=pk)
    if request.method == "POST":
        form = PermisoEmpleadoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Permiso actualizado.")
            return redirect("reloj_permisos_list")
    else:
        form = PermisoEmpleadoForm(instance=obj)
    return render(request, "reloj/permiso_form.html", {"form": form, "modo": "Editar", "obj": obj})


@staff_required
@require_POST
def permiso_approve(request, pk):
    """Aprobar/rechazar permiso rápido (AJAX o POST normal)."""
    obj = get_object_or_404(PermisoEmpleado, pk=pk)
    action = (request.POST.get("action") or "").lower()
    comentario = (request.POST.get("comentario") or "").strip()
    if action not in ("aprobar", "rechazar"):
        return HttpResponseBadRequest("Acción inválida")
    obj.aprobado = (action == "aprobar")
    obj.autorizado_por = request.user
    if comentario:
        obj.comentario_autorizacion = comentario
    obj.save()
    if _is_ajax(request):
        return JsonResponse({"success": True, "aprobado": obj.aprobado})
    messages.success(request, "Permiso actualizado.")
    return redirect("reloj_permisos_list")


@staff_required
def permiso_delete(request, pk):
    obj = get_object_or_404(PermisoEmpleado, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Permiso eliminado.")
        return redirect("reloj_permisos_list")
    return render(request, "reloj/confirm_delete.html", {"obj": obj, "titulo": "Eliminar permiso"})
