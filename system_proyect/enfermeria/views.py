# views.py

import datetime
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

from .models import (
    AtencionMedica,
    InventarioMedicamento,
    UsoMedicamento,
)
from .forms import (
    AtencionMedicaForm,
    InventarioMedicamentoForm,
    UsoMedicamentoForm,
)


@login_required
def enfermeria_dashboard(request):
    return render(request, 'enfermeria/dashboard.html')


# ================= ATENCIÓN MÉDICA =================

@login_required
def atencion_form(request):
    delete_id = request.GET.get('delete')
    edit_id   = request.GET.get('edit')

    if delete_id:
        get_object_or_404(AtencionMedica, pk=delete_id).delete()
        return redirect('enfermeria:atencion_form')

    if request.method == 'POST':
        pk = request.POST.get('pk')
        if pk:
            instancia = get_object_or_404(AtencionMedica, pk=pk)
            form = AtencionMedicaForm(request.POST, instance=instancia)
        else:
            form = AtencionMedicaForm(request.POST)
        if form.is_valid():
            form.save()
            request.session['mensaje_exito'] = 'Ficha guardada correctamente'
            return redirect('enfermeria:atencion_form')
    else:
        instancia = get_object_or_404(AtencionMedica, pk=edit_id) if edit_id else None
        form = AtencionMedicaForm(instance=instancia)

    registros = AtencionMedica.objects.order_by('-fecha_hora')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/atencion_form.html', {
        'form': form,
        'records': registros,
        'edit_id': edit_id or '',
        'year': year,
    })


