from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
import io, os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from django.db import connections
from django.db.models import Count
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
from tickets.models import Ticket


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
    reportes_informativo = ReporteInformativo.objects.filter(usuario=usuario, area='bilingue').order_by('-fecha')
    reportes_conductual = ReporteConductual.objects.filter(usuario=usuario, area='bilingue').order_by('-fecha')
    reportes_progress = ProgressReport.objects.filter(usuario=usuario).order_by('-fecha')

    # AGREGA ESTA LÍNEA (ajusta el filtro si tienes FK usuario)
    tickets_usuario = Ticket.objects.filter(email=usuario.email).order_by('-created_at')

    return render(request, 'conducta/historial_maestro.html', {
        'reportes_informativo': reportes_informativo,
        'reportes_conductual': reportes_conductual,
        'reportes_progress': reportes_progress,
        'tickets_usuario': tickets_usuario,      # <- AGREGA AQUÍ
        'area': 'bilingue',
    })

@login_required
def historial_maestro_colegio(request):
    usuario = request.user
    reportes_informativo = ReporteInformativo.objects.filter(usuario=usuario, area='colegio').order_by('-fecha')
    reportes_conductual = ReporteConductual.objects.filter(usuario=usuario, area='colegio').order_by('-fecha')

    tickets_usuario = Ticket.objects.filter(email=usuario.email).order_by('-created_at')

    return render(request, 'conducta/historial_maestro.html', {
        'reportes_informativo': reportes_informativo,
        'reportes_conductual': reportes_conductual,
        'reportes_progress': [],   # vacía para mantener compatibilidad
        'tickets_usuario': tickets_usuario,      # <- AGREGA AQUÍ
        'area': 'colegio',
    })

# ----------- EDITOR DE REPORTES ( SOLO COORDINADOR) -----------
def es_coordinador(user):
    return user.groups.filter(name="Coordinador").exists()

@login_required
def editar_reporte_conductual(request, pk):
    try:
        reporte = get_object_or_404(ReporteConductual, pk=pk)
        alumnos_choices = [(reporte.alumno_id, reporte.alumno_nombre)]
        materia_docente_choices = [(reporte.materia, f"{reporte.materia} – {reporte.docente}")]
        if request.method == 'POST':
            form = ReporteConductualForm(request.POST, alumnos_choices=alumnos_choices, materia_docente_choices=materia_docente_choices)
            if form.is_valid():
                reporte.comentario = form.cleaned_data['comentario']
                if es_coordinador(request.user):
                    reporte.coordinador_firma = form.cleaned_data['coordinador_firma']
                    reporte.estado = form.cleaned_data['estado']
                reporte.save()
                messages.success(request, "Reporte conductual actualizado correctamente.")
                return redirect('dashboard_coordinador', area=reporte.area)
        else:
            initial = {
                'fecha': reporte.fecha,
                'alumno': reporte.alumno_id,
                'grado': reporte.grado,
                'materia_docente': reporte.materia,
                'comentario': reporte.comentario,
                'coordinador_firma': reporte.coordinador_firma,
                'estado': reporte.estado,
            }
            form = ReporteConductualForm(initial=initial, alumnos_choices=alumnos_choices, materia_docente_choices=materia_docente_choices)
        return render(request, 'conducta/editor_conductual.html', {
            'form': form,
            'reporte': reporte,
            'es_coordinador': es_coordinador(request.user),
        })
    except Exception as e:
        import traceback
        return HttpResponse(f"<pre>{e}\n\n{traceback.format_exc()}</pre>")


@login_required
def editar_reporte_informativo(request, pk):
    try:
        reporte = get_object_or_404(ReporteInformativo, pk=pk)
        alumnos_choices = [(reporte.alumno_id, reporte.alumno_nombre)]
        materia_docente_choices = [(reporte.materia, f"{reporte.materia} – {reporte.docente}")]
        if request.method == 'POST':
            form = ReporteInformativoForm(request.POST, alumnos_choices=alumnos_choices, materia_docente_choices=materia_docente_choices)
            if form.is_valid():
                reporte.comentario = form.cleaned_data['comentario']
                if es_coordinador(request.user):
                    reporte.coordinador_firma = form.cleaned_data['coordinador_firma']
                    reporte.estado = form.cleaned_data['estado']
                reporte.save()
                messages.success(request, "Reporte informativo actualizado correctamente.")
                return redirect('dashboard_coordinador', area=reporte.area)
        else:
            initial = {
                'fecha': reporte.fecha,
                'alumno': reporte.alumno_id,
                'grado': reporte.grado,
                'materia_docente': reporte.materia,
                'comentario': reporte.comentario,
                'coordinador_firma': reporte.coordinador_firma,
                'estado': reporte.estado,
            }
            form = ReporteInformativoForm(initial=initial, alumnos_choices=alumnos_choices, materia_docente_choices=materia_docente_choices)
        return render(request, 'conducta/editor_informativo.html', {
            'form': form,
            'reporte': reporte,
            'es_coordinador': es_coordinador(request.user),
        })
    except Exception as e:
        import traceback
        return HttpResponse(f"<pre>{e}\n\n{traceback.format_exc()}</pre>")


