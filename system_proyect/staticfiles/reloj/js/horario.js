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

    // Enviar formulario de AGREGAR horario (por AJAX)
    $(document).on('submit', '#formAgregarHorario', function(e) {
        e.preventDefault();
        var $form = $(this);
        $.ajax({
            type: 'POST',
            url: $form.attr('action'),
            data: $form.serialize(),
            headers: { 'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val() },
            success: function(response){
                if (response.success) {
                    Swal.fire('¡Éxito!', 'Horario registrado correctamente.', 'success');
                    $('#agregarHorarioModal').modal('hide');
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    Swal.fire('Error', 'Revisa los datos del formulario.', 'error');
                    // Muestra errores de campos si los hay
                    if (response.errors) {
                        let errores = Object.values(response.errors).map(v => v.join(', ')).join('<br>');
                        Swal.fire('Error', errores, 'error');
                    }
                }
            },
            error: function(){
                Swal.fire('Error', 'No se pudo conectar al servidor.', 'error');
            }
        });
    });

    // Enviar formulario de EDITAR horario (si editas con AJAX)
    $(document).on('submit', '#formEditarHorario', function(e) {
        e.preventDefault();
        var $form = $(this);
        $.ajax({
            type: 'POST',
            url: $form.attr('action'),
            data: $form.serialize(),
            headers: { 'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val() },
            success: function(response){
                if (response.success) {
                    Swal.fire('¡Éxito!', 'Horario editado correctamente.', 'success');
                    $('#editarHorarioModal').modal('hide');
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    Swal.fire('Error', 'Revisa los datos del formulario.', 'error');
                    if (response.errors) {
                        let errores = Object.values(response.errors).map(v => v.join(', ')).join('<br>');
                        Swal.fire('Error', errores, 'error');
                    }
                }
            },
            error: function(){
                Swal.fire('Error', 'No se pudo conectar al servidor.', 'error');
            }
        });
    });

    // Autocompletar el campo ID Empleado al seleccionar nombre
    $(document).on('change', '#id_nombre_dropdown', function() {
        let id = $(this).val();
        $('#id_emp_code').val(id);
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
