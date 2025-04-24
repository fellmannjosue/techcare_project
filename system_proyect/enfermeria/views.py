from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.db.models import Sum
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .models import AtencionMedica, InventarioMedicamento, UsoMedicamento
from .forms import AtencionMedicaForm, InventarioMedicamentoForm, UsoMedicamentoForm
import io


@login_required
def enfermeria_dashboard(request):
    return render(request, 'enfermeria/dashboard.html')


# ============ ATENCIÓN MÉDICA ============

@login_required
def atencion_form(request):
    delete_id = request.GET.get('delete')
    edit_id = request.GET.get('edit')
    if delete_id:
        get_object_or_404(AtencionMedica, pk=delete_id).delete()
        return redirect('enfermeria:atencion_form')

    form = None
    if request.method == 'POST':
        pk = request.POST.get('pk')
        if pk:
            instance = get_object_or_404(AtencionMedica, pk=pk)
            form = AtencionMedicaForm(request.POST, instance=instance)
        else:
            form = AtencionMedicaForm(request.POST)
        if form.is_valid():
            form.save()
            request.session['mensaje_exito'] = 'Ficha guardada correctamente'
            return redirect('enfermeria:atencion_form')
    else:
        instance = get_object_or_404(AtencionMedica, pk=edit_id) if edit_id else None
        form = AtencionMedicaForm(instance=instance)

    records = AtencionMedica.objects.order_by('-fecha_hora')
    return render(request, 'enfermeria/atencion_form.html', {
        'form': form,
        'records': records,
        'edit_id': edit_id or ''
    })


@login_required
def atencion_download_pdf(request, pk):
    rec = get_object_or_404(AtencionMedica, pk=pk)
    buf = io.BytesIO()
    w, h = 210 * mm, 297 * mm
    pdf = canvas.Canvas(buf, pagesize=(w, h))
    pdf.setTitle(f"Atencion_{rec.pk}")
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, w, h, fill=1, stroke=0)

    # Logo
    logo = finders.find('accounts/img/ana-transformed.png')
    if logo:
        pdf.drawImage(logo, 15 * mm, h - 45 * mm, width=30 * mm, height=30 * mm)

    # Título
    pdf.setFont("Helvetica-Bold", 18)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(w / 2, h - 25 * mm, "Ficha de Atención Médica")

    # Datos en tabla
    tabla_data = [
        ["ID:", f"ANA-{rec.pk:03d}"],
        ["Estudiante:", rec.estudiante],
        ["Grado:", rec.grado.nombre],
        ["Fecha y Hora:", rec.fecha_hora.strftime("%d-%m-%Y %H:%M")],
        ["Atendido por:", rec.atendido_por.nombre],
        ["Motivo:", rec.motivo],
        ["Tratamiento:", rec.tratamiento],
    ]
    tabla = Table(tabla_data, colWidths=[60 * mm, 110 * mm])
    tabla.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    tabla.wrapOn(pdf, w, h)
    tabla.drawOn(pdf, 20 * mm, h - 160 * mm)

    # Texto descriptivo
    texto = (
        f"El estudiante <b>{rec.estudiante}</b> del grado <b>{rec.grado.nombre}</b> fue atendido "
        f"el día <b>{rec.fecha_hora.strftime('%d/%m/%Y')}</b> a las <b>{rec.fecha_hora.strftime('%H:%M')}</b> "
        f"por el profesional <b>{rec.atendido_por.nombre}</b>. Se le brindó el <b>tratamiento</b> "
        f"porque: <b>{rec.motivo}</b>. El tratamiento aplicado fue: <b>{rec.tratamiento}</b>."
    )
    style = ParagraphStyle('custom', fontSize=13, leading=18)
    paragraph = Paragraph(texto, style)
    frame = Frame(20 * mm, h - 250 * mm, w - 40 * mm, 80 * mm, showBoundary=0)
    frame.addFromList([paragraph], pdf)

    pdf.showPage()
    pdf.save()
    buf.seek(0)
    return HttpResponse(buf, content_type='application/pdf')


# ============ INVENTARIO ============

@login_required
def inventario_list(request):
    items = InventarioMedicamento.objects.order_by('-fecha_ingreso')
    return render(request, 'enfermeria/inventario_list.html', {'items': items})


@login_required
def inventario_create(request):
    form = InventarioMedicamentoForm(request.POST or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.modificado_por = request.user
        item.save()
        request.session['mensaje_exito'] = 'Medicamento agregado correctamente'
        return redirect('enfermeria:inventario_list')
    return render(request, 'enfermeria/inventario_form.html', {
        'form': form,
        'title': 'Agregar Medicamento'
    })


@login_required
def inventario_edit_cantidad(request, pk):
    item = get_object_or_404(InventarioMedicamento, pk=pk)
    form = InventarioMedicamentoForm(request.POST or None, instance=item)
    if form.is_valid():
        item = form.save(commit=False)
        item.modificado_por = request.user  # ✅ AQUÍ SE ASIGNA
        item.save()
        request.session['mensaje_exito'] = 'Cantidad actualizada correctamente'
        return redirect('enfermeria:inventario_list')
    return render(request, 'enfermeria/inventario_form.html', {
        'form': form,
        'title': f'Editar Cantidad – {item.nombre}'
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
            return redirect('enfermeria:inventario_list')
        else:
            form.add_error('cantidad_usada', 'Cantidad excede lo disponible.')
    return render(request, 'enfermeria/uso_form.html', {
        'form': form,
        'title': 'Registrar Uso de Medicamento'
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
        ("Nombre:", med.nombre),
        ("Proveedor:", med.proveedor.nombre),
        ("Fecha de Ingreso:", med.fecha_ingreso.strftime("%d-%m-%Y")),
        ("Cantidad Disponible:", med.cantidad_existente),
        ("Total Usado:", total_usado),
        ("Modificado por:", med.modificado_por.username if med.modificado_por else "—"),
    ]:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.setFillColor(colors.black)
        pdf.drawString(20 * mm, y, label)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(65 * mm, y, str(val))
        y -= 10 * mm

    pdf.showPage()
    pdf.save()
    buf.seek(0)
    return HttpResponse(buf, content_type='application/pdf')


# ============ HISTORIAL DE USOS ============

@login_required
def historial_uso(request, pk):
    med = get_object_or_404(InventarioMedicamento, pk=pk)
    usos = med.usos.order_by('-fecha_uso')
    return render(request, 'enfermeria/historial_uso.html', {
        'medicamento': med,
        'usos': usos
    })
