import io
import os
import datetime

from django.shortcuts           import render, redirect, get_object_or_404
from django.conf                import settings
from django.urls                import reverse
from django.core.mail           import EmailMessage
from django.http                import HttpResponse, JsonResponse
from django.contrib.staticfiles import finders
from django.db.models           import Sum, Q
from django.db                  import connections
from reportlab.lib              import colors
from reportlab.lib.units        import mm
from reportlab.pdfgen           import canvas
from reportlab.platypus         import Paragraph, Frame, Table, TableStyle
from reportlab.lib.styles       import ParagraphStyle

from .models import (
    AtencionMedica,
    InventarioMedicamento,
    UsoMedicamento,
    TblPrsDtosGen,
    Grado,
)
from .forms  import (
    AtencionMedicaForm,
    InventarioMedicamentoForm,
    UsoMedicamentoForm,
)


def enfermeria_dashboard(request):
    return render(request, 'enfermeria2/dashboard.html')


def atencion_form(request):
    delete_id = request.GET.get('delete')
    edit_id   = request.GET.get('edit')

    # 1) Si viene ?delete=..., borramos y redirigimos
    if delete_id:
        get_object_or_404(AtencionMedica, pk=delete_id).delete()
        return redirect('enfermeria2:atencion_form')

    # 2) Tiramos la query a SQL Server para obtener los alumnos
    sql = """
      SELECT 
  d.PersonaID,
  -- Concatenamos primero Nombres y luego Apellidos
  ISNULL(d.Nombre1,'') 
    + CASE WHEN d.Nombre2 IS NOT NULL AND d.Nombre2 <> '' THEN ' ' + d.Nombre2 ELSE '' END
    + ' ' +
  ISNULL(d.Apellido1,'')
    + CASE WHEN d.Apellido2 IS NOT NULL AND d.Apellido2 <> '' THEN ' ' + d.Apellido2 ELSE '' END
    AS NombreCompl,
  da.Descripcion    AS AreaDesc,
  c.CrsoNumero,
  c.GrupoNumero
 FROM dbo.tblPrsDtosGen AS d
 JOIN dbo.tblPrsTipo           AS t  ON d.PersonaID = t.PersonaID
 JOIN dbo.tblEdcArea           AS a  ON t.IngrEgrID  = a.IngrEgrID
 JOIN dbo.tblEdcEjecCrso       AS ec ON a.AreaID     = ec.AreaID
 JOIN dbo.tblEdcCrso           AS c  ON ec.CrsoID     = c.CrsoID
 JOIN dbo.tblEdcDescripAreaEdc AS da ON a.DescrAreaEdcID = da.DescrAreaEdcID
 WHERE d.Alum = 1
  AND DATEPART(yy, c.FechaInicio) = DATEPART(yyyy, GETDATE())
  AND da.Descripcion IN (N'PrimariaBL', N'ColegioBL', N'PreescolarBL')
  AND ec.Desertor    = 0
  AND ec.TrasladoPer = 0
 ORDER BY 
  da.Descripcion,
  c.CrsoNumero,
  c.GrupoNumero,
  NombreCompl;

    """
    with connections['padres_sqlserver'].cursor() as cursor:
        cursor.execute(sql)
        filas = cursor.fetchall()

    students = [{
        'id':    pid,
        'label': nombre.strip(),
        'grado': f"{area} {crso}-{grupo}"
    } for pid, nombre, area, crso, grupo in filas]

    # 3) Si es POST, procesamos
    instancia = get_object_or_404(AtencionMedica, pk=edit_id) if edit_id else None
    if request.method == 'POST':
        # 3a) extraemos con get() para no KeyError
        persona_id = request.POST.get('estudiante')
        grado_txt  = request.POST.get('grado')

        # 3b) cloneamos el POST y eliminamos esos dos campos
        post_data = request.POST.copy()
        post_data.pop('estudiante', None)
        post_data.pop('grado', None)

        form = AtencionMedicaForm(post_data, instance=instancia)
        if form.is_valid():
            obj = form.save(commit=False)

            # 3c) rellenamos el nombre completo
            if persona_id:
                persona = TblPrsDtosGen.objects.using('padres_sqlserver') \
                                               .get(PersonaID=persona_id)
                partes = filter(None, (
                    persona.Apellido1, persona.Apellido2,
                    persona.Nombre1,   persona.Nombre2
                ))
                obj.estudiante = " ".join(partes)

            # 3d) obtenemos o creamos el Grado
            if grado_txt:
                grado_obj, _ = Grado.objects.get_or_create(nombre=grado_txt)
                obj.grado = grado_obj

            obj.save()
            form.save_m2m()
            request.session['mensaje_exito'] = 'Ficha guardada correctamente'
            return redirect('enfermeria2:atencion_form')
    else:
        form = AtencionMedicaForm(instance=instancia)

    # 4) Finalmente rendereamos
    registros = AtencionMedica.objects.order_by('-fecha_hora')
    year      = datetime.datetime.now().year
    contexto  = {
        'form':          form,
        'records':       registros,
        'edit_id':       edit_id or '',
        'year':          year,
        'students':      students,
        'mensaje_exito': request.session.pop('mensaje_exito', None),
    }
    return render(request, 'enfermeria2/atencion_form.html', contexto)

