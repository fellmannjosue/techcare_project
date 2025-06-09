import io
import os
import datetime

from django.shortcuts    import render, redirect, get_object_or_404
from django.conf         import settings
from django.urls         import reverse
from django.core.mail    import EmailMessage
from django.http         import HttpResponse, JsonResponse
from django.contrib.staticfiles import finders
from django.db.models    import Sum, Q

from reportlab.lib       import colors
from reportlab.lib.units import mm
from reportlab.pdfgen    import canvas
from reportlab.platypus  import Paragraph, Frame, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

from .models  import (
    AtencionMedica,
    InventarioMedicamento,
    UsoMedicamento,
    TblPrsDtosGen,
)
from .forms   import (
    AtencionMedicaForm,
    InventarioMedicamentoForm,
    UsoMedicamentoForm,
)


def enfermeria_dashboard(request):
    return render(request, 'enfermeria2/dashboard.html')


# ================= ATENCIÓN MÉDICA =================

def atencion_form(request):
    delete_id = request.GET.get('delete')
    edit_id   = request.GET.get('edit')

    if delete_id:
        get_object_or_404(AtencionMedica, pk=delete_id).delete()
        return redirect('enfermeria2:atencion_form')

    if request.method == 'POST':
        pk = request.POST.get('pk')
        if pk:
            instancia = get_object_or_404(AtencionMedica, pk=pk)
            form = AtencionMedicaForm(request.POST, instance=instancia)
        else:
            form = AtencionMedicaForm(request.POST)
        if form.is_valid():
            form.save()
            request.session['mensaje_exito'] = 'Ficha guardada correctamente'
            return redirect('enfermeria2:atencion_form')
    else:
        instancia = get_object_or_404(AtencionMedica, pk=edit_id) if edit_id else None
        form = AtencionMedicaForm(instance=instancia)

    registros = AtencionMedica.objects.order_by('-fecha_hora')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria2/atencion_form.html', {
        'form': form,
        'records': registros,
        'edit_id': edit_id or '',
        'year': year,
    })


