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

from .models import Computadora, Televisor, Impresora, Router, DataShow
from .forms import CategoryUpdateForm, ComputadoraForm, TelevisorForm, ImpresoraForm, RouterForm, DataShowForm


@login_required
def dashboard(request):
    year = datetime.datetime.now().year
    return render(request, 'inventario/dashboard.html', {'year': year})


@login_required
def inventario_por_categoria(request):
    year = datetime.datetime.now().year

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

    mapping = [
        (Computadora, 'Computadora', 'modelo'),
        (Televisor,   'Televisor',   'modelo'),
        (Impresora,   'Impresora',   'nombre'),
        (Router,      'Router',      'modelo'),
        (DataShow,    'DataShow',    'serie'),
    ]
    items = None
    for Model, label, field in mapping:
        qs = Model.objects.annotate(
            tipo=Value(label, output_field=CharField()),
            descripcion=F(field),
            categoria=F('category'),
        ).values('tipo', 'id', 'descripcion', 'categoria')
        items = qs if items is None else items.union(qs)

    return render(request, 'inventario/inventario_por_categoria.html', {
        'items': items,
        'form':  form,
        'year':  year,
    })


@login_required
def inventario_registros(request):
    year = datetime.datetime.now().year
    mapping = [
        (Computadora, 'Computadora', 'modelo'),
        (Televisor,   'Televisor',   'modelo'),
        (Impresora,   'Impresora',   'nombre'),
        (Router,      'Router',      'modelo'),
        (DataShow,    'DataShow',    'serie'),
    ]
    items = None
    for Model, label, field in mapping:
        qs = Model.objects.annotate(
            tipo=Value(label, output_field=CharField()),
            descripcion=F(field),
            categoria=F('category'),
        ).values('tipo', 'id', 'descripcion', 'categoria')
        items = qs if items is None else items.union(qs)

    return render(request, 'inventario/inventario_registros.html', {
        'items': items,
        'year':  year,
    })


@login_required
def descargar_qr(request, tipo, pk):
    """
    Genera y descarga un PNG con el QR que apunta al PDF de la ficha.
    """
    pdf_url = request.build_absolute_uri(
        reverse('inventario:download_model_pdf', args=[tipo.lower(), pk])
    )
    img = qrcode.make(pdf_url)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return HttpResponse(
        buf.read(),
        content_type='image/png',
        headers={'Content-Disposition': f'attachment; filename="qr_{tipo}_{pk}.png"'}
    )


@login_required
def download_model_pdf(request, tipo, pk):
    """
    Genera la ficha PDF de cualquier ítem (Computadora, Televisor, etc.)
    usando ReportLab y una tabla de sus campos.
    """
    model_map = {
        'computadora': Computadora,
        'televisor':   Televisor,
        'impresora':   Impresora,
        'router':      Router,
        'datashow':    DataShow,
    }
    Modelo = model_map.get(tipo.lower())
    if not Modelo:
        return HttpResponse(status=404)

    obj = get_object_or_404(Modelo, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{tipo}_{pk}.pdf"'

    w, h = 15 * cm, 15 * cm
    pdf = canvas.Canvas(response, pagesize=(w, h))
    pdf.setTitle(f"{tipo.capitalize()} – ID {getattr(obj, 'asset_id', obj.pk)}")

    # Fondo
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, w, h, fill=1)

    # Logo
    logo_path = finders.find('inventario/img/ana.jpg')
    if logo_path:
        sz = 60
        x = (w - sz) / 2
        y = h - sz - 30
        pdf.drawImage(logo_path, x, y, width=sz, height=sz)

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(w/2, y - 20, f"Ficha de {tipo.capitalize()}")

    # Datos en tabla
    data = [["Campo", "Valor"]]
    for field in obj._meta.fields:
        # evita el ID interno si asset_id existe
        name = field.verbose_name.title()
        val  = field.value_from_object(obj)
        data.append([name, str(val)])

    table = Table(data, colWidths=[5*cm, 8*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#007bff")),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.gray),
        ("FONTNAME",   (0,1), (-1,-1), "Helvetica"),
    ]))
    table.wrapOn(pdf, w, h)
    table.drawOn(pdf, x=2*cm, y=h - 8*cm)

    pdf.showPage()
    pdf.save()
    return response


@login_required
def inventario_computadoras(request):
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
        'form': form, 'year': year, 'computadoras': computadoras,
    })


@login_required
def inventario_televisores(request):
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
        'form': form, 'year': year, 'televisores': televisores,
    })


@login_required
def inventario_impresoras(request):
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
        'form': form, 'year': year, 'impresoras': impresoras,
    })


@login_required
def inventario_routers(request):
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
        'form': form, 'year': year, 'routers': routers,
    })


@login_required
def inventario_datashows(request):
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
        'form': form, 'year': year, 'datashows': datashows,
    })
