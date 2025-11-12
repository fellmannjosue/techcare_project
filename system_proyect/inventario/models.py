# inventario/models.py

from django.db import models

class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('Equipo Informatico', 'Equipo Informatico'),
        ('Equipo de poyecion',   'Equipo de poyecion'),
        ('Equipo de red',         'Equipo de red'),
        ('Equipo digital',        'Equipo digital'),
        ('Equipo de impresion',   'Equipo de impresion'),
    ]

    category = models.CharField('Categoría',
        max_length=100,
        choices=CATEGORY_CHOICES
    )
    details  = models.CharField('Detalles', max_length=255)
    # creado_at removido

    def __str__(self):
        return f"{self.category} - {self.details}"


class Computadora(models.Model):
    asset_id        = models.CharField("ID Computadora", max_length=50, unique=True)
    modelo          = models.CharField("Modelo", max_length=100)
    serie           = models.CharField("Serie", max_length=100)
    ip              = models.GenericIPAddressField("IP", protocol='both', unpack_ipv4=True)
    asignado_a      = models.CharField("Asignado a", max_length=100)
    area            = models.CharField("Área", max_length=100)
    grado           = models.CharField("Grado", max_length=50)
    fecha_instalado = models.DateField("Fecha de Instalación")
    observaciones   = models.TextField("Observaciones", blank=True, null=True)

    category = models.CharField(
        'Categoría',
        max_length=100,
        choices=InventoryItem.CATEGORY_CHOICES,
        blank=True,
        null=True
    )

    # NUEVO CAMPO PARA AGRUPAR
    grupo = models.PositiveIntegerField(
        "Grupo",
        blank=True,
        null=True,
        help_text="Número de grupo para clasificar computadoras"
    )

    def __str__(self):
        return f"{self.asset_id} – {self.modelo}"



class Televisor(models.Model):
    asset_id      = models.CharField("ID Televisor", max_length=50, unique=True)
    modelo        = models.CharField("Modelo", max_length=100)
    serie         = models.CharField("Serie", max_length=100)
    ip            = models.GenericIPAddressField("IP", protocol='both', unpack_ipv4=True)
    grado         = models.CharField("Grado", max_length=50)
    area          = models.CharField("Área", max_length=100)
    observaciones = models.TextField("Observaciones", blank=True, null=True)

    category = models.CharField(max_length=100,
        choices=InventoryItem.CATEGORY_CHOICES,
        blank=True, null=True
    )


class Impresora(models.Model):
    asset_id            = models.CharField("ID Impresora", max_length=50, unique=True)
    nombre              = models.CharField("Nombre", max_length=100)
    modelo              = models.CharField("Modelo", max_length=100)
    serie               = models.CharField("Serie", max_length=100)
    asignado_a          = models.CharField("Asignado a", max_length=100)
    nivel_tinta         = models.CharField("Nivel de Tinta", max_length=50)
    ultima_vez_llenado  = models.DateField("Última vez de llenado")
    cantidad_impresiones = models.PositiveIntegerField("Cantidad de impresiones")
    a_color             = models.BooleanField("A color", default=False)
    observaciones       = models.TextField("Observaciones", blank=True, null=True)

    category = models.CharField(max_length=100,
        choices=InventoryItem.CATEGORY_CHOICES,
        blank=True, null=True
    )


class Router(models.Model):
    asset_id      = models.CharField("ID Router", max_length=50, unique=True)
    modelo        = models.CharField("Modelo", max_length=100)
    serie         = models.CharField("Serie", max_length=100)
    nombre_router = models.CharField("Nombre del Router", max_length=100)
    clave_router  = models.CharField("Clave del Router", max_length=100)
    ip_asignada   = models.GenericIPAddressField("IP Asignada", protocol='both', unpack_ipv4=True)
    ip_uso        = models.GenericIPAddressField("IP de Uso", protocol='both', unpack_ipv4=True)
    ubicado       = models.CharField("Ubicado", max_length=100)
    observaciones = models.TextField("Observaciones", blank=True, null=True)

    category = models.CharField(max_length=100,
        choices=InventoryItem.CATEGORY_CHOICES,
        blank=True, null=True
    )


class DataShow(models.Model):
    asset_id        = models.CharField("ID DataShow", max_length=50, unique=True)
    nombre          = models.CharField("Nombre", max_length=100)
    modelo          = models.CharField("Modelo", max_length=100)
    serie           = models.CharField("Serie", max_length=100)
    estado          = models.CharField("Estado", max_length=50)
    cable_corriente = models.BooleanField("Cable Corriente", default=False)
    hdmi            = models.BooleanField("HDMI", default=False)
    vga             = models.BooleanField("VGA", default=False)
    extension       = models.BooleanField("Extensión", default=False)
    observaciones   = models.TextField("Observaciones", blank=True, null=True)

    category = models.CharField(max_length=100,
        choices=InventoryItem.CATEGORY_CHOICES,
        blank=True, null=True
    )
