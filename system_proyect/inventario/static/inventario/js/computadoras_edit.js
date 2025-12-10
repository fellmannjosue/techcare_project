$(document).ready(function () {

    // Abrir modal de edición
    $(document).on("click", ".editar-computadora", function () {
        let id = $(this).data("id");

        $("#modal-computadora-body").html(`
            <div class="text-center py-5">
                <div class="spinner-border text-primary"></div>
                <p class="mt-2">Cargando datos...</p>
            </div>
        `);

        $("#modalEditarComputadora").modal("show");

        $.get(`/inventario/computadora/edit/${id}/`, function (html) {
            $("#modal-computadora-body").html(html);
        });
    });

    // Guardar edición
    $(document).on("submit", "#form-edit-computadora", function (e) {
        e.preventDefault();

        let id = $("#computadora-id").val();
        let formData = $(this).serialize();

        $.post(`/inventario/computadora/edit/${id}/`, formData, function (resp) {
            if (resp.ok) {
                Swal.fire("Actualizado", "Los cambios fueron guardados.", "success")
                    .then(() => location.reload());
            } else {
                Swal.fire("Error", "Verifica los campos ingresados.", "error");
            }
        });
    });

    // Eliminar
    $(document).on("click", ".eliminar-computadora", function () {
        let id = $(this).data("id");

        Swal.fire({
            title: "¿Eliminar computadora?",
            text: "Esta acción no se puede deshacer.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar"
        }).then((res) => {
            if (res.isConfirmed) {
                $.post(`/inventario/computadora/delete/${id}/`, function (resp) {
                    if (resp.ok) {
                        Swal.fire("Eliminado", "Registro eliminado.", "success")
                            .then(() => location.reload());
                    }
                });
            }
        });
    });

});
