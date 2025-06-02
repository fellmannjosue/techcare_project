import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib import colors

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
)

@login_required
def dashboard(request):
    """Dashboard con los 8 botones de inventario."""
    year = datetime.datetime.now().year
    return render(request, 'inventario/dashboard.html', {
        'year': year,
    })

@login_required
def inventario_por_categoria(request):
    """Formulario y lista de InventoryItem (categorías genéricas)."""
    year = datetime.datetime.now().year

    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:inventario_por_categoria')
    else:
        form = InventoryItemForm()

    items = InventoryItem.objects.order_by('-created_at')
    return render(request, 'inventario/inventario_por_categoria.html', {
        'form':  form,
        'items': items,
        'year':  year,
    })

@login_required
def download_item_pdf(request, item_id):
    """Genera la ficha PDF de un InventoryItem."""
    item = get_object_or_404(InventoryItem, id=item_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="item_{item.id}.pdf"'

    cm = 28.35
    w, h = 15*cm, 15*cm
    pdf = canvas.Canvas(response, pagesize=(w, h))
    pdf.setTitle(f"Ficha Inventario – ID {item.id}")

    # Fondo
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, w, h, fill=1)

    # Logo
    logo_path = finders.find('inventario/img/ana.jpg')
    if logo_path:
        logo_w = logo_h = 60
        x = (w - logo_w) / 2
        y = h - logo_h - 30
        pdf.setFillColor(colors.white)
        pdf.rect(x-5, y-5, logo_w+10, logo_h+10, fill=1)
        pdf.drawImage(logo_path, x, y, width=logo_w, height=logo_h)

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(w/2, y-20, "Ficha de Inventario")

    # Datos
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColor(colors.black)
    y0 = y - 50
    def draw(label, val, offset):
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(w/2, y0 - offset, label)
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(w/2, y0 - offset - 15, str(val))

    draw("ID:",        item.id,           0)
    draw("Categoría:", item.category,    60)
    draw("Detalles:",  item.details,     120)
    draw("Fecha:",     item.created_at.strftime('%d-%m-%Y'), 180)

    # Pie
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.setFillColor(colors.gray)
    pdf.drawCentredString(w/2, 20, "Sistema de Inventariado – Asociación Nuevo Amanecer")

    pdf.showPage()
    pdf.save()
    return response

# views.py
@login_required
def inventario_computadoras(request):
    year = datetime.datetime.now().year
    computadoras = Computadora.objects.order_by('-id')  # renombrado

    if request.method == 'POST':
        form = ComputadoraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:inventario_computadoras')
    else:
        form = ComputadoraForm()

    return render(request, 'inventario/inventario_computadoras.html', {
        'form':         form,
        'year':         year,
        'computadoras': computadoras,  # aquí también
    })



@login_required
def inventario_televisores(request):
    """Formulario para Televisores."""
    year = datetime.datetime.now().year
    if request.method == 'POST':
        form = TelevisorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:dashboard')
    else:
        form = TelevisorForm()
    return render(request, 'inventario/inventario_televisores.html', {
        'form': form,
        'year': year,
    })

@login_required
def inventario_impresoras(request):
    """Formulario para Impresoras."""
    year = datetime.datetime.now().year
    if request.method == 'POST':
        form = ImpresoraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:dashboard')
    else:
        form = ImpresoraForm()
    return render(request, 'inventario/inventario_impresoras.html', {
        'form': form,
        'year': year,
    })

@login_required
def inventario_routers(request):
    """Formulario para Routers."""
    year = datetime.datetime.now().year
    if request.method == 'POST':
        form = RouterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:dashboard')
    else:
        form = RouterForm()
    return render(request, 'inventario/inventario_routers.html', {
        'form': form,
        'year': year,
    })

@login_required
def inventario_datashows(request):
    """Formulario para DataShows."""
    year = datetime.datetime.now().year
    if request.method == 'POST':
        form = DataShowForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:dashboard')
    else:
        form = DataShowForm()
    return render(request, 'inventario/inventario_datashows.html', {
        'form': form,
        'year': year,
    })

@login_required
def inventario_registros(request):
    """
    Ver registros: tabla desplegable según la categoría seleccionada.
    Pasa 'year' para el footer y asegura que 'cat' no sea None.
    """
    year = datetime.datetime.now().year
    cat  = request.GET.get('cat', '')  # valor por defecto vacío

    if cat == 'computadoras':
        qs = Computadora.objects.all()
    elif cat == 'televisores':
        qs = Televisor.objects.all()
    elif cat == 'impresoras':
        qs = Impresora.objects.all()
    elif cat == 'routers':
        qs = Router.objects.all()
    elif cat == 'datashows':
        qs = DataShow.objects.all()
    else:
        qs = []

    return render(request, 'inventario/inventario_registros.html', {
        'queryset': qs,
        'category': cat,
        'year':     year,
    })
