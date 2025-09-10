$(function() {
  // Inicializar select2 en alumno y materia_docente
  $('#id_alumno, #id_materia_docente').select2({
    width: '100%',
    minimumResultsForSearch: 10,
    dropdownParent: $('.form-container')
  });

  // Llenar grado automáticamente desde data-grado del <option> seleccionado
  $('#id_alumno').on('change', function() {
    let grado = $(this).find('option:selected').data('grado') || '';
    $('#grado-display').val(grado);
    $('#id_grado').val(grado);
  });

  // Al cargar la página (ej. modo editar)
  let $alumno = $('#id_alumno');
  let initialGrado = $alumno.find('option:selected').data('grado') || '';
  $('#grado-display').val(initialGrado);
  $('#id_grado').val(initialGrado);

  // Limitar scroll de select2
  $(document).on('select2:open', function() {
    $('.select2-results__options').css('max-height', '300px');
  });

  // Oculta alertas de éxito tras unos segundos
  setTimeout(function() {
    $('.alert-success').fadeOut('slow');
  }, 4000);
});
