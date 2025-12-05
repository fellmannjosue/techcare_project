# ============================================================
# 🔎 RESÚMENES GLOBALES PARA DASHBOARDS TECHCARE
# ------------------------------------------------------------
# Este archivo NO crea notificaciones y NO usa la tabla
# Notificacion. Su único propósito es devolver datos rápidos
# para actualizar tarjetas del panel (tickets, citas, reloj,
# reportes, etc.)
# ============================================================

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

# Importación de modelos desde cada módulo
from tickets.models import Ticket
from citas_billingue.models import Appointment_bl
from citas_colegio.models import Appointment_col
from conducta.models import ReporteInformativo, ReporteConductual, ProgressReport
from reloj.models import TiempoCompensatorio, PermisoEmpleado


# ============================================================
# 🧩 UTILIDAD — Formateo de fechas para JSON
# ============================================================
def fmt(dt):
    return dt.strftime("%d/%m/%Y %H:%M")


# ============================================================
# 📌 RESUMEN DE TICKETS — Para técnicos y administración
# ============================================================
@require_GET
@login_required
def summary_tickets(request):
    pendientes = Ticket.objects.filter(status="pendiente").order_by("-id")

    return JsonResponse({
        "total": pendientes.count(),
        "items": [
            {
                "id": t.id,
                "ticket_id": t.ticket_id,
                "titulo": f"Ticket #{t.ticket_id}",
                "descripcion": f"{t.name}: {t.description[:60]}...",
                "fecha": fmt(t.fecha_creacion),
            }
            for t in pendientes[:5]
        ]
    })


# ============================================================
# 📌 RESUMEN CITAS BL — Para administración y coordinación BL
# ============================================================
@require_GET
@login_required
def summary_citas_bl(request):
    citas = Appointment_bl.objects.filter(status="pendiente").order_by("-id")

    return JsonResponse({
        "total": citas.count(),
        "items": [
            {
                "id": c.id,
                "titulo": f"Cita BL — {c.padre}",
                "descripcion": f"Maestro: {c.maestro}",
                "fecha": fmt(c.fecha),
            }
            for c in citas[:5]
        ]
    })


# ============================================================
# 📌 RESUMEN CITAS COLEGIO/VOC — Para coordinación y admin
# ============================================================
@require_GET
@login_required
def summary_citas_col(request):
    citas = Appointment_col.objects.filter(status="pendiente").order_by("-id")

    return JsonResponse({
        "total": citas.count(),
        "items": [
            {
                "id": c.id,
                "titulo": f"Cita Colegio/Voc — {c.padre}",
                "descripcion": f"Maestro: {c.maestro}",
                "fecha": fmt(c.fecha),
            }
            for c in citas[:5]
        ]
    })


# ============================================================
# 📌 RESUMEN REPORTES — Coordinación Bilingüe
# ============================================================
@require_GET
@login_required
def summary_coordinacion_bl(request):
    info = ReporteInformativo.objects.filter(area="bilingue").order_by("-id")[:3]
    conducta = ReporteConductual.objects.filter(area="bilingue").order_by("-id")[:3]
    progress = ProgressReport.objects.filter(area="bilingue").order_by("-id")[:3]

    recientes = list(info) + list(conducta) + list(progress)
    recientes.sort(key=lambda x: x.id, reverse=True)

    return JsonResponse({
        "total": len(recientes),
        "items": [
            {
                "id": r.id,
                "titulo": "Nuevo Reporte BL",
                "descripcion": str(r),
                "fecha": fmt(r.fecha),
            }
            for r in recientes[:5]
        ]
    })


# ============================================================
# 📌 RESUMEN REPORTES — Coordinación Colegio
# ============================================================
@require_GET
@login_required
def summary_coordinacion_col(request):
    info = ReporteInformativo.objects.filter(area="colegio").order_by("-id")[:3]
    conducta = ReporteConductual.objects.filter(area="colegio").order_by("-id")[:3]
    progress = ProgressReport.objects.filter(area="colegio").order_by("-id")[:3]

    recientes = list(info) + list(conducta) + list(progress)
    recientes.sort(key=lambda x: x.id, reverse=True)

    return JsonResponse({
        "total": len(recientes),
        "items": [
            {
                "id": r.id,
                "titulo": "Nuevo Reporte Colegio",
                "descripcion": str(r),
                "fecha": fmt(r.fecha),
            }
            for r in recientes[:5]
        ]
    })


# ============================================================
# 📌 RESUMEN RELOJ — Permisos y Compensatorios Pendientes
# ============================================================
@require_GET
@login_required
def summary_reloj(request):
    permisos = PermisoEmpleado.objects.filter(status="pendiente").order_by("-id")[:5]
    compensatorios = TiempoCompensatorio.objects.filter(status="pendiente").order_by("-id")[:5]

    recientes = list(permisos) + list(compensatorios)
    recientes.sort(key=lambda x: x.id, reverse=True)

    return JsonResponse({
        "total": len(recientes),
        "items": [
            {
                "id": r.id,
                "titulo": "Solicitud en Reloj",
                "descripcion": str(r),
                "fecha": fmt(r.fecha),
            }
            for r in recientes[:5]
        ]
    })
