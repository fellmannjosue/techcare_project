# inventario/views.py

import datetime
import io
import qrcode

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import F, Value, CharField
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.staticfiles import finders

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm

from .models import (
    InventoryItem,
    Computadora,
    Televisor,
    Impresora,
    Router,
    DataShow,
)
from .forms import (
    InventoryItemForm,
    ComputadoraForm,
    TelevisorForm,
    ImpresoraForm,
    RouterForm,
    DataShowForm,
    CategoryUpdateForm,
)


@login_required
def dashboard(request):
    """Dashboard con los botones principales de inventario."""
    year = datetime.datetime.now().year
    return render(request, 'inventario/dashboard.html', {
        'year': year,
    })


@login_required
def inventario_por_categoria(request):
    """
    Lista unificada de Computadoras, Televisores, Impresoras, Routers y DataShows
    con formulario inline para cambiar la categoría al vuelo.
    """
    year = datetime.datetime.now().year

    # Procesar formulario inline de cambio de categoría
    if request.method == 'POST':
        form = CategoryUpdateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada correctamente.")
            return redirect('inventario:inventario_por_categoria')
        else:
            messages.error(request, "Error al actualizar categoría.")
    else:
        form = CategoryUpdateForm()

    # Construir y unir los querysets anotados
    mapping = [
        (Computadora, 'Computadora', 'modelo'),
        (Televisor,   'Televisor',   'modelo'),
        (Impresora,   'Impresora',   'nombre'),
        (Router,      'Router',      'modelo'),
        (DataShow,    'DataShow',    'serie'),
    ]
    items_qs = None
    for Model, tipo_label, campo in mapping:
        qs = Model.objects.annotate(
            tipo=Value(tipo_label, output_field=CharField()),
            descripcion=F(campo),
            categoria=F('category'),
        ).values('tipo', 'id', 'descripcion', 'categoria')
        items_qs = qs if items_qs is None else items_qs.union(qs)

    return render(request, 'inventario/inventario_por_categoria.html', {
        'items': items_qs,
        'form':  form,
        'year':  year,
    })


@login_required
def inventario_registros(request):
    """
    Ver todos los registros en una tabla con DataTables
    y botón para descargar PDF vía QR.
    """
    mapping = [
        (Computadora, 'Computadora', 'modelo'),
        (Televisor,   'Televisor',   'modelo'),
        (Impresora,   'Impresora',   'nombre'),
        (Router,      'Router',      'modelo'),
        (DataShow,    'DataShow',    'serie'),
    ]
    items_qs = None
    for Model, tipo_label, campo in mapping:
        qs = Model.objects.annotate(
            tipo=Value(tipo_label, output_field=CharField()),
            descripcion=F(campo),
            categoria=F('category'),
        ).values('tipo', 'id', 'descripcion', 'categoria')
        items_qs = qs if items_qs is None else items_qs.union(qs)

    year = datetime.datetime.now().year
    return render(request, 'inventario/inventario_registros.html', {
        'items': items_qs,
        'year':  year,
    })


@login_required
def descargar_qr(request, tipo, pk):
    """
    Genera y descarga un PNG con el QR que apunta
    al PDF de la ficha (download_item_pdf).
    """
    pdf_url = request.build_absolute_uri(
        reverse('inventario:download_item_pdf', args=[pk])
    )
    img = qrcode.make(pdf_url)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    response = HttpResponse(buf.read(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="qr_{tipo}_{pk}.png"'
    return response


@login_required
def download_item_pdf(request, item_id):
    """
    Genera la ficha PDF de un InventoryItem usando ReportLab
    y la devuelve como descarga.
    """
    item = get_object_or_404(InventoryItem, id=item_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="item_{item.id}.pdf"'

    # Dimensiones en cm
    w, h = 15 * cm, 15 * cm
    pdf = canvas.Canvas(response, pagesize=(w, h))
    pdf.setTitle(f"Ficha de Inventario – ID {item.id}")

    # Fondo
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, w, h, fill=1)

    # Logo
    logo_path = finders.find('inventario/img/ana.jpg')
    if logo_path:
        logo_sz = 60
        x = (w - logo_sz) / 2
        y = h - logo_sz - 30
        pdf.drawImage(logo_path, x, y, width=logo_sz, height=logo_sz)

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(w / 2, y - 20, "Ficha de Inventario")

    # Datos en tabla
    data = [
        ["Campo",      "Valor"],
        ["ID",         str(item.id)],
        ["Categoría",  item.category],
        ["Detalles",   item.details],
        ["Fecha",      item.created_at.strftime('%d-%m-%Y %H:%M')],
    ]
    table = Table(data, colWidths=[5 * cm, 8 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007bff")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.gray),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
    ]))

    # Posicionar la tabla
    table.wrapOn(pdf, w, h)
    table.drawOn(pdf, x=2 * cm, y=h - 8 * cm)

    pdf.showPage()
    pdf.save()
    return response


@login_required
def inventario_computadoras(request):
    """Formulario y lista de Computadoras."""
    year = datetime.datetime.now().year
    if request.method == 'POST':
        form = ComputadoraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:inventario_computadoras')
    else:
        form = ComputadoraForm()
    computadoras = Computadora.objects.order_by('-id')
    return render(request, 'inventario/inventario_computadoras.html', {
        'form': form, 'year': year, 'computadoras': computadoras
    })


@login_required
def inventario_televisores(request):
    """Formulario y lista de Televisores."""
    year = datetime.datetime.now().year
    if request.method == 'POST':
        form = TelevisorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:inventario_televisores')
    else:
        form = TelevisorForm()
    televisores = Televisor.objects.order_by('-id')
    return render(request, 'inventario/inventario_televisores.html', {
        'form': form, 'year': year, 'televisores': televisores
    })


@login_required
def inventario_impresoras(request):
    """Formulario y lista de Impresoras."""
    year = datetime.datetime.now().year
    if request.method == 'POST':
        form = ImpresoraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:inventario_impresoras')
    else:
        form = ImpresoraForm()
    impresoras = Impresora.objects.order_by('-id')
    return render(request, 'inventario/inventario_impresoras.html', {
        'form': form, 'year': year, 'impresoras': impresoras
    })


@login_required
def inventario_routers(request):
    """Formulario y lista de Routers."""
    year = datetime.datetime.now().year
    if request.method == 'POST':
        form = RouterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:inventario_routers')
    else:
        form = RouterForm()
    routers = Router.objects.order_by('-id')
    return render(request, 'inventario/inventario_routers.html', {
        'form': form, 'year': year, 'routers': routers
    })


@login_required
def inventario_datashows(request):
    """Formulario y lista de DataShows."""
    year = datetime.datetime.now().year
    if request.method == 'POST':
        form = DataShowForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:inventario_datashows')
    else:
        form = DataShowForm()
    datashows = DataShow.objects.order_by('-id')
    return render(request, 'inventario/inventario_datashows.html', {
        'form': form, 'year': year, 'datashows': datashows
    })
