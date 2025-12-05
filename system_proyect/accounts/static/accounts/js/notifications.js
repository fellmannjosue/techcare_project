const URL_NOTIS = "/core/api/notificaciones/";
const URL_MARCAR = "/core/api/notificaciones/marcar/";

let notisPrevias = new Set();

function playNotifSound() {
    let audio = document.getElementById("notifSound");
    if (audio) audio.play().catch(() => {});
}

function actualizarCampana(cantidad) {
    let badge = document.getElementById("badgeNotificaciones");
    if (!badge) return;

    if (cantidad > 0) {
        badge.style.display = "inline-block";
        badge.innerText = cantidad;
    } else {
        badge.style.display = "none";
    }
}

function cargarNotificaciones() {
    fetch(URL_NOTIS)
    .then(r => r.json())
    .then(data => {
        if (!data.ok) return;

        let notis = data.notificaciones || [];

        let idsActuales = new Set(notis.map(n => n.id));
        let nuevas = [...idsActuales].filter(id => !notisPrevias.has(id));

        if (nuevas.length > 0) playNotifSound();

        notisPrevias = idsActuales;

        actualizarCampana(notis.length);
    })
    .catch(err => console.error("Error notif:", err));
}

setInterval(cargarNotificaciones, 5000);
document.addEventListener("DOMContentLoaded", cargarNotificaciones);