@login_required
def editar_progress_report(request, pk):
    try:
        reporte = get_object_or_404(ProgressReport, pk=pk)
        alumnos_choices = [(reporte.alumno_id, reporte.alumno_nombre)]
        if request.method == 'POST':
            form = ProgressReportForm(request.POST, alumnos_choices=alumnos_choices)
            if form.is_valid():
                reporte.comentario_general = form.cleaned_data['comentario_general']
                if es_coordinador(request.user):
                    reporte.coordinador_firma = form.cleaned_data['coordinador_firma']
                    reporte.estado = form.cleaned_data['estado']
                reporte.save()
                messages.success(request, "Progress report actualizado correctamente.")
                return redirect('dashboard_coordinador', area='bilingue')
        else:
            initial = {
                'fecha': reporte.fecha,
                'alumno': reporte.alumno_id,
                'grado': reporte.grado,
                'semana_inicio': reporte.semana_inicio,
                'semana_fin': reporte.semana_fin,
                'comentario_general': reporte.comentario_general,
                'coordinador_firma': reporte.coordinador_firma,
                'estado': reporte.estado,
            }
            form = ProgressReportForm(initial=initial, alumnos_choices=alumnos_choices)
        return render(request, 'conducta/editor_progress.html', {
            'form': form,
            'reporte': reporte,
            'es_coordinador': es_coordinador(request.user),
        })
    except Exception as e:
        import traceback
        return HttpResponse(f"<pre>{e}\n\n{traceback.format_exc()}</pre>")


# -----------  DESCARGA EN PDF  -----------

@login_required
def descargar_pdf_informativo(request, pk):
    from .models import ReporteInformativo
    reporte = get_object_or_404(ReporteInformativo, pk=pk)
    buf = io.BytesIO()
    w, h = letter
    pdf = canvas.Canvas(buf, pagesize=letter)
    pdf.setTitle("reporte_informativo.pdf")

    # Logo centrado
    width_logo = 35 * mm
    height_logo = 35 * mm
    x_logo = (w - width_logo) / 2
    logo_path = os.path.join(settings.STATIC_ROOT, "conducta/img/ana-transformed.png")
    if os.path.exists(logo_path):
        pdf.drawImage(
            logo_path,
            x=x_logo,
            y=h-40*mm,
            width=width_logo,
            height=height_logo,
            mask='auto'
        )
    y_actual = h - 48*mm

    # Título y datos
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(w/2, y_actual, "Nuevo Amanecer School" if reporte.area == "bilingue" else "C.E.M.N.G Nuevo Amanecer")
    y_actual -= 12*mm
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(w/2, y_actual, "Reporte informativo")
    y_actual -= 15*mm

    pdf.setFont("Helvetica", 11)
    pdf.drawString(32*mm, y_actual, f"Nombre: {reporte.alumno_nombre}")
    pdf.drawString(110*mm, y_actual, f"Grado: {reporte.grado}")
    y_actual -= 8*mm
    pdf.drawString(32*mm, y_actual, f"Docente: {reporte.docente or ''}")
    pdf.drawString(110*mm, y_actual, f"Fecha: {reporte.fecha.strftime('%d/%m/%Y') if reporte.fecha else ''}")
    y_actual -= 8*mm
    pdf.drawString(32*mm, y_actual, "Comentario:")
    y_actual -= 7*mm

    pdf.setFont("Helvetica-Oblique", 10)
    for line in reporte.comentario.split('\n'):
        pdf.drawString(38*mm, y_actual, line)
        y_actual -= 5*mm

    # -------- FIRMA DOCENTE --------
    y_firma = 35 * mm
    x_firma = 38 * mm
    largo_firma = 60 * mm

    # Línea de firma
    pdf.setStrokeColor(colors.black)
    pdf.setLineWidth(0.7)
    pdf.line(x_firma, y_firma, x_firma + largo_firma, y_firma)

    # Texto debajo de la línea (firma del docente)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(x_firma, y_firma - 5*mm, "Firma del Docente:")
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x_firma + 32*mm, y_firma - 5*mm, f"{reporte.docente or ''}")

    pdf.save()
    buf.seek(0)
    return HttpResponse(buf, content_type="application/pdf")

