// Materias por tipo de grado
const MATERIAS_PRIMARIA = [
  "Math", "Phonics", "Spelling", "Reading", "Language", "Science", "Español", "CCSS", "Asociadas"
];
const MATERIAS_COLEGIO = [
  "Math", "Spelling", "Reading", "Language", "Science", "Español", "CCSS", "Cívica", "Asociadas"
];

// Devuelve si un grado es primaria
function esPrimaria(grado) {
  if (!grado) return false;
  return grado.toLowerCase().includes('primariabl');
}

// Genera filas según grado
function generarFilasTablaMaterias(grado, values = {}) {
  let materias = esPrimaria(grado) ? MATERIAS_PRIMARIA : MATERIAS_COLEGIO;
  let html = '';
  materias.forEach((mat, idx) => {
    if (mat !== "Asociadas") {
      html += `
        <tr>
          <td><strong>${mat}</strong></td>
          <td><input type="text" name="asignacion_${mat}[]" class="form-control" autocomplete="off"></td>
          <td><input type="text" name="comentario_${mat}[]" class="form-control" autocomplete="off"></td>
        </tr>
      `;
    } else {
      // Solo una fila para "Asociadas", con botón +
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

// Evento para actualizar grado
$('#id_alumno').on('change', function () {
  let grado = $(this).find('option:selected').data('grado') || '';
  $('#grado-display').val(grado);
  $('#id_grado').val(grado);
  generarFilasTablaMaterias(grado);
});

// Inicializar tabla al cargar si hay alumno seleccionado
$(document).ready(function () {
  let $alumno = $('#id_alumno');
  let initialGrado = $alumno.find('option:selected').data('grado') || '';
  $('#grado-display').val(initialGrado);
  $('#id_grado').val(initialGrado);
  if (initialGrado) generarFilasTablaMaterias(initialGrado);
});

// Delegar evento para agregar más filas de "Asociadas"
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

// Delegar evento para eliminar filas extra de "Asociadas"
$('#tabla-materias').on('click', '.remove-asociada', function () {
  $(this).closest('tr').remove();
});

// Enter en input de asociadas agrega nueva fila
$('#tabla-materias').on('keydown', '.input-asociadas', function (e) {
  if (e.key === 'Enter') {
    e.preventDefault();
    $('#fila-asociadas .add-asociada').trigger('click');
    // Focus en el nuevo input
    setTimeout(function () {
      $('#fila-asociadas').next('.asociada-extra').find('input[type="text"]').first().focus();
    }, 100);
  }
});
