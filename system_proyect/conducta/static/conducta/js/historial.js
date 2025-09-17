document.addEventListener('DOMContentLoaded', function() {
    // Modal para detalles de ticket
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
});
