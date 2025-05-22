from django.db import models

class InventarioCamara(models.Model):
    nombre       = models.CharField("Nombre de cámara",   max_length=100)
    modelo       = models.CharField("Modelo",             max_length=100)
    serie        = models.CharField("Serie",              max_length=100)
    tipo         = models.CharField("Tipo de cámara",     max_length=50)
    ip_camara    = models.GenericIPAddressField("IP cámara")
    ip_acceso    = models.GenericIPAddressField("IP de acceso")
    ubic_gabinete= models.CharField("Ubicación gabinete", max_length=100)
    canal        = models.CharField("Canal",              max_length=10)
    nvr          = models.CharField("NVR",                max_length=100)

    def __str__(self):
        return f"{self.nombre} ({self.modelo})"


class ContableCamara(models.Model):
    modelo            = models.CharField("Modelo",            max_length=100)
    nombre            = models.CharField("Nombre",            max_length=100)
    cantidad_modelo   = models.PositiveIntegerField("Cantidad")
    total             = models.DecimalField("Total", max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} – {self.cantidad_modelo}"


class IdentificacionCamaraGabinete(models.Model):
    numero_gabinete = models.CharField("Núm. Gabinete",    max_length=50)
    switches        = models.PositiveIntegerField("Cant. switches")
    patchcords      = models.PositiveIntegerField("Cant. patchcord")
    puerto          = models.CharField("Puerto",            max_length=50)
    camara          = models.ForeignKey(InventarioCamara, on_delete=models.CASCADE, verbose_name="Cámara")
    nvr             = models.CharField("NVR",               max_length=100)

    def __str__(self):
        return f"Gabinete {self.numero_gabinete} – Puerto {self.puerto}"
