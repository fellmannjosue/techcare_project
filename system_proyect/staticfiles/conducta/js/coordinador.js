// static/conducta/js/coordinador.js

$(function() {
    // Inicializar DataTable en la tabla principal
    if ($('#tabla-coordinador').length) {
        $('#tabla-coordinador').DataTable({
            "order": [[2, "desc"]],
            "language": {
                "url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
            }
        });
    }

    // Acción para mostrar historial del alumno en modal
    $(document).on('click', '.btn-historial', function() {
        let alumno_id = $(this).data('alumno');
        $('#historial-content').html('<div class="text-center text-muted py-3">Cargando historial...</div>');
        $('#modalHistorial').modal('show');
        $.get('/conducta/coordinador/historial/alumno/' + alumno_id + '/', function(data) {
            $('#historial-content').html(data);
        }).fail(function() {
            $('#historial-content').html('<div class="alert alert-danger">Error al cargar historial.</div>');
        });
    });

    // Mostrar el modal de advertencia si el usuario intenta descargar PDF sin 3 reportes
    $(document).on('click', '.btn-pdf-disabled', function(e) {
        e.preventDefault();
        $('#modalTresFaltas').modal('show');
    });
});
