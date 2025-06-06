// static/enfermeria/js/historial.js

document.addEventListener('DOMContentLoaded', function () {
  // 1) Obtener referencias a los elementos del DOM
  const studentSelect    = document.getElementById('studentSelect');
  const historyContainer = document.getElementById('historyContainer');
  const historyBody      = document.getElementById('historyBody');

  // Si alguno no existe, detenemos la ejecución para evitar errores
  if (!studentSelect || !historyContainer || !historyBody) {
    console.error('historial.js: falta algún elemento del DOM (studentSelect, historyContainer o historyBody).');
    return;
  }

  // 2) Leemos la URL JSON desde data-url del <select>
  const fetchUrl = studentSelect.dataset.url || '';
  if (!fetchUrl) {
    console.error('historial.js: No se encontró data-url en #studentSelect');
    return;
  }

  // 3) Escuchamos el evento change en el dropdown
  studentSelect.addEventListener('change', function () {
    const student = this.value;

    // Ocultamos la tabla y limpiamos las filas previas
    historyContainer.style.display = 'none';
    historyBody.innerHTML = '';

    if (!student) {
      // Si no hay estudiante seleccionado, no hacemos fetch
      return;
    }

    // Montamos la URL completa con el parámetro student
    const url = fetchUrl + '?student=' + encodeURIComponent(student);

    // 4) Enviamos el fetch al servidor
    fetch(url, {
      credentials: 'same-origin'  // para enviar cookies de sesión si es necesario
    })
    .then(async (res) => {
      if (res.status === 204) {
        // No hay historial para este estudiante
        historyBody.innerHTML = `
          <tr>
            <td colspan="6" class="text-center py-3 text-muted">
              No hay registros de atención para este estudiante.
            </td>
          </tr>`;
        historyContainer.style.display = 'block';
        return;
      }

      if (!res.ok) {
        // Si la respuesta no es 200, intentamos leer el JSON de error
        let data = {};
        try {
          data = await res.json();
        } catch (e) {
          // no hacemos nada, data queda vacío
        }
        alert('Error: ' + (data.error || res.statusText || 'Error inesperado'));
        return;
      }

      // Convertimos la respuesta a un objeto JS
      let data;
      try {
        data = await res.json();
      } catch (e) {
        console.error('historial.js: fallo al parsear JSON', e);
        alert('Error: respuesta inválida del servidor.');
        return;
      }

      // data.history debe ser un array
      const lista = data.history;
      if (!Array.isArray(lista) || lista.length === 0) {
        historyBody.innerHTML = `
          <tr>
            <td colspan="6" class="text-center py-3 text-muted">
              No hay registros de atención para este estudiante.
            </td>
          </tr>`;
        historyContainer.style.display = 'block';
        return;
      }

      // 5) Recorremos el array y creamos una fila por cada registro
      lista.forEach((item, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${index + 1}</td>
          <td>${item.date_time || '-'}</td>
          <td>${item.grade     || '-'}</td>
          <td>${item.reason    || '-'}</td>
          <td>${item.treatment || '-'}</td>
          <td>${item.attendant || '-'}</td>
        `;
        historyBody.appendChild(row);
      });

      // Finalmente, mostramos la tabla
      historyContainer.style.display = 'block';
    })
    .catch(err => {
      console.error('historial.js: error de red', err);
      alert('Se produjo un error de red al cargar el historial médico.');
    });
  });
});
