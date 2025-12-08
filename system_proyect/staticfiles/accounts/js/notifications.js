// =======================================
// CONFIG
// =======================================
const URL_NOTIS = "/core/api/notificaciones/";
const URL_MARCAR = "/core/api/notificaciones/marcar/";

let notisPrevias = new Set();
let dropdownAbierto = false;

// =======================================
// Reproducir sonido
// =======================================
function playNotifSound() {
    let audio = document.getElementById("notifSound");
    if (audio) {
        audio.volume = 0.5;
        audio.play().catch(() => {});
    }
}

// =======================================
// Actualiza el número del badge
// =======================================
function actualizarCampana(cantidad) {
    let badge = document.getElementById("badgeNotificaciones");
    if (!badge) return;

    if (cantidad > 0) {
        badge.classList.remove("d-none");
        badge.style.display = "inline-block";
        badge.innerText = cantidad;
    } else {
        badge.classList.add("d-none");
        badge.style.display = "none";
    }
}

// =======================================
// Renderiza notificaciones en el dropdown
// =======================================
function renderizarLista(notis) {
    let lista = document.getElementById("listaNotificaciones");
    if (!lista) return;

    lista.innerHTML = "";

    if (notis.length === 0) {
        lista.innerHTML = `
            <li class="p-3 text-center text-muted">
                <i class="fa-regular fa-bell-slash fa-lg mb-2"></i><br>
                Sin notificaciones
            </li>`;
        return;
    }

    notis.forEach(n => {
        let item = document.createElement("li");

        item.innerHTML = `
            <div class="p-2 border-bottom small">
                <div class="fw-bold text-primary">
                    ${n.modulo.toUpperCase()}
                </div>
                <div>${n.mensaje}</div>
                <div class="text-muted" style="font-size: 11px;">
                    ${n.fecha}
                </div>
            </div>
        `;

        lista.appendChild(item);
    });
}

// =======================================
// Cargar notificaciones del backend
// =======================================
function cargarNotificaciones() {
    fetch(URL_NOTIS)
    .then(r => r.json())
    .then(data => {
        if (!data.ok) return;

        let notis = data.notificaciones || [];

        // IDs actuales
        let idsActuales = new Set(notis.map(n => n.id));

        // Detectar nuevas notificaciones
        let nuevas = [...idsActuales].filter(id => !notisPrevias.has(id));
        if (nuevas.length > 0 && notisPrevias.size > 0) {
            playNotifSound();
        }

        // Actualizar set
        notisPrevias = idsActuales;

        // Actualizar campanita
        actualizarCampana(notis.length);

        // Si el dropdown está abierto → renderizar
        if (dropdownAbierto) {
            renderizarLista(notis);
        }
    })
    .catch(err => console.error("Error al cargar notificaciones:", err));
}

// =======================================
// Marcar notificaciones como leídas
// =======================================
function marcarNotificacionesLeidas() {
    fetch(URL_MARCAR, { method: "POST", headers: { "X-CSRFToken": getCSRFToken() }})
    .then(r => r.json())
    .then(() => {
        actualizarCampana(0);
        notisPrevias.clear();
    })
    .catch(err => console.error("Error al marcar leídas:", err));
}

// =======================================
// Detectar apertura del dropdown
// =======================================
document.addEventListener("DOMContentLoaded", () => {
    let dropdown = document.getElementById("notifDropdownToggle");

    if (dropdown) {
        dropdown.addEventListener("click", () => {
            dropdownAbierto = true;

            // Cargar inmediatamente lo más reciente
            fetch(URL_NOTIS)
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    renderizarLista(data.notificaciones);
                    marcarNotificacionesLeidas();
                }
            });
        });
    }

    cargarNotificaciones();
});

// =======================================
// Ejecución cada 5 segundos
// =======================================
setInterval(cargarNotificaciones, 5000);

// =======================================
// Extra: obtener CSRF token
// =======================================
function getCSRFToken() {
    let cookieValue = null;
    const name = 'csrftoken';
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let c of cookies) {
            c = c.trim();
            if (c.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(c.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
