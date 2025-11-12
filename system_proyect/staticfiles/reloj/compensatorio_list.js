function formatDetalle(d) {
  return `
    <div class="p-3 bg-light border rounded">
      <div><strong>Motivo:</strong> ${d.motivo || '—'}</div>
      <div><strong>Minutos registrados:</strong> ${d.minutos || '—'}</div>
      <div><strong>Creado:</strong> ${d.creado_en || '—'}</div>
      <div><strong>Estado:</strong> ${
        d.estado == "APPR" ? "Aprobado" :
        d.estado == "REJC" ? "Rechazado" : "Pendiente"
      }</div>
      <div><strong>Aprobado por:</strong> ${d.aprobador || '—'}</div>
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', function () {
  let table = $('#compensatorio-table').DataTable({
    paging: false,  // usa la paginación Django si tienes muchas filas
    ordering: true,
    info: false,
    language: { url: '//cdn.datatables.net/plug-ins/1.13.8/i18n/es-ES.json' },
    columnDefs: [{ orderable: false, targets: 0 }]
  });

  $('#compensatorio-table tbody').on('click', 'td.details-control', function () {
    let tr = $(this).closest('tr');
    let row = table.row(tr);

    let d = tr.data('detalle');
    if (typeof d === 'string') d = JSON.parse(d);

    if (row.child.isShown()) {
      row.child.hide();
      tr.removeClass('shown');
      $(this).find('i').removeClass('fa-caret-down').addClass('fa-caret-right');
    } else {
      row.child(formatDetalle(d)).show();
      tr.addClass('shown');
      $(this).find('i').removeClass('fa-caret-right').addClass('fa-caret-down');
    }
  });
});
