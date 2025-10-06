// --- global.js: Notificaciones en tiempo real ---
const notifUrl = "/core/notificaciones/";
const marcarLeidasUrl = "/core/notificaciones/marcar-leidas/";

let notificacionesPrevias = new Set();

function playNotifSound() {
  try {
    document.getElementById('notifSound').play();
  } catch (e) {}
}

function mostrarBadge(count) {
  const badge = document.getElementById('badgeNotificaciones');
  if (!badge) return;
  if (count > 0) {
    badge.style.display = '';
    badge.textContent = count;
  } else {
    badge.style.display = 'none';
    badge.textContent = '';
  }
}

function renderNotificaciones(notis) {
  const lista = document.getElementById('listaNotificaciones');
  if (!lista) return;
  lista.innerHTML = '';
  if (notis.length === 0) {
    lista.innerHTML = '<li class="dropdown-item text-muted text-center">No hay notificaciones nuevas</li>';
    return;
  }
  notis.forEach(n => {
    const li = document.createElement('li');
    li.className = "dropdown-item";
    li.innerHTML = `
      <div>
        <span class="badge bg-${n.tipo === 'alerta' ? 'warning' : (n.tipo === 'error' ? 'danger' : (n.tipo === 'exito' ? 'success' : 'primary'))} me-2">&nbsp;</span>
        <strong>${n.mensaje}</strong>
        <div class="small text-muted">${n.fecha}</div>
      </div>
    `;
    lista.appendChild(li);
  });
  // Botón para marcar como leídas
  const liBtn = document.createElement('li');
  liBtn.innerHTML = `
    <button class="btn btn-sm btn-link w-100 text-center" id="marcarLeidasBtn">Marcar todas como leídas</button>
  `;
  lista.appendChild(liBtn);
  document.getElementById('marcarLeidasBtn').onclick = marcarTodasLeidas;
}

function marcarTodasLeidas() {
  fetch(notifUrl, { credentials: 'include' })
    .then(r => r.json())
    .then(data => {
      const ids = data.notificaciones.map(n => n.id);
      if (ids.length === 0) return;
      fetch(marcarLeidasUrl, {
        method: 'POST',
        credentials: 'include',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken()},
        body: JSON.stringify({ids: ids})
      }).then(() => {
        mostrarBadge(0);
        renderNotificaciones([]);
      });
    });
}

// Utilidad para CSRF (si usas Django)
function getCSRFToken() {
  let value = "; " + document.cookie;
  let parts = value.split("; csrftoken=");
  if (parts.length === 2) return parts.pop().split(";").shift();
}

// Polling cada 15 segundos (ajusta a gusto)
function cargarNotificaciones() {
  fetch(notifUrl, { credentials: 'include' })
    .then(r => r.json())
    .then(data => {
      const notis = data.notificaciones || [];
      mostrarBadge(notis.length);
      renderNotificaciones(notis);
      // Sonido solo si hay nuevas
      const idsActuales = new Set(notis.map(n => n.id));
      const nuevas = [...idsActuales].filter(x => !notificacionesPrevias.has(x));
      if (nuevas.length > 0) playNotifSound();
      notificacionesPrevias = idsActuales;
    });
}

setInterval(cargarNotificaciones, 15000);
document.addEventListener('DOMContentLoaded', cargarNotificaciones);
