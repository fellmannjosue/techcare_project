 let lastTotal = 0;
        function checkNotifications() {
            fetch("{% url 'check_new_notifications' %}")
              .then(r => r.json())
              .then(data => {
                const total = data.citas_pendientes + data.tickets_pendientes;
                const el = document.querySelector('.notification-count');
                if (total > 0) {
                  el.textContent = total;
                  el.style.display = 'inline-block';
                  if (total > lastTotal) {
                    Swal.fire({
                      title: '¡Tienes notificaciones nuevas!',
                      text: `Citas: ${data.citas_pendientes}, Tickets: ${data.tickets_pendientes}`,
                      icon: 'info',
                      confirmButtonText: 'OK'
                    });
                  }
                } else {
                  el.style.display = 'none';
                }
                lastTotal = total;
              })
              .catch(console.error);
        }
        checkNotifications();
        setInterval(checkNotifications, 60000);
