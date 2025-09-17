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
    IncisoConductual,
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
                label = nombre.strip()
                grado = f"{area} {crso}-{grupo}"
                alumnos.append({'id': str(pid), 'label': label, 'grado': grado})
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
                label = nombre.strip()
                grado = f"{area} {crso}-{grupo}"
                alumnos.append({'id': str(pid), 'label': label, 'grado': grado})
    except Exception as e:
        print(">>> ERROR SQL COLEGIO:", e)
    return alumnos

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
# DASHBOARDS Y FORMULARIOS
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

# ------------ REPORTE INFORMATIVO  ------------

@login_required
def reporte_informativo_bilingue(request):
    area = 'bilingue'
    students = obtener_alumnos_bilingue()  
    materia_docente_choices = get_materia_docente_choices(area)
    fecha = timezone.now().strftime("%Y-%m-%dT%H:%M")

    if request.method == 'POST':
        alumno_id = request.POST.get('alumno')
        grado = request.POST.get('grado')
        materia_docente_id = request.POST.get('materia_docente')
        comentario = request.POST.get('comentario', "")
        alumno_obj = next((a for a in students if a['id'] == alumno_id), None)
        alumno_label = alumno_obj['label'] if alumno_obj else ""
        materia = docente = ""
        if materia_docente_id:
            md_obj = MateriaDocenteBilingue.objects.filter(pk=materia_docente_id).first()
            if md_obj:
                materia = md_obj.materia
                docente = md_obj.docente
        ReporteInformativo.objects.create(
            usuario=request.user,
            area=area,
            alumno_id=alumno_id,
            alumno_nombre=alumno_label,
            grado=grado,
            materia=materia,
            docente=docente,
            comentario=comentario
        )
        messages.success(request, "¡Reporte registrado correctamente!")
        return redirect('reporte_informativo_bilingue')

    return render(request, 'conducta/form_informativo.html', {
        'students': students,    
        'materia_docente_choices': materia_docente_choices,
        'fecha': fecha,
        'area': area,
    })

@login_required
def reporte_informativo_colegio(request):
    area = 'colegio'
    students = obtener_alumnos_colegio()
    materia_docente_choices = get_materia_docente_choices(area)
    fecha = timezone.now().strftime("%Y-%m-%dT%H:%M")

    if request.method == 'POST':
        alumno_id = request.POST.get('alumno')
        grado = request.POST.get('grado')
        materia_docente_id = request.POST.get('materia_docente')
        comentario = request.POST.get('comentario', "")
        alumno_obj = next((a for a in students if a['id'] == alumno_id), None)
        alumno_label = alumno_obj['label'] if alumno_obj else ""
        materia = docente = ""
        if materia_docente_id:
            md_obj = MateriaDocenteColegio.objects.filter(pk=materia_docente_id).first()
            if md_obj:
                materia = md_obj.materia
                docente = md_obj.docente
        ReporteInformativo.objects.create(
            usuario=request.user,
            area=area,
            alumno_id=alumno_id,
            alumno_nombre=alumno_label,
            grado=grado,
            materia=materia,
            docente=docente,
            comentario=comentario
        )
        messages.success(request, "¡Reporte registrado correctamente!")
        return redirect('reporte_informativo_colegio')

    return render(request, 'conducta/form_informativo.html', {
        'students': students,
        'materia_docente_choices': materia_docente_choices,
        'fecha': fecha,
        'area': area,
    })

# ------------ REPORTE CONDUCTUAL  ------------

@login_required
def reporte_conductual_bilingue(request):
    area = 'bilingue'
    students = obtener_alumnos_bilingue()
    materia_docente_choices = get_materia_docente_choices(area)
    fecha = timezone.now().strftime("%Y-%m-%d")
    # Obtiene incisos por severidad
    incisos_leve = IncisoConductual.objects.filter(activo=True, tipo='leve').order_by('descripcion')
    incisos_grave = IncisoConductual.objects.filter(activo=True, tipo='grave').order_by('descripcion')
    incisos_muygrave = IncisoConductual.objects.filter(activo=True, tipo='muy_grave').order_by('descripcion')

    if request.method == 'POST':
        alumno_id = request.POST.get('alumno')
        grado = request.POST.get('grado')
        materia_docente_id = request.POST.get('materia_docente')
        fecha_val = request.POST.get('fecha')
        comentario = request.POST.get('comentario', "")

        # Obtén las listas seleccionadas si el checkbox está activo
        ids_leve = request.POST.getlist('inciso_leve[]') if request.POST.get('chk_leve') else []
        ids_grave = request.POST.getlist('inciso_grave[]') if request.POST.get('chk_grave') else []
        ids_muygrave = request.POST.getlist('inciso_muygrave[]') if request.POST.get('chk_muygrave') else []

        alumno_obj = next((a for a in students if a['id'] == alumno_id), None)
        alumno_label = alumno_obj['label'] if alumno_obj else ""
        materia = docente = ""
        if materia_docente_id:
            md_obj = MateriaDocenteBilingue.objects.filter(pk=materia_docente_id).first()
            if md_obj:
                materia = md_obj.materia
                docente = md_obj.docente

        # Crea el reporte sin los ManyToMany
        reporte = ReporteConductual.objects.create(
            usuario=request.user,
            area=area,
            alumno_id=alumno_id,
            alumno_nombre=alumno_label,
            grado=grado,
            materia=materia,
            docente=docente,
            fecha=fecha_val,
            comentario=comentario,
        )
        # Asocia los incisos ManyToMany
        if ids_leve:
            reporte.incisos_leve.set(ids_leve)
        if ids_grave:
            reporte.incisos_grave.set(ids_grave)
        if ids_muygrave:
            reporte.incisos_muygrave.set(ids_muygrave)

        messages.success(request, "¡Reporte conductual registrado correctamente!")
        return redirect('reporte_conductual_bilingue')

    return render(request, 'conducta/form_conductual.html', {
        'students': students,
        'materia_docente_choices': materia_docente_choices,
        'fecha': fecha,
        'area': area,
        'incisos_leve': incisos_leve,
        'incisos_grave': incisos_grave,
        'incisos_muygrave': incisos_muygrave,
    })

