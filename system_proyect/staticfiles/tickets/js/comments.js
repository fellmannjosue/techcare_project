document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('formComentario') || document.getElementById('formComentarioTech');
    const chatDiv = document.getElementById('chat-mensajes');
    // Detectar el ticket ID desde la URL actual (funciona con /ticket/<id>/comentarios/)
    const ticketId = window.location.pathname.match(/(\d+)/)[0];

    function scrollChatToBottom() {
        if (chatDiv) {
            chatDiv.scrollTop = chatDiv.scrollHeight;
        }
    }

    // AJAX para cargar mensajes
    function cargarMensajes() {
        fetch(`/ticket_comments/ajax/${ticketId}/`, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(resp => resp.json())
        .then(res => {
            chatDiv.innerHTML = res.html;
            scrollChatToBottom();
        });
    }

    // Autorefresco cada 1 segundo
    setInterval(cargarMensajes, 1000);
    // Primera carga al abrir
    cargarMensajes();

    // AJAX para enviar comentario
    if (form) {
        form.addEventListener('submit', function(e){
            e.preventDefault();
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
                        text: res.mensaje,
                        confirmButtonText: 'OK',
                        allowOutsideClick: false
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: res.error || 'No se pudo enviar el comentario.',
                        confirmButtonText: 'Cerrar'
                    });
                }
            }).catch(err => {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo enviar el comentario. Intenta de nuevo.',
                    confirmButtonText: 'OK'
                });
            });
        });
    }
});
