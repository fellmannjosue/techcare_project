from django.shortcuts import render, get_object_or_404, redirect
from django.db import connections
from django.urls import reverse
from django import forms
from datetime import datetime
from .models import EmployeeSchedule
from .forms import EmployeeScheduleForm

# Utilidad: obtener lista de empleados reales desde zkbiotime
def get_empleados_zkbiotime():
    with connections['zkbio_sqlserver'].cursor() as cursor:
        cursor.execute("SELECT emp_code, first_name + ' ' + last_name AS nombre FROM dbo.personnel_employee ORDER BY first_name, last_name")
        return cursor.fetchall()

# DASHBOARD PRINCIPAL DE RELOJ
def dashboard(request):
    return render(request, 'reloj/dashboard.html')

def grafica(request):
    return render(request, 'reloj/grafica.html')

def exportar_pdf(request):
    return render(request, 'reloj/reporte.html', {'pdf': True})

# REPORTE DE ASISTENCIA PRINCIPAL
def reporte(request):
    hoy = datetime.today()
    fecha_inicio_default = hoy.replace(day=1).strftime('%Y-%m-%d')
    fecha_fin_default = hoy.strftime('%Y-%m-%d')

    fecha_inicio = request.GET.get('fecha_inicio', fecha_inicio_default)
    fecha_fin = request.GET.get('fecha_fin', fecha_fin_default)

    datos = []
    error = None

    if request.GET.get('fecha_inicio') and request.GET.get('fecha_fin'):
        query = f"""
        DECLARE @fechaInicio DATE = '{fecha_inicio}';
        DECLARE @fechaFin DATE = '{fecha_fin}';

        ;WITH fechas AS (
            SELECT @fechaInicio AS Fecha
            UNION ALL
            SELECT DATEADD(DAY, 1, Fecha)
            FROM fechas
            WHERE Fecha < @fechaFin
        ),
        marcas AS (
            SELECT
                emp_code,
                CONVERT(DATE, punch_time) AS fecha,
                CONVERT(VARCHAR(5), CAST(punch_time AS TIME), 108) AS hora
            FROM dbo.iclock_transaction
        )
        SELECT 
            e.emp_code AS ID_Empleado,
            e.first_name + ' ' + e.last_name AS Empleado,
            d.dept_name AS Departamento,
            f.Fecha,
            ISNULL(
                (SELECT STRING_AGG(m.hora, ',') 
                 FROM marcas m 
                 WHERE m.emp_code = e.emp_code AND m.fecha = f.Fecha),
                ''
            ) AS Marcas,
            COUNT(m.hora) AS Cantidad_Marcas,
            CASE 
                WHEN COUNT(m.hora) = 0 THEN 'AUSENTE'
                ELSE 'PRESENTE'
            END AS Estado
        FROM fechas f
        CROSS JOIN dbo.personnel_employee e
        LEFT JOIN dbo.personnel_department d ON e.department_id = d.id
        LEFT JOIN marcas m ON m.emp_code = e.emp_code AND m.fecha = f.Fecha
        WHERE f.Fecha BETWEEN @fechaInicio AND @fechaFin
        GROUP BY e.emp_code, e.first_name, e.last_name, d.dept_name, f.Fecha
        ORDER BY e.emp_code, f.Fecha
        OPTION (MAXRECURSION 0);
        """
        try:
            with connections['zkbio_sqlserver'].cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columnas = [col[0] for col in cursor.description]
                for r in rows:
                    datos.append(dict(zip(columnas, r)))
        except Exception as e:
            error = f"Error al consultar la base de datos: {str(e)}"

    contexto = {
        'datos': datos,
        'error': error,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    return render(request, 'reloj/reporte.html', contexto)


# LISTADO DE HORARIOS DE EMPLEADOS
def horarios_list(request):
    horarios = EmployeeSchedule.objects.all().order_by('nombre', 'emp_code')
    return render(request, 'reloj/horarios_list.html', {'horarios': horarios})

# AGREGAR HORARIO DE EMPLEADO (Dropdown empleados reales, autocompleta ID)
def horarios_add(request):
    empleados = get_empleados_zkbiotime()
    EMPLEADOS_CHOICES = [('', '--- Selecciona ---')] + [(e[0], f"{e[1]} ({e[0]})") for e in empleados]

    class EmployeeScheduleCustomForm(EmployeeScheduleForm):
        nombre = forms.ChoiceField(
            choices=EMPLEADOS_CHOICES,
            label="Empleado",
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_nombre_dropdown'})
        )
        emp_code = forms.CharField(widget=forms.TextInput(attrs={
            'readonly': 'readonly', 'class': 'form-control', 'id': 'id_emp_code'
        }))

    if request.method == 'POST':
        form = EmployeeScheduleCustomForm(request.POST)
        if form.is_valid():
            emp_code = form.cleaned_data['nombre']
            instance = form.save(commit=False)
            instance.emp_code = emp_code
            # Guarda solo el nombre (sin el ID entre paréntesis)
            instance.nombre = dict(form.fields['nombre'].choices).get(emp_code, emp_code).split(' (')[0]
            instance.save()
            return redirect('horarios_list')
    else:
        form = EmployeeScheduleCustomForm()

    return render(request, 'reloj/horario_form.html', {'form': form, 'modo': 'Agregar'})

# EDITAR HORARIO DE EMPLEADO (Dropdown selecciona el empleado actual)
def horarios_edit(request, pk):
    horario = get_object_or_404(EmployeeSchedule, pk=pk)
    empleados = get_empleados_zkbiotime()
    EMPLEADOS_CHOICES = [('', '--- Selecciona ---')] + [(e[0], f"{e[1]} ({e[0]})") for e in empleados]

    class EmployeeScheduleCustomForm(EmployeeScheduleForm):
        nombre = forms.ChoiceField(
            choices=EMPLEADOS_CHOICES,
            label="Empleado",
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_nombre_dropdown'})
        )
        emp_code = forms.CharField(widget=forms.TextInput(attrs={
            'readonly': 'readonly', 'class': 'form-control', 'id': 'id_emp_code'
        }))

    if request.method == 'POST':
        form = EmployeeScheduleCustomForm(request.POST, instance=horario)
        if form.is_valid():
            emp_code = form.cleaned_data['nombre']
            instance = form.save(commit=False)
            instance.emp_code = emp_code
            instance.nombre = dict(form.fields['nombre'].choices).get(emp_code, emp_code).split(' (')[0]
            instance.save()
            return redirect('horarios_list')
    else:
        form = EmployeeScheduleCustomForm(instance=horario)
        # Preselecciona el nombre (opción del dropdown) usando emp_code
        form.fields['nombre'].initial = horario.emp_code

    return render(request, 'reloj/horario_form.html', {'form': form, 'modo': 'Editar'})

# TEST SQL SERVER CONNECTION
def test_sqlserver_connection(request):
    try:
        with connections['zkbio_sqlserver'].cursor() as cursor:
            cursor.execute("SELECT TOP 1 * FROM dbo.personnel_employee")
            row = cursor.fetchone()
            msg = f"Conexión OK: {row}"
    except Exception as e:
        msg = f"ERROR de conexión: {e}"
    return render(request, 'reloj/test_sql.html', {'mensaje': msg})


def tiempo_por_hora(request):
    """
    Muestra primera/última marca por día/empleado usando el query original (sin modificar),
    y calcula en Python: colores (entrada/salida) + tiempo extra/faltante.
    Si no hay horario por empleado, usa defaults 07:00–15:00.
    """

    # 1) Fechas por defecto (mes actual)
    hoy = datetime.today()
    fecha_inicio_default = hoy.replace(day=1).strftime('%Y-%m-%d')
    fecha_fin_default = hoy.strftime('%Y-%m-%d')

    fecha_inicio = request.GET.get('fecha_inicio', fecha_inicio_default)
    fecha_fin = request.GET.get('fecha_fin', fecha_fin_default)

    datos = []
    error = None

    # 2) TU QUERY SIN CAMBIOS (copiado tal cual)
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
        d.dept_name AS Departamento,
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
    LEFT JOIN dbo.personnel_department d ON e.department_id = d.id
    LEFT JOIN dbo.iclock_transaction t 
           ON t.emp_code = e.emp_code AND CONVERT(DATE, t.punch_time) = f.Fecha
    GROUP BY e.emp_code, e.first_name, e.last_name, d.dept_name, f.Fecha
    ORDER BY e.emp_code, f.Fecha
    OPTION (MAXRECURSION 0);
    """

    try:
        with connections['zkbio_sqlserver'].cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columnas = [col[0] for col in cursor.description]

            # === Depuración en consola ===
            print("==[Tiempo por Hora]==")
            print(f"Rango: {fecha_inicio} -> {fecha_fin}")
            print(f"Total filas recibidas (SQL): {len(rows)}")

            # Horario por defecto si no hay integración a calendario propio
            H_ENTRADA_DEF = "07:00"
            H_SALIDA_DEF  = "15:00"
            fmt_hora = "%H:%M"

            def fmt_dt_to_hhmm(dt_val):
                """Convierte datetime/time/str a 'HH:MM' o None."""
                if dt_val is None:
                    return None
                if isinstance(dt_val, str):
                    # ya viene como cadena; intenta normalizar HH:MM
                    try:
                        return datetime.strptime(dt_val[:5], fmt_hora).strftime(fmt_hora)
                    except Exception:
                        # Último recurso: intenta parsear como datetime completo
                        try:
                            return datetime.strptime(dt_val, "%Y-%m-%d %H:%M:%S").strftime(fmt_hora)
                        except Exception:
                            return dt_val  # lo dejamos como viene
                try:
                    # Si viene datetime/time, formatea
                    return dt_val.strftime(fmt_hora)
                except Exception:
                    return None

            for i, r in enumerate(rows):
                row = dict(zip(columnas, r))

                # Normaliza horas reales a "HH:MM"
                h_entrada_real = fmt_dt_to_hhmm(row.get('Hora_Entrada'))
                h_salida_real  = fmt_dt_to_hhmm(row.get('Hora_Salida'))

                # Horario programado (defaults; NO tocamos el SQL)
                h_entrada_prog = H_ENTRADA_DEF
                h_salida_prog  = H_SALIDA_DEF

                color_entrada_class = ""   # 'hora-verde' | 'hora-rojo'
                color_salida_class  = ""   # 'hora-verde' | 'hora-rojo' | 'hora-azul'
                tiempo_extra = ""          # '1h 25m' / '25 min'
                tiempo_faltante = ""       # idem

                try:
                    if h_entrada_real and h_salida_real:
                        t_entrada_real = datetime.strptime(h_entrada_real, fmt_hora)
                        t_entrada_prog = datetime.strptime(h_entrada_prog, fmt_hora)
                        t_salida_real  = datetime.strptime(h_salida_real,  fmt_hora)
                        t_salida_prog  = datetime.strptime(h_salida_prog,  fmt_hora)

                        # Colores llegada
                        color_entrada_class = "hora-verde" if t_entrada_real <= t_entrada_prog else "hora-rojo"

                        # Colores salida
                        if t_salida_real > t_salida_prog:
                            color_salida_class = "hora-azul"
                        elif t_salida_real == t_salida_prog:
                            color_salida_class = "hora-verde"
                        else:
                            color_salida_class = "hora-rojo"

                        # Diferencias en minutos (real vs programado)
                        total_real = (t_salida_real - t_entrada_real).total_seconds() // 60
                        total_prog = (t_salida_prog - t_entrada_prog).total_seconds() // 60
                        diferencia = int(total_real - total_prog)

                        if diferencia > 0:
                            horas = diferencia // 60
                            minutos = diferencia % 60
                            tiempo_extra = f"{horas}h {minutos}m" if horas else f"{minutos} min"
                        elif diferencia < 0:
                            diferencia_abs = abs(diferencia)
                            horas = diferencia_abs // 60
                            minutos = diferencia_abs % 60
                            tiempo_faltante = f"{horas}h {minutos}m" if horas else f"{diferencia_abs} min"

                except Exception as ex:
                    print(f"[WARN] Fila #{i} con error de cálculo: {ex}")
                    color_entrada_class = ""
                    color_salida_class = ""
                    tiempo_extra = ""
                    tiempo_faltante = ""

                # Adjunta campos usados por el template
                row['Hora_Entrada']        = h_entrada_real or "—"
                row['Hora_Salida']         = h_salida_real or "—"
                row['Color_Entrada_Class'] = color_entrada_class
                row['Color_Salida_Class']  = color_salida_class
                row['Tiempo_Extra']        = tiempo_extra
                row['Tiempo_Faltante']     = tiempo_faltante

                datos.append(row)

            # Muestras
            print(f"Total filas procesadas (vista): {len(datos)}")
            for j, r0 in enumerate(datos[:5]):
                print(f"[{j}] emp={r0.get('ID_Empleado')} fecha={r0.get('Fecha')} "
                      f"in={r0.get('Hora_Entrada')} out={r0.get('Hora_Salida')} "
                      f"extra={r0.get('Tiempo_Extra')} falt={r0.get('Tiempo_Faltante')}")

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
        'total_filas': len(datos),
    }
    return render(request, 'reloj/tiempo_por_hora.html', contexto)
