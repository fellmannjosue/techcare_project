function showSwal(message) {
  if (typeof Swal !== 'undefined') {
    Swal.fire(message);
  } else {
    alert(message);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (typeof GLOBAL_USERNAME !== 'undefined' && GLOBAL_USERNAME) {
    if (typeof SHOW_WELCOME !== 'undefined' && SHOW_WELCOME) {
      showSwal('¡Bienvenido ' + GLOBAL_USERNAME + '!');
    }
    if (document.querySelector('form')) {
      showSwal('Hola ' + GLOBAL_USERNAME + ', listo para registrar hoy');
    }
  }

  document.querySelectorAll('button[data-message]').forEach(btn => {
    btn.addEventListener('click', () => {
      showSwal(btn.dataset.message);
    });
  });
});

let inactivityTimer;
function resetInactivityTimer() {
  clearTimeout(inactivityTimer);
  inactivityTimer = setTimeout(() => {
    if (typeof LOGOUT_URL !== 'undefined') {
      fetch(LOGOUT_URL).then(() => location.reload());
    }
  }, 600000);
}
['mousemove', 'keydown', 'scroll', 'touchstart', 'click'].forEach(evt => {
  document.addEventListener(evt, resetInactivityTimer);
});
resetInactivityTimer();
