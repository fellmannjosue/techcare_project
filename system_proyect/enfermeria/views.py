# views.py

import datetime
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame, Table, TableStyle
from reportlab.lib.pagesizes import letter

from reportlab.lib.styles import ParagraphStyle

from .models import (
    AtencionMedica,
    InventarioMedicamento,
    UsoMedicamento,
)
from .forms import (
    AtencionMedicaForm,
    InventarioMedicamentoForm,
    UsoMedicamentoForm,
)


@login_required
def enfermeria_dashboard(request):
    return render(request, 'enfermeria/dashboard.html')


# ================= ATENCIÓN MÉDICA =================

@login_required
def atencion_form(request):
    delete_id = request.GET.get('delete')
    edit_id   = request.GET.get('edit')

    if delete_id:
        get_object_or_404(AtencionMedica, pk=delete_id).delete()
        return redirect('enfermeria:atencion_form')

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
            return redirect('enfermeria:atencion_form')
    else:
        instancia = get_object_or_404(AtencionMedica, pk=edit_id) if edit_id else None
        form = AtencionMedicaForm(instance=instancia)

    registros = AtencionMedica.objects.order_by('-fecha_hora')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/atencion_form.html', {
        'form': form,
        'records': registros,
        'edit_id': edit_id or '',
        'year': year,
    })


@login_required
def atencion_download_pdf(request, pk):
    # 1) Recuperar datos y preparar buffer
    rec = get_object_or_404(AtencionMedica, pk=pk)
    buf = io.BytesIO()
    w, h = letter   # carta
    pdf = canvas.Canvas(buf, pagesize=letter)
    pdf.setTitle(f"ficha_de_atencion_{rec.estudiante.replace(' ', '_')}")

    # 2) Fondo claro
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, w, h, fill=1, stroke=0)

    # 3) Encabezado informativo
    pdf.setFont("Helvetica-Oblique", 12)
    pdf.setFillColor(colors.darkgray)
    pdf.drawCentredString(
        w/2,
        h - 15*mm,
        "Este es un mensaje de nuestro departamento de enfermería"
    )

    # 4) Título principal
    pdf.setFont("Helvetica-Bold", 20)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(
        w/2,
        h - 30*mm,
        "Ficha de Atención Médica"
    )

    # 5) Párrafo informativo con negritas
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
        fontSize=12,
        leading=18,  # más espacio entre líneas
        textColor=colors.black,
    )
    paragraph = Paragraph(texto, style)
    ancho_texto = w - 40*mm
    _, alto_parrafo = paragraph.wrap(ancho_texto, h)

    # Colocar párrafo con separación extra
    y_parrafo = (h - 30*mm) - 15*mm - alto_parrafo
    paragraph.drawOn(pdf, 20*mm, y_parrafo)

    # 6) Subtítulo de la tabla
    y_subt = y_parrafo - 15*mm
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(
        w/2,
        y_subt,
        "Detalle de la atención brindada"
    )

    # 7) Tabla con datos
    datos = [
        ["Estudiante:",   rec.estudiante],
        ["Grado:",        rec.grado.nombre],
        ["Fecha y Hora:", rec.fecha_hora.strftime("%d-%m-%Y %H:%M")],
        ["Motivo:",       rec.motivo],
        ["Tratamiento:",  rec.tratamiento],
    ]
    tabla = Table(datos, colWidths=[50*mm, 120*mm])
    tabla.setStyle(TableStyle([
        ('GRID',          (0,0), (-1,-1), 0.25, colors.grey),
        ('FONTSIZE',      (0,0), (-1,-1), 12),
        ('FONTNAME',      (0,0), (-1,-1), 'Helvetica'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    _, alto_tabla = tabla.wrap(ancho_texto, h)

    # Dibujar tabla con separación
    y_tabla_top = y_subt - 15*mm
    tabla.drawOn(pdf, 20*mm, y_tabla_top - alto_tabla)

    # 8) Línea de firma con etiqueta "Firma" y nombre centrado
    y_base  = y_tabla_top - alto_tabla
    y_linea = y_base - 30*mm
    largo   = 80 * mm
    x0      = (w/2) - (largo/2)
    x1      = x0 + largo

    pdf.setStrokeColor(colors.black)
    pdf.setLineWidth(0.5)
    pdf.line(x0, y_linea, x1, y_linea)

    pdf.setFont("Helvetica-Bold", 12)
    # Etiqueta "Firma" a la izquierda de la línea
    pdf.drawString(x0, y_linea + 5*mm, "Firma:")
    # Nombre del atendido por centrado sobre la línea
    pdf.drawCentredString(w/2, y_linea + 5*mm, rec.atendido_por.nombre)

    # 9) Finalizar y devolver
    pdf.showPage()
    pdf.save()
    buf.seek(0)
    return HttpResponse(buf, content_type='application/pdf')




# ================= INVENTARIO MEDICAMENTOS =================

@login_required
def inventario_list(request):
    items = InventarioMedicamento.objects.order_by('-fecha_ingreso')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/inventario_list.html', {
        'items': items,
        'year': year,
    })


@login_required
def inventario_create(request):
    form = InventarioMedicamentoForm(request.POST or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.modificado_por = request.user
        item.save()
        request.session['mensaje_exito'] = 'Medicamento agregado correctamente'
        return redirect('enfermeria:inventario_list')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/inventario_form.html', {
        'form': form,
        'title': 'Agregar Medicamento',
        'year': year,
    })


@login_required
def inventario_edit_cantidad(request, pk):
    item = get_object_or_404(InventarioMedicamento, pk=pk)
    form = InventarioMedicamentoForm(request.POST or None, instance=item)
    if form.is_valid():
        item = form.save(commit=False)
        item.modificado_por = request.user
        item.save()
        request.session['mensaje_exito'] = 'Cantidad actualizada correctamente'
        return redirect('enfermeria:inventario_list')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/inventario_form.html', {
        'form': form,
        'title': f'Editar Medicamento – {item.nombre}',
        'year': year,
    })


@login_required
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
            # Regresamos a la pantalla de atención:
            return redirect('enfermeria:atencion_form')
        form.add_error('cantidad_usada', 'Cantidad excede lo disponible.')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/uso_form.html', {
        'form': form,
        'title': 'Registrar Uso de Medicamento',
        'year': year,
    })


@login_required
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
        ("Presentación:",     med.presentacion.nombre),
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
    return HttpResponse(buf, content_type='application/pdf')


@login_required
def historial_uso(request, pk):
    med = get_object_or_404(InventarioMedicamento, pk=pk)
    usos = med.usos.order_by('-fecha_uso')
    return render(request, 'enfermeria/historial_uso.html', {
        'medicamento': med,
        'usos': usos
    })


# ================= HISTORIAL MÉDICO =================

@login_required
def medical_history(request):
    # Lista de nombres únicos de estudiante
    students = (
        AtencionMedica.objects
        .values_list('estudiante', flat=True)
        .distinct()
        .order_by('estudiante')
    )
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/medical_history.html', {
        'students': students,
        'year': year,
    })


@login_required
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