def draw_paragraph(pdf, text, x, y, max_width, font="Helvetica", font_size=10, bold=False, italic=False, leading=13):
    """
    Dibuja un párrafo con saltos de línea y justificación manual en ReportLab.
    """
    from reportlab.pdfbase.pdfmetrics import stringWidth
    fontname = font
    if bold and italic:
        fontname = "Helvetica-BoldOblique"
    elif bold:
        fontname = "Helvetica-Bold"
    elif italic:
        fontname = "Helvetica-Oblique"
    pdf.setFont(fontname, font_size)
    lines = []
    for raw_line in text.split('\n'):
        line = ""
        for word in raw_line.split():
            test_line = f"{line} {word}".strip()
            if stringWidth(test_line, fontname, font_size) < max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        lines.append(line)
    for l in lines:
        pdf.drawString(x, y, l)
        y -= leading
    return y


@login_required
def descargar_pdf_conductual_3_strikes(request, pk):
    from .models import ReporteConductual
    reporte = get_object_or_404(ReporteConductual, pk=pk)
    reportes = list(ReporteConductual.objects.filter(
        area=reporte.area,
        alumno_id=reporte.alumno_id
    ).order_by('fecha')[:3])

    if len(reportes) < 3:
        return HttpResponse("Este alumno aún no tiene 3 reportes conductuales.", content_type="text/plain")

    buf = io.BytesIO()
    w, h = letter
    pdf = canvas.Canvas(buf, pagesize=letter)
    pdf.setTitle("reporte_conductual_3_strikes.pdf")

    # Logo centrado
    width_logo = 35 * mm
    height_logo = 35 * mm
    x_logo = (w - width_logo) / 2
    logo_path = os.path.join(settings.STATIC_ROOT, "conducta/img/ana-transformed.png")
    if os.path.exists(logo_path):
        pdf.drawImage(
            logo_path,
            x=x_logo,
            y=h-40*mm,
            width=width_logo,
            height=height_logo,
            mask='auto'
        )
    y_actual = h - 47 * mm

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    titulo = "Nuevo Amanecer School" if reporte.area == "bilingue" else "C.E.M.N.G Nuevo Amanecer"
    pdf.drawCentredString(w/2, y_actual, titulo)
    y_actual -= 12*mm
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(w/2, y_actual, "Reporte conductual – 3 Strikes")
    y_actual -= 10*mm

    # --- CADA REPORTE ---
    for idx, rep in enumerate(reportes, 1):
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(32*mm, y_actual, f"Reporte #{idx} ({', '.join(['Leve' if rep.incisos_leve.exists() else '', 'Grave' if rep.incisos_grave.exists() else '', 'Muy Grave' if rep.incisos_muygrave.exists() else '']).replace(',,',',').strip(', ')})")
        y_actual -= 8*mm

        # Fila: Nombre/Grado/Docente/Fecha
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(32*mm, y_actual, "Nombre:")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(60*mm, y_actual, rep.alumno_nombre)

        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(120*mm, y_actual, "Grado:")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(140*mm, y_actual, rep.grado)
        y_actual -= 6*mm

        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(32*mm, y_actual, "Docente/Materia:")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(75*mm, y_actual, rep.docente)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(120*mm, y_actual, "Fecha:")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(140*mm, y_actual, rep.fecha.strftime('%d/%m/%Y'))
        y_actual -= 7*mm

        # Incisos (párrafo)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(32*mm, y_actual, "Inciso:")
        y_actual -= 6*mm

        incisos = [i.descripcion for i in rep.incisos_leve.all()] + [i.descripcion for i in rep.incisos_grave.all()] + [i.descripcion for i in rep.incisos_muygrave.all()]
        if incisos:
            text_obj = pdf.beginText(38*mm, y_actual)
            text_obj.setFont("Helvetica-BoldOblique", 10)
            wrap_len = 95  # Ajusta a gusto (número de caracteres por línea)
            for inciso in incisos:
                lines = [inciso[i:i+wrap_len] for i in range(0, len(inciso), wrap_len)]
                for ln in lines:
                    text_obj.textLine(ln)
                    y_actual -= 5*mm
            pdf.drawText(text_obj)
            y_actual = text_obj.getY() - 1*mm
        else:
            pdf.setFont("Helvetica", 10)
            pdf.drawString(38*mm, y_actual, "-")
            y_actual -= 5*mm

        # Descripción (Comentario)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(32*mm, y_actual, "Descripción:")
        y_actual -= 5*mm
        if rep.comentario:
            text_obj = pdf.beginText(38*mm, y_actual)
            text_obj.setFont("Helvetica-Oblique", 10)
            for line in rep.comentario.split("\n"):
                text_obj.textLine(line)
                y_actual -= 5*mm
            pdf.drawText(text_obj)
            y_actual = text_obj.getY() - 1*mm
        else:
            pdf.setFont("Helvetica", 10)
            pdf.drawString(38*mm, y_actual, "-")
            y_actual -= 5*mm

        # Espacio entre reportes
        y_actual -= 4*mm
        pdf.setStrokeColor(colors.grey)
        pdf.line(30*mm, y_actual, w-30*mm, y_actual)
        y_actual -= 8*mm

    # FIRMAS PARA LLENAR EN FÍSICO
    y_firmas = 20*mm
    x_firma = [34*mm, 91*mm, 146*mm]
    if reporte.area == "colegio":
        etiquetas = ["Firma Padre de Familia", "Firma del Docente/Orientación", "Firma de Consejería"]
    else:
        etiquetas = ["Firma Padre de Familia", "Firma del Docente", "Firma del Coordinador"]

    for i in range(3):
        pdf.setStrokeColor(colors.black)
        pdf.line(x_firma[i], y_firmas, x_firma[i]+42*mm, y_firmas)
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(x_firma[i]+21*mm, y_firmas-5*mm, etiquetas[i])

    pdf.save()
    buf.seek(0)
    return HttpResponse(buf, content_type="application/pdf")


