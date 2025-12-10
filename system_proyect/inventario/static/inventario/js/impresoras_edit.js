$(document).ready(function () {

    $(document).on("click", ".editar-impresora", function () {
        let id = $(this).data("id");

        $("#modal-impresora-body").html(`
            <div class="text-center py-5">
                <div class="spinner-border text-primary"></div>
                <p class="mt-2">Cargando datos...</p>
            </div>
        `);

        $("#modalEditarImpresora").modal("show");

        $.get(`/inventario/impresora/edit/${id}/`, function (html) {
            $("#modal-impresora-body").html(html);
        });
    });

    $(document).on("submit", "#form-edit-impresora", function (e) {
        e.preventDefault();

        let id = $("#impresora-id").val();
        let formData = $(this).serialize();

        $.post(`/inventario/impresora/edit/${id}/`, formData, function (resp) {
            resp.ok
                ? Swal.fire("Actualizado", "Cambios guardados.", "success").then(() => location.reload())
                : Swal.fire("Error", "Corrige los campos.", "error");
        });
    });

    $(document).on("click", ".eliminar-impresora", function () {
        let id = $(this).data("id");

        Swal.fire({
            title: "¿Eliminar impresora?",
            icon: "warning",
            showCancelButton: true
        }).then((r) => {
            if (r.isConfirmed) {
                $.post(`/inventario/impresora/delete/${id}/`, function () {
                    Swal.fire("Eliminada", "Registro eliminado.", "success")
                        .then(() => location.reload());
                });
            }
        });
    });

});
