from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.db.models import Sum
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from .models import AtencionMedica, InventarioMedicamento, UsoMedicamento
from .forms import AtencionMedicaForm, InventarioMedicamentoForm, UsoMedicamentoForm
import io

@login_required
def enfermeria_dashboard(request):
    return render(request, 'enfermeria/dashboard.html')


# ATENCIÓN MÉDICA (SE MANTIENE IGUAL)
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

    logo = finders.find('accounts/img/ana-transformed.png')
    if logo:
        pdf.drawImage(logo, 15 * mm, h - 45 * mm, width=30 * mm, height=30 * mm)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(w / 2, h - 25 * mm, "Ficha de Atención Médica")

    y = h - 60 * mm
    for label, val in [
        ("ID:", f"ANA-{rec.pk:03d}"),
        ("Estudiante:", rec.estudiante),
        ("Grado:", rec.grado.nombre),
        ("Fecha y Hora:", rec.fecha_hora.strftime("%d-%m-%Y %H:%M")),
        ("Atendido por:", rec.atendido_por.nombre),
        ("Motivo:", rec.motivo),
        ("Tratamiento:", rec.tratamiento),
    ]:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.setFillColor(colors.black)
        pdf.drawString(20 * mm, y, label)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(55 * mm, y, val)
        y -= 10 * mm

    pdf.showPage()
    pdf.save()
    buf.seek(0)
    return HttpResponse(buf, content_type='application/pdf')


# INVENTARIO DE MEDICAMENTOS
@login_required
def inventario_list(request):
    items = InventarioMedicamento.objects.order_by('-fecha_ingreso')
    return render(request, 'enfermeria/inventario_list.html', {'items': items})


@login_required
def inventario_create(request):
    form = InventarioMedicamentoForm(request.POST or None)
    if form.is_valid():
        form.save()
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
        form.save()
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
