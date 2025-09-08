from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connections
from .forms import (
    ReporteInformativoForm,
    ReporteConductualForm,
    ProgressReportForm,
)
from django.utils import timezone

# ————————————————————————————————
# CHOICES desde SQL Server y MySQL
# ————————————————————————————————

def obtener_alumnos_bilingue():
    query = """
    SELECT d.PersonaID, 
           ISNULL(d.Nombre1,'') + 
           CASE WHEN d.Nombre2 IS NOT NULL AND d.Nombre2 <> '' THEN ' ' + d.Nombre2 ELSE '' END + ' ' +
           ISNULL(d.Apellido1,'') + 
           CASE WHEN d.Apellido2 IS NOT NULL AND d.Apellido2 <> '' THEN ' ' + d.Apellido2 ELSE '' END AS NombreCompl,
           da.Descripcion AS AreaDesc, c.CrsoNumero, c.GrupoNumero
      FROM dbo.tblPrsDtosGen AS d
      JOIN dbo.tblPrsTipo           AS t  ON d.PersonaID = t.PersonaID
      JOIN dbo.tblEdcArea           AS a  ON t.IngrEgrID  = a.IngrEgrID
      JOIN dbo.tblEdcEjecCrso       AS ec ON a.AreaID     = ec.AreaID
      JOIN dbo.tblEdcCrso           AS c  ON ec.CrsoID    = c.CrsoID
      JOIN dbo.tblEdcDescripAreaEdc AS da ON a.DescrAreaEdcID = da.DescrAreaEdcID
     WHERE d.Alum = 1 AND DATEPART(yy, c.FechaInicio) = DATEPART(yyyy, GETDATE())
       AND da.Descripcion IN (N'PrimariaBL', N'ColegioBL', N'PreescolarBL')
       AND ec.Desertor = 0 AND ec.TrasladoPer = 0
     ORDER BY da.Descripcion, c.CrsoNumero, c.GrupoNumero, NombreCompl
    """
    alumnos = []
    try:
        with connections['padres_sqlserver'].cursor() as cursor:
            cursor.execute(query)
            for pid, nombre, area, crso, grupo in cursor.fetchall():
                label = f"{nombre.strip()} ({area}) - {crso}{grupo}"
                alumnos.append((pid, label))
    except Exception as e:
        print(">>> ERROR SQL BILINGUE:", e)
    return alumnos

def obtener_alumnos_colegio():
    query = """
    SELECT TOP (100) PERCENT d.PersonaID,
           ISNULL(d.Nombre1, '') + 
           CASE WHEN d.Nombre2 IS NOT NULL AND d.Nombre2 <> '' THEN ' ' + d.Nombre2 ELSE '' END + ' ' +
           ISNULL(d.Apellido1, '') + 
           CASE WHEN d.Apellido2 IS NOT NULL AND d.Apellido2 <> '' THEN ' ' + d.Apellido2 ELSE '' END AS NombreCompl,
           da.Descripcion AS AreaDesc, c.CrsoNumero, c.GrupoNumero
      FROM dbo.tblPrsDtosGen AS d
     INNER JOIN dbo.tblPrsTipo           AS t  ON d.PersonaID = t.PersonaID
     INNER JOIN dbo.tblEdcArea           AS a  ON t.IngrEgrID  = a.IngrEgrID
     INNER JOIN dbo.tblEdcEjecCrso       AS ec ON a.AreaID     = ec.AreaID
     INNER JOIN dbo.tblEdcCrso           AS c  ON ec.CrsoID    = c.CrsoID
     INNER JOIN dbo.tblEdcDescripAreaEdc AS da ON a.DescrAreaEdcID = da.DescrAreaEdcID
     WHERE (d.Alum = 1) 
       AND (DATEPART(yy, c.FechaInicio) = DATEPART(yyyy, GETDATE()))
       AND (da.Descripcion IN (N'Colegio', N'Bachillerato')) 
       AND (ec.Desertor = 0) AND (ec.TrasladoPer = 0)
     ORDER BY AreaDesc, c.CrsoNumero, c.GrupoNumero, NombreCompl
    """
    alumnos = []
    try:
        with connections['padres_sqlserver'].cursor() as cursor:
            cursor.execute(query)
            for pid, nombre, area, crso, grupo in cursor.fetchall():
                label = f"{nombre.strip()} ({area}) - {crso}{grupo}"
                alumnos.append((pid, label))
    except Exception as e:
        print(">>> ERROR SQL COLEGIO:", e)
    return alumnos

def obtener_materias(area):
    # Materias de MySQL (sponsors2)
    table = "citas_billingue_subject_bl" if area == 'bilingue' else "citas_colegio_subject_col"
    sql = f"SELECT id, nombre FROM sponsors2.{table} ORDER BY nombre"
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute(sql)
            return [(str(row[0]), row[1]) for row in cursor.fetchall()]
    except Exception as e:
        print(">>> ERROR SQL MATERIAS:", e)
        return []

def obtener_docentes_por_materia(area, materia_id):
    # Docentes de MySQL (sponsors2), filtrados por materia
    if area == 'bilingue':
        table = "citas_billingue_teacher_bl"
        subject_col = "subject_id"
    else:
        table = "citas_colegio_teacher_col"
        subject_col = "subject_id"
    sql = f"SELECT id, nombre FROM sponsors2.{table} WHERE {subject_col} = %s ORDER BY nombre"
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute(sql, [materia_id])
            return [(str(row[0]), row[1]) for row in cursor.fetchall()]
    except Exception as e:
        print(">>> ERROR SQL DOCENTES:", e)
        return []

