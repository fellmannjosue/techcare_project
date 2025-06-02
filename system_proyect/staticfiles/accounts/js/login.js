// static/accounts/js/login.js

// Campo contraseña y ojo
const loginForm = document.getElementById('loginForm');
const loadingOverlay = document.getElementById('loadingOverlay');
const passwordField = document.getElementById('password');
const eyeIcon = document.getElementById('eyeIcon');

// Ruta absoluta a las imágenes del ojo
const EYE_OPENED_SRC = '/static/accounts/img/eye_opened.png';
const EYE_CLOSED_SRC = '/static/accounts/img/eye_closed.png';

/**
 * Mostrar el overlay de carga cuando se envía el formulario.
 * Hacemos un pequeño retraso para que se aprecie la animación.
 */
loginForm.addEventListener('submit', function (e) {
  e.preventDefault();                // prevenimos el submit inmediato
  loadingOverlay.classList.add('show');
  setTimeout(() => {
    loginForm.submit();             // finalmente enviamos el formulario
  }, 1500);
});

/**
 * Alterna el campo 'password' <-> 'text' y cambia el ícono.
 */
function togglePassword() {
  if (passwordField.type === 'password') {
    passwordField.type = 'text';
    eyeIcon.src = EYE_OPENED_SRC;
  } else {
    passwordField.type = 'password';
    eyeIcon.src = EYE_CLOSED_SRC;
  }
}
