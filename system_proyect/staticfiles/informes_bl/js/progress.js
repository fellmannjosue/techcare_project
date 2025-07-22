document.addEventListener('DOMContentLoaded', function() {
  // Detectar cambios en el form y advertir al salir
  const form = document.querySelector('form');
  let isDirty = false;

  if (form) {
    form.addEventListener('input', () => {
      isDirty = true;
    });

    window.addEventListener('beforeunload', function(e) {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    });
  }

  // Inicializar DataTables si la tabla tiene id="entries-table"
  const table = document.getElementById('entries-table');
  if (table) {
    // Asegúrate de incluir DataTables en tu base.html o aquí
    $(table).DataTable({
      paging:   false,
      info:     false,
      searching:false,
      ordering:  true,
      columnDefs: [
        { orderable: false, targets: [1,2] }
      ]
    });
  }
});
