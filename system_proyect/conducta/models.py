from django.db import models
from django.contrib.auth.models import User

# Áreas posibles para los reportes
AREA_CHOICES = (
    ('bilingue', 'Bilingüe'),
    ('colegio', 'Colegio/CFP'),
)

# ─────────────────────────────
# Inciso Conductual
# ─────────────────────────────
class IncisoConductual(models.Model):
    TIPO_CHOICES = (
        ('leve', 'Leve'),
        ('grave', 'Grave'),
        ('muy_grave', 'Muy Grave'),
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo de Inciso")
    descripcion = models.CharField(max_length=500, verbose_name="Descripción del inciso")
    activo = models.BooleanField(default=True, verbose_name="¿Activo?")

    def __str__(self):
        return f'{self.get_tipo_display()}: {self.descripcion}'

    class Meta:
        verbose_name = "Inciso Conductual"
        verbose_name_plural = "Incisos Conductuales"
        ordering = ['tipo', 'descripcion']

# ─────────────────────────────
# Materia-Docente (Bilingüe)
# ─────────────────────────────
class MateriaDocenteBilingue(models.Model):
    materia = models.CharField(max_length=100, verbose_name="Materia")
    docente = models.CharField(max_length=100, verbose_name="Docente")
    activo = models.BooleanField(default=True, verbose_name="¿Activo?")

    def __str__(self):
        return f"{self.materia} – {self.docente}"

    class Meta:
        verbose_name = "Materia-Docente Bilingüe"
        verbose_name_plural = "Materias-Docentes Bilingüe"
        ordering = ['materia', 'docente']

# ─────────────────────────────
# Materia-Docente (Colegio)
# ─────────────────────────────
class MateriaDocenteColegio(models.Model):
    materia = models.CharField(max_length=100, verbose_name="Materia")
    docente = models.CharField(max_length=100, verbose_name="Docente")
    activo = models.BooleanField(default=True, verbose_name="¿Activo?")

    def __str__(self):
        return f"{self.materia} – {self.docente}"

    class Meta:
        verbose_name = "Materia-Docente Colegio"
        verbose_name_plural = "Materias-Docentes Colegio"
        ordering = ['materia', 'docente']

# ─────────────────────────────
# Reporte Conductual
# ─────────────────────────────
class ReporteConductual(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario que reporta")
    area = models.CharField(max_length=10, choices=AREA_CHOICES, default='bilingue', verbose_name="Área")
    alumno_id = models.CharField(max_length=50, verbose_name="ID Alumno")
    alumno_nombre = models.CharField(max_length=120, verbose_name="Nombre del Alumno")
    grado = models.CharField(max_length=50, verbose_name="Grado")

    # Opcional: ForeignKey a MateriaDocente según área (puedes mejorar luego)
    materia = models.CharField(max_length=100, verbose_name="Materia")
    docente = models.CharField(max_length=100, verbose_name="Docente")

    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    leve = models.BooleanField(default=False, verbose_name="Leve")
    inciso_leve = models.ForeignKey(
        IncisoConductual, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='conductuales_leve',
        limit_choices_to={'tipo': 'leve', 'activo': True},
        verbose_name="Inciso Leve"
    )
    grave = models.BooleanField(default=False, verbose_name="Grave")
    inciso_grave = models.ForeignKey(
        IncisoConductual, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='conductuales_grave',
        limit_choices_to={'tipo': 'grave', 'activo': True},
        verbose_name="Inciso Grave"
    )
    muy_grave = models.BooleanField(default=False, verbose_name="Muy grave")
    inciso_muy_grave = models.ForeignKey(
        IncisoConductual, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='conductuales_muy_grave',
        limit_choices_to={'tipo': 'muy_grave', 'activo': True},
        verbose_name="Inciso Muy Grave"
    )

    comentario = models.TextField(blank=True, null=True, verbose_name="Comentario adicional")

    def __str__(self):
        return f'{self.alumno_nombre} - {self.materia} - {self.usuario.username} ({self.get_area_display()})'

    class Meta:
        verbose_name = "Reporte Conductual"
        verbose_name_plural = "Reportes Conductuales"
        ordering = ['-fecha']

# ─────────────────────────────
# Reporte Informativo
# ─────────────────────────────
class ReporteInformativo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario que reporta")
    area = models.CharField(max_length=10, choices=AREA_CHOICES, default='bilingue', verbose_name="Área")
    alumno_id = models.CharField(max_length=50, verbose_name="ID Alumno")
    alumno_nombre = models.CharField(max_length=120, verbose_name="Nombre del Alumno")
    grado = models.CharField(max_length=50, verbose_name="Grado")
    materia = models.CharField(max_length=100, verbose_name="Materia")
    docente = models.CharField(max_length=100, verbose_name="Docente")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    comentario = models.TextField(blank=True, null=True, verbose_name="Comentario")

    def __str__(self):
        return f'{self.alumno_nombre} - {self.materia} - {self.usuario.username} ({self.get_area_display()})'

    class Meta:
        verbose_name = "Reporte Informativo"
        verbose_name_plural = "Reportes Informativos"
        ordering = ['-fecha']

# ─────────────────────────────
# Progress Report
# ─────────────────────────────
class ProgressReport(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario que reporta")
    alumno_id = models.CharField(max_length=50, verbose_name="ID Alumno")
    alumno_nombre = models.CharField(max_length=120, verbose_name="Nombre del Alumno")
    grado = models.CharField(max_length=50, verbose_name="Grado")
    semana_inicio = models.DateField(verbose_name="Semana inicio")
    semana_fin = models.DateField(verbose_name="Semana fin")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    materias_json = models.JSONField(verbose_name="Detalle materias", blank=True, null=True)
    comentario_general = models.TextField(blank=True, null=True, verbose_name="Comentario General")

    def __str__(self):
        return f'Progress {self.alumno_nombre} ({self.semana_inicio} - {self.semana_fin})'

    class Meta:
        verbose_name = "Progress Report"
        verbose_name_plural = "Progress Reports"
        ordering = ['-fecha']