@login_required
def atencion_download_pdf(request, pk):
    # 1) Recuperar el registro de Atención Médica y preparar el buffer para el PDF
    rec = get_object_or_404(AtencionMedica, pk=pk)
    buf = io.BytesIO()
    w, h = 210 * mm, 297 * mm                    # dimenciones A4 en milímetros
    pdf = canvas.Canvas(buf, pagesize=(w, h))
    pdf.setTitle(f"ficha_de_atencion_medica_{rec.pk}")
    
    # ———————————————————————————————————————————————
    # 2) Fondo claro de toda la página
    # Pintamos un rectángulo que cubre todo el PDF con color #f8f9fa
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, w, h, fill=1, stroke=0)
    
    # ———————————————————————————————————————————————
    # 3) Encabezado superior (mensaje informativo en gris)
    # Usamos Helvetica-Oblique, tamaño 12, color gris oscuro.
    pdf.setFont("Helvetica-Oblique", 12)
    pdf.setFillColor(colors.darkgray)
    pdf.drawCentredString(
        w / 2,
        h - 10 * mm,  # 10 mm por debajo del borde superior
        "Este es un mensaje de nuestro departamento de enfermería"
    )
    
    # ———————————————————————————————————————————————
    # 4) Título principal (centrado justo debajo del encabezado)
    # Usamos Helvetica-Bold, tamaño 20, color negro.
    pdf.setFont("Helvetica-Bold", 20)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(
        w / 2,
        h - 20 * mm,  # 20 mm por debajo del borde superior (10 mm para el encabezado + 10 mm extra)
        "Ficha de Atención Médica"
    )
    
    # ———————————————————————————————————————————————
    # 5) TEXTO PRINCIPAL (párrafo informativo)
    # Se define el contenido en HTML básico (<br/> para saltos de línea, <b> para negrita).
    texto = (
        "Estimado padre / madre de familia:<br/>"
        "El motivo de la ficha es para notificarle que su hij@ fue atendido en el departamento de enfermería.<br/><br/>"
        f"Se le brindó a su hijo(a) <b>{rec.estudiante}</b> del grado <b>{rec.grado.nombre}</b> "
        f"quien fue atendido el día <b>{rec.fecha_hora.strftime('%d/%m/%Y')}</b> "
        f"a las <b>{rec.fecha_hora.strftime('%H:%M')}</b> por el coordinador "
        f"<b>{rec.atendido_por.nombre}</b>, ya que no se sentía bien y presentaba: "
        f"<b>{rec.motivo}</b>. Se le trató con: <b>{rec.tratamiento}</b>."
    )
    
    # Definimos un estilo para el párrafo (fuente, tamaño, interlineado, color)
    style = ParagraphStyle(
        'texto_principal',
        fontName='Helvetica',
        fontSize=14,
        leading=18,             # espacio entre líneas
        textColor=colors.black
    )
    
    # Calcular la coordenada “y” para que el texto quede a 50 mm bajo el título
    #   • El título está en y = h - 20 mm
    #   • Queremos 50 mm de espacio libre justo debajo del título
    #   • El propio párrafo ocupa 50 mm de alto
    #   → Entonces: y_frame = h - 20 mm - 50 mm - 50 mm = h - 120 mm
    y_frame = h - (20 * mm) - (50 * mm) - (50 * mm)
    
    # Creamos un Frame que contendrá el párrafo. 
    frame_texto = Frame(
        20 * mm,      # x = 20 mm desde borde izquierdo
        y_frame,      # y = calculado arriba (h - 120 mm)
        w - 40 * mm,  # ancho total menos márgenes (20 mm a cada lado)
        50 * mm,      # alto = 50 mm (espacio dedicado al párrafo)
        showBoundary=0
    )
    
    paragraph = Paragraph(texto, style)
    # Insertamos el párrafo dentro del Frame
    frame_texto.addFromList([paragraph], pdf)
    
    # ———————————————————————————————————————————————
    # 6) Subtítulo (detalle de la tabla)
    # Lo ubicamos 10 mm por debajo del párrafo. 
    #   • El párrafo ocupa 50 mm de alto y arrancó en y_frame
    #   → Línea base del párrafo está en y_frame
    #   → Subtítulo en y_subtitulo = y_frame - 10 mm
    y_subtitulo = y_frame - (10 * mm)
    
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(
        w / 2,
        y_subtitulo,
        "Detalle de la atención que se brindó en el departamento de enfermería"
    )
    
    # ———————————————————————————————————————————————
    # 7) Tabla con datos de la atención
    tabla_data = [
        ["Estudiante:",    rec.estudiante],
        ["Grado:",         rec.grado.nombre],
        ["Fecha y Hora:",  rec.fecha_hora.strftime("%d-%m-%Y %H:%M")],
        ["Atendido por:",  rec.atendido_por.nombre],
        ["Motivo:",        rec.motivo],
        ["Tratamiento:",   rec.tratamiento],
    ]
    tabla = Table(tabla_data, colWidths=[50 * mm, 120 * mm])
    tabla.setStyle(TableStyle([
        ('GRID',          (0, 0), (-1, -1), 0.25, colors.grey),
        ('FONTSIZE',      (0, 0), (-1, -1), 14),
        ('FONTNAME',      (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    # Calculamos la altura aproximada de la tabla:
    #   • 6 filas × ~8 mm por fila = ~48 mm
    altura_tabla_aprox = len(tabla_data) * 8 * mm
    
    # Ubicamos la tabla 10 mm por debajo del subtítulo:
    #   • subtítulo está en y_subtitulo
    #   → tope de la tabla (arriba) = y_subtitulo - 10 mm
    y_arriba_tabla = y_subtitulo - (10 * mm)
    
    # Dibujamos la tabla de modo que su base quede en (y_arriba_tabla - altura_tabla_aprox)
    tabla.wrapOn(pdf, w, h)
    tabla.drawOn(pdf, 20 * mm, y_arriba_tabla - altura_tabla_aprox)
    
    # ———————————————————————————————————————————————
    # 8) Línea de firma (80 mm por debajo del final de la tabla)
    #   • Base de la tabla está en y_base_tabla = y_arriba_tabla - altura_tabla_aprox
    #   → Queremos 80 mm por debajo de esa base para la línea
    y_base_tabla = y_arriba_tabla - altura_tabla_aprox
    y_firma = y_base_tabla - (80 * mm)
    
    # Dibujar la palabra “Firma:” 2 mm por encima de la línea, al inicio de la misma
    x_inicio = (w / 2) - (50 * mm)  # coordenada X inicial: 50 mm a izquierda del centro
    pdf.setFont("Helvetica", 12)
    pdf.setFillColor(colors.black)
    pdf.drawString(x_inicio, y_firma + (2 * mm), "Firma:")
    
    # Dibujar la línea de 100 mm de largo, centrada horizontalmente
    x_fin = (w / 2) + (50 * mm)     # 50 mm a derecha del centro
    pdf.setStrokeColor(colors.black)
    pdf.setLineWidth(0.5)
    pdf.line(x_inicio, y_firma, x_fin, y_firma)
    
    # ———————————————————————————————————————————————
    # 9) Finalizamos el PDF y regresamos la respuesta HTTP
    pdf.showPage()
    pdf.save()
    buf.seek(0)
    return HttpResponse(buf, content_type='application/pdf')


# ================= INVENTARIO MEDICAMENTOS =================

@login_required
def inventario_list(request):
    items = InventarioMedicamento.objects.order_by('-fecha_ingreso')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/inventario_list.html', {
        'items': items,
        'year': year,
    })


@login_required
def inventario_create(request):
    form = InventarioMedicamentoForm(request.POST or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.modificado_por = request.user
        item.save()
        request.session['mensaje_exito'] = 'Medicamento agregado correctamente'
        return redirect('enfermeria:inventario_list')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/inventario_form.html', {
        'form': form,
        'title': 'Agregar Medicamento',
        'year': year,
    })


@login_required
def inventario_edit_cantidad(request, pk):
    item = get_object_or_404(InventarioMedicamento, pk=pk)
    form = InventarioMedicamentoForm(request.POST or None, instance=item)
    if form.is_valid():
        item = form.save(commit=False)
        item.modificado_por = request.user
        item.save()
        request.session['mensaje_exito'] = 'Cantidad actualizada correctamente'
        return redirect('enfermeria:inventario_list')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/inventario_form.html', {
        'form': form,
        'title': f'Editar Medicamento – {item.nombre}',
        'year': year,
    })


