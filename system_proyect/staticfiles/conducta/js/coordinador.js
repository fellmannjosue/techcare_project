$(document).ready(function() {
    $('#tabla-coordinador').DataTable({
        "order": [[2, "desc"]],
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
        }
    });

    // Acción para el botón historial
    $('.btn-historial').on('click', function() {
        let alumno_id = $(this).data('alumno');
        $('#historial-content').html('Cargando...');
        $('#modalHistorial').modal('show');
        // Aquí puedes hacer AJAX a tu vista que devuelva el historial de reportes de ese alumno
        // Ejemplo:
        $.get('/conducta/coordinador/historial/alumno/' + alumno_id + '/', function(data) {
            $('#historial-content').html(data);
        }).fail(function() {
            $('#historial-content').html('<div class="alert alert-danger">Error al cargar historial.</div>');
        });
    });
});