@login_required
def descargar_pdf_conductual(request, pk):
    from .models import ReporteConductual
    reporte = get_object_or_404(ReporteConductual, pk=pk)
    buf = io.BytesIO()
    w, h = letter
    pdf = canvas.Canvas(buf, pagesize=letter)
    pdf.setTitle("reporte_conductual.pdf")

    width_logo = 35 * mm
    height_logo = 35 * mm
    x_logo = (w - width_logo) / 2
    logo_path = os.path.join(settings.STATIC_ROOT, "conducta/img/ana-transformed.png")
    if os.path.exists(logo_path):
        pdf.drawImage(
            logo_path,
            x=x_logo,
            y=h-40*mm,
            width=width_logo,
            height=height_logo,
            mask='auto'
        )
    y_actual = h - 48*mm

    # --- Título y cabecera ---
    pdf.setFont("Helvetica-Bold", 16)
    titulo = "Nuevo Amanecer School" if reporte.area == "bilingue" else "C.E.M.N.G Nuevo Amanecer"
    pdf.drawCentredString(w/2, y_actual, titulo)
    y_actual -= 12*mm
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(w/2, y_actual, "Reporte conductual")
    y_actual -= 10*mm

    # Datos generales (alineados)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(32*mm, y_actual, "Nombre:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(60*mm, y_actual, reporte.alumno_nombre)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(110*mm, y_actual, "Grado:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(130*mm, y_actual, reporte.grado)
    y_actual -= 7*mm
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(32*mm, y_actual, "Docente:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(60*mm, y_actual, reporte.docente or "")
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(110*mm, y_actual, "Fecha:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(130*mm, y_actual, reporte.fecha.strftime('%d/%m/%Y') if reporte.fecha else '')
    y_actual -= 9*mm

    # Incisos (Leve, Grave, Muy grave)
    maxw = w - 50*mm
    for tipo, label in [("incisos_leve", "Leve"), ("incisos_grave", "Grave"), ("incisos_muygrave", "Muy Grave")]:
        incisos = getattr(reporte, tipo).all()
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(32*mm, y_actual, f"Incisos {label}:")
        y_actual -= 6*mm
        if incisos:
            for i in incisos:
                y_actual = draw_paragraph(
                    pdf, i.descripcion, x=38*mm, y=y_actual, max_width=maxw, font="Helvetica", font_size=10, bold=True, italic=True, leading=11
                )
        else:
            pdf.setFont("Helvetica-Oblique", 10)
            pdf.drawString(38*mm, y_actual, "-")
            y_actual -= 6*mm
        y_actual -= 3*mm

    # Comentario Docente
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(32*mm, y_actual, "Comentario del Docente:")
    y_actual -= 6*mm
    y_actual = draw_paragraph(
        pdf, reporte.comentario or "-", x=38*mm, y=y_actual, max_width=maxw, font="Helvetica", font_size=10, italic=True, leading=11
    )

    # Comentario Coordinador (si existe)
    if hasattr(reporte, 'comentario_coordinador') and reporte.comentario_coordinador:
        pdf.setFont("Helvetica-Bold", 11)
        y_actual -= 4*mm
        pdf.drawString(32*mm, y_actual, "Comentario del Coordinador:")
        y_actual -= 6*mm
        y_actual = draw_paragraph(
            pdf, reporte.comentario_coordinador, x=38*mm, y=y_actual, max_width=maxw, font="Helvetica", font_size=10, italic=True, leading=11
        )

    # ====== FIRMAS DOCENTE Y COORDINADOR (baja si falta espacio) ======
    y_firma = max(y_actual - 18*mm, 32*mm)
    x_firma_doc = 38 * mm
    x_firma_coord = 110 * mm
    largo_firma = 60 * mm

    pdf.setStrokeColor(colors.black)
    pdf.setLineWidth(0.7)
    pdf.line(x_firma_doc, y_firma, x_firma_doc + largo_firma, y_firma)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(x_firma_doc, y_firma - 5*mm, "Firma del Docente:")
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x_firma_doc + 32*mm, y_firma - 5*mm, f"{reporte.docente or ''}")

    pdf.setStrokeColor(colors.black)
    pdf.line(x_firma_coord, y_firma, x_firma_coord + largo_firma, y_firma)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(x_firma_coord, y_firma - 5*mm, "Firma del Coordinador:")
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x_firma_coord + 32*mm, y_firma - 5*mm, f"{getattr(reporte, 'coordinador_firma', '') or ''}")

    pdf.save()
    buf.seek(0)
    return HttpResponse(buf, content_type="application/pdf")


