// static/citas_colegio/js/motivo_col.js
document.addEventListener('DOMContentLoaded', function () {
    const gradeSelect   = document.getElementById('grade');
    const subjectSelect = document.getElementById('subject');
    const teacherField  = document.getElementById('teacher');
    const areaField     = document.getElementById('area');
    const reasonInput   = document.getElementById('reason');
    const nextButton    = document.getElementById('next-motivo');
    const csrfToken     = document.getElementById('js-data').dataset.csrfToken;

    gradeSelect.addEventListener('change', function () {
        const gradeId = this.value;
        subjectSelect.innerHTML = '<option value="">Seleccione la materia</option>';
        teacherField.value = '';
        areaField.value = '';

        if (!gradeId) return;

        fetch(`/citas_colegio/get-subjects-by-grade_col/?grade_id=${gradeId}`)
            .then(resp => resp.json())
            .then(data => {
                if (data.subjects) {
                    data.subjects.forEach(subject => {
                        const option = document.createElement('option');
                        option.value = subject.id;
                        option.textContent = subject.name;
                        subjectSelect.appendChild(option);
                    });
                } else {
                    subjectSelect.innerHTML = '<option value="">No hay materias disponibles</option>';
                }
            })
            .catch(() => {
                Swal.fire({
                    title: 'Error',
                    text: 'No se pudieron cargar las materias. Inténtelo nuevamente.',
                    icon: 'error',
                    confirmButtonText: 'Aceptar',
                });
            });
    });

    subjectSelect.addEventListener('change', function () {
        const subjectId = this.value;
        teacherField.value = '';
        areaField.value = '';

        if (!subjectId) return;

        fetch(`/citas_colegio/get-teacher-by-subject_col/?subject_id=${subjectId}`)
            .then(resp => resp.json())
            .then(data => {
                if (data.teacher) {
                    teacherField.value = data.teacher.name;
                    areaField.value    = data.teacher.area;
                }
            })
            .catch(() => {
                Swal.fire({
                    title: 'Error',
                    text: 'No se pudo cargar la información del maestro.',
                    icon: 'error',
                    confirmButtonText: 'Aceptar',
                });
            });
    });

    nextButton.addEventListener('click', function () {
        const gradeValue   = gradeSelect.value;
        const subjectValue = subjectSelect.value;
        const reasonValue  = reasonInput.value.trim();

        if (!gradeValue || !subjectValue || !reasonValue) {
            Swal.fire({
                title: 'Error',
                text: 'Por favor complete todos los campos antes de continuar.',
                icon: 'error',
                confirmButtonText: 'Aceptar',
            });
            return;
        }

        fetch('/citas_colegio/motivo_col/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                grade:   gradeValue,
                subject: subjectValue,
                reason:  reasonValue,
            }),
        })
        .then(resp => resp.json())
        .then(data => {
            if (data.appointment_id) {
                Swal.fire({
                    title: 'Datos guardados',
                    text: 'Redirigiendo a la selección de fecha...',
                    icon: 'success',
                    timer: 2000,
                    showConfirmButton: false,
                }).then(() => {
                    window.location.href = `/citas_colegio/select-date_col/${data.appointment_id}/`;
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
                text: 'Error al guardar los datos. Inténtelo nuevamente.',
                icon: 'error',
                confirmButtonText: 'Aceptar',
            });
        });
    });
});
