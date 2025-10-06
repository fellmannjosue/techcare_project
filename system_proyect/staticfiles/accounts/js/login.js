document.addEventListener('DOMContentLoaded', function() {
    const pwdInput = document.getElementById('password');
    const eyeIcon = document.getElementById('eyeIcon');
    if (pwdInput && eyeIcon) {
        eyeIcon.addEventListener('click', function() {
            if (pwdInput.type === 'password') {
                pwdInput.type = 'text';
                eyeIcon.src = eyeIcon.src.replace('eye_closed.png', 'eye_open.png');
            } else {
                pwdInput.type = 'password';
                eyeIcon.src = eyeIcon.src.replace('eye_open.png', 'eye_closed.png');
            }
        });
    }

    // (Opcional) Desactiva el botón para evitar doble submit
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            const btn = loginForm.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = "Ingresando...";
            }
        });
    }
});
