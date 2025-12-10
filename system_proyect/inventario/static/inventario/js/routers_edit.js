$(document).ready(function () {

    $(document).on("click", ".editar-router", function () {
        let id = $(this).data("id");

        $("#modal-router-body").html(`
            <div class="text-center py-5">
                <div class="spinner-border text-primary"></div>
                <p class="mt-2">Cargando datos...</p>
            </div>
        `);

        $("#modalEditarRouter").modal("show");

        $.get(`/inventario/router/edit/${id}/`, function (html) {
            $("#modal-router-body").html(html);
        });
    });

    $(document).on("submit", "#form-edit-router", function (e) {
        e.preventDefault();

        let id = $("#router-id").val();

        $.post(`/inventario/router/edit/${id}/`, $(this).serialize(), function (resp) {
            resp.ok
                ? Swal.fire("Actualizado", "Router actualizado.", "success").then(() => location.reload())
                : Swal.fire("Error", "Revisa los datos ingresados.", "error");
        });
    });

    $(document).on("click", ".eliminar-router", function () {
        let id = $(this).data("id");

        Swal.fire({
            title: "¿Eliminar router?",
            icon: "warning",
            showCancelButton: true
        }).then((r) => {
            if (r.isConfirmed) {
                $.post(`/inventario/router/delete/${id}/`, function () {
                    Swal.fire("Eliminado", "Registro eliminado.", "success")
                        .then(() => location.reload());
                });
            }
        });
    });

});
