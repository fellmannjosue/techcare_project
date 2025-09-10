$(function() {
  // Inicializar Select2 para los combos
  $('#id_alumno, #id_materia_docente').select2({
    width: '100%',
    minimumResultsForSearch: 10,
    dropdownParent: $('.form-container')
  });

  // Limitar scroll de opciones del dropdown a 300px
  $(document).on('select2:open', function() {
    $('.select2-results__options').css('max-height', '300px');
  });

  // Autollenar grado al seleccionar estudiante
  $('#id_alumno').on('change', function() {
    let alumno_id = $(this).val();
    if (alumno_id) {
      $.get('/conducta/ajax/grado/', { alumno_id: alumno_id }, function(data) {
        $('#id_grado').val(data.grado || '');
      });
    } else {
      $('#id_grado').val('');
    }
  });

  // Si ya hay un alumno seleccionado al cargar, carga el grado
  var selected_alumno = $('#id_alumno').val();
  if (selected_alumno) {
    $.get('/conducta/ajax/grado/', { alumno_id: selected_alumno }, function(data) {
      $('#id_grado').val(data.grado || '');
    });
  }
});
