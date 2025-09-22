document.addEventListener('DOMContentLoaded', function() {
    // ------ SELECTORES ------
    const statusForm = document.getElementById('form-status-ticket');
    const statusSelect = document.getElementById('chat-status-select');
    const commentsInput = document.getElementById('ticket-comments');
    const badgeStatus = document.getElementById('badge-status');
    const chatDiv = document.getElementById('chat-mensajes');
    const form = document.getElementById('formComentario') || document.getElementById('formComentarioTech');

    // ------ OBTIENE TICKET ID DE LA URL ------
    const ticketId = window.location.pathname.match(/(\d+)/)[0];

    // ------ FUNCIONES ------
    function scrollChatToBottom() {
        if (chatDiv) {
            chatDiv.scrollTop = chatDiv.scrollHeight;
        }
    }

    // Cargar mensajes chat AJAX
    function cargarMensajes() {
        fetch(`/tickets/ticket_comments/ajax/${ticketId}/`, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(resp => resp.json())
        .then(res => {
            chatDiv.innerHTML = res.html;
            scrollChatToBottom();
        });
    }

    // Obtener status y comentarios generales en tiempo real
    function getTicketStatus() {
        fetch(`/tickets/ticket_status_get_ajax/${ticketId}/`, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(resp => resp.json())
        .then(res => {
            if (statusSelect && res.status) {
                statusSelect.value = res.status;
            }
            if (badgeStatus && res.status) {
                badgeStatus.innerText = res.status;
                // Cambia color según status
                let color = "bg-secondary";
                if (res.status === "Pendiente") color = "bg-warning text-dark";
                if (res.status === "En Proceso") color = "bg-info text-dark";
                if (res.status === "Resuelto") color = "bg-success";
                badgeStatus.className = `badge ${color}`;
            }
            // Sincroniza comentarios generales
            if (commentsInput && res.comments !== undefined) {
                commentsInput.value = res.comments;
            }
            // Deshabilitar chat si resuelto (solo para usuarios normales)
            if (res.status === "Resuelto") {
                if (form) {
                    let textarea = form.querySelector('textarea, [name="mensaje"]');
                    let boton = form.querySelector('button[type="submit"]');
                    if (textarea) textarea.disabled = true;
                    if (boton) {
                        boton.disabled = true;
                        boton.innerText = "Ticket cerrado";
                    }
                }
                if (statusForm) {
                    let btnStatus = statusForm.querySelector('button[type="submit"]');
                    if (btnStatus) btnStatus.disabled = true;
                }
            } else {
                if (form) {
                    let textarea = form.querySelector('textarea, [name="mensaje"]');
                    let boton = form.querySelector('button[type="submit"]');
                    if (textarea) textarea.disabled = false;
                    if (boton) {
                        boton.disabled = false;
                        boton.innerText = "Enviar";
                    }
                }
                if (statusForm) {
                    let btnStatus = statusForm.querySelector('button[type="submit"]');
                    if (btnStatus) btnStatus.disabled = false;
                }
            }
        });
    }

    // ------ AUTOSYNC ------
    setInterval(cargarMensajes, 2000);
    setInterval(getTicketStatus, 2000);
    cargarMensajes();
    getTicketStatus();

    // ------ ACTUALIZAR STATUS AJAX ------
    if (statusForm && statusSelect) {
        statusForm.addEventListener('submit', function(e) {
            e.preventDefault();
            fetch(`/tickets/ticket_status_update_ajax/${ticketId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams({
                    status: statusSelect.value,
                    comments: commentsInput ? commentsInput.value : ""
                })
            })
            .then(resp => resp.json())
            .then(res => {
                if (res.ok) {
                    Swal.fire({
                        toast: true,
                        position: 'top-end',
                        timer: 1400,
                        showConfirmButton: false,
                        icon: 'success',
                        title: `Estado actualizado a "${statusSelect.value}"`
                    });
                    getTicketStatus();
                } else {
                    Swal.fire('Error', res.error || 'No se pudo actualizar el estado.', 'error');
                }
            });
        });
    }

    // ------ ENVÍO DE COMENTARIO CHAT ------
    if (form) {
        form.addEventListener('submit', function(e){
            e.preventDefault();
            // Prevención si el ticket está cerrado
            if (statusSelect && statusSelect.value === "Resuelto") {
                Swal.fire('Ticket Cerrado', 'No se pueden agregar comentarios a un ticket resuelto.', 'info');
                return;
            }
            var data = new FormData(form);
            fetch(window.location.pathname, {
                method: 'POST',
                body: data,
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            })
            .then(resp => resp.json())
            .then(res => {
                if(res.ok) {
                    form.reset();
                    cargarMensajes();
                    Swal.fire({
                        icon: 'success',
                        title: 'Comentario enviado',
                        timer: 1200,
                        showConfirmButton: false
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: res.error || 'No se pudo enviar el comentario.'
                    });
                }
            }).catch(() => {
                Swal.fire('Error', 'No se pudo enviar el comentario. Intenta de nuevo.', 'error');
            });
        });
    }
});
