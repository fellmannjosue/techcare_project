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
    # Aquí iría la lógica para calcular los datos avanzados.
    datos = []  # Por ahora vacío o de prueba
    return render(request, 'reloj/tiempo_por_hora.html', {'datos': datos})
