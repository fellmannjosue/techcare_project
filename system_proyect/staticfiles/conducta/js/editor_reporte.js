document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form-editor-reporte');
    if (form) {
        form.addEventListener('submit', function (e) {
            // Validación simple (puedes mejorarla)
            // e.preventDefault(); // Si quieres prevenir envío para test
            // alert('¡Guardando cambios!');
        });
    }
});
