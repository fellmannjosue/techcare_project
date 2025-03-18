import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from .models import InventoryItem
from .forms import InventoryItemForm

# URL pública para el logo
PUBLIC_IMAGE_URL = "https://soporte.ana-hn.org:437/static/inventory/img/ana.jpg"

@login_required
def inventory_dashboard(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_dashboard')
        else:
            print(form.errors)
    else:
        form = InventoryItemForm()

    items = InventoryItem.objects.all()
    return render(request, 'inventario/inventory_dashboard.html', {'form': form, 'items': items})


@login_required
def download_item_pdf(request, item_id):
    # Obtén el objeto del inventario
    item = get_object_or_404(InventoryItem, id=item_id)

    # Configurar la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="item_{item.id}.pdf"'

    # Crear el lienzo PDF con dimensiones específicas (15 cm x 15 cm)
    card_width = 15 * 28.35  # 15 cm en puntos
    card_height = 15 * 28.35  # 15 cm en puntos
    pdf = canvas.Canvas(response, pagesize=(card_width, card_height))
    pdf.setTitle(f"Ficha de Inventario - ID {item.id}")

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
    line_height = 30

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(card_width / 2, logo_y - 20, "Ficha de Inventario")

    # Contenido (Texto más grande y en negrita)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColor(colors.black)

    y_position = logo_y - 70  # Espaciado inicial debajo del título
    pdf.drawCentredString(card_width / 2, y_position, f"ID:")
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(card_width / 2, y_position - 15, f"{item.id}")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(card_width / 2, y_position - 45, f"Categoría:")
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(card_width / 2, y_position - 60, f"{item.category}")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(card_width / 2, y_position - 90, f"Detalles:")
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(card_width / 2, y_position - 105, f"{item.details}")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(card_width / 2, y_position - 135, f"Fecha:")
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(card_width / 2, y_position - 150, f"{item.created_at.strftime('%d-%m-%Y')}")

    # Pie de página
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.setFillColor(colors.gray)
    pdf.drawCentredString(card_width / 2, margin, "Sistema de Inventariado - Asociacion Nuevo Amanecer")

    # Finalizar el PDF
    pdf.showPage()
    pdf.save()

    return response
