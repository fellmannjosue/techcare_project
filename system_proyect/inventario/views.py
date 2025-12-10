# ==============================================================
# INVENTARIO – VISTAS COMPLETAS Y COMPATIBLES CON AJAX + MODALES
# ==============================================================

import datetime
import io
import qrcode
from PIL import Image

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import F, Value, CharField
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import cm

from .models import (
    Computadora, Televisor, Impresora, Router, DataShow, Monitor
)

from .forms import (
    CategoryUpdateForm,
    ComputadoraForm,
    TelevisorForm,
    ImpresoraForm,
    RouterForm,
    DataShowForm,
    ComputadoraFilterForm,
    MonitorForm
)

# ==============================================================
# QR PARA FICHAS
# ==============================================================

def descargar_qr(request, tipo, pk):
    path = reverse("inventario:download_model_pdf", args=[tipo.lower(), pk])
    pdf_url = f"https://servicios.ana-hn.org:437{path}"

    img = qrcode.make(pdf_url)
    rgb = img.convert("RGB")
    buffer = io.BytesIO()
    rgb.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)

    return HttpResponse(
        buffer.read(),
        content_type="image/jpeg",
        headers={"Content-Disposition": f'attachment; filename="qr_{tipo}_{pk}.jpg"'}
    )

# ==============================================================
# DASHBOARD
# ==============================================================

@login_required
def dashboard(request):
    year = datetime.datetime.now().year
    return render(request, "inventario/dashboard.html", {"year": year})

# ==============================================================
# POR CATEGORÍA
# ==============================================================

@login_required
def inventario_por_categoria(request):
    year = datetime.datetime.now().year

    if request.method == "POST":
        form = CategoryUpdateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada con éxito.")
            return redirect("inventario:inventario_por_categoria")
        messages.error(request, "Error al actualizar la categoría.")
    else:
        form = CategoryUpdateForm()

    mapping = [
        (Computadora, "Computadora", "modelo"),
        (Televisor, "Televisor", "modelo"),
        (Impresora, "Impresora", "nombre"),
        (Router, "Router", "modelo"),
        (DataShow, "DataShow", "serie"),
        (Monitor, "Monitor", "modelo"),
    ]

    items = None
    for Model, label, field in mapping:
        qs = Model.objects.annotate(
            tipo=Value(label, output_field=CharField()),
            descripcion=F(field),
            categoria=F("category"),
        ).values("tipo", "id", "descripcion", "categoria")

        items = qs if items is None else items.union(qs)

    return render(request, "inventario/inventario_por_categoria.html", {
        "items": items,
        "form": form,
        "year": year
    })

# ==============================================================
# INVENTARIOS (CREATE + LIST)
# ==============================================================

@login_required
def inventario_computadoras(request):
    year = datetime.datetime.now().year

    if request.method == "POST":
        form = ComputadoraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventario:inventario_computadoras")
    else:
        form = ComputadoraForm()

    return render(request, "inventario/inventario_computadoras.html", {
        "form": form,
        "year": year,
        "computadoras": Computadora.objects.order_by("-id")
    })


@login_required
def computadoras_list(request):
    year = datetime.datetime.now().year
    form = ComputadoraFilterForm(request.GET or None)
    qs = Computadora.objects.order_by("-fecha_instalado")

    if form.is_valid():
        cd = form.cleaned_data
        for field, val in cd.items():
            if val:
                qs = qs.filter(**{f"{field}__icontains": val})

    return render(request, "inventario/filtro_computadoras.html", {
        "form": form,
        "computadoras": qs,
        "year": year
    })


@login_required
def inventario_televisores(request):
    year = datetime.datetime.now().year

    if request.method == "POST":
        form = TelevisorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventario:inventario_televisores")
    else:
        form = TelevisorForm()

    return render(request, "inventario/inventario_televisores.html", {
        "form": form,
        "year": year,
        "televisores": Televisor.objects.order_by("-id")
    })


@login_required
def inventario_impresoras(request):
    year = datetime.datetime.now().year

    if request.method == "POST":
        form = ImpresoraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventario:inventario_impresoras")
    else:
        form = ImpresoraForm()

    return render(request, "inventario/inventario_impresoras.html", {
        "form": form,
        "year": year,
        "impresoras": Impresora.objects.order_by("-id")
    })


@login_required
def inventario_routers(request):
    year = datetime.datetime.now().year

    if request.method == "POST":
        form = RouterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventario:inventario_routers")
    else:
        form = RouterForm()

    return render(request, "inventario/inventario_routers.html", {
        "form": form,
        "year": year,
        "routers": Router.objects.order_by("-id")
    })


