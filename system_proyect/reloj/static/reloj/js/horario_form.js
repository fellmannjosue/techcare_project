// static/reloj/horario_form.js

document.addEventListener('DOMContentLoaded', function () {
    // Autocompleta el ID cuando seleccionas un empleado
    const dropdown = document.getElementById('id_nombre_dropdown');
    const idInput = document.getElementById('id_emp_code');
    if (dropdown && idInput) {
        dropdown.addEventListener('change', function () {
            idInput.value = this.value;
        });
    }

    // Mensajes Django (SweetAlert2)
    if (window.django_messages && window.django_messages.length > 0) {
        Swal.fire({
            icon: 'success',
            title: '¡Listo!',
            text: window.django_messages[0],
            timer: 1800,
            showConfirmButton: false
        });
    }
});
