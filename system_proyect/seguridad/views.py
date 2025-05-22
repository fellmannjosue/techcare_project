# seguridad/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import (
    InventarioCamara,
    ContableCamara,
    IdentificacionCamaraGabinete,
)
from .forms import (
    InventarioCamaraForm,
    ContableCamaraForm,
    IdentificacionCamaraGabineteForm,
)

# ────────────────────────────────────────────────────────────
# Dashboard principal del módulo Seguridad
# ────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    return render(request, 'seguridad/dashboard.html', {
        'year': timezone.now().year
    })


# ────────────────────────────────────────────────────────────
# Inventario de Cámaras
# ────────────────────────────────────────────────────────────
@login_required
def inventario_list(request):
    """
    Muestra el formulario y la tabla de InventarioCamara.
    Procesa POST para crear un nuevo registro.
    """
    form = InventarioCamaraForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('seguridad:inventario_list')

    items = InventarioCamara.objects.all().order_by('nombre')
    return render(request, 'seguridad/inventory_form.html', {
        'form':  form,
        'items': items,
    })


@login_required
def inventario_update(request, pk):
    """
    Carga el formulario para editar InventarioCamara(pk=pk).
    """
    instance = get_object_or_404(InventarioCamara, pk=pk)
    form = InventarioCamaraForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('seguridad:inventario_list')

    items = InventarioCamara.objects.all().order_by('nombre')
    return render(request, 'seguridad/inventory_form.html', {
        'form':  form,
        'items': items,
    })


@login_required
def inventario_delete(request, pk):
    """
    Elimina el registro de InventarioCamara(pk=pk) y redirige al listado.
    """
    instance = get_object_or_404(InventarioCamara, pk=pk)
    instance.delete()
    return redirect('seguridad:inventario_list')


# ────────────────────────────────────────────────────────────
# Sistema Contable de Cámaras
# ────────────────────────────────────────────────────────────
@login_required
def contable_list(request):
    """
    Muestra el formulario y la tabla de ContableCamara.
    Procesa POST para crear un nuevo registro.
    """
    form = ContableCamaraForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('seguridad:contable_list')

    items = ContableCamara.objects.all().order_by('modelo')
    return render(request, 'seguridad/accounting_form.html', {
        'form':  form,
        'items': items,
    })


@login_required
def contable_update(request, pk):
    """
    Carga el formulario para editar ContableCamara(pk=pk).
    """
    instance = get_object_or_404(ContableCamara, pk=pk)
    form = ContableCamaraForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('seguridad:contable_list')

    items = ContableCamara.objects.all().order_by('modelo')
    return render(request, 'seguridad/accounting_form.html', {
        'form':  form,
        'items': items,
    })


@login_required
def contable_delete(request, pk):
    """
    Elimina el registro de ContableCamara(pk=pk) y redirige al listado.
    """
    instance = get_object_or_404(ContableCamara, pk=pk)
    instance.delete()
    return redirect('seguridad:contable_list')


# ────────────────────────────────────────────────────────────
# Identificación de Cámaras y Gabinetes
# ────────────────────────────────────────────────────────────
@login_required
def identificacion_list(request):
    """
    Muestra el formulario y la tabla de IdentificacionCamaraGabinete.
    Procesa POST para crear un nuevo registro.
    """
    form = IdentificacionCamaraGabineteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('seguridad:identificacion_list')

    items = IdentificacionCamaraGabinete.objects.all().order_by('numero_gabinete')
    return render(request, 'seguridad/identification_form.html', {
        'form':  form,
        'items': items,
    })


@login_required
def identificacion_update(request, pk):
    """
    Carga el formulario para editar IdentificacionCamaraGabinete(pk=pk).
    """
    instance = get_object_or_404(IdentificacionCamaraGabinete, pk=pk)
    form = IdentificacionCamaraGabineteForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('seguridad:identificacion_list')

    items = IdentificacionCamaraGabinete.objects.all().order_by('numero_gabinete')
    return render(request, 'seguridad/identification_form.html', {
        'form':  form,
        'items': items,
    })


@login_required
def identificacion_delete(request, pk):
    """
    Elimina el registro de IdentificacionCamaraGabinete(pk=pk) y redirige al listado.
    """
    instance = get_object_or_404(IdentificacionCamaraGabinete, pk=pk)
    instance.delete()
    return redirect('seguridad:identificacion_list')