@login_required
def reporte_conductual_colegio(request):
    area = 'colegio'
    students = obtener_alumnos_colegio()
    materia_docente_choices = get_materia_docente_choices(area)
    fecha = timezone.now().strftime("%Y-%m-%d")
    incisos_leve = IncisoConductual.objects.filter(activo=True, tipo='leve').order_by('descripcion')
    incisos_grave = IncisoConductual.objects.filter(activo=True, tipo='grave').order_by('descripcion')
    incisos_muygrave = IncisoConductual.objects.filter(activo=True, tipo='muy_grave').order_by('descripcion')

    if request.method == 'POST':
        alumno_id = request.POST.get('alumno')
        grado = request.POST.get('grado')
        materia_docente_id = request.POST.get('materia_docente')
        fecha_val = request.POST.get('fecha')
        comentario = request.POST.get('comentario', "")

        ids_leve = request.POST.getlist('inciso_leve[]') if request.POST.get('chk_leve') else []
        ids_grave = request.POST.getlist('inciso_grave[]') if request.POST.get('chk_grave') else []
        ids_muygrave = request.POST.getlist('inciso_muygrave[]') if request.POST.get('chk_muygrave') else []

        alumno_obj = next((a for a in students if a['id'] == alumno_id), None)
        alumno_label = alumno_obj['label'] if alumno_obj else ""
        materia = docente = ""
        if materia_docente_id:
            md_obj = MateriaDocenteColegio.objects.filter(pk=materia_docente_id).first()
            if md_obj:
                materia = md_obj.materia
                docente = md_obj.docente

        reporte = ReporteConductual.objects.create(
            usuario=request.user,
            area=area,
            alumno_id=alumno_id,
            alumno_nombre=alumno_label,
            grado=grado,
            materia=materia,
            docente=docente,
            fecha=fecha_val,
            comentario=comentario,
        )
        if ids_leve:
            reporte.incisos_leve.set(ids_leve)
        if ids_grave:
            reporte.incisos_grave.set(ids_grave)
        if ids_muygrave:
            reporte.incisos_muygrave.set(ids_muygrave)

        messages.success(request, "¡Reporte conductual registrado correctamente!")
        return redirect('reporte_conductual_colegio')

    return render(request, 'conducta/form_conductual.html', {
        'students': students,
        'materia_docente_choices': materia_docente_choices,
        'fecha': fecha,
        'area': area,
        'incisos_leve': incisos_leve,
        'incisos_grave': incisos_grave,
        'incisos_muygrave': incisos_muygrave,
    })


#-------------- PROGRESS REPORT -----------------

