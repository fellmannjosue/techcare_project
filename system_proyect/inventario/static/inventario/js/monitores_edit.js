$(document).ready(function () {

    $(document).on("click", ".editar-monitor", function () {
        let id = $(this).data("id");

        $("#modal-monitor-body").html(`
            <div class="text-center py-5">
                <div class="spinner-border text-primary"></div>
                <p class="mt-2">Cargando datos...</p>
            </div>
        `);

        $("#modalEditarMonitor").modal("show");

        $.get(`/inventario/monitor/edit/${id}/`, function (html) {
            $("#modal-monitor-body").html(html);
        });
    });

    $(document).on("submit", "#form-edit-monitor", function (e) {
        e.preventDefault();

        let id = $("#monitor-id").val();

        $.post(`/inventario/monitor/edit/${id}/`, $(this).serialize(), function (resp) {
            resp.ok
                ? Swal.fire("Actualizado", "Monitor actualizado.", "success").then(() => location.reload())
                : Swal.fire("Error", "Corrige los datos.", "error");
        });
    });

    $(document).on("click", ".eliminar-monitor", function () {
        let id = $(this).data("id");

        Swal.fire({
            title: "¿Eliminar monitor?",
            icon: "warning",
            showCancelButton: true
        }).then((r) => {
            if (r.isConfirmed) {
                $.post(`/inventario/monitor/delete/${id}/`, function () {
                    Swal.fire("Eliminado", "Registro eliminado.", "success")
                        .then(() => location.reload());
                });
            }
        });
    });

});
