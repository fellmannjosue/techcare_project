from django.db import models
from django.conf import settings  # Para AUTH_USER_MODEL y MEDIA settings
import os

# ——————————————————————————————————————————————
# Modelos existentes en MySQL (sponsors3)
# ——————————————————————————————————————————————

class Grado(models.Model):
    nombre = models.CharField("Grado", max_length=50)

    class Meta:
        verbose_name = "Grado"
        verbose_name_plural = "Grados"

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    nombre = models.CharField("Nombre del Profesional", max_length=100)

    class Meta:
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

    def __str__(self):
        return self.nombre


class AtencionMedica(models.Model):
    estudiante   = models.CharField("Nombre del Estudiante", max_length=100)
    grado        = models.ForeignKey(
        Grado,
        on_delete=models.PROTECT,
        verbose_name="Grado"
    )
    fecha_hora   = models.DateTimeField("Fecha y Hora")
    atendido_por = models.ForeignKey(
        Medico,
        on_delete=models.PROTECT,
        verbose_name="Atendido por"
    )
    motivo       = models.TextField("Motivo")
    tratamiento  = models.TextField("Tratamiento")
    creado       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Atención Médica"
        verbose_name_plural = "Atenciones Médicas"

    def __str__(self):
        return f"{self.estudiante} – {self.fecha_hora:%d-%m-%Y %H:%M}"

    # ——————————————————————————————————————————————
    # Métodos para manejar el PDF asociado a esta atención
    # ——————————————————————————————————————————————

    def get_pdf_path(self):
        """
        Devuelve la ruta absoluta en disco al archivo PDF.
        (Por ejemplo, MEDIA_ROOT/pdfs/atencion_<id>.pdf)
        """
        filename = f"pdfs/atencion_{self.id}.pdf"
        return os.path.join(settings.MEDIA_ROOT, filename)

    def get_pdf_url(self):
        """
        Devuelve la URL pública del PDF para incrustarlo en un <iframe>.
        (Por ejemplo, MEDIA_URL + 'pdfs/atencion_<id>.pdf')
        """
        filename = f"pdfs/atencion_{self.id}.pdf"
        return settings.MEDIA_URL + filename


class Proveedor(models.Model):
    nombre = models.CharField("Nombre del Proveedor", max_length=100)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.nombre


class Responsable(models.Model):
    nombre = models.CharField("Nombre del Responsable", max_length=100)

    class Meta:
        verbose_name = "Responsable"
        verbose_name_plural = "Responsables"

    def __str__(self):
        return self.nombre


class Presentacion(models.Model):
    """
    Cada instancia representa una forma/presentación farmacéutica:
    blíster, ml, crema, roll-on, etc.  
    Estas opciones se gestionan desde el admin.
    """
    nombre = models.CharField("Presentación", max_length=50, unique=True)

    class Meta:
        verbose_name = "Presentación"
        verbose_name_plural = "Presentaciones"

    def __str__(self):
        return self.nombre


class InventarioMedicamento(models.Model):
    nombre             = models.CharField("Medicamento", max_length=100)
    fecha_ingreso      = models.DateField("Fecha de Ingreso")
    proveedor          = models.ForeignKey(Proveedor, on_delete=models.PROTECT, verbose_name="Proveedor")
    cantidad_existente = models.PositiveIntegerField("Cantidad Existente")
    modificado_por     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Modificado por"
    )

    # ← Ahora permitimos null en existentes
    presentacion = models.ForeignKey(
        Presentacion,
        on_delete=models.PROTECT,
        verbose_name="Presentación",
        help_text="Selecciona blíster, ml, crema, roll-on, etc.",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"

    def __str__(self):
        return f"{self.nombre} ({self.presentacion or '—'} – {self.cantidad_existente} disp.)"


class UsoMedicamento(models.Model):
    medicamento     = models.ForeignKey(
        InventarioMedicamento,
        on_delete=models.CASCADE,
        related_name='usos'
    )
    cantidad_usada  = models.PositiveIntegerField("Cantidad Usada")
    responsable     = models.ForeignKey(
        Responsable,
        on_delete=models.PROTECT,
        verbose_name="Responsable"
    )
    comentario      = models.TextField("Comentario", blank=True, null=True)
    fecha_uso       = models.DateTimeField("Fecha de Uso", auto_now_add=True)

    class Meta:
        verbose_name = "Uso de Medicamento"
        verbose_name_plural = "Usos de Medicamentos"

    def __str__(self):
        return f"{self.medicamento.nombre} - {self.cantidad_usada} usado(s)"


# ——————————————————————————————————————————————
# Modelo “no administrado” para SQL Server (Test2)
# ——————————————————————————————————————————————

class TblPrsDtosGen(models.Model):
    PersonaID = models.BigIntegerField(primary_key=True)
    Nombre1   = models.CharField(max_length=100, blank=True, null=True)
    Nombre2   = models.CharField(max_length=100, blank=True, null=True)
    Apellido1 = models.CharField(max_length=100, blank=True, null=True)
    Apellido2 = models.CharField(max_length=100, blank=True, null=True)
    Email     = models.CharField(max_length=254, blank=True, null=True)
    Email2    = models.CharField(max_length=254, blank=True, null=True)
    Email3    = models.CharField(max_length=254, blank=True, null=True)
    alum      = models.IntegerField(db_column='alum', blank=True, null=True)

    class Meta:
        managed  = False
        db_table = 'tblPrsDtosGen'  # Nombre exacto de la tabla en SQL Server

    def __str__(self):
        partes = [self.Nombre1, self.Nombre2, self.Apellido1, self.Apellido2]
        nombre_completo = " ".join([p for p in partes if p])
        return f"{self.PersonaID}: {nombre_completo}"
