document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('formComentarioTech');
    if (!form) return;

    form.addEventListener('submit', function(e){
        e.preventDefault();
        const data = new FormData(form);

        fetch(window.location.pathname, {
            method: 'POST',
            body: data,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
                // Si necesitas CSRF, agrega aquí: 'X-CSRFToken': csrf_token
            }
        })
        .then(resp => resp.json())
        .then(res => {
            if(res.ok) {
                Swal.fire({
                    icon: 'success',
                    title: 'Comentario enviado',
                    text: res.mensaje || '¡Comentario enviado correctamente!',
                    confirmButtonText: 'OK',
                    allowOutsideClick: false
                }).then(() => {
                    // Recarga la página para mostrar el comentario
                    location.reload();
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: res.error || 'No se pudo enviar el comentario. Revisa los campos e inténtalo de nuevo.',
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
});
