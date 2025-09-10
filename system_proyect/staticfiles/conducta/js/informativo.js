// Requiere: JQuery, Select2 y SweetAlert2 incluidos en tu template HTML

$(document).ready(function() {
    // Inicializa Select2 en los selects
    $('#id_alumno, #id_materia, #id_docente').select2({
        width: '100%',
        dropdownParent: $('.form-container'),
        minimumResultsForSearch: 5, // Siempre muestra búsqueda si hay más de 5
        dropdownAutoWidth: true,
        // Limita el alto del dropdown (con CSS)
    });

    // Limita el alto del dropdown (solo visual, aplica a todos los Select2)
    $('<style>')
        .prop('type', 'text/css')
        .html('.select2-results__options { max-height: 230px !important; overflow-y: auto !important; }')
        .appendTo('head');

    // Cuando seleccionas un alumno, carga el grado automático
    $('#id_alumno').on('change', function() {
        var alumno_id = $(this).val();
        if (alumno_id) {
            $.get(window.url_ajax_grado_alumno, { alumno_id: alumno_id }, function(data) {
                $('#id_grado').val(data.grado || '');
            });
        } else {
            $('#id_grado').val('');
        }
    });

    // Cuando seleccionas materia, carga docentes por AJAX
    $('#id_materia').on('change', function(){
        var materia_id = $(this).val();
        var area = window.area_actual || ''; // area viene como variable global desde el template
        var $docente = $('#id_docente');
        $docente.empty().trigger('change');
        if (materia_id) {
            $.get(window.url_ajax_docentes_por_materia, { materia_id: materia_id, area: area }, function(data){
                $docente.empty();
                $docente.append($('<option>', { value: '', text: 'Seleccione una opción...' }));
                $.each(data.docentes, function(idx, item){
                    $docente.append($('<option>', { value: item[0], text: item[1] }));
                });
                $docente.trigger('change'); // refresca select2
            });
        }
    });

    // Mostrar mensaje de éxito con SweetAlert2 al enviar (si NO usas AJAX)
    $('#formReporteInformativo').on('submit', function(e){
        // Si el submit es por AJAX, aquí va tu lógica de envío
        // Si usas POST normal, esto solo muestra el loader hasta que recargue
        // (Descomenta si quieres interceptar el submit y usar AJAX)
        // e.preventDefault();
        // ...envío por AJAX...

        // Mostrar un loader o mensaje temporal (esto es visual)
        Swal.fire({
            icon: 'success',
            title: '¡Reporte guardado!',
            showConfirmButton: false,
            timer: 1500
        });
    });

    // Si quieres que al cargar la página y hay un alumno seleccionado, autollenar el grado
    if ($('#id_alumno').val()) {
        $('#id_alumno').trigger('change');
    }
});
