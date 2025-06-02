// static/citas_billingue/js/dashboard.js
document.addEventListener('DOMContentLoaded', () => {
  const deleteForms = document.querySelectorAll('.delete-form');

  deleteForms.forEach(form => {
    const btn = form.querySelector('.delete-btn');
    btn.addEventListener('click', () => {
      Swal.fire({
        title: '¿Estás seguro de eliminar esta cita?',
        text: "Esta acción no se puede deshacer.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      }).then((result) => {
        if (result.isConfirmed) {
          form.submit();
        }
      });
    });
  });
});