@login_required
def descargar_pdf_progress(request, pk):
    return HttpResponse("PDF Progress Report #{}".format(pk))

#--------------  DASHBOARD COORDINADOR -----------------
@login_required
def dashboard_coordinador(request, area):
    """
    Dashboard coordinador: muestra todos los reportes de Informativo, Conductual y Progress
    según el área.
    """
    # Traer todos los reportes por área
    if area == 'bilingue':
        reportes_informativo = ReporteInformativo.objects.filter(area='bilingue')
        reportes_conductual = ReporteConductual.objects.filter(area='bilingue')
        reportes_progress = ProgressReport.objects.all()  # solo bilingüe tiene progress
    elif area == 'colegio':
        reportes_informativo = ReporteInformativo.objects.filter(area='colegio')
        reportes_conductual = ReporteConductual.objects.filter(area='colegio')
        reportes_progress = []  # colegio NO tiene progress
    else:
        return redirect('menu')  # área inválida

    # Calcula "strikes" (conteo de reportes conductuales por alumno)
    # Dict { alumno_id: count }
    strikes = {}
    qs = reportes_conductual.values('alumno_id').annotate(total=Count('id')).filter(total__gte=3)
    for row in qs:
        strikes[row['alumno_id']] = row['total']

    contexto = {
        'area': area,
        'reportes_informativo': reportes_informativo,
        'reportes_conductual': reportes_conductual,
        'reportes_progress': reportes_progress,
        'strikes': strikes,
    }
    return render(request, 'conducta/dashboard_coordinador.html', contexto)

@login_required
def historial_alumno_coordinador(request, alumno_id):
    """
    Devuelve el historial de reportes (informativo, conductual, progress)
    para un alumno específico. Se usa en el modal del dashboard coordinador.
    """
    informativos = ReporteInformativo.objects.filter(alumno_id=alumno_id).order_by('-fecha')
    conductuales = ReporteConductual.objects.filter(alumno_id=alumno_id).order_by('-fecha')
    progress = ProgressReport.objects.filter(alumno_id=alumno_id).order_by('-fecha')
    context = {
        'informativos': informativos,
        'conductuales': conductuales,
        'progress': progress,
    }
    html = render_to_string('conducta/lista_reportes.html', context)
    return HttpResponse(html)