# ————————————————————————————————
# DASHBOARDS
# ————————————————————————————————

@login_required
def dashboard_coordinador_bilingue(request):
    return render(request, 'conducta/dashboard_coordinador_bilingue.html')

@login_required
def dashboard_coordinador_colegio(request):
    return render(request, 'conducta/dashboard_coordinador_colegio.html')

@login_required
def dashboard_maestro(request):
    user = request.user
    area = None
    if user.groups.filter(name='maestros_bilingue').exists():
        area = 'bilingue'
    elif user.groups.filter(name='maestros_colegio').exists():
        area = 'colegio'
    return render(request, 'conducta/dashboard_maestros.html', {'area': area})

# ————————————————————————————————
# FORMULARIOS DE REPORTES
# ————————————————————————————————

@login_required
def reporte_informativo_bilingue(request):
    area = 'bilingue'
    alumnos_choices  = obtener_alumnos_bilingue()
    materias_choices = obtener_materias(area)
    docentes_choices = []
    fecha = timezone.now().strftime("%Y-%m-%dT%H:%M")
    if request.method == 'POST':
        form = ReporteInformativoForm(
            alumnos_choices=alumnos_choices,
            materias_choices=materias_choices,
            docentes_choices=docentes_choices,
            data=request.POST
        )
        if form.is_valid():
            # Guardar el reporte aquí
            pass
    else:
        form = ReporteInformativoForm(
            alumnos_choices=alumnos_choices,
            materias_choices=materias_choices,
            docentes_choices=docentes_choices,
            initial={'fecha': fecha}
        )
    return render(request, 'conducta/form_informativo.html', {
        'form': form,
        'area': area,
    })

@login_required
def reporte_informativo_colegio(request):
    area = 'colegio'
    alumnos_choices  = obtener_alumnos_colegio()
    materias_choices = obtener_materias(area)
    docentes_choices = []
    fecha = timezone.now().strftime("%Y-%m-%dT%H:%M")
    if request.method == 'POST':
        form = ReporteInformativoForm(
            alumnos_choices=alumnos_choices,
            materias_choices=materias_choices,
            docentes_choices=docentes_choices,
            data=request.POST
        )
        if form.is_valid():
            # Guardar el reporte aquí
            pass
    else:
        form = ReporteInformativoForm(
            alumnos_choices=alumnos_choices,
            materias_choices=materias_choices,
            docentes_choices=docentes_choices,
            initial={'fecha': fecha}
        )
    return render(request, 'conducta/form_informativo.html', {
        'form': form,
        'area': area,
    })

# AJAX: docentes por materia
@login_required
def ajax_docentes_por_materia(request):
    materia_id = request.GET.get('materia_id')
    area = request.GET.get('area')
    docentes = obtener_docentes_por_materia(area, materia_id)
    return JsonResponse({'docentes': docentes})

# AJAX: grado según alumno
@login_required
def ajax_grado_alumno(request):
    alumno_id = request.GET.get('alumno_id')
    # TODO: Consultar el grado real del alumno usando SQL Server, igual que en Atención Médica
    grado = ""
    # Aquí la lógica real para consultar el grado por el alumno_id
    # ...
    return JsonResponse({'grado': grado})

# ————————————————————————————————
# RESTO DE VISTAS (igual)
# ————————————————————————————————

@login_required
def reporte_conductual_bilingue(request):
    # ... igual que informativo, pero con ReporteConductualForm ...
    pass

@login_required
def reporte_conductual_colegio(request):
    # ... igual que informativo, pero con ReporteConductualForm ...
    pass

@login_required
def progress_report_bilingue(request):
    # ... igual pero con ProgressReportForm ...
    pass

@login_required
def historial_maestro_bilingue(request):
    return render(request, 'conducta/historial_maestro.html')

@login_required
def historial_maestro_colegio(request):
    return render(request, 'conducta/historial_maestro.html')

@login_required
def historial_conductual_coordinador_bilingue(request):
    return render(request, 'conducta/lista_reportes.html')

@login_required
def historial_conductual_coordinador_colegio(request):
    return render(request, 'conducta/lista_reportes.html')

@login_required
def historial_informativo_coordinador_bilingue(request):
    return render(request, 'conducta/lista_reportes.html')

@login_required
def historial_informativo_coordinador_colegio(request):
    return render(request, 'conducta/lista_reportes.html')

@login_required
def historial_progress_coordinador_bilingue(request):
    return render(request, 'conducta/lista_reportes.html')

@login_required
def reporte_general_tres_faltas_bilingue(request):
    return render(request, 'conducta/reporte_general.html')

@login_required
def reporte_general_tres_faltas_colegio(request):
    return render(request, 'conducta/reporte_general.html')

@login_required
def detalle_reporte(request, pk):
    return render(request, 'conducta/detalle_reporte.html')

@login_required
def editar_reporte(request, pk):
    return render(request, 'conducta/editar_reporte.html')

@login_required
def descargar_pdf_reporte(request, pk):
    return render(request, 'conducta/descargar_pdf.html')
