// static/reloj/horarios_list.js

document.addEventListener('DOMContentLoaded', function () {
    // Inicializa DataTable si la tabla existe
    if (window.jQuery && $('#tablaHorarios').length) {
        $('#tablaHorarios').DataTable({
            language: {
                "lengthMenu": "Mostrar _MENU_ registros",
                "zeroRecords": "No hay registros",
                "info": "Mostrando _START_ a _END_ de _TOTAL_",
                "infoEmpty": "No hay registros disponibles",
                "infoFiltered": "(filtrado de _MAX_ registros totales)",
                "search": "Buscar:",
                "paginate": {
                    "first": "Primero",
                    "last": "Último",
                    "next": "Siguiente",
                    "previous": "Anterior"
                }
            }
        });
    }

    // Modal AJAX para edición
    $('#editarHorarioModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var horarioId = button.data('id');
        var modal = $(this);
        if (horarioId && window.horarios_edit_url) {
            $.get(window.horarios_edit_url.replace('99999', horarioId), function (data) {
                modal.find('#modalHorarioContent').html(data);
            });
        }
    });

    // Mensajes Django (SweetAlert2)
    if (window.django_messages && window.django_messages.length > 0) {
        Swal.fire({
            icon: 'success',
            title: '¡Listo!',
            text: window.django_messages[0],
            timer: 1800,
            showConfirmButton: false
        });
    }
});
