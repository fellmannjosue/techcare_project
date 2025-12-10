from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = "inventario"

urlpatterns = [

    # ---------------------------------------------------------
    # DASHBOARD Y LISTADOS
    # ---------------------------------------------------------
    path("", views.dashboard, name="dashboard"),
    path("por_categoria/", views.inventario_por_categoria, name="inventario_por_categoria"),

    path("computadoras/", views.inventario_computadoras, name="inventario_computadoras"),
    path("computadoras/filtro/", views.computadoras_list, name="filtro_computadoras"),

    path("televisores/", views.inventario_televisores, name="inventario_televisores"),
    path("impresoras/", views.inventario_impresoras, name="inventario_impresoras"),
    path("routers/", views.inventario_routers, name="inventario_routers"),
    path("datashows/", views.inventario_datashows, name="inventario_datashows"),
    path("monitores/", views.inventario_monitores, name="inventario_monitores"),

    path("registros/", views.inventario_registros, name="inventario_registros"),

    # ---------------------------------------------------------
    # PDF + QR
    # ---------------------------------------------------------
    path("download/<str:tipo>/<int:pk>/", views.download_model_pdf, name="download_model_pdf"),
    path("registros/qr/<str:tipo>/<int:pk>/", views.descargar_qr, name="descargar_qr"),

    # Atajo al menú principal
    path("menu/", lambda req: redirect("accounts:menu"), name="menu"),

    # ---------------------------------------------------------
    # GET - Cargar formulario en MODAL (AJAX)
    # ---------------------------------------------------------
    path("computadora/get/<int:pk>/", views.get_computadora, name="get_computadora"),
    path("televisor/get/<int:pk>/", views.get_televisor, name="get_televisor"),
    path("impresora/get/<int:pk>/", views.get_impresora, name="get_impresora"),
    path("router/get/<int:pk>/", views.get_router, name="get_router"),
    path("datashow/get/<int:pk>/", views.get_datashow, name="get_datashow"),
    path("monitor/get/<int:pk>/", views.get_monitor, name="get_monitor"),

    # ---------------------------------------------------------
    # UPDATE - Guardar cambios vía AJAX (POST)
    # ---------------------------------------------------------
    path("computadora/update/<int:pk>/", views.update_computadora, name="update_computadora"),
    path("televisor/update/<int:pk>/", views.update_televisor, name="update_televisor"),
    path("impresora/update/<int:pk>/", views.update_impresora, name="update_impresora"),
    path("router/update/<int:pk>/", views.update_router, name="update_router"),
    path("datashow/update/<int:pk>/", views.update_datashow, name="update_datashow"),
    path("monitor/update/<int:pk>/", views.update_monitor, name="update_monitor"),

    # ---------------------------------------------------------
    # DELETE - Eliminar vía AJAX
    # ---------------------------------------------------------
    path("computadora/delete/<int:pk>/", views.eliminar_computadora, name="delete_computadora"),
    path("televisor/delete/<int:pk>/", views.eliminar_televisor, name="delete_televisor"),
    path("impresora/delete/<int:pk>/", views.eliminar_impresora, name="delete_impresora"),
    path("router/delete/<int:pk>/", views.eliminar_router, name="delete_router"),
    path("datashow/delete/<int:pk>/", views.eliminar_datashow, name="delete_datashow"),
    path("monitor/delete/<int:pk>/", views.eliminar_monitor, name="delete_monitor"),
]