@login_required
def inventario_datashows(request):
    year = datetime.datetime.now().year

    if request.method == "POST":
        form = DataShowForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventario:inventario_datashows")
    else:
        form = DataShowForm()

    return render(request, "inventario/inventario_datashows.html", {
        "form": form,
        "year": year,
        "datashows": DataShow.objects.order_by("-id")
    })


@login_required
def inventario_monitores(request):
    year = datetime.datetime.now().year

    if request.method == "POST":
        form = MonitorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventario:inventario_monitores")
    else:
        form = MonitorForm()

    return render(request, "inventario/inventario_monitores.html", {
        "form": form,
        "year": year,
        "monitores": Monitor.objects.order_by("-id")
    })


# ==============================================================
# INVENTARIO REGISTROS (TABS CONSOLIDADOS)
# ==============================================================

@login_required
def inventario_registros(request):
    year = datetime.datetime.now().year

    return render(request, "inventario/inventario_registros.html", {
        "computadoras": Computadora.objects.order_by("id"),
        "impresoras": Impresora.objects.order_by("id"),
        "televisores": Televisor.objects.order_by("id"),
        "routers": Router.objects.order_by("id"),
        "datashows": DataShow.objects.order_by("id"),
        "monitores": Monitor.objects.order_by("id"),
        "year": year,
    })

# ==============================================================
# GET (Cargar formulario en el modal)
# ==============================================================

@login_required
def get_computadora(request, pk):
    obj = get_object_or_404(Computadora, pk=pk)
    form = ComputadoraForm(instance=obj)
    return render(request, "inventario/edit_computadora.html", {"form": form, "obj": obj})

@login_required
def get_televisor(request, pk):
    obj = get_object_or_404(Televisor, pk=pk)
    form = TelevisorForm(instance=obj)
    return render(request, "inventario/edit_televisor.html", {"form": form, "obj": obj})

@login_required
def get_impresora(request, pk):
    obj = get_object_or_404(Impresora, pk=pk)
    form = ImpresoraForm(instance=obj)
    return render(request, "inventario/edit_impresora.html", {"form": form, "obj": obj})

@login_required
def get_router(request, pk):
    obj = get_object_or_404(Router, pk=pk)
    form = RouterForm(instance=obj)
    return render(request, "inventario/edit_router.html", {"form": form, "obj": obj})

@login_required
def get_datashow(request, pk):
    obj = get_object_or_404(DataShow, pk=pk)
    form = DataShowForm(instance=obj)
    return render(request, "inventario/edit_datashow.html", {"form": form, "obj": obj})

@login_required
def get_monitor(request, pk):
    obj = get_object_or_404(Monitor, pk=pk)
    form = MonitorForm(instance=obj)
    return render(request, "inventario/edit_monitor.html", {"form": form, "obj": obj})

# ==============================================================
# UPDATE (Guardar cambios vía AJAX)
# ==============================================================

@login_required
def update_computadora(request, pk):
    obj = get_object_or_404(Computadora, pk=pk)
    form = ComputadoraForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False, "errors": form.errors})


@login_required
def update_televisor(request, pk):
    obj = get_object_or_404(Televisor, pk=pk)
    form = TelevisorForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False, "errors": form.errors})


@login_required
def update_impresora(request, pk):
    obj = get_object_or_404(Impresora, pk=pk)
    form = ImpresoraForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False, "errors": form.errors})


@login_required
def update_router(request, pk):
    obj = get_object_or_404(Router, pk=pk)
    form = RouterForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False, "errors": form.errors})


@login_required
def update_datashow(request, pk):
    obj = get_object_or_404(DataShow, pk=pk)
    form = DataShowForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False, "errors": form.errors})


@login_required
def update_monitor(request, pk):
    obj = get_object_or_404(Monitor, pk=pk)
    form = MonitorForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False, "errors": form.errors})

# ==============================================================
# DELETE (JSON)
# ==============================================================

@login_required
def eliminar_computadora(request, pk):
    get_object_or_404(Computadora, pk=pk).delete()
    return JsonResponse({"ok": True})

@login_required
def eliminar_televisor(request, pk):
    get_object_or_404(Televisor, pk=pk).delete()
    return JsonResponse({"ok": True})

@login_required
def eliminar_impresora(request, pk):
    get_object_or_404(Impresora, pk=pk).delete()
    return JsonResponse({"ok": True})