def atencion_download_pdf(request, pk):
    # 1) Recuperar el registro de Atención Médica
    rec = get_object_or_404(AtencionMedica, pk=pk)

    # 2) Preparar buffer y lienzo
    buf = io.BytesIO()
    w, h = 210 * mm, 297 * mm  # A4
    pdf = canvas.Canvas(buf, pagesize=(w, h))

    # 3) Fondo claro
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, w, h, fill=1, stroke=0)

    # 4) Encabezado superior
    pdf.setFont("Helvetica-Oblique", 12)
    pdf.setFillColor(colors.darkgray)
    pdf.drawCentredString(
        w / 2,
        h - 10 * mm,
        "Este es un mensaje de nuestro departamento de enfermería"
    )

    # 5) Título principal
    pdf.setFont("Helvetica-Bold", 20)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(
        w / 2,
        h - 20 * mm,
        "Ficha de Atención Médica"
    )

    # 6) Texto informativo
    texto = (
        "Estimado padre / madre de familia:<br/>"
        "El motivo de la ficha es para notificarle que su hij@ fue atendido en el departamento de enfermería.<br/><br/>"
        f"Se le brindó a su hijo(a) <b>{rec.estudiante}</b> del grado <b>{rec.grado.nombre}</b> "
        f"quien fue atendido el día <b>{rec.fecha_hora.strftime('%d/%m/%Y')}</b> "
        f"a las <b>{rec.fecha_hora.strftime('%H:%M')}</b> por el coordinador "
        f"<b>{rec.atendido_por.nombre}</b>, ya que no se sentía bien y presentaba: "
        f"<b>{rec.motivo}</b>. Se le trató con: <b>{rec.tratamiento}</b>."
    )
    style = ParagraphStyle(
        'texto_principal',
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.black
    )
    # Calcular posición del párrafo
    y_frame = h - (20 * mm) - (50 * mm) - (50 * mm)
    frame_texto = Frame(
        20 * mm,
        y_frame,
        w - 40 * mm,
        50 * mm,
        showBoundary=0
    )
    paragraph = Paragraph(texto, style)
    frame_texto.addFromList([paragraph], pdf)

    # 7) Subtítulo de tabla
    y_subtitulo = y_frame - (10 * mm)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(
        w / 2,
        y_subtitulo,
        "Detalle de la atención que se brindó en el departamento de enfermería"
    )

    # 8) Tabla de datos
    tabla_data = [
        ["Estudiante:",    rec.estudiante],
        ["Grado:",         rec.grado.nombre],
        ["Fecha y Hora:",  rec.fecha_hora.strftime("%d-%m-%Y %H:%M")],
        ["Atendido por:",  rec.atendido_por.nombre],
        ["Motivo:",        rec.motivo],
        ["Tratamiento:",   rec.tratamiento],
    ]
    tabla = Table(tabla_data, colWidths=[50 * mm, 120 * mm])
    tabla.setStyle(TableStyle([
        ('GRID',          (0, 0), (-1, -1), 0.25, colors.grey),
        ('FONTSIZE',      (0, 0), (-1, -1), 14),
        ('FONTNAME',      (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    altura_tabla_aprox = len(tabla_data) * 8 * mm
    y_arriba_tabla = y_subtitulo - (10 * mm)
    tabla.wrapOn(pdf, w, h)
    tabla.drawOn(pdf, 20 * mm, y_arriba_tabla - altura_tabla_aprox)

    # 9) Línea de firma
    y_base_tabla = y_arriba_tabla - altura_tabla_aprox
    y_firma = y_base_tabla - (80 * mm)
    x_inicio = (w / 2) - (50 * mm)
    x_fin    = (w / 2) + (50 * mm)

    pdf.setFont("Helvetica", 12)
    pdf.drawString(x_inicio, y_firma + (2 * mm), "Firma:")
    pdf.setStrokeColor(colors.black)
    pdf.setLineWidth(0.5)
    pdf.line(x_inicio, y_firma, x_fin, y_firma)

    # 10) Nombre del profesional SOBRE la línea
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(
        w / 2,
        y_firma + (3 * mm),
        rec.atendido_por.nombre
    )

    # 11) Finalizar y devolver
    pdf.showPage()
    pdf.save()
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='application/pdf')




def enviar_correo(request, atencion_id):
    atencion = get_object_or_404(AtencionMedica, pk=atencion_id)

    # Cargamos TODOS los registros de TblPrsDtosGen
    personas = TblPrsDtosGen.objects.using('padres_sqlserver').all()

    pdf_url = reverse('enfermeria2:atencion_pdf', args=[atencion.pk])

    default_asunto = f"Ficha médica de {atencion.estudiante}"
    default_mensaje = (
        f"Estimado/a padre/madre de {atencion.estudiante},\n\n"
        "Adjunto encontrará la ficha médica de su hijo(a). Por favor, revise el documento "
        "y contáctenos si tiene alguna duda.\n\n"
        "Saludos cordiales,\nDepartamento de Enfermería"
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

            # Adjuntar el PDF en memoria
            pdf_response = atencion_download_pdf(request, atencion.pk)
            correo.attach(
                f"ficha_{atencion.pk}.pdf",
                pdf_response.content,
                'application/pdf'
            )

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
        'year': year,
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
        'form': form,
        'title': 'Agregar Medicamento',
        'year': year,
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
        'form': form,
        'title': f'Editar Medicamento – {item.nombre}',
        'year': year,
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
        'form': form,
        'title': 'Registrar Uso de Medicamento',
        'year': year,
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
    pdf.rect(0, 0, w, h, fill=1, stroke=0)

    logo = finders.find('accounts/img/ana-transformed.png')
    if logo:
        pdf.drawImage(logo, 15 * mm, h - 45 * mm, width=30 * mm, height=30 * mm)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(w / 2, h - 25 * mm, "Reporte de Medicamento")

    y = h - 60 * mm
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
        pdf.drawString(20 * mm, y, label)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(65 * mm, y, str(val))
        y -= 10 * mm

    pdf.showPage()
    pdf.save()
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='application/pdf')


def historial_uso(request, pk):
    med = get_object_or_404(InventarioMedicamento, pk=pk)
    usos = med.usos.order_by('-fecha_uso')
    return render(request, 'enfermeria2/historial_uso.html', {
        'medicamento': med,
        'usos': usos
    })


# ================= HISTORIAL MÉDICO =================

def medical_history(request):
    students = (
        AtencionMedica.objects
        .values_list('estudiante', flat=True)
        .distinct()
        .order_by('estudiante')
    )
    year = datetime.datetime.now().year
    return render(request, 'enfermeria2/medical_history.html', {
        'students': students,
        'year': year,
    })


def get_medical_history_data(request):
    student_name = request.GET.get('student')
    if not student_name:
        return JsonResponse({'error': 'Falta el parámetro "student"'}, status=400)

    registros = (
        AtencionMedica.objects
        .filter(estudiante=student_name)
        .order_by('-fecha_hora')
    )

    if not registros.exists():
        return JsonResponse({}, status=204)

    lista = []
    for rec in registros:
        lista.append({
            'grade':     rec.grado.nombre,
            'date_time': rec.fecha_hora.strftime('%Y-%m-%d %H:%M'),
            'reason':    rec.motivo,
            'treatment': rec.tratamiento,
            'attendant': rec.atendido_por.nombre,
        })

    return JsonResponse({'history': lista})
