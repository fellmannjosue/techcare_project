from django.db import models
from django.contrib.auth.models import User

# ────────────────
# Choices globales
# ────────────────
AREA_CHOICES = (
    ('bilingue', 'Bilingüe'),
    ('colegio', 'Colegio/CFP'),
)

ESTADO_CHOICES = (
    ('enviado', 'Enviado'),
    ('revisando', 'Revisando'),
    ('revisado', 'Revisado'),
    ('aprobado', 'Aprobado'),
)

COORDINADORES_BL = [
    ("Mrs. Osorto", "Mrs. Osorto"),
    ("Miss Alcerro", "Miss Alcerro"),
    ("Miss Angela", "Miss Angela"),
]

COORDINADORES_COL = [
    ("profe. Licona", "Profe. Licona"),
    ("profe. Felipe", "Profe. Felipe"),
    ("profe. Gabriela", "Profe. Gabriela"),
]

# ────────────────
# Inciso Conductual
# ────────────────
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

# ────────────────
# Materia-Docente (Bilingüe)
# ────────────────
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

# ────────────────
# Materia-Docente (Colegio)
# ────────────────
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

# ────────────────
# Reporte Conductual
# ────────────────
class ReporteConductual(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario que reporta")
    area = models.CharField(max_length=10, choices=AREA_CHOICES, default='bilingue', verbose_name="Área")
    alumno_id = models.CharField(max_length=50, verbose_name="ID Alumno")
    alumno_nombre = models.CharField(max_length=120, verbose_name="Nombre del Alumno")
    grado = models.CharField(max_length=50, verbose_name="Grado")
    materia = models.CharField(max_length=100, verbose_name="Materia")
    docente = models.CharField(max_length=100, verbose_name="Docente")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    incisos_leve = models.ManyToManyField(
        IncisoConductual, blank=True,
        related_name='conductuales_leve',
        limit_choices_to={'tipo': 'leve', 'activo': True},
        verbose_name="Incisos Leve"
    )
    incisos_grave = models.ManyToManyField(
        IncisoConductual, blank=True,
        related_name='conductuales_grave',
        limit_choices_to={'tipo': 'grave', 'activo': True},
        verbose_name="Incisos Grave"
    )
    incisos_muygrave = models.ManyToManyField(
        IncisoConductual, blank=True,
        related_name='conductuales_muygrave',
        limit_choices_to={'tipo': 'muy_grave', 'activo': True},
        verbose_name="Incisos Muy Grave"
    )

    comentario = models.TextField(blank=True, null=True, verbose_name="Comentario adicional")
    coordinador_firma = models.CharField("Coordinador que aprueba", max_length=100, blank=True, null=True, help_text="Nombre del coordinador que aprobó/firmó el reporte.")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='enviado', verbose_name="Estado del reporte")
    comentario_coordinador = models.TextField("Comentario del Coordinador", blank=True, null=True, help_text="Observación, recomendación o motivo de la revisión/aprobación.")

    def __str__(self):
        return f'{self.alumno_nombre} - {self.materia} - {self.usuario.username} ({self.get_area_display()})'

    class Meta:
        verbose_name = "Reporte Conductual"
        verbose_name_plural = "Reportes Conductuales"
        ordering = ['-fecha']

# ────────────────
# Reporte Informativo
# ────────────────
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

    coordinador_firma = models.CharField("Coordinador que aprueba", max_length=100, blank=True, null=True, help_text="Nombre del coordinador que aprobó/firmó el reporte.")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='enviado', verbose_name="Estado del reporte")
    comentario_coordinador = models.TextField("Comentario del Coordinador", blank=True, null=True, help_text="Observación, recomendación o motivo de la revisión/aprobación.")

    def __str__(self):
        return f'{self.alumno_nombre} - {self.materia} - {self.usuario.username} ({self.get_area_display()})'

    class Meta:
        verbose_name = "Reporte Informativo"
        verbose_name_plural = "Reportes Informativos"
        ordering = ['-fecha']

# ────────────────
# Progress Report
# ────────────────
class ProgressReport(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario que reporta")
    alumno_id = models.CharField(max_length=50, verbose_name="ID Alumno")
    alumno_nombre = models.CharField(max_length=120, verbose_name="Nombre del Alumno")
    grado = models.CharField(max_length=50, verbose_name="Grado")
    semana_inicio = models.DateField(verbose_name="Semana inicio")
    semana_fin = models.DateField(verbose_name="Semana fin")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    materias_json = models.JSONField(verbose_name="Detalle materias", blank=True, default=list)
    comentario_general = models.TextField(blank=True, null=True, verbose_name="Comentario General")

    coordinador_firma = models.CharField("Coordinador que aprueba", max_length=100, blank=True, null=True, help_text="Nombre del coordinador que aprobó/firmó el reporte.")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='enviado', verbose_name="Estado del reporte")
    comentario_coordinador = models.TextField("Comentario del Coordinador", blank=True, null=True, help_text="Observación, recomendación o motivo de la revisión/aprobación.")

    def __str__(self):
        return f'Progress {self.alumno_nombre} ({self.semana_inicio} - {self.semana_fin})'

    class Meta:
        verbose_name = "Progress Report"
        verbose_name_plural = "Progress Reports"
        ordering = ['-fecha']
