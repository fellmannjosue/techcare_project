import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from .models import InventoryItem
from .forms import InventoryItemForm


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
    """
    Genera un PDF para un InventoryItem, cargando el logo
    desde los archivos estáticos con django.contrib.staticfiles.finders.
    """
    item = get_object_or_404(InventoryItem, id=item_id)

    # Preparamos la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="item_{item.id}.pdf"'

    # Dimensiones (15 cm x 15 cm)
    card_w  = 15 * 28.35
    card_h  = 15 * 28.35
    pdf     = canvas.Canvas(response, pagesize=(card_w, card_h))
    pdf.setTitle(f"Ficha de Inventario - ID {item.id}")

    # Fondo claro
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, card_w, card_h, fill=1)

    # --- Logo estático ---
    logo_path = finders.find('inventario/img/ana.jpg')
    if logo_path:
        logo_w, logo_h = 60, 60
        logo_x = (card_w - logo_w) / 2
        logo_y = card_h - logo_h - 30

        # Fondo blanco tras el logo
        pdf.setFillColor(colors.white)
        pdf.rect(logo_x - 5, logo_y - 5, logo_w + 10, logo_h + 10, fill=1)

        # Dibujamos el logo desde ruta local
        pdf.drawImage(logo_path, logo_x, logo_y, width=logo_w, height=logo_h)

    # Título centrado
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(card_w / 2, logo_y - 20, "Ficha de Inventario")

    # Contenido
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColor(colors.black)
    y0 = logo_y - 50

    def draw_centered(label, value, y_offset):
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(card_w/2, y0 - y_offset, label)
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(card_w/2, y0 - y_offset - 15, str(value))

    draw_centered("ID:",        item.id,              0)
    draw_centered("Categoría:", item.category,       60)
    draw_centered("Detalles:",  item.details,        120)
    draw_centered("Fecha:",     item.created_at.strftime('%d-%m-%Y'), 180)

    # Pie
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.setFillColor(colors.gray)
    pdf.drawCentredString(card_w/2, 20, "Sistema de Inventariado - Asociación Nuevo Amanecer")

    pdf.showPage()
    pdf.save()
    return response