$(function() {
  // ===============================
  // 1. Inicializar Select2
  // ===============================
  $('#id_alumno, #id_materia_docente').select2({
    width: '100%',
    minimumResultsForSearch: 10,
    dropdownParent: $('.form-container')
  });

  // ===============================
  // 2. Select2 para incisos (solo si existen en el formulario)
  // ===============================
  if ($('#inciso_leve').length) {
    $('#inciso_leve, #inciso_grave, #inciso_muygrave').select2({
      width: '100%',
      dropdownParent: $('.form-container'),
      templateResult: function(data) {
        if (!data.id) return data.text;
        return $('<span style="white-space: pre-line;">' + data.text + '</span>');
      },
      templateSelection: function(data) {
        if (!data.id) return data.text;
        return $('<span style="white-space: pre-line;">' + data.text + '</span>');
      }
    });
  }

  // ===============================
  // 3. Autollenado de grado (universal, seguro y robusto)
  // ===============================
  function setGrado() {
    let grado = '';
    // Usa Select2 si existe
    let select2Data = $('#id_alumno').select2('data');
    if (select2Data && select2Data[0] && select2Data[0].element) {
      grado = $(select2Data[0].element).data('grado') || '';
    } else {
      grado = $('#id_alumno').find('option:selected').data('grado') || '';
    }
    $('#grado-display').val(grado);
    $('#id_grado').val(grado);
  }
  // Evento para autollenar grado
  $('#id_alumno').on('select2:select change', setGrado);
  // Autollenar al cargar la página
  setGrado();
  // Autollenar justo antes de enviar
  $('#formReporteConductual, #formReporteInformativo').on('submit', setGrado);

  // ===============================
  // 4. Lógica de incisos y checkboxes (solo Conductual)
  // ===============================
  if ($('#inciso_leve').length) {
    // Activa/disactiva incisos por check
    function activarInciso(checkboxId, selectId, textareaId) {
      $(checkboxId).on('change', function() {
        $(selectId).prop('disabled', !this.checked).trigger('change');
        if (!this.checked) {
          $(selectId).val('').trigger('change');
          if (textareaId) $(textareaId).val('');
        }
      });
    }
    activarInciso('#chk_leve', '#inciso_leve', '#txt_incisos_leve');
    activarInciso('#chk_grave', '#inciso_grave', '#txt_incisos_grave');
    activarInciso('#chk_muygrave', '#inciso_muygrave', '#txt_incisos_muygrave');

    // Si el checkbox ya viene marcado, activa el select
    if ($('#chk_leve').is(':checked')) $('#inciso_leve').prop('disabled', false);
    if ($('#chk_grave').is(':checked')) $('#inciso_grave').prop('disabled', false);
    if ($('#chk_muygrave').is(':checked')) $('#inciso_muygrave').prop('disabled', false);

    // Mostrar seleccionados en textarea
    function actualizarTextareaIncisos(selectorSelect, selectorTextarea) {
      var incisos = [];
      $(selectorSelect + ' option:selected').each(function() {
        incisos.push($(this).text());
      });
      $(selectorTextarea).val(incisos.length > 0 ? incisos.join('\n\n') : '');
    }
    $('#inciso_leve').on('change', function() { actualizarTextareaIncisos('#inciso_leve', '#txt_incisos_leve'); });
    $('#inciso_grave').on('change', function() { actualizarTextareaIncisos('#inciso_grave', '#txt_incisos_grave'); });
    $('#inciso_muygrave').on('change', function() { actualizarTextareaIncisos('#inciso_muygrave', '#txt_incisos_muygrave'); });

    // Inicializar textareas al cargar
    actualizarTextareaIncisos('#inciso_leve', '#txt_incisos_leve');
    actualizarTextareaIncisos('#inciso_grave', '#txt_incisos_grave');
    actualizarTextareaIncisos('#inciso_muygrave', '#txt_incisos_muygrave');
  }

  // ===============================
  // 5. Limitar scroll de Select2
  // ===============================
  $(document).on('select2:open', function() {
    $('.select2-results__options').css('max-height', '300px');
  });

  // ===============================
  // 6. Ocultar alertas de éxito tras unos segundos
  // ===============================
  setTimeout(function() {
    $('.alert-success').fadeOut('slow');
  }, 4000);
});
