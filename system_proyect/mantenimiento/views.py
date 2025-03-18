import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from .models import MaintenanceRecord
from .forms import MaintenanceRecordForm

# URL pública para el logo
PUBLIC_IMAGE_URL = "https://soporte.ana-hn.org:437/static/inventory/img/ana.jpg"

@login_required
def maintenance_dashboard(request):
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('maintenance_dashboard')
        else:
            print(form.errors)
    else:
        form = MaintenanceRecordForm()

    records = MaintenanceRecord.objects.all()
    return render(request, 'mantenimiento/maintenance_dashboard.html', {'form': form, 'records': records})


@login_required
def download_maintenance_pdf(request, record_id):
    # Obtén el objeto de la ficha de mantenimiento
    record = get_object_or_404(MaintenanceRecord, id=record_id)

    # Configurar la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="maintenance_record_{record.id}.pdf"'

    # Crear el lienzo PDF con dimensiones específicas (20 cm x 20 cm)
    card_width = 20 * 28.35  # 20 cm en puntos
    card_height = 20 * 28.35  # 20 cm en puntos
    pdf = canvas.Canvas(response, pagesize=(card_width, card_height))
    pdf.setTitle(f"Ficha de Mantenimiento - ID {record.id}")

    # Fondo de la tarjeta
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, card_width, card_height, fill=1)

    # Añadir el logo con un fondo blanco detrás
    try:
        logo_width = 60  # Ajusta el ancho del logo
        logo_height = 60  # Ajusta la altura del logo
        logo_x = (card_width - logo_width) / 2  # Centrado horizontalmente
        logo_y = card_height - logo_height - 30  # Espaciado desde el borde superior

        # Fondo blanco detrás del logo
        pdf.setFillColor(colors.white)
        pdf.rect(logo_x - 5, logo_y - 5, logo_width + 10, logo_height + 10, fill=1)

        # Dibuja el logo
        pdf.drawImage(PUBLIC_IMAGE_URL, logo_x, logo_y, width=logo_width, height=logo_height)
    except Exception as e:
        print(f"Error al cargar el logo: {e}")

    # Estilo general
    margin = 20
    line_height = 25
    col1_x = margin
    col2_x = card_width / 2 + margin

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(card_width / 2, logo_y - 20, "Ficha de Mantenimiento")

    y_position = logo_y - 70

    # Columna 1
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(col1_x, y_position, "ID:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(col1_x + 80, y_position, f"ANA-{record.id:02d}")

    y_position -= line_height
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(col1_x, y_position, "Equipo:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(col1_x + 80, y_position, f"{record.equipment_name}")

    y_position -= line_height
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(col1_x, y_position, "Problema:")
    pdf.setFont("Helvetica", 12)
    # Ajuste para evitar texto montado
    text = pdf.beginText(col1_x + 80, y_position)
    text.setFont("Helvetica", 12)
    text.setTextOrigin(col1_x + 80, y_position)
    text.setWordSpace(4)
    text.textLines(record.problem_description)
    pdf.drawText(text)

    # Columna 2
    y_position = logo_y - 70
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(col2_x, y_position, "Fecha:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(col2_x + 80, y_position, f"{record.maintenance_date.strftime('%d-%m-%Y')}")

    y_position -= line_height
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(col2_x, y_position, "Técnico:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(col2_x + 80, y_position, f"{record.technician}")

    y_position -= line_height
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(col2_x, y_position, "Tipo:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(col2_x + 80, y_position, f"{record.maintenance_type}")

    y_position -= line_height
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(col2_x, y_position, "Estado:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(col2_x + 80, y_position, f"{record.maintenance_status}")

    # Detalles adicionales
    y_position -= line_height * 2
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(col1_x, y_position, "Actividades Realizadas:")
    pdf.setFont("Helvetica", 12)
    text = pdf.beginText(col1_x + 200, y_position)
    text.textLines(record.activities_done.replace("■■", "\n-"))
    pdf.drawText(text)

    y_position -= line_height * 2
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(col1_x, y_position, "Observaciones:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(col1_x + 200, y_position, f"{record.observations}")

    # Pie de página
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.setFillColor(colors.gray)
    pdf.drawCentredString(card_width / 2, margin, "Sistema de Mantenimiento - Asociacion Nuevo Amanecer")

    # Finalizar el PDF
    pdf.showPage()
    pdf.save()

    return response
