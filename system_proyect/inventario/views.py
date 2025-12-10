# inventario/views.py

import datetime
import io
import qrcode
from PIL import Image

from django.shortcuts           import render, redirect, get_object_or_404
from django.urls                import reverse
from django.db.models           import F, Value, CharField
from django.http                import HttpResponse
from django.contrib             import messages
from django.contrib.auth.decorators import login_required

from reportlab.pdfgen           import canvas
from reportlab.lib              import colors
from reportlab.platypus         import Table, TableStyle
from reportlab.lib.pagesizes    import letter, landscape
from reportlab.lib.units        import cm

from .models    import Computadora, Televisor, Impresora, Router, DataShow, Monitor
from .forms     import (
    CategoryUpdateForm,
    ComputadoraForm,
    TelevisorForm,
    ImpresoraForm,
    RouterForm,
    DataShowForm,
    ComputadoraFilterForm,
    MonitorForm,
)


def descargar_qr(request, tipo, pk):
    """
    Genera un código QR (JPEG) que apunta a la URL de descarga de la ficha PDF
    de un objeto (computadora, televisor, etc.).
    """
    # Construye la URL absoluta al endpoint de PDF
    path = reverse('inventario:download_model_pdf', args=[tipo.lower(), pk])
    pdf_url = f"https://servicios.ana-hn.org:437{path}"  # ← SIEMPRE este dominio y puerto

    # Generación de QR y conversión a JPEG
    img = qrcode.make(pdf_url)
    rgb_img = img.convert("RGB")
    buf = io.BytesIO()
    rgb_img.save(buf, format='JPEG', quality=85)
    buf.seek(0)

    # Devolver imagen como attachment
    return HttpResponse(
        buf.read(),
        content_type='image/jpeg',
        headers={'Content-Disposition': f'attachment; filename="qr_{tipo}_{pk}.jpg"'}
    )


@login_required
def dashboard(request):
    """
    Vista principal del módulo de inventario.
    Muestra el dashboard con enlaces a los diferentes submódulos.
    """
    year = datetime.datetime.now().year
    return render(request, 'inventario/dashboard.html', {'year': year})


@login_required
def inventario_por_categoria(request):
    """
    Muestra un listado consolidado de todos los ítems de inventario,
    agrupados por categoría. Incluye un formulario inline para actualizar
    la categoría de cada registro.
    """
    year = datetime.datetime.now().year

    # Procesar el formulario de actualización de categoría
    if request.method == 'POST':
        form = CategoryUpdateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada correctamente.")
            return redirect('inventario:inventario_por_categoria')
        messages.error(request, "Error al actualizar categoría.")
    else:
        form = CategoryUpdateForm()

    # Unir los querysets de cada modelo en uno solo
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
    """
    Vista para crear nuevas computadoras y listar todas las computadoras
    registradas, sin filtros avanzados. Ordena por ID descendente.
    """
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
        'form':         form,
        'year':         year,
        'computadoras': qs,
    })


@login_required
def computadoras_list(request):
    """
    Nueva vista de lista de computadoras con filtrado por campos.
    Usa ComputadoraFilterForm para capturar criterios de búsqueda via GET.
    """
    year = datetime.datetime.now().year
    form = ComputadoraFilterForm(request.GET or None)

    # Queryset inicial: todas las computadoras, ordenadas por fecha de instalación desc.
    qs = Computadora.objects.order_by('-fecha_instalado')

    # Aplicar filtros si el formulario es válido
    if form.is_valid():
        cd = form.cleaned_data
        if cd['asset_id']:
            qs = qs.filter(asset_id__icontains=cd['asset_id'])
        if cd['modelo']:
            qs = qs.filter(modelo__icontains=cd['modelo'])
        if cd['serie']:
            qs = qs.filter(serie__icontains=cd['serie'])
        if cd['ip']:
            qs = qs.filter(ip__icontains=cd['ip'])
        if cd['asignado_a']:
            qs = qs.filter(asignado_a__icontains=cd['asignado_a'])
        if cd['area']:
            qs = qs.filter(area__icontains=cd['area'])
        if cd['grado']:
            qs = qs.filter(grado__icontains=cd['grado'])
        if cd['fecha_instalado']:
            qs = qs.filter(fecha_instalado=cd['fecha_instalado'])

    return render(request, 'inventario/filtro_computadoras.html', {
        'form':         form,
        'computadoras': qs,
        'year':         year,
    })


