// ===========================
//  PROGRESS.JS — PROGRESS REPORT
// ===========================

// --- MATERIAS POR GRADO ---
const MATERIAS_PRIMARIA = [
  "Math", "Phonics", "Spelling", "Reading", "Language",
  "Science", "Español", "CCSS", "Asociadas"
];
const MATERIAS_COLEGIO = [
  "Math", "Spelling", "Reading", "Language", "Science",
  "Español", "CCSS", "Cívica", "Asociadas"
];

// --- DETERMINA SI ES PRIMARIA ---
function esPrimaria(grado) {
  if (!grado) return false;
  return grado.toLowerCase().includes('primariabl') || grado.toLowerCase().includes('preescolar');
}

// --- GENERA LA TABLA DE MATERIAS ---
function generarFilasTablaMaterias(grado, values = {}) {
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

// =========== INICIALIZAR ==============
$(document).ready(function () {
  // --- ACTIVAR SELECT2 EN ALUMNO ---
  $('#id_alumno').select2({
    placeholder: "-- Selecciona un estudiante --",
    minimumResultsForSearch: 0,    // SIEMPRE mostrar buscador
    width: '100%',
    allowClear: true,
    dropdownParent: $('#id_alumno').parent() // Previene bugs en modals
  });

  // --- Inicializar la tabla si ya hay alumno seleccionado ---
  let $alumno = $('#id_alumno');
  let initialGrado = $alumno.find('option:selected').data('grado') || '';
  $('#grado-display').val(initialGrado);
  $('#id_grado').val(initialGrado);
  if (initialGrado) generarFilasTablaMaterias(initialGrado);
});

// =========== CAMBIO DE ALUMNO ==========
$('#id_alumno').on('change', function () {
  let grado = $(this).find('option:selected').data('grado') || '';
  $('#grado-display').val(grado);
  $('#id_grado').val(grado);
  generarFilasTablaMaterias(grado);
});

// ========== ASOCIADAS: AGREGAR FILAS EXTRA ===========
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

// ========== ASOCIADAS: ELIMINAR FILA ===========
$('#tabla-materias').on('click', '.remove-asociada', function () {
  $(this).closest('tr').remove();
});

// ========== ASOCIADAS: ENTER CREA FILA ===========
$('#tabla-materias').on('keydown', '.input-asociadas', function (e) {
  if (e.key === 'Enter') {
    e.preventDefault();
    $('#fila-asociadas .add-asociada').trigger('click');
    setTimeout(function () {
      $('#fila-asociadas').next('.asociada-extra').find('input[type="text"]').first().focus();
    }, 100);
  }
});