def atencion_download_pdf(request, pk):
    rec = get_object_or_404(AtencionMedica, pk=pk)
    buf = io.BytesIO()
    w, h = 210 * mm, 297 * mm
    pdf = canvas.Canvas(buf, pagesize=(w, h))

    # Fondo
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, w, h, fill=1, stroke=0)

    # Encabezado
    pdf.setFont("Helvetica-Oblique", 12)
    pdf.setFillColor(colors.darkgray)
    pdf.drawCentredString(w/2, h-10*mm, "Departamento de Enfermería")

    # Título
    pdf.setFont("Helvetica-Bold", 20)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(w/2, h-20*mm, "Ficha de Atención Médica")

    # Texto
    texto = (
        f"Estimado padre/madre:\n\n"
        f"Su hijo(a) <b>{rec.estudiante}</b> del grado <b>{rec.grado}</b> "
        f"fue atendido el {rec.fecha_hora.strftime('%d/%m/%Y')} "
        f"a las {rec.fecha_hora.strftime('%H:%M')}.\n\n"
        f"Motivo: {rec.motivo}\n"
        f"Tratamiento: {rec.tratamiento}"
    )
    style = ParagraphStyle('texto', fontName='Helvetica', fontSize=14, leading=18)
    frame = Frame(20*mm, h-80*mm, w-40*mm, 50*mm, showBoundary=0)
    frame.addFromList([Paragraph(texto, style)], pdf)

    # Tabla resumen
    data = [
        ["Estudiante:", rec.estudiante],
        ["Grado:", rec.grado],
        ["Fecha y Hora:", rec.fecha_hora.strftime("%d-%m-%Y %H:%M")],
        ["Motivo:", rec.motivo],
        ["Tratamiento:", rec.tratamiento],
    ]
    table = Table(data, colWidths=[50*mm, 120*mm])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    table.wrapOn(pdf, w, h)
    table.drawOn(pdf, 20*mm, h-140*mm)

    pdf.showPage()
    pdf.save()
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='application/pdf')


def enviar_correo(request, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)
    personas = TblPrsDtosGen.objects.using('padres_sqlserver').filter(alum=1)
    pdf_url  = reverse('enfermeria2:atencion_pdf', args=[atencion.pk])
    default_asunto  = f"Ficha médica de {atencion.estudiante}"
    default_mensaje = (
        f"Estimado/a padre/madre de {atencion.estudiante},\n\n"
        "Adjunto la ficha médica.\n\nSaludos."
    )

    error_msg = None
    success   = False

    if request.method == 'POST':
        email_destino = request.POST.get('email')
        asunto        = request.POST.get('asunto')  or default_asunto
        cuerpo        = request.POST.get('mensaje') or default_mensaje

        if email_destino:
            correo = EmailMessage(
                subject=asunto,
                body=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_destino],
            )
            correo.content_subtype = 'html'
            pdf_resp = atencion_download_pdf(request, atencion.pk)
            correo.attach(f"ficha_{atencion.pk}.pdf", pdf_resp.content, 'application/pdf')
            try:
                correo.send(fail_silently=False)
                success = True
                return redirect('enfermeria2:atencion_form')
            except Exception as e:
                error_msg = str(e)

    return render(request, 'enfermeria2/enviar_correo.html', {
        'atencion':  atencion,
        'personas':  personas,
        'pdf_url':   pdf_url,
        'asunto':    default_asunto,
        'mensaje':   default_mensaje,
        'error_msg': error_msg,
        'success':   success,
    })


# ================= INVENTARIO MEDICAMENTOS =================

