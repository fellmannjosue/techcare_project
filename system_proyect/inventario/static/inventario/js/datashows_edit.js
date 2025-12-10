$(document).ready(function () {

    $(document).on("click", ".editar-datashow", function () {
        let id = $(this).data("id");

        $("#modal-datashow-body").html(`
            <div class="text-center py-5">
                <div class="spinner-border text-primary"></div>
                <p class="mt-2">Cargando datos...</p>
            </div>
        `);

        $("#modalEditarDataShow").modal("show");

        $.get(`/inventario/datashow/edit/${id}/`, function (html) {
            $("#modal-datashow-body").html(html);
        });
    });

    $(document).on("submit", "#form-edit-datashow", function (e) {
        e.preventDefault();

        let id = $("#datashow-id").val();

        $.post(`/inventario/datashow/edit/${id}/`, $(this).serialize(), function (resp) {
            resp.ok
                ? Swal.fire("Actualizado", "DataShow actualizado.", "success").then(() => location.reload())
                : Swal.fire("Error", "Corrige los campos.", "error");
        });
    });

    $(document).on("click", ".eliminar-datashow", function () {
        let id = $(this).data("id");

        Swal.fire({
            title: "¿Eliminar DataShow?",
            icon: "warning",
            showCancelButton: true
        }).then((r) => {
            if (r.isConfirmed) {
                $.post(`/inventario/datashow/delete/${id}/`, function () {
                    Swal.fire("Eliminado", "Registro eliminado.", "success")
                        .then(() => location.reload());
                });
            }
        });
    });

});
