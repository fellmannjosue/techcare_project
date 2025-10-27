document.addEventListener('DOMContentLoaded', function () {
    // ====== DataTable en listado ======
    if (window.jQuery && $('#tablaHorarios').length) {
        $('#tablaHorarios').DataTable({
            language: {
                lengthMenu: "Mostrar _MENU_ registros",
                zeroRecords: "No hay registros",
                info: "Mostrando _START_ a _END_ de _TOTAL_",
                infoEmpty: "No hay registros disponibles",
                infoFiltered: "(filtrado de _MAX_ registros totales)",
                search: "Buscar:",
                paginate: {
                    first: "Primero",
                    last: "Último",
                    next: "Siguiente",
                    previous: "Anterior"
                }
            }
        });
    }

    // ====== Helpers ======
    function syncEmpCodeAndLabel(ctx) {
        // ctx: root dentro del cual buscar (document o contenido del modal)
        const $ctx = ctx ? $(ctx) : $(document);
        const $sel = $ctx.find('#id_nombre_dropdown');
        const $id  = $ctx.find('#id_emp_code');
        const $lbl = $ctx.find('#selected-employee-label');

        if ($sel.length && $id.length) {
            $id.val($sel.val() || '');
        }
        if ($sel.length && $lbl.length) {
            const opt = $sel[0].options[$sel[0].selectedIndex];
            $lbl.text(opt ? opt.text : '—');
        }
    }

    // ====== Modal AJAX para edición ======
    $('#editarHorarioModal').on('show.bs.modal', function (event) {
        const button = $(event.relatedTarget);
        const horarioId = button.data('id');
        const modal = $(this);
        if (horarioId && window.horarios_edit_url) {
            $.get(window.horarios_edit_url.replace('99999', horarioId), function (html) {
                modal.find('#modalHorarioContent').html(html);

                // Sincroniza emp_code y label al cargar el formulario dentro del modal
                syncEmpCodeAndLabel(modal);

                // Delegado: cambio de empleado dentro del modal
                modal.off('change.empSel').on('change.empSel', '#id_nombre_dropdown', function(){
                    syncEmpCodeAndLabel(modal);
                });
            });
        }
    });

    // ====== Envío por AJAX (AGREGAR) ======
    $(document).on('submit', '#formAgregarHorario', function(e) {
        e.preventDefault();
        const $form = $(this);
        $.ajax({
            type: 'POST',
            url: $form.attr('action') || window.location.href,
            data: $form.serialize(),
            headers: { 'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val() },
            success: function(response){
                if (response && response.success) {
                    Swal.fire('¡Éxito!', 'Horario registrado correctamente.', 'success');
                    $('#agregarHorarioModal').modal('hide');
                    setTimeout(() => window.location.reload(), 800);
                } else {
                    const msg = (response && response.errors)
                        ? Object.values(response.errors).map(v => v.join(', ')).join('<br>')
                        : 'Revisa los datos del formulario.';
                    Swal.fire('Error', msg, 'error');
                }
            },
            error: function(){
                Swal.fire('Error', 'No se pudo conectar al servidor.', 'error');
            }
        });
    });

    // ====== Envío por AJAX (EDITAR) ======
    $(document).on('submit', '#formEditarHorario', function(e) {
        e.preventDefault();
        const $form = $(this);
        $.ajax({
            type: 'POST',
            url: $form.attr('action') || window.location.href,
            data: $form.serialize(),
            headers: { 'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val() },
            success: function(response){
                if (response && response.success) {
                    Swal.fire('¡Éxito!', 'Horario editado correctamente.', 'success');
                    $('#editarHorarioModal').modal('hide');
                    setTimeout(() => window.location.reload(), 800);
                } else {
                    const msg = (response && response.errors)
                        ? Object.values(response.errors).map(v => v.join(', ')).join('<br>')
                        : 'Revisa los datos del formulario.';
                    Swal.fire('Error', msg, 'error');
                }
            },
            error: function(){
                Swal.fire('Error', 'No se pudo conectar al servidor.', 'error');
            }
        });
    });

    // ====== Autocompletar emp_code + label (página normal o modal) ======
    $(document).on('change', '#id_nombre_dropdown', function() {
        syncEmpCodeAndLabel(document);
    });

    // Sincroniza al cargar (para vista de página completa)
    syncEmpCodeAndLabel(document);

    // ====== Mensajes Django (SweetAlert2) ======
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
