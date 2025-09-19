$(function() {
  // ============================
  // 1. Select2 para selects largos
  // ============================
  $('#id_alumno, #id_materia_docente').select2({
    width: '100%',
    minimumResultsForSearch: 10,
    dropdownParent: $('.form-container')
  });

  // ==============================
  // 2. Select2 para incisos (múltiple)
  // ==============================
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

  // =================================================
  // 3. Inicializar selects habilitados si el checkbox ya viene marcado
  // =================================================
  if ($('#chk_leve').is(':checked')) {
    $('#inciso_leve').prop('disabled', false);
  }
  if ($('#chk_grave').is(':checked')) {
    $('#inciso_grave').prop('disabled', false);
  }
  if ($('#chk_muygrave').is(':checked')) {
    $('#inciso_muygrave').prop('disabled', false);
  }

  // ==========================================
  // 4. Lógica de activar/desactivar selects por checkbox
  // ==========================================
  $('#chk_leve').on('change', function() {
    $('#inciso_leve').prop('disabled', !this.checked).trigger('change');
    if (!this.checked) {
      $('#inciso_leve').val('').trigger('change');
      $('#txt_incisos_leve').val('');
    }
  });
  $('#chk_grave').on('change', function() {
    $('#inciso_grave').prop('disabled', !this.checked).trigger('change');
    if (!this.checked) {
      $('#inciso_grave').val('').trigger('change');
      $('#txt_incisos_grave').val('');
    }
  });
  $('#chk_muygrave').on('change', function() {
    $('#inciso_muygrave').prop('disabled', !this.checked).trigger('change');
    if (!this.checked) {
      $('#inciso_muygrave').val('').trigger('change');
      $('#txt_incisos_muygrave').val('');
    }
  });

  // ======================================
  // 5. Mostrar incisos seleccionados en textarea
  // ======================================
  function actualizarTextareaIncisos(selectorSelect, selectorTextarea) {
    var incisos = [];
    $(selectorSelect + ' option:selected').each(function() {
      incisos.push($(this).text());
    });
    $(selectorTextarea).val(incisos.length > 0 ? incisos.join('\n\n') : '');
  }
  $('#inciso_leve').on('change', function() {
    actualizarTextareaIncisos('#inciso_leve', '#txt_incisos_leve');
  });
  $('#inciso_grave').on('change', function() {
    actualizarTextareaIncisos('#inciso_grave', '#txt_incisos_grave');
  });
  $('#inciso_muygrave').on('change', function() {
    actualizarTextareaIncisos('#inciso_muygrave', '#txt_incisos_muygrave');
  });

  // Inicializar los textareas al cargar
  actualizarTextareaIncisos('#inciso_leve', '#txt_incisos_leve');
  actualizarTextareaIncisos('#inciso_grave', '#txt_incisos_grave');
  actualizarTextareaIncisos('#inciso_muygrave', '#txt_incisos_muygrave');

  // ==========================
  // 6. Limitar scroll de select2
  // ==========================
  $(document).on('select2:open', function() {
    $('.select2-results__options').css('max-height', '300px');
  });

  // ================================
  // 7. Ocultar alertas de éxito después de 4 segundos
  // ================================
  setTimeout(function() {
    $('.alert-success').fadeOut('slow');
  }, 4000);

  // ============================================
  // 8. Autollenado del campo Grado según Estudiante
  // ============================================
$('#id_alumno').on('select2:select', function (e) {
    console.log(e.params.data.element); // <-- Verás el <option> real
    let grado = $(e.params.data.element).data('grado');
    console.log('grado:', grado);
    $('#grado-display').val(grado || '');
    $('#id_grado').val(grado || '');
});

  // Al cargar la página, autollenar si hay uno seleccionado
  let $alumno = $('#id_alumno');
  let initialGrado = $alumno.find('option:selected').data('grado') || '';
  $('#grado-display').val(initialGrado);
  $('#id_grado').val(initialGrado);
});
