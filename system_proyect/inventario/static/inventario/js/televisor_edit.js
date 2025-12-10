$(document).ready(function () {

    $(document).on("click", ".editar-televisor", function () {
        let id = $(this).data("id");

        $("#modal-televisor-body").html(`
            <div class="text-center py-5">
                <div class="spinner-border text-primary"></div>
                <p class="mt-2">Cargando datos...</p>
            </div>
        `);

        $("#modalEditarTelevisor").modal("show");

        $.get(`/inventario/televisor/edit/${id}/`, function (html) {
            $("#modal-televisor-body").html(html);
        });
    });

    $(document).on("submit", "#form-edit-televisor", function (e) {
        e.preventDefault();

        let id = $("#televisor-id").val();
        let formData = $(this).serialize();

        $.post(`/inventario/televisor/edit/${id}/`, formData, function (resp) {
            if (resp.ok) {
                Swal.fire("Actualizado", "Televisor modificado correctamente.", "success")
                    .then(() => location.reload());
            }
        });
    });

    $(document).on("click", ".eliminar-televisor", function () {
        let id = $(this).data("id");

        Swal.fire({
            title: "¿Eliminar televisor?",
            icon: "warning",
            showCancelButton: true
        }).then((r) => {
            if (r.isConfirmed) {
                $.post(`/inventario/televisor/delete/${id}/`, function (resp) {
                    Swal.fire("Eliminado", "Registro eliminado.", "success")
                        .then(() => location.reload());
                });
            }
        });
    });

});