@login_required
def uso_create(request):
    form = UsoMedicamentoForm(request.POST or None)
    if form.is_valid():
        uso = form.save(commit=False)
        med = uso.medicamento
        if uso.cantidad_usada <= med.cantidad_existente:
            med.cantidad_existente -= uso.cantidad_usada
            med.save()
            uso.save()
            request.session['mensaje_exito'] = 'Uso registrado correctamente'
            # Regresamos a la pantalla de atención:
            return redirect('enfermeria:atencion_form')
        form.add_error('cantidad_usada', 'Cantidad excede lo disponible.')
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/uso_form.html', {
        'form': form,
        'title': 'Registrar Uso de Medicamento',
        'year': year,
    })


@login_required
def inventario_pdf(request, pk):
    med = get_object_or_404(InventarioMedicamento, pk=pk)
    usos = med.usos.order_by('-fecha_uso')
    total_usado = usos.aggregate(total=Sum('cantidad_usada'))['total'] or 0

    buf = io.BytesIO()
    w, h = 210 * mm, 297 * mm
    pdf = canvas.Canvas(buf, pagesize=(w, h))
    pdf.setTitle(f"Medicamento_{med.pk}")
    pdf.setFillColor(colors.HexColor("#f8f9fa"))
    pdf.rect(0, 0, w, h, fill=1, stroke=0)

    logo = finders.find('accounts/img/ana-transformed.png')
    if logo:
        pdf.drawImage(logo, 15 * mm, h - 45 * mm, width=30 * mm, height=30 * mm)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.setFillColor(colors.HexColor("#007bff"))
    pdf.drawCentredString(w / 2, h - 25 * mm, "Reporte de Medicamento")

    y = h - 60 * mm
    for label, val in [
        ("Nombre:",           med.nombre),
        ("Proveedor:",        med.proveedor.nombre),
        ("Presentación:",     med.presentacion.nombre),
        ("Fecha de Ingreso:", med.fecha_ingreso.strftime("%d-%m-%Y")),
        ("Disponible:",       med.cantidad_existente),
        ("Total Usado:",      total_usado),
        ("Modificado por:",   med.modificado_por.username if med.modificado_por else "—"),
    ]:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(20 * mm, y, label)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(65 * mm, y, str(val))
        y -= 10 * mm

    pdf.showPage()
    pdf.save()
    buf.seek(0)
    return HttpResponse(buf, content_type='application/pdf')


@login_required
def historial_uso(request, pk):
    med = get_object_or_404(InventarioMedicamento, pk=pk)
    usos = med.usos.order_by('-fecha_uso')
    return render(request, 'enfermeria/historial_uso.html', {
        'medicamento': med,
        'usos': usos
    })


# ================= HISTORIAL MÉDICO =================

@login_required
def medical_history(request):
    # Lista de nombres únicos de estudiante
    students = (
        AtencionMedica.objects
        .values_list('estudiante', flat=True)
        .distinct()
        .order_by('estudiante')
    )
    year = datetime.datetime.now().year
    return render(request, 'enfermeria/medical_history.html', {
        'students': students,
        'year': year,
    })


@login_required
def get_medical_history_data(request):
    student_name = request.GET.get('student')
    if not student_name:
        return JsonResponse({'error': 'Falta el parámetro "student"'}, status=400)

    registros = (
        AtencionMedica.objects
        .filter(estudiante=student_name)
        .order_by('-fecha_hora')
    )

    if not registros.exists():
        return JsonResponse({}, status=204)

    lista = []
    for rec in registros:
        lista.append({
            'grade':     rec.grado.nombre,
            'date_time': rec.fecha_hora.strftime('%Y-%m-%d %H:%M'),
            'reason':    rec.motivo,
            'treatment': rec.tratamiento,
            'attendant': rec.atendido_por.nombre,
        })

    return JsonResponse({'history': lista})
