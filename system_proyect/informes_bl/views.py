# informes_bl/views.py

import os
import io

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

from .models import ProgressReport, ReportEntry
from .forms import ProgressReportForm, ReportEntryFormSet

@login_required
def notas_dashboard(request):
    """
    Sub‐dashboard “Notas y Informes” con los 6 botones.
    """
    return render(request, 'informes_bl/notas_dashboard.html')


@login_required
def progress_list(request):
    """
    Lista todos los ProgressReport con botones Crear, Editar, Imprimir y Borrar.
    """
    reports = ProgressReport.objects.order_by('-semana_inicio')
    return render(request, 'informes_bl/progress_list.html', {
        'reports': reports
    })


@login_required
def progress_edit(request, pk=None):
    """
    Crear (pk=None) o editar (pk dado) un ProgressReport y sus entradas.
    """
    if pk:
        report = get_object_or_404(ProgressReport, pk=pk)
        editing = True
    else:
        report = ProgressReport()
        editing = False

    if request.method == 'POST':
        form    = ProgressReportForm(request.POST, instance=report)
        formset = ReportEntryFormSet(request.POST, instance=report)
        if form.is_valid() and formset.is_valid():
            report = form.save()
            formset.save()
            messages.success(request, "Reporte guardado correctamente.")
            return redirect('informes_bl:progress_list')
    else:
        form    = ProgressReportForm(instance=report)
        formset = ReportEntryFormSet(instance=report)

    return render(request, 'informes_bl/progress_form.html', {
        'form': form,
        'formset': formset,
        'editing': editing,
    })


@login_required
def progress_delete(request, pk):
    """
    Elimina un ProgressReport y redirige a la lista.
    """
    report = get_object_or_404(ProgressReport, pk=pk)
    report.delete()
    messages.success(request, "Reporte eliminado.")
    return redirect('informes_bl:progress_list')


@login_required
def progress_print(request, pk):
    """
    Genera el PDF de un ProgressReport usando tu plantilla de fondo.
    """
    report = get_object_or_404(ProgressReport, pk=pk)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Ruta al fondo (asegúrate de que STATICFILES_DIRS incluye 'static/')
    template_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'progress_template.jpg')
    p.drawImage(template_path, 0, 0, width=21*cm, height=27.9*cm)

    # Encabezado
    p.setFont("Helvetica-Bold", 18)
    p.drawString(3*cm, 25*cm, "Progress Report")
    p.setFont("Helvetica", 12)
    p.drawString(3*cm, 24*cm, f"Name: {report.alumno_nombre}")
    p.drawString(3*cm, 23*cm, f"Weeks: {report.semana_inicio} – {report.semana_fin}")

    # Construir tabla de materias
    data = [["Materia", "Asignación", "Comentario/Observación"]]
    for entry in report.entries.all():
        data.append([
            entry.materia.nombre,
            entry.asignacion,
            entry.observacion
        ])

    table = Table(data, colWidths=[5*cm, 6*cm, 8*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    table.wrapOn(p, 0, 0)
    table.drawOn(p, 3*cm, 15*cm)

    p.showPage()
    p.save()
    buffer.seek(0)

    return HttpResponse(
        buffer,
        content_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="progress_{pk}.pdf"'}
    )