@login_required
def inventario_televisores(request):
    """
    Vista para crear y listar televisores. Ordena por ID descendente.
    """
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
        'form':       form,
        'year':       year,
        'televisores': qs,
    })


@login_required
def inventario_impresoras(request):
    """
    Vista para crear y listar impresoras. Ordena por ID descendente.
    """
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
        'form':       form,
        'year':       year,
        'impresoras': qs,
    })


@login_required
def inventario_routers(request):
    """
    Vista para crear y listar routers. Ordena por ID descendente.
    """
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
        'form':    form,
        'year':    year,
        'routers': qs,
    })


@login_required
def inventario_datashows(request):
    """
    Vista para crear y listar DataShows. Ordena por ID descendente.
    """
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
        'form':      form,
        'year':      year,
        'datashows': qs,
    })


@login_required
def inventario_registros(request):
    """
    Vista que carga cada categoría de inventario en listas separadas
    para que los TABS del template puedan mostrar los datos correctamente.
    """

    year = datetime.datetime.now().year

    # Cargar registros individuales (orden correcto ascendente)
    computadoras = Computadora.objects.all().order_by('id')
    impresoras   = Impresora.objects.all().order_by('id')
    televisores  = Televisor.objects.all().order_by('id')
    routers      = Router.objects.all().order_by('id')
    datashows    = DataShow.objects.all().order_by('id')

    # MONITORES (si aún no existe el modelo, no romper)
    try:
        from .models import Monitor
        monitores = Monitor.objects.all().order_by('id')
    except:
        monitores = []

    # Enviar todo al HTML
    return render(request, "inventario/inventario_registros.html", {
        "computadoras": computadoras,
        "impresoras":   impresoras,
        "televisores":  televisores,
        "routers":      routers,
        "datashows":    datashows,
        "monitores":    monitores,
        "year":         year,
    })

@login_required
def inventario_monitores(request):
    """
    Vista para crear y listar monitores. Ordena por ID descendente.
    """
    year = datetime.datetime.now().year

    if request.method == 'POST':
        form = MonitorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:inventario_monitores')
    else:
        form = MonitorForm()

    qs = Monitor.objects.order_by('-id')

    return render(request, 'inventario/inventario_monitores.html', {
        'form':       form,
        'year':       year,
        'monitores':  qs,
    })


def download_model_pdf(request, tipo, pk):
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

    # Preparar lienzo PDF en horizontal
    buffer = io.BytesIO()
    width, height = landscape(letter)
    pdf = canvas.Canvas(buffer, pagesize=(width, height))
    pdf.setTitle(f"Ficha de {tipo.capitalize()} – {getattr(obj, 'asset_id', obj.pk)}")

    # Fondo blanco
    pdf.setFillColor(colors.white)
    pdf.rect(0, 0, width, height, fill=1, stroke=0)

    # Título
    pdf.setFont("Helvetica-Bold", 24)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(width / 2, height - 50, f"Ficha de {tipo.capitalize()}")

    # Construir tabla con datos
    data = [["Campo", "Valor"]]
    for label, attr in campos:
        val = getattr(obj, attr)
        if isinstance(val, bool):
            val = "Sí" if val else "No"
        data.append([label, str(val)])

    # Estilo de tabla
    table_width = width - 4 * cm
    col1 = table_width * 0.35
    col2 = table_width * 0.65
    table = Table(data, colWidths=[col1, col2], hAlign='CENTER')
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007bff")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 14),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",   (0, 1), (-1, -1), 12),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ]))

    # Dibujar tabla centrada
    tw, th = table.wrap(0, 0)
    x = (width - tw) / 2
    y = height - 80 - th
    table.drawOn(pdf, x, y)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return HttpResponse(
        buffer.read(),
        content_type='application/pdf',
        headers={'Content-Disposition': 'inline; filename="ficha.pdf"'}
    )
