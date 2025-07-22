# informes_bl/models.py

from django.db import models
from django.db import connection

# Tu consulta original para obtener alumnos
SQL_OBTENER_ALUMNOS = """
    SELECT 
      d.PersonaID,
      ISNULL(d.Nombre1,'')
        + CASE WHEN d.Nombre2 IS NOT NULL AND d.Nombre2 <> '' THEN ' ' + d.Nombre2 ELSE '' END
        + ' ' + ISNULL(d.Apellido1,'')
        + CASE WHEN d.Apellido2 IS NOT NULL AND d.Apellido2 <> '' THEN ' ' + d.Apellido2 ELSE '' END
        AS NombreCompl
    FROM dbo.tblPrsDtosGen AS d
    JOIN dbo.tblPrsTipo           AS t  ON d.PersonaID = t.PersonaID
    JOIN dbo.tblEdcArea           AS a  ON t.IngrEgrID  = a.IngrEgrID
    JOIN dbo.tblEdcEjecCrso       AS ec ON a.AreaID     = ec.AreaID
    JOIN dbo.tblEdcCrso           AS c  ON ec.CrsoID     = c.CrsoID
    JOIN dbo.tblEdcDescripAreaEdc AS da ON a.DescrAreaEdcID = da.DescrAreaEdcID
    WHERE d.Alum = 1
      AND DATEPART(yy, c.FechaInicio) = DATEPART(yyyy, GETDATE())
      AND da.Descripcion IN (N'PrimariaBL', N'ColegioBL', N'PreescolarBL')
      AND ec.Desertor    = 0
      AND ec.TrasladoPer = 0
    ORDER BY NombreCompl
"""

class ProgressReport(models.Model):
    persona_id     = models.IntegerField("PersonaID")
    semana_inicio  = models.DateField("Semana desde")
    semana_fin     = models.DateField("Semana hasta")
    creado         = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Progress Report"
        verbose_name_plural = "Progress Reports"

    def __str__(self):
        return f"{self.alumno_nombre} [{self.semana_inicio} – {self.semana_fin}]"

    @property
    def alumno_nombre(self):
        """Ejecuta la consulta SQL para obtener el NombreCompl según persona_id"""
        with connection.cursor() as cursor:
            cursor.execute(SQL_OBTENER_ALUMNOS + " AND d.PersonaID = %s", [self.persona_id])
            row = cursor.fetchone()
        return row[1] if row else f"ID {self.persona_id}"


class Materia(models.Model):
    nombre = models.CharField("Materia", max_length=100, unique=True)

    class Meta:
        verbose_name        = "Materia"
        verbose_name_plural = "Materias"

    def __str__(self):
        return self.nombre


class ReportEntry(models.Model):
    reporte     = models.ForeignKey(
        ProgressReport,
        related_name="entries",
        on_delete=models.CASCADE,
        verbose_name="Reporte"
    )
    materia     = models.ForeignKey(
        Materia,
        on_delete=models.PROTECT,
        verbose_name="Materia"
    )
    asignacion  = models.CharField("Asignación", max_length=200, blank=True)
    observacion = models.TextField("Comentario/Observación", blank=True)

    class Meta:
        verbose_name        = "Entrada de Reporte"
        verbose_name_plural = "Entradas de Reporte"
        ordering            = ['materia']

    def __str__(self):
        return f"{self.reporte} – {self.materia}"
