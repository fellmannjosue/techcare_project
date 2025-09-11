$(function() {
  // Select2 para selects largos
  $('#id_alumno, #id_materia_docente').select2({
    width: '100%',
    minimumResultsForSearch: 10,
    dropdownParent: $('.form-container')
  });

  // Select2 para incisos, con formato de párrafo/saltos de línea
  $('#inciso_leve, #inciso_grave, #inciso_muygrave').select2({
    width: '100%',
    dropdownParent: $('.form-container'),
    templateResult: function(data) {
      // Respeta saltos de línea en las opciones
      if (!data.id) return data.text;
      return $('<span style="white-space: pre-line;">' + data.text + '</span>');
    },
    templateSelection: function(data) {
      if (!data.id) return data.text;
      return $('<span style="white-space: pre-line;">' + data.text + '</span>');
    }
  });

  // Llenar grado automáticamente
  $('#id_alumno').on('change', function() {
    let grado = $(this).find('option:selected').data('grado') || '';
    $('#grado-display').val(grado);
    $('#id_grado').val(grado);
  });
  let $alumno = $('#id_alumno');
  let initialGrado = $alumno.find('option:selected').data('grado') || '';
  $('#grado-display').val(initialGrado);
  $('#id_grado').val(initialGrado);

  // Activar/desactivar dropdown de inciso según el checkbox
  $('#chk_leve').on('change', function() {
    $('#inciso_leve').prop('disabled', !this.checked).trigger('change');
    if (!this.checked) $('#inciso_leve').val('').trigger('change');
  });
  $('#chk_grave').on('change', function() {
    $('#inciso_grave').prop('disabled', !this.checked).trigger('change');
    if (!this.checked) $('#inciso_grave').val('').trigger('change');
  });
  $('#chk_muygrave').on('change', function() {
    $('#inciso_muygrave').prop('disabled', !this.checked).trigger('change');
    if (!this.checked) $('#inciso_muygrave').val('').trigger('change');
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
