// static/citas_billingue/js/motivo_bl.js

document.addEventListener('DOMContentLoaded', function () {
  const gradeSelect   = document.getElementById('grade');
  const subjectSelect = document.getElementById('subject');
  const teacherField  = document.getElementById('teacher');
  const areaField     = document.getElementById('area');
  const reasonInput   = document.getElementById('reason');
  const nextButton    = document.getElementById('next-motivo');
  const form          = document.getElementById('motivo-form');

  // Cuando se seleccione un grado, cargamos las materias asociadas
  gradeSelect.addEventListener('change', function () {
    const gradeId = this.value;

    if (gradeId) {
      fetch(`/citas_billingue/get-subjects-by-grade/?grade_id=${gradeId}`)
        .then(response => response.json())
        .then(data => {
          if (data.subjects) {
            subjectSelect.innerHTML = '<option value="">Seleccione la materia</option>';
            data.subjects.forEach(subject => {
              const option = document.createElement('option');
              option.value = subject.id;
              option.textContent = subject.name;
              subjectSelect.appendChild(option);
            });
          } else {
            subjectSelect.innerHTML = '<option value="">No hay materias disponibles</option>';
          }
          // Limpiar campos de maestro y área
          teacherField.value = '';
          areaField.value = '';
        })
        .catch(() => {
          Swal.fire({
            title: 'Error',
            text: 'No se pudieron cargar las materias. Por favor, inténtelo nuevamente.',
            icon: 'error',
            confirmButtonText: 'Aceptar',
          });
        });
    } else {
      subjectSelect.innerHTML = '<option value="">Seleccione la materia</option>';
      teacherField.value = '';
      areaField.value = '';
    }
  });

  // Cuando se seleccione una materia, cargamos el maestro y el área
  subjectSelect.addEventListener('change', function () {
    const subjectId = this.value;

    if (subjectId) {
      fetch(`/citas_billingue/get-teacher-by-subject/?subject_id=${subjectId}`)
        .then(response => response.json())
        .then(data => {
          if (data.teacher) {
            teacherField.value = data.teacher.name;
            areaField.value    = data.teacher.area;
          } else {
            teacherField.value = '';
            areaField.value    = '';
          }
        })
        .catch(() => {
          Swal.fire({
            title: 'Error',
            text: 'No se pudieron cargar los datos del maestro. Por favor, inténtelo nuevamente.',
            icon: 'error',
            confirmButtonText: 'Aceptar',
          });
        });
    } else {
      teacherField.value = '';
      areaField.value    = '';
    }
  });

  // Al hacer clic en “Siguiente”, enviamos el POST con fetch
  nextButton.addEventListener('click', function () {
    const gradeValue   = gradeSelect.value;
    const subjectValue = subjectSelect.value;
    const reasonValue  = reasonInput.value.trim();

    if (gradeValue && subjectValue && reasonValue) {
      fetch('/citas_billingue/motivo_bl/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': CSRF_TOKEN      // Usamos la constante que expusimos en el HTML
        },
        body: new URLSearchParams({
          grade:   gradeValue,
          subject: subjectValue,
          reason:  reasonValue
        })
      })
        .then(response => response.json())
        .then(data => {
          if (data.appointment_id) {
            Swal.fire({
              title: 'Datos guardados',
              text: 'Redirigiendo a la selección de fecha...',
              icon: 'success',
              timer: 2000,
              showConfirmButton: false
            }).then(() => {
              window.location.href = `/citas_billingue/select-date_bl/${data.appointment_id}/`;
            });
          } else {
            Swal.fire({
              title: 'Error',
              text: data.error || 'No se pudo obtener el ID de la cita.',
              icon: 'error',
              confirmButtonText: 'Aceptar',
            });
          }
        })
        .catch(() => {
          Swal.fire({
            title: 'Error',
            text: 'Ocurrió un error al guardar los datos. Por favor, inténtelo nuevamente.',
            icon: 'error',
            confirmButtonText: 'Aceptar',
          });
        });
    } else {
      Swal.fire({
        title: 'Error',
        text: 'Por favor, complete todos los campos antes de continuar.',
        icon: 'error',
        confirmButtonText: 'Aceptar',
      });
    }
  });
});