@login_required
def progress_report_bilingue(request):
    MATERIAS_PRIMARIA = [
        "Math", "Phonics", "Spelling", "Reading", "Language",
        "Science", "Español", "CCSS", "Asociadas"
    ]
    MATERIAS_COLEGIO = [
        "Math", "Spelling", "Reading", "Language", "Science",
        "Español", "CCSS", "Cívica", "Asociadas"
    ]

    students = obtener_alumnos_bilingue()
    alumnos_choices = [(s['id'], s['label']) for s in students]

    materias = MATERIAS_PRIMARIA
    grado = ""
    alumno_id = ""
    if request.method == 'POST':
        form = ProgressReportForm(alumnos_choices=alumnos_choices, data=request.POST)
        alumno_id = request.POST.get('alumno')
        grado = request.POST.get('grado', '')
        if alumno_id:
            alumno_obj = next((s for s in students if s['id'] == alumno_id), None)
            if alumno_obj:
                grado = alumno_obj['grado']
        if grado and ("Primaria" in grado or "Preescolar" in grado):
            materias = MATERIAS_PRIMARIA
        else:
            materias = MATERIAS_COLEGIO

        if form.is_valid():
            # Procesar materias
            materias_list = []
            for materia in materias:
                if materia == "Asociadas":
                    # Inputs dinámicos: asociadas[], asociadas_comentario[]
                    asociadas = request.POST.getlist('asociadas[]')
                    asociadas_comentario = request.POST.getlist('asociadas_comentario[]')
                    for idx in range(len(asociadas)):
                        nombre = asociadas[idx]
                        comentario = asociadas_comentario[idx] if idx < len(asociadas_comentario) else ""
                        materias_list.append({
                            'materia': 'Asociadas',
                            'asignacion': nombre,
                            'comentario': comentario,
                        })
                else:
                    asignacion = request.POST.get(f"asignacion_{materia}", "")
                    comentario = request.POST.get(f"comentario_{materia}", "")
                    materias_list.append({
                        'materia': materia,
                        'asignacion': asignacion,
                        'comentario': comentario,
                    })
            semana_inicio = form.cleaned_data.get('semana_inicio')
            semana_fin = form.cleaned_data.get('semana_fin')
            comentario_general = form.cleaned_data.get('comentario_general', "")
            alumno_id = form.cleaned_data.get('alumno')
            alumno_obj = next((s for s in students if s['id'] == alumno_id), None)
            alumno_label = alumno_obj['label'] if alumno_obj else ""
            grado = form.cleaned_data.get('grado')
            # Guarda el ProgressReport con JSON
            ProgressReport.objects.create(
                usuario=request.user,
                alumno_id=alumno_id,
                alumno_nombre=alumno_label,
                grado=grado,
                semana_inicio=semana_inicio,
                semana_fin=semana_fin,
                comentario_general=comentario_general,
                materias_json=materias_list
            )
            messages.success(request, "¡Progress report registrado correctamente!")
            return redirect('progress_report_bilingue')
    else:
        form = ProgressReportForm(alumnos_choices=alumnos_choices)
        materias = MATERIAS_PRIMARIA

    return render(request, 'conducta/form_progress.html', {
        'form': form,
        'materias': materias,
        'students': students,
        'grado': grado,
    })


#-------------- HISTORIAL MAESTROS -----------------

@login_required
def historial_maestro_bilingue(request):
    usuario = request.user
    # Puedes filtrar más si tienes campos de área en los modelos
    reportes_informativo = ReporteInformativo.objects.filter(usuario=usuario, area='bilingue').order_by('-fecha')
    reportes_conductual = ReporteConductual.objects.filter(usuario=usuario, area='bilingue').order_by('-fecha')
    reportes_progress = ProgressReport.objects.filter(usuario=usuario).order_by('-fecha')  # Solo bilingüe tiene progress

    return render(request, 'conducta/historial_maestro.html', {
        'reportes_informativo': reportes_informativo,
        'reportes_conductual': reportes_conductual,
        'reportes_progress': reportes_progress,
        'area': 'bilingue',
    })

@login_required
def historial_maestro_colegio(request):
    usuario = request.user
    reportes_informativo = ReporteInformativo.objects.filter(usuario=usuario, area='colegio').order_by('-fecha')
    reportes_conductual = ReporteConductual.objects.filter(usuario=usuario, area='colegio').order_by('-fecha')
    # No incluye progress, porque solo se usa en bilingüe

    return render(request, 'conducta/historial_maestro.html', {
        'reportes_informativo': reportes_informativo,
        'reportes_conductual': reportes_conductual,
        'reportes_progress': [],  # vacía si quieres usar la misma plantilla
        'area': 'colegio',
    })



# ----------- funciones secundarias -----------
from django.http import HttpResponse

@login_required
def editar_reporte_informativo(request, pk):
    return HttpResponse("Editar Reporte Informativo #{}".format(pk))

@login_required
def descargar_pdf_informativo(request, pk):
    return HttpResponse("PDF Reporte Informativo #{}".format(pk))

@login_required
def editar_reporte_conductual(request, pk):
    return HttpResponse("Editar Reporte Conductual #{}".format(pk))

@login_required
def descargar_pdf_conductual(request, pk):
    return HttpResponse("PDF Reporte Conductual #{}".format(pk))

@login_required
def editar_progress_report(request, pk):
    return HttpResponse("Editar Progress Report #{}".format(pk))

@login_required
def descargar_pdf_progress(request, pk):
    return HttpResponse("PDF Progress Report #{}".format(pk))



#--------------  DASHBOARD COORDINADOR -----------------

@login_required
def dashboard_coordinador_bilingue(request):
    return render(request, 'conducta/dashboard_coordinador_bilingue.html')

@login_required
def dashboard_coordinador_colegio(request):
    return render(request, 'conducta/dashboard_coordinador_colegio.html')


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
