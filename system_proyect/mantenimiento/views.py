import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from .models import MaintenanceRecord
from .forms import MaintenanceRecordForm


@login_required
def maintenance_dashboard(request):
    """
    Vista unificada para listar registros de mantenimiento y crear nuevos.
    """
    # 1. (Mejora) Considerar uso de mensajes de Django en lugar de print para errores de formulario.
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('maintenance_dashboard')
    else:
        form = MaintenanceRecordForm()

    # 2. (Optimización) Si la tabla crece mucho, paginar 'records' en lugar de cargar todo.
    records = MaintenanceRecord.objects.all().order_by('-date')

    return render(request, 'mantenimiento/maintenance_dashboard.html', {
        'form': form,
        'records': records,
    })

@login_required
def download_maintenance_pdf(request, record_id):
    """
    Genera un PDF con los detalles de un MaintenanceRecord específico,
    cargando el logo desde archivos estáticos con django.contrib.staticfiles.finders.
    """
    record = get_object_or_404(MaintenanceRecord, id=record_id)

    # Preparamos la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="maintenance_record_{record.id}.pdf"'
    )

    # Dimensiones de la tarjeta (20cm x 20cm en puntos)
    card_width  = 20 * 28.35
    card_height = 20 * 28.35
    pdf = canvas.Canvas(response, pagesize=(card_width, card_height))
    pdf.setTitle(f"Ficha de Mantenimiento - ID {record.id}")

    # Fondo
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, card_width, card_height, fill=1)

    # Intentamos cargar el logo desde staticfiles
    logo_path = finders.find('mantenimiento/img/ana.jpg')
    if logo_path:
        logo_w, logo_h = 60, 60
        logo_x = (card_width - logo_w) / 2
        logo_y = card_height - logo_h - 30

        # Fondo blanco tras el logo
        pdf.setFillColor(colors.white)
        pdf.rect(logo_x - 5, logo_y - 5, logo_w + 10, logo_h + 10, fill=1)

        # Dibujamos el logo
        pdf.drawImage(logo_path, logo_x, logo_y, width=logo_w, height=logo_h)

    # Título centrado
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(card_width / 2, logo_y - 20, "Ficha de Mantenimiento")

    # Posiciones y estilo
    margin = 20
    line_h = 20
    col1_x = margin
    col2_x = card_width / 2 + margin
    y1 = logo_y - 60
    y2 = logo_y - 60

    def draw_field(x, y, label, value):
        pdf.setFont("Helvetica-Bold", 12)
        pdf.setFillColor(colors.black)
        pdf.drawString(x, y, label)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(x + 100, y, str(value))

    # Columna izquierda
    draw_field(col1_x, y1, "Equipo:",      record.equipment_id);   y1 -= line_h
    draw_field(col1_x, y1, "Modelo:",      record.model);          y1 -= line_h
    draw_field(col1_x, y1, "Serie:",       record.serie);          y1 -= line_h
    draw_field(col1_x, y1, "Maestro:",     record.teacher_name);   y1 -= line_h
    draw_field(col1_x, y1, "Grado:",       record.grade)

    # Columna derecha
    draw_field(col2_x, y2, "Fecha:",       record.date.strftime('%d-%m-%Y'));   y2 -= line_h
    draw_field(col2_x, y2, "Estado:",      record.status);                      y2 -= line_h
    draw_field(col2_x, y2, "Solución:",    record.solucion or "-");             y2 -= line_h
    draw_field(col2_x, y2, "Observaciones:", record.observaciones or "-")

    # Pie de página
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.setFillColor(colors.gray)
    pdf.drawCentredString(
        card_width / 2,
        margin,
        "Sistema de Mantenimiento - Asociación Nuevo Amanecer"
    )

    pdf.showPage()
    pdf.save()
    return response