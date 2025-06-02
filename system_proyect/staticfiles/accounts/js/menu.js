// static/accounts/js/menu.js

let lastTotal = 0;

function checkNotifications() {
  fetch(NOTIFICATIONS_URL)
    .then(r => r.json())
    .then(data => {
      const total = data.citas_pendientes + data.tickets_pendientes;
      const badge = document.querySelector('.notification-count');

      if (total > 0) {
        badge.textContent = total;
        badge.style.display = 'inline-block';

        if (total > lastTotal) {
          Swal.fire({
            title: '¡Tienes notificaciones nuevas!',
            text: `Citas: ${data.citas_pendientes}, Tickets: ${data.tickets_pendientes}`,
            icon: 'info',
            confirmButtonText: 'OK'
          });
        }
      } else {
        badge.style.display = 'none';
      }

      lastTotal = total;
    })
    .catch(console.error);
}

document.addEventListener('DOMContentLoaded', () => {
  // Ejecutar la primera comprobación inmediatamente
  checkNotifications();
  // Repetir cada 60 segundos (60000 ms)
  setInterval(checkNotifications, 60000);
});
