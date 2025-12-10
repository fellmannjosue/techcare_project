$(document).ready(function () {

    // ------------------------------------------------------------
    // 1. EVENTO: CLICK EN BOTÓN EDITAR
    // ------------------------------------------------------------
    $(document).on("click", ".editar-btn", function () {
        const pcID = $(this).data("id");
        const url = `/inventario/computadoras/edit-form/${pcID}/`;

        // Spinner de carga
        $("#modal-computadora-body").html(`
            <div class="text-center py-5">
              <div class="spinner-border text-primary"></div>
              <p class="mt-2">Cargando datos...</p>
            </div>
        `);

        // Llamada AJAX para traer el formulario
        $.get(url, function (response) {
            $("#modal-computadora-body").html(response);

            // Mostrar modal
            const modal = new bootstrap.Modal(
                document.getElementById("modalEditarComputadora")
            );
            modal.show();
        }).fail(function () {
            $("#modal-computadora-body").html(`
                <div class="alert alert-danger">
                    Error cargando formulario. Intente nuevamente.
                </div>
            `);
        });
    });


    // ------------------------------------------------------------
    // 2. EVENTO: SUBMIT DEL FORMULARIO EDITAR (AJAX POST)
    // ------------------------------------------------------------
    $(document).on("submit", "#formEditarComputadora", function (e) {
        e.preventDefault();

        const pcID = $("#computadora_id").val();
        const url = `/inventario/computadoras/edit/${pcID}/`;
        const formData = $(this).serialize();

        // Deshabilitar botón mientras se envía
        $("#btnSaveComputadora")
            .prop("disabled", true)
            .text("Guardando...");

        $.post(url, formData, function (response) {
            if (response === "OK") {
                // Recargar página para ver cambios
                location.reload();
            }
        })
        .fail(function () {
            alert("Hubo un error al guardar los cambios.");
        })
        .always(function () {
            $("#btnSaveComputadora")
                .prop("disabled", false)
                .text("Guardar Cambios");
        });
    });

});
