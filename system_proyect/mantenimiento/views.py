import os
import textwrap
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib import colors

from .models import MaintenanceRecord
from .forms import MaintenanceRecordForm


@login_required
def maintenance_dashboard(request):
    """
    Vista unificada para listar y crear registros de mantenimiento.
    """
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            form.save()
            # ← redirige usando el namespace 'mantenimiento'
            return redirect('mantenimiento:maintenance_dashboard')
    else:
        form = MaintenanceRecordForm()

    records = MaintenanceRecord.objects.all().order_by('-date')
    return render(request, 'mantenimiento/maintenance_dashboard.html', {
        'form': form,
        'records': records,
    })


@login_required
def download_maintenance_pdf(request, record_id):
    """
    Genera un PDF tamaño 16×5.5 cm con logo, campos multilinea
    para 'Solución' y 'Observaciones' y línea de firma.
    """
    record = get_object_or_404(MaintenanceRecord, id=record_id)

    # 1) Buffer en memoria
    buffer = BytesIO()
    card_w = 160 * 2.83465  # 16 cm
    card_h =  55 * 2.83465  # 5.5 cm

    # 2) Canvas apuntando al buffer
    pdf = canvas.Canvas(buffer, pagesize=(card_w, card_h))
    pdf.setTitle(f"Ficha de Mantenimiento - ID {record.id}")

    # Fondo claro
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, card_w, card_h, fill=1)

    # Logo en esquina superior
    logo_path = finders.find('mantenimiento/img/ana.jpg')
    if logo_path:
        pdf.drawImage(logo_path, 10, card_h - 40, width=30, height=30)

    # Variables de layout
    margin, line_h = 10, 12
    col1, col2 = margin + 40, card_w/2 + 10
    y1 = y2 = card_h - 20

    def draw_field(x, y, label, val):
        pdf.setFont("Helvetica-Bold", 9)
        pdf.setFillColor(colors.black)
        pdf.drawString(x, y, label)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(x + 60, y, str(val))
        return y - line_h

    # Columna izquierda
    y1 = draw_field(col1, y1, "Equipo:",  record.equipment_id)
    y1 = draw_field(col1, y1, "Modelo:",  record.model)
    y1 = draw_field(col1, y1, "Serie:",   record.serie)
    y1 = draw_field(col1, y1, "Maestro:", record.teacher_name)
    y1 = draw_field(col1, y1, "Grado:",   record.grade)

    # Columna derecha básica
    y2 = draw_field(col2, y2, "Fecha:",  record.date.strftime('%d-%m-%Y'))
    y2 = draw_field(col2, y2, "Estado:", record.status)

    # Solución multilinea
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(col2, y2, "Solución:")
    pdf.setFont("Helvetica", 9)
    wrap_w = int((card_w - col2 - margin) / 6)
    for line in textwrap.wrap(record.solucion or "-", wrap_w):
        y2 -= line_h
        pdf.drawString(col2 + 60, y2, line)
    y2 -= line_h  # espacio extra

    # Observaciones multilinea
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(col2, y2, "Observaciones:")
    pdf.setFont("Helvetica", 9)
    for line in textwrap.wrap(record.observaciones or "-", wrap_w):
        y2 -= line_h
        pdf.drawString(col2 + 60, y2, line)

    # Línea de firma centrada, un poco más arriba
    sign_y = margin + 40
    pdf.setLineWidth(1)
    pdf.line(card_w/2 - 50, sign_y, card_w/2 + 50, sign_y)
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(card_w/2, sign_y - 12, "Firma:")

    # Pie de página
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.setFillColor(colors.gray)
    pdf.drawCentredString(
        card_w/2,
        margin,
        "Sistema de Mantenimiento - Asociación Nuevo Amanecer"
    )

    # 3) Terminar PDF y volcar al buffer
    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    # 4) Enviar respuesta completa
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="maintenance_record_{record.id}.pdf"'
    )
    return response
