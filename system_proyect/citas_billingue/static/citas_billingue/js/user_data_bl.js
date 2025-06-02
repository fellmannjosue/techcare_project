// static/citas_billingue/js/user_data_bl.js

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('user-data-form');

  form.addEventListener('submit', function (e) {
    const parentName  = document.getElementById('parent_name').value.trim();
    const studentName = document.getElementById('student_name').value.trim();
    const relationship = document.getElementById('relationship').value;

    if (!parentName || !studentName || !relationship) {
      e.preventDefault(); // Detener el envío del formulario si falta un campo
      Swal.fire({
        title: 'Error',
        text: 'Por favor, complete todos los campos antes de continuar.',
        icon: 'error',
        confirmButtonText: 'Aceptar'
      });
    }
  });
});
