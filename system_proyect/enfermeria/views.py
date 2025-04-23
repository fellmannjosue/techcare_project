# enfermeria/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import AtencionMedica, InventarioMedicamento
from .forms import AtencionMedicaForm, InventarioMedicamentoForm

@login_required
def enfermeria_dashboard(request):
    """
    Dashboard principal de Enfermería con dos opciones:
    - Atención Médica
    - Inventario de Medicamentos
    """
    return render(request, 'enfermeria/dashboard.html')

@login_required
def atencion_list(request):
    records = AtencionMedica.objects.order_by('-fecha_hora')
    return render(request, 'enfermeria/atencion_list.html', {'records': records})

@login_required
def atencion_create(request):
    form = AtencionMedicaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('enfermeria:atencion_list')
    return render(request, 'enfermeria/atencion_form.html', {
        'form': form,
        'title': 'Nueva Atención Médica'
    })

@login_required
def atencion_edit(request, pk):
    rec = get_object_or_404(AtencionMedica, pk=pk)
    form = AtencionMedicaForm(request.POST or None, instance=rec)
    if form.is_valid():
        form.save()
        return redirect('enfermeria:atencion_list')
    return render(request, 'enfermeria/atencion_form.html', {
        'form': form,
        'title': f'Editar Atención #{pk}'
    })

@login_required
def atencion_delete(request, pk):
    rec = get_object_or_404(AtencionMedica, pk=pk)
    if request.method == 'POST':
        rec.delete()
        return redirect('enfermeria:atencion_list')
    return render(request, 'enfermeria/atencion_confirm_delete.html', {'object': rec})

@login_required
def atencion_download_pdf(request, pk):
    # Aquí iría la lógica ReportLab para generar el PDF de AtencionMedica
    ...

@login_required
def inventario_list(request):
    items = InventarioMedicamento.objects.order_by('-fecha_ingreso')
    return render(request, 'enfermeria/inventario_list.html', {'items': items})

@login_required
def inventario_create(request):
    form = InventarioMedicamentoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('enfermeria:inventario_list')
    return render(request, 'enfermeria/inventario_form.html', {
        'form': form,
        'title': 'Nuevo Ítem de Inventario'
    })