@login_required
def eliminar_router(request, pk):
    get_object_or_404(Router, pk=pk).delete()
    return JsonResponse({"ok": True})

@login_required
def eliminar_datashow(request, pk):
    get_object_or_404(DataShow, pk=pk).delete()
    return JsonResponse({"ok": True})

@login_required
def eliminar_monitor(request, pk):
    get_object_or_404(Monitor, pk=pk).delete()
    return JsonResponse({"ok": True})


# ==============================================================
# PDF GENERATOR
# ==============================================================

def download_model_pdf(request, tipo, pk):
    model_map = {
        "computadora": Computadora,
        "televisor": Televisor,
        "impresora": Impresora,
        "router": Router,
        "datashow": DataShow,
        "monitor": Monitor,
    }

    fields_map = {
        "computadora": [
            ("ID", "asset_id"),
            ("Modelo", "modelo"),
            ("Serie", "serie"),
            ("IP", "ip"),
            ("Categoría", "category"),
            ("Asignado a", "asignado_a"),
            ("Área", "area"),
            ("Grado", "grado"),
            ("Fecha Instalación", "fecha_instalado"),
            ("Observaciones", "observaciones"),
        ],
        "televisor": [
            ("ID", "asset_id"),
            ("Modelo", "modelo"),
            ("Serie", "serie"),
            ("IP", "ip"),
            ("Categoría", "category"),
            ("Grado", "grado"),
            ("Área", "area"),
            ("Observaciones", "observaciones"),
        ],
        "impresora": [
            ("ID", "asset_id"),
            ("Nombre", "nombre"),
            ("Modelo", "modelo"),
            ("Serie", "serie"),
            ("Categoría", "category"),
            ("Asignado a", "asignado_a"),
            ("Nivel Tinta", "nivel_tinta"),
            ("Últ. Llenado", "ultima_vez_llenado"),
            ("Cantidad Impresiones", "cantidad_impresiones"),
            ("A Color", "a_color"),
            ("Observaciones", "observaciones"),
        ],
        "router": [
            ("ID", "asset_id"),
            ("Modelo", "modelo"),
            ("Serie", "serie"),
            ("Categoría", "category"),
            ("Nombre Router", "nombre_router"),
            ("Clave Router", "clave_router"),
            ("IP Asignada", "ip_asignada"),
            ("IP de Uso", "ip_uso"),
            ("Ubicado", "ubicado"),
            ("Observaciones", "observaciones"),
        ],
        "datashow": [
            ("ID", "asset_id"),
            ("Nombre", "nombre"),
            ("Modelo", "modelo"),
            ("Serie", "serie"),
            ("Categoría", "category"),
            ("Estado", "estado"),
            ("Cable Corriente", "cable_corriente"),
            ("HDMI", "hdmi"),
            ("VGA", "vga"),
            ("Extensión", "extension"),
            ("Observaciones", "observaciones"),
        ],
        "monitor": [
            ("ID", "asset_id"),
            ("Modelo", "modelo"),
            ("Serie", "serie"),
            ("Pulgadas", "pulgadas"),
            ("Asignado a", "asignado_a"),
            ("Área", "area"),
            ("Grado", "grado"),
            ("Categoría", "category"),
            ("Observaciones", "observaciones"),
        ],
    }

    tipo = tipo.lower()

    if tipo not in model_map:
        return HttpResponse("Modelo inválido", status=404)

    Model = model_map[tipo]
    campos = fields_map[tipo]

    obj = get_object_or_404(Model, pk=pk)

    buffer = io.BytesIO()
    width, height = landscape(letter)
    pdf = canvas.Canvas(buffer, pagesize=(width, height))

    pdf.setFont("Helvetica-Bold", 24)
    pdf.setFillColor(colors.HexColor("#0056b3"))
    pdf.drawCentredString(width / 2, height - 50, f"Ficha de {tipo.capitalize()}")

    data = [["Campo", "Valor"]]
    for label, attr in campos:
        val = getattr(obj, attr)
        if isinstance(val, bool):
            val = "Sí" if val else "No"
        data.append([label, str(val)])

    table = Table(data, colWidths=[width * 0.3, width * 0.6])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0056b3")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
    ]))

    tw, th = table.wrap(0, 0)
    x = (width - tw) / 2
    y = height - 100 - th
    table.drawOn(pdf, x, y)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return HttpResponse(buffer.read(), content_type="application/pdf")
