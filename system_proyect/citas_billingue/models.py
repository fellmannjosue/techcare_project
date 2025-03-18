from django.db import models


class Relationship_bl(models.Model):
    """Tipo de parentesco (padre, madre, tutor, etc.)."""
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Grade_bl(models.Model):
    """Nombre del grado (Primero, Segundo, etc.)."""
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Teacher_bl(models.Model):
    """Información del maestro."""
    name = models.CharField(max_length=255)
    area = models.CharField(
        max_length=50,
        choices=[
           ('Ingles de kinder a tecero 2', 'Ingles de kinder a tecero 2'),
            ('Ingles de cuarto a noveno', 'Ingles de cuarto a noveno'),
            ('Español', 'Español'),
            ('Matematicas', 'Matematicas ')
        ]
    )
    class_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Subject_bl(models.Model):
    """Materias impartidas, vinculadas con un grado y un maestro."""
    name = models.CharField(max_length=255)
    grade = models.ForeignKey(Grade_bl, on_delete=models.CASCADE, related_name='subjects')  # Relación con el grado
    teacher = models.ForeignKey(Teacher_bl, on_delete=models.CASCADE, related_name='subjects')  # Relación con el maestro

    def __str__(self):
        return f"{self.name} ({self.grade.name})"


class Schedule_bl(models.Model):
    """Horario del maestro."""
    teacher = models.ForeignKey(Teacher_bl, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ('Monday', 'Lunes'),
            ('Tuesday', 'Martes'),
            ('Wednesday', 'Miércoles'),
            ('Thursday', 'Jueves'),
            ('Friday', 'Viernes'),
            ('Saturday', 'Sábado'),
            ('Sunday', 'Domingo'),
        ]
    )
    start_time = models.TimeField()  # Hora de inicio
    end_time = models.TimeField()  # Hora de fin

    def __str__(self):
        return f"{self.teacher.name} - {self.day_of_week} ({self.start_time} - {self.end_time})"


class Appointment_bl(models.Model):
    """Citas agendadas por los padres."""
    parent_name = models.CharField(max_length=255)  # Nombre del padre
    student_name = models.CharField(max_length=255)  # Nombre del alumno
    relationship = models.ForeignKey(Relationship_bl, on_delete=models.CASCADE)  # Parentesco
    grade = models.ForeignKey(Grade_bl, on_delete=models.CASCADE)  # Grado del alumno
    subject = models.ForeignKey(Subject_bl, on_delete=models.CASCADE, null=True, blank=True)  # Permitir nulo Materia seleccionada
    teacher = models.ForeignKey(Teacher_bl, on_delete=models.CASCADE)  # Maestro relacionado (rellenado automáticamente)
    area = models.CharField(max_length=50)  # Área del maestro (rellenado automáticamente)
    reason = models.TextField()  # Razón o motivo de la cita
    date = models.DateField(null=True, blank=True)  # Fecha de la cita
    time = models.TimeField(null=True, blank=True)  # Hora de la cita
    email = models.EmailField(null=True, blank=True)  # Correo electrónico
    phone = models.CharField(max_length=15, null=True, blank=True)  # Teléfono de contacto
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Confirmada', 'Confirmada'),
            ('Cancelada', 'Cancelada'),
        ],
        default='Pendiente'
    )  # Estado de la cita

    def __str__(self):
        return f"{self.parent_name} - {self.teacher.name} ({self.date} {self.time})"