def inventario_list(request):
    items = InventarioMedicamento.objects.order_by('-fecha_ingreso')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria2/inventario_list.html', {
        'items': items,
        'year':  year,
    })


def inventario_create(request):
    form = InventarioMedicamentoForm(request.POST or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.modificado_por = request.user
        item.save()
        request.session['mensaje_exito'] = 'Medicamento agregado correctamente'
        return redirect('enfermeria2:inventario_list')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria2/inventario_form.html', {
        'form':  form,
        'title': 'Agregar Medicamento',
        'year':  year,
    })


def inventario_edit_cantidad(request, pk):
    item = get_object_or_404(InventarioMedicamento, pk=pk)
    form = InventarioMedicamentoForm(request.POST or None, instance=item)
    if form.is_valid():
        item = form.save(commit=False)
        item.modificado_por = request.user
        item.save()
        request.session['mensaje_exito'] = 'Cantidad actualizada correctamente'
        return redirect('enfermeria2:inventario_list')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria2/inventario_form.html', {
        'form':  form,
        'title': f'Editar Medicamento – {item.nombre}',
        'year':  year,
    })


def uso_create(request):
    form = UsoMedicamentoForm(request.POST or None)
    if form.is_valid():
        uso = form.save(commit=False)
        med = uso.medicamento
        if uso.cantidad_usada <= med.cantidad_existente:
            med.cantidad_existente -= uso.cantidad_usada
            med.save()
            uso.save()
            request.session['mensaje_exito'] = 'Uso registrado correctamente'
            return redirect('enfermeria2:atencion_form')
        form.add_error('cantidad_usada', 'Cantidad excede lo disponible.')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria2/uso_form.html', {
        'form':  form,
        'title': 'Registrar Uso de Medicamento',
        'year':  year,
    })


def inventario_pdf(request, pk):
    med = get_object_or_404(InventarioMedicamento, pk=pk)
    usos = med.usos.order_by('-fecha_uso')
    total_usado = usos.aggregate(total=Sum('cantidad_usada'))['total'] or 0

    buf = io.BytesIO()
    w, h = 210 * mm, 297 * mm
    pdf = canvas.Canvas(buf, pagesize=(w, h))
    pdf.setTitle(f"Medicamento_{med.pk}")
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, w, h, fill=1)

    logo = finders.find('accounts/img/ana-transformed.png')
    if logo:
        pdf.drawImage(logo, 15*mm, h-45*mm, width=30*mm, height=30*mm)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(w/2, h-25*mm, "Reporte de Medicamento")

    y = h-60*mm
    for label, val in [
        ("Nombre:",           med.nombre),
        ("Proveedor:",        med.proveedor.nombre),
        ("Presentación:",     med.presentacion.nombre if med.presentacion else "—"),
        ("Fecha de Ingreso:", med.fecha_ingreso.strftime("%d-%m-%Y")),
        ("Disponible:",       med.cantidad_existente),
        ("Total Usado:",      total_usado),
        ("Modificado por:",   med.modificado_por.username if med.modificado_por else "—"),
    ]:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(20*mm, y, label)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(65*mm, y, str(val))
        y -= 10*mm

    pdf.showPage()
    pdf.save()
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='application/pdf')


def historial_uso(request, pk):
    med = get_object_or_404(InventarioMedicamento, pk=pk)
    usos = med.usos.order_by('-fecha_uso')
    return render(request, 'enfermeria2/historial_uso.html', {
        'medicamento': med,
        'usos':        usos,
    })


# ================= HISTORIAL MÉDICO =================

def medical_history(request):
    students = (
        AtencionMedica.objects
        .values_list('estudiante', flat=True)
        .distinct()
        .order_by('estudiante')
    )
    return render(request, 'enfermeria2/medical_history.html', {
        'students': students,
        'year':     datetime.datetime.now().year,
    })


def get_medical_history_data(request):
    student_name = request.GET.get('student')
    if not student_name:
        return JsonResponse({'error': 'Falta parámetro student'}, status=400)

    registros = (
        AtencionMedica.objects
        .filter(estudiante=student_name)
        .order_by('-fecha_hora')
    )
    if not registros.exists():
        return JsonResponse({}, status=204)

    history = [{
        'grade':     rec.grado,
        'date_time': rec.fecha_hora.strftime('%Y-%m-%d %H:%M'),
        'reason':    rec.motivo,
        'treatment': rec.tratamiento,
    } for rec in registros]

    return JsonResponse({'history': history})
