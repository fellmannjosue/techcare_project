from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Dashboards
@login_required
def dashboard_coordinador_bilingue(request):
    return render(request, 'conducta/dashboard_coordinador_bilingue.html')

@login_required
def dashboard_coordinador_colegio(request):
    return render(request, 'conducta/dashboard_coordinador_colegio.html')

@login_required
def dashboard_maestro(request):
    user = request.user
    if user.groups.filter(name='maestros_bilingue').exists():
        area = 'bilingue'
    elif user.groups.filter(name='maestros_colegio').exists():
        area = 'colegio'
    else:
        area = None
    return render(request, 'conducta/dashboard_maestros.html', {'area': area})


# Formularios de reportes
@login_required
def reporte_conductual_bilingue(request):
    return render(request, 'conducta/form_conductual.html')

@login_required
def reporte_conductual_colegio(request):
    return render(request, 'conducta/form_conductual.html')

@login_required
def reporte_informativo_bilingue(request):
    return render(request, 'conducta/form_informativo.html')

@login_required
def reporte_informativo_colegio(request):
    return render(request, 'conducta/form_informativo.html')

@login_required
def progress_report_bilingue(request):
    return render(request, 'conducta/form_progress.html')

# Historiales maestro
@login_required
def historial_maestro_bilingue(request):
    return render(request, 'conducta/historial_maestro.html')

@login_required
def historial_maestro_colegio(request):
    return render(request, 'conducta/historial_maestro.html')

# Historiales coordinador y reportes generales
@login_required
def historial_conductual_coordinador_bilingue(request):
    return render(request, 'conducta/lista_reportes.html')

@login_required
def historial_conductual_coordinador_colegio(request):
    return render(request, 'conducta/lista_reportes.html')

@login_required
def historial_informativo_coordinador_bilingue(request):
    return render(request, 'conducta/lista_reportes.html')

@login_required
def historial_informativo_coordinador_colegio(request):
    return render(request, 'conducta/lista_reportes.html')

@login_required
def historial_progress_coordinador_bilingue(request):
    return render(request, 'conducta/lista_reportes.html')

@login_required
def reporte_general_tres_faltas_bilingue(request):
    return render(request, 'conducta/reporte_general.html')

@login_required
def reporte_general_tres_faltas_colegio(request):
    return render(request, 'conducta/reporte_general.html')

# Detalle, editar y PDF
@login_required
def detalle_reporte(request, pk):
    return render(request, 'conducta/detalle_reporte.html')

@login_required
def editar_reporte(request, pk):
    return render(request, 'conducta/editar_reporte.html')

@login_required
def descargar_pdf_reporte(request, pk):
    return render(request, 'conducta/descargar_pdf.html')

# Puedes agregar aquí vistas extra para AJAX, etc, más adelante
