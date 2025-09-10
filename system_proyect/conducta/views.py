from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connections
from django.utils import timezone
from .forms import (
    ReporteInformativoForm,
    ReporteConductualForm,
    ProgressReportForm
)
from .models import (
    ReporteInformativo,
    ReporteConductual,
    ProgressReport,
    MateriaDocenteBilingue,
    MateriaDocenteColegio
)

# ---------------------------
# FUNCIONES AUXILIARES
# ---------------------------

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
                grado = f"{area} {crso}-{grupo}"
                alumnos.append((str(pid), label, grado))
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
                grado = f"{area} {crso}-{grupo}"
                alumnos.append((str(pid), label, grado))
    except Exception as e:
        print(">>> ERROR SQL COLEGIO:", e)
    return alumnos

def obtener_grado_alumno(alumno_id):
    query = """
    SELECT TOP 1 da.Descripcion, c.CrsoNumero, c.GrupoNumero
      FROM dbo.tblPrsDtosGen AS d
      JOIN dbo.tblPrsTipo           AS t  ON d.PersonaID = t.PersonaID
      JOIN dbo.tblEdcArea           AS a  ON t.IngrEgrID  = a.IngrEgrID
      JOIN dbo.tblEdcEjecCrso       AS ec ON a.AreaID     = ec.AreaID
      JOIN dbo.tblEdcCrso           AS c  ON ec.CrsoID    = c.CrsoID
      JOIN dbo.tblEdcDescripAreaEdc AS da ON a.DescrAreaEdcID = da.DescrAreaEdcID
     WHERE d.PersonaID = %s
     ORDER BY ec.FechaInicio DESC
    """
    try:
        with connections['padres_sqlserver'].cursor() as cursor:
            cursor.execute(query, [alumno_id])
            row = cursor.fetchone()
            if row:
                area, crso, grupo = row
                return f"{area} {crso}-{grupo}"
    except Exception as e:
        print(">>> ERROR SQL GRADO:", e)
    return ""

def get_materia_docente_choices(area):
    if area == 'bilingue':
        return [
            (str(md.pk), f"{md.materia} — {md.docente}")
            for md in MateriaDocenteBilingue.objects.filter(activo=True)
        ]
    else:
        return [
            (str(md.pk), f"{md.materia} — {md.docente}")
            for md in MateriaDocenteColegio.objects.filter(activo=True)
        ]

# ---------------------------
# DASHBOARDS Y REPORTES
# ---------------------------

@login_required
def dashboard_maestro(request):
    user = request.user
    area = None
    if user.groups.filter(name='maestros_bilingue').exists():
        area = 'bilingue'
    elif user.groups.filter(name='maestros_colegio').exists():
        area = 'colegio'
    return render(request, 'conducta/dashboard_maestros.html', {'area': area})

@login_required
def dashboard_coordinador_bilingue(request):
    return render(request, 'conducta/dashboard_coordinador_bilingue.html')

@login_required
def dashboard_coordinador_colegio(request):
    return render(request, 'conducta/dashboard_coordinador_colegio.html')

# ------------ REPORTE INFORMATIVO --------------

@login_required
def reporte_informativo_bilingue(request):
    area = 'bilingue'
    alumnos = obtener_alumnos_bilingue()  # [(id, label, grado)]
    alumnos_choices = [(a[0], a[1]) for a in alumnos]
    materia_docente_choices = get_materia_docente_choices(area)
    fecha = timezone.now().strftime("%Y-%m-%dT%H:%M")

    if request.method == 'POST':
        form = ReporteInformativoForm(
            alumnos_choices=alumnos_choices,
            materia_docente_choices=materia_docente_choices,
            data=request.POST
        )
        if form.is_valid():
            alumno_id = form.cleaned_data['alumno']
            alumno_obj = next((a for a in alumnos if a[0] == alumno_id), None)
            alumno_label = alumno_obj[1] if alumno_obj else ""
            grado = alumno_obj[2] if alumno_obj else ""
            materia_docente_id = form.cleaned_data['materia_docente']
            md_obj = MateriaDocenteBilingue.objects.filter(pk=materia_docente_id).first() if materia_docente_id else None
            materia = md_obj.materia if md_obj else ""
            docente = md_obj.docente if md_obj else ""
            ReporteInformativo.objects.create(
                usuario=request.user,
                area=area,
                alumno_id=alumno_id,
                alumno_nombre=alumno_label,
                grado=grado,
                materia=materia,
                docente=docente,
                comentario=form.cleaned_data.get('comentario', "")
            )
            messages.success(request, "¡Reporte registrado correctamente!")
            return redirect('reporte_informativo_bilingue')
    else:
        form = ReporteInformativoForm(
            alumnos_choices=alumnos_choices,
            materia_docente_choices=materia_docente_choices,
            initial={'fecha': fecha}
        )

    return render(request, 'conducta/form_informativo.html', {
        'form': form,
        'area': area,
    })

@login_required
def reporte_informativo_colegio(request):
    area = 'colegio'
    alumnos = obtener_alumnos_colegio()  # [(id, label, grado)]
    alumnos_choices = [(a[0], a[1]) for a in alumnos]
    materia_docente_choices = get_materia_docente_choices(area)
    fecha = timezone.now().strftime("%Y-%m-%dT%H:%M")

    if request.method == 'POST':
        form = ReporteInformativoForm(
            alumnos_choices=alumnos_choices,
            materia_docente_choices=materia_docente_choices,
            data=request.POST
        )
        if form.is_valid():
            alumno_id = form.cleaned_data['alumno']
            alumno_obj = next((a for a in alumnos if a[0] == alumno_id), None)
            alumno_label = alumno_obj[1] if alumno_obj else ""
            grado = alumno_obj[2] if alumno_obj else ""
            materia_docente_id = form.cleaned_data['materia_docente']
            md_obj = MateriaDocenteColegio.objects.filter(pk=materia_docente_id).first() if materia_docente_id else None
            materia = md_obj.materia if md_obj else ""
            docente = md_obj.docente if md_obj else ""
            ReporteInformativo.objects.create(
                usuario=request.user,
                area=area,
                alumno_id=alumno_id,
                alumno_nombre=alumno_label,
                grado=grado,
                materia=materia,
                docente=docente,
                comentario=form.cleaned_data.get('comentario', "")
            )
            messages.success(request, "¡Reporte registrado correctamente!")
            return redirect('reporte_informativo_colegio')
    else:
        form = ReporteInformativoForm(
            alumnos_choices=alumnos_choices,
            materia_docente_choices=materia_docente_choices,
            initial={'fecha': fecha}
        )

    return render(request, 'conducta/form_informativo.html', {
        'form': form,
        'area': area,
    })

# ------------ AJAX: Grado Automático ------------

@login_required
def ajax_grado_alumno(request):
    alumno_id = request.GET.get('alumno_id')
    grado = ""
    if alumno_id:
        grado = obtener_grado_alumno(alumno_id)
    return JsonResponse({'grado': grado})

# ------------ RESTO DE VISTAS, IGUAL ------------

@login_required
def reporte_conductual_bilingue(request):
    pass

@login_required
def reporte_conductual_colegio(request):
    pass

@login_required
def progress_report_bilingue(request):
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
