document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('formComentario');
    if (!form) return;

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
                Swal.fire({
                    icon: 'success',
                    title: 'Comentario enviado',
                    text: res.mensaje,
                    confirmButtonText: 'OK',
                    allowOutsideClick: false
                }).then(() => {
                    location.reload();
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
});
