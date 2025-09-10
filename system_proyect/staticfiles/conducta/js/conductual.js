$(function() {
  // Inicializar select2
  $('#id_alumno, #id_materia_docente').select2({
    width: '100%',
    minimumResultsForSearch: 10,
    dropdownParent: $('.form-container')
  });

  // Llenar grado automático
  $('#id_alumno').on('change', function() {
    let grado = $(this).find('option:selected').data('grado') || '';
    $('#grado-display').val(grado);
    $('#id_grado').val(grado);
  });
  let $alumno = $('#id_alumno');
  let initialGrado = $alumno.find('option:selected').data('grado') || '';
  $('#grado-display').val(initialGrado);
  $('#id_grado').val(initialGrado);

  // Check para activar/desactivar los dropdowns de incisos
  $('#chk_leve').on('change', function() {
    $('#inciso_leve').prop('disabled', !this.checked);
    if (!this.checked) $('#inciso_leve').val('');
  });
  $('#chk_grave').on('change', function() {
    $('#inciso_grave').prop('disabled', !this.checked);
    if (!this.checked) $('#inciso_grave').val('');
  });
  $('#chk_muygrave').on('change', function() {
    $('#inciso_muygrave').prop('disabled', !this.checked);
    if (!this.checked) $('#inciso_muygrave').val('');
  });

  // Limitar scroll select2
  $(document).on('select2:open', function() {
    $('.select2-results__options').css('max-height', '300px');
  });

  // Ocultar alertas de éxito
  setTimeout(function() {
    $('.alert-success').fadeOut('slow');
  }, 4000);
});
