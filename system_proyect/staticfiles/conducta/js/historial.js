document.addEventListener('DOMContentLoaded', function() {
    // MODAL DE DETALLE DE TICKET AL CLIC EN ID (NO CAMBIA NADA)
    document.querySelectorAll('.link-ticket').forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            let id = this.dataset.ticketId;
            let nombre = this.dataset.name;
            let email = this.dataset.email;
            let descripcion = this.dataset.description;
            let status = this.dataset.status;
            let fecha = this.dataset.fecha;
            let adjunto = this.dataset.adjunto;

            Swal.fire({
                title: `<span style="color:#1967d2; font-weight:bold;">${id}</span>`,
                html: `
                  <div style="text-align:left; font-size:16px;">
                    <b>Nombre:</b> ${nombre}<br>
                    <b>Correo:</b> ${email}<br>
                    <b>Fecha:</b> ${fecha}<br>
                    <b>Status:</b> <span class="badge bg-info text-dark">${status}</span><br>
                    <b>Adjunto:</b> ${
                      adjunto
                        ? `<a href="${adjunto}" target="_blank" class="btn btn-sm btn-outline-secondary">Ver archivo</a>`
                        : '<span class="text-muted">No</span>'
                    }<br>
                    <b>Descripción:</b><br>
                    <textarea class="form-control" rows="5" readonly style="resize:none;">${descripcion}</textarea>
                  </div>
                `,
                showCloseButton: true,
                showConfirmButton: false,
                width: 440,
                customClass: {
                    popup: 'swal2-border-radius'
                }
            });
        });
    });

    // MODAL DE CONFIRMACIÓN AL CLIC EN "CHAT"
    document.querySelectorAll('.btn-chat').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            let ticketId = btn.dataset.ticketId;
            let nombre = btn.dataset.nombre || 'Usuario';

            Swal.fire({
                title: '¿Deseas iniciar el chat con soporte técnico?',
                html: `<b>${nombre}</b>, te estás comunicando con el soporte técnico.<br>Por favor, espera a ser atendido.`,
                icon: 'info',
                showCancelButton: true,
                confirmButtonText: 'Sí, iniciar chat',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    // RUTA CORRECTA Y ABSOLUTA
                    // Soporta si el sistema está en /tickets/ o raíz
                    let base = window.location.origin;
                    // Si tu historial de tickets está en /conducta/historial_maestro/
                    // Esto va a /tickets/ticket/xx/comentarios/
                   window.location.href = `/tickets/ticket/${ticketId}/comentarios/`;
                } else {
                    Swal.fire({
                        title: 'Chat no iniciado',
                        text: 'Pronto soporte técnico se comunicará contigo. Este pendiente de su correo.',
                        icon: 'warning',
                        confirmButtonText: 'OK'
                    });
                }
            });
        });
    });
});
