// ===========================
//   JS UNIFICADO CONDUCTA + INFORMATIVO + PROGRESS REPORT
// ===========================

$(function () {

  // ===================================================
  // ============  PROGRESS REPORT - JS DINÁMICO  ======
  // ===================================================
  // Materias según tipo de grado
  const MATERIAS_PRIMARIA = [
    "Math", "Phonics", "Spelling", "Reading", "Language",
    "Science", "Español", "CCSS", "Asociadas"
  ];
  const MATERIAS_COLEGIO = [
    "Math", "Spelling", "Reading", "Language", "Science",
    "Español", "CCSS", "Cívica", "Asociadas"
  ];

  // Devuelve si el grado es primaria
  function esPrimaria(grado) {
    if (!grado) return false;
    return grado.toLowerCase().includes('primariabl') || grado.toLowerCase().includes('preescolar');
  }

  // Genera la tabla de materias
  function generarFilasTablaMaterias(grado) {
    let materias = esPrimaria(grado) ? MATERIAS_PRIMARIA : MATERIAS_COLEGIO;
    let html = '';
    materias.forEach(mat => {
      if (mat !== "Asociadas") {
        html += `
          <tr>
            <td><strong>${mat}</strong></td>
            <td>
              <input type="text" name="asignacion_${mat}" class="form-control" autocomplete="off">
            </td>
            <td>
              <input type="text" name="comentario_${mat}" class="form-control" autocomplete="off">
            </td>
          </tr>
        `;
      } else {
        html += `
          <tr id="fila-asociadas">
            <td><strong>Asociadas</strong></td>
            <td>
              <input type="text" name="asignacion_Asociadas[]" class="form-control input-asociadas" autocomplete="off">
            </td>
            <td class="d-flex align-items-center gap-2">
              <button type="button" class="btn btn-success btn-sm add-asociada me-2" title="Agregar otra fila">+</button>
              <input type="text" name="comentario_Asociadas[]" class="form-control input-asociadas flex-grow-1" autocomplete="off">
            </td>
          </tr>
        `;
      }
    });
    $("#tabla-materias-body").html(html);
  }

  // ========== Inicializar Progress Report ==========
  if ($('#id_alumno').length && $('#tabla-materias').length) {
    // --- ACTIVAR SELECT2 EN ALUMNO ---
    $('#id_alumno').select2({
      placeholder: "-- Selecciona un estudiante --",
      minimumResultsForSearch: 0,
      width: '100%',
      allowClear: true,
      dropdownParent: $('#id_alumno').parent()
    });

    // --- Inicializar la tabla y autollenar grado ---
    function setGradoProgress() {
      let grado = '';
      let select2Data = $('#id_alumno').select2('data');
      if (select2Data && select2Data[0] && select2Data[0].element) {
        grado = $(select2Data[0].element).data('grado') || '';
      } else {
        grado = $('#id_alumno').find('option:selected').data('grado') || '';
      }
      $('#grado-display').val(grado);
      $('#id_grado').val(grado);
      generarFilasTablaMaterias(grado);
    }
    setGradoProgress();
    $('#id_alumno').on('select2:select change', setGradoProgress);

    // --------- Lógica Asociadas (agregar/eliminar/Enter) -----------
    $('#tabla-materias').on('click', '.add-asociada', function () {
      let nuevaFila = `
        <tr class="asociada-extra">
          <td></td>
          <td><input type="text" name="asignacion_Asociadas[]" class="form-control input-asociadas" autocomplete="off"></td>
          <td class="d-flex align-items-center gap-2">
            <button type="button" class="btn btn-danger btn-sm remove-asociada me-2" title="Eliminar fila">&ndash;</button>
            <input type="text" name="comentario_Asociadas[]" class="form-control input-asociadas flex-grow-1" autocomplete="off">
          </td>
        </tr>
      `;
      $('#fila-asociadas').after(nuevaFila);
    });

    $('#tabla-materias').on('click', '.remove-asociada', function () {
      $(this).closest('tr').remove();
    });

    $('#tabla-materias').on('keydown', '.input-asociadas', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        $('#fila-asociadas .add-asociada').trigger('click');
        setTimeout(function () {
          $('#fila-asociadas').next('.asociada-extra').find('input[type="text"]').first().focus();
        }, 100);
      }
    });
  }

  // ===================================================
  // === JS PARA CONDUCTUAL E INFORMATIVO (Select2, Incisos, Autollenado Grado)
  // ===================================================
  // Aplica Select2 a campos de alumno y materia/docente si existen
  $('#id_alumno, #id_materia_docente').each(function () {
    if ($(this).length) {
      $(this).select2({
        placeholder: "-- Selecciona --",
        minimumResultsForSearch: 0,
        width: '100%',
        allowClear: true,
        dropdownParent: $(this).parent()
      });
    }
  });

  // Lógica de autollenado de grado en Conductual/Informativo (si existe campo grado)
  function setGradoUniversal() {
    let grado = '';
    let select2Data = $('#id_alumno').select2('data');
    if (select2Data && select2Data[0] && select2Data[0].element) {
      grado = $(select2Data[0].element).data('grado') || '';
    } else {
      grado = $('#id_alumno').find('option:selected').data('grado') || '';
    }
    $('#grado-display').val(grado);
    $('#id_grado').val(grado);
  }
  // Se ejecuta si existen campos de grado en el formulario
  if ($('#id_grado').length && $('#grado-display').length) {
    $('#id_alumno').on('select2:select change', setGradoUniversal);
    setGradoUniversal();
  }

  // ============= Select2 para incisos conductuales (si existen) ===========
  if ($('#inciso_leve').length) {
    $('#inciso_leve, #inciso_grave, #inciso_muygrave').select2({
      width: '100%',
      dropdownParent: $('.form-container').length ? $('.form-container') : $('body'),
      templateResult: function (data) {
        if (!data.id) return data.text;
        return $('<span style="white-space: pre-line;">' + data.text + '</span>');
      },
      templateSelection: function (data) {
        if (!data.id) return data.text;
        return $('<span style="white-space: pre-line;">' + data.text + '</span>');
      }
    });

    // Lógica checkboxes: activa/desactiva select y textarea
    function activarInciso(checkboxId, selectId, textareaId) {
      $(checkboxId).on('change', function () {
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

    if ($('#chk_leve').is(':checked')) $('#inciso_leve').prop('disabled', false);
    if ($('#chk_grave').is(':checked')) $('#inciso_grave').prop('disabled', false);
    if ($('#chk_muygrave').is(':checked')) $('#inciso_muygrave').prop('disabled', false);

    // Mostrar seleccionados en textarea
    function actualizarTextareaIncisos(selectorSelect, selectorTextarea) {
      var incisos = [];
      $(selectorSelect + ' option:selected').each(function () {
        incisos.push($(this).text());
      });
      $(selectorTextarea).val(incisos.length > 0 ? incisos.join('\n\n') : '');
    }
    $('#inciso_leve').on('change', function () { actualizarTextareaIncisos('#inciso_leve', '#txt_incisos_leve'); });
    $('#inciso_grave').on('change', function () { actualizarTextareaIncisos('#inciso_grave', '#txt_incisos_grave'); });
    $('#inciso_muygrave').on('change', function () { actualizarTextareaIncisos('#inciso_muygrave', '#txt_incisos_muygrave'); });

    // Inicializar textareas
    actualizarTextareaIncisos('#inciso_leve', '#txt_incisos_leve');
    actualizarTextareaIncisos('#inciso_grave', '#txt_incisos_grave');
    actualizarTextareaIncisos('#inciso_muygrave', '#txt_incisos_muygrave');
  }

  // ===============================
  // Limitar scroll de Select2 y auto-hide alerts
  // ===============================
  $(document).on('select2:open', function () {
    $('.select2-results__options').css('max-height', '300px');
  });

  setTimeout(function () {
    $('.alert-success').fadeOut('slow');
  }, 4000);

});
