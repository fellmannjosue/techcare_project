# inventario/views.py

import datetime
import io
import qrcode

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import F, Value, CharField
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import cm

from .models import Computadora, Televisor, Impresora, Router, DataShow
from .forms import (
    CategoryUpdateForm,
    ComputadoraForm,
    TelevisorForm,
    ImpresoraForm,
    RouterForm,
    DataShowForm,
)


@login_required
def dashboard(request):
    """Dashboard con los botones principales."""
    year = datetime.datetime.now().year
    return render(request, 'inventario/dashboard.html', {'year': year})


@login_required
def inventario_por_categoria(request):
    """
    Unifica todos los modelos y permite cambiar categoría inline.
    """
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
    items_qs = None
    for Model, label, field in mapping:
        qs = Model.objects.annotate(
            tipo=Value(label, output_field=CharField()),
            descripcion=F(field),
            categoria=F('category'),
        ).values('tipo', 'id', 'descripcion', 'categoria')
        items_qs = qs if items_qs is None else items_qs.union(qs)

    return render(request, 'inventario/inventario_por_categoria.html', {
        'items': items_qs,
        'form':  form,
        'year':  year,
    })


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
    qs = Computadora.objects.order_by('-id')
    return render(request, 'inventario/inventario_computadoras.html', {
        'form': form,
        'year': year,
        'computadoras': qs,
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
    qs = Televisor.objects.order_by('-id')
    return render(request, 'inventario/inventario_televisores.html', {
        'form': form,
        'year': year,
        'televisores': qs,
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
    qs = Impresora.objects.order_by('-id')
    return render(request, 'inventario/inventario_impresoras.html', {
        'form': form,
        'year': year,
        'impresoras': qs,
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
    qs = Router.objects.order_by('-id')
    return render(request, 'inventario/inventario_routers.html', {
        'form': form,
        'year': year,
        'routers': qs,
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
    qs = DataShow.objects.order_by('-id')
    return render(request, 'inventario/inventario_datashows.html', {
        'form': form,
        'year': year,
        'datashows': qs,
    })


@login_required
def inventario_registros(request):
    """Muestra todos los registros en DataTables con botón QR."""
    year = datetime.datetime.now().year
    mapping = [
        (Computadora, 'Computadora', 'modelo'),
        (Televisor,   'Televisor',   'modelo'),
        (Impresora,   'Impresora',   'nombre'),
        (Router,      'Router',      'modelo'),
        (DataShow,    'DataShow',    'serie'),
    ]
    items_qs = None
    for Model, label, field in mapping:
        qs = Model.objects.annotate(
            tipo=Value(label, output_field=CharField()),
            descripcion=F(field),
            categoria=F('category'),
        ).values('tipo', 'id', 'descripcion', 'categoria')
        items_qs = qs if items_qs is None else items_qs.union(qs)

    return render(request, 'inventario/inventario_registros.html', {
        'items': items_qs,
        'year':  year,
    })


def descargar_qr(request, tipo, pk):
    """
    Genera y descarga un PNG con el QR que apunta al PDF,
    incluyendo el puerto correcto.
    """
    path = reverse('inventario:download_model_pdf', args=[tipo.lower(), pk])
    server_name = request.META.get('SERVER_NAME', request.get_host())
    server_port = request.META.get('SERVER_PORT')
    host = f"{server_name}:{server_port}" if server_port not in ('80', '443') else server_name
    scheme = 'https' if request.is_secure() else 'http'
    pdf_url = f"{scheme}://{host}{path}"

    img = qrcode.make(pdf_url)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return HttpResponse(
        buf.read(),
        content_type='image/png',
        headers={'Content-Disposition': f'attachment; filename="qr_{tipo}_{pk}.png"'}
    )


def download_model_pdf(request, tipo, pk):
    """
    Genera un PDF (Carta horizontal, sin logo) mostrando los campos del ítem,
    centrado con título grande y vista inline.
    """
    # Modelos y campos específicos
    model_map = {
        'computadora': Computadora,
        'televisor':   Televisor,
        'impresora':   Impresora,
        'router':      Router,
        'datashow':    DataShow,
    }
    fields_map = {
        'computadora': [
            ('ID', 'asset_id'),
            ('Modelo', 'modelo'),
            ('Serie', 'serie'),
            ('IP', 'ip'),
            ('Categoría', 'category'),
            ('Asignado a', 'asignado_a'),
            ('Área', 'area'),
            ('Grado', 'grado'),
            ('Fecha Instalación', 'fecha_instalado'),
            ('Observaciones', 'observaciones'),
        ],
        'televisor': [
            ('ID', 'asset_id'),
            ('Modelo', 'modelo'),
            ('Serie', 'serie'),
            ('IP', 'ip'),
            ('Categoría', 'category'),
            ('Grado', 'grado'),
            ('Área', 'area'),
            ('Observaciones', 'observaciones'),
        ],
        'impresora': [
            ('ID', 'asset_id'),
            ('Nombre', 'nombre'),
            ('Modelo', 'modelo'),
            ('Serie', 'serie'),
            ('Categoría', 'category'),
            ('Asignado a', 'asignado_a'),
            ('Nivel Tinta', 'nivel_tinta'),
            ('Últ. llenado', 'ultima_vez_llenado'),
            ('Cant. impresiones', 'cantidad_impresiones'),
            ('A color', 'a_color'),
            ('Observaciones', 'observaciones'),
        ],
        'router': [
            ('ID', 'asset_id'),
            ('Modelo', 'modelo'),
            ('Serie', 'serie'),
            ('Categoría', 'category'),
            ('Nombre Router', 'nombre_router'),
            ('Clave Router', 'clave_router'),
            ('IP Asignada', 'ip_asignada'),
            ('IP de Uso', 'ip_uso'),
            ('Ubicado', 'ubicado'),
            ('Observaciones', 'observaciones'),
        ],
        'datashow': [
            ('ID', 'asset_id'),
            ('Nombre', 'nombre'),
            ('Modelo', 'modelo'),
            ('Serie', 'serie'),
            ('Categoría', 'category'),
            ('Estado', 'estado'),
            ('Cable Corriente', 'cable_corriente'),
            ('HDMI', 'hdmi'),
            ('VGA', 'vga'),
            ('Extensión', 'extension'),
            ('Observaciones', 'observaciones'),
        ],
    }

    tipo = tipo.lower()
    Modelo = model_map.get(tipo)
    campos = fields_map.get(tipo)
    if not Modelo or not campos:
        return HttpResponse(status=404)

    obj = get_object_or_404(Modelo, pk=pk)

    # Crear PDF
    buffer = io.BytesIO()
    width, height = landscape(letter)
    pdf = canvas.Canvas(buffer, pagesize=(width, height))
    pdf.setTitle(f"Ficha de {tipo.capitalize()} – {getattr(obj, 'asset_id', obj.pk)}")

    # Fondo
    pdf.setFillColor(colors.white)
    pdf.rect(0, 0, width, height, fill=1, stroke=0)

    # Título grande centrado
    pdf.setFont("Helvetica-Bold", 24)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(width / 2, height - 50, f"Ficha de {tipo.capitalize()}")

    # Tabla de datos
    data = [["Campo", "Valor"]]
    for label, attr in campos:
        val = getattr(obj, attr)
        if isinstance(val, bool):
            val = "Sí" if val else "No"
        data.append([label, str(val)])

    table = Table(data, colWidths=[6 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007bff")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.gray),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ]))

    # Centrar la tabla
    table_width, table_height = table.wrap(0, 0)
    x = (width - table_width) / 2
    y = height - 80 - table_height
    table.drawOn(pdf, x, y)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return HttpResponse(
        buffer.read(),
        content_type='application/pdf',
        headers={'Content-Disposition': 'inline; filename="ficha.pdf"'}
    )
