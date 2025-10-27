
// === Auto-Refresh reutilizable para páginas de reporte ===
// - Recarga cada 5 min (300000 ms) solo si la página está visible.
// - Tiene un interruptor "Auto-refresh" y un contador.
// - La preferencia se guarda en localStorage por ruta (pathname).

(function () {
  const FIVE_MIN = 300000; // 5 min
  const KEY = 'autoRefresh:' + location.pathname;

  let enabled = (localStorage.getItem(KEY) || 'on') === 'on';
  let timer = null;
  let nextAt = null;

  // UI: insertar switch + contador en un lugar visible
  function injectControls() {
    const host = document.querySelector('[data-autorefresh-host]') || document.body;
    if (!host) return;

    if (document.getElementById('autoRefreshWrap')) return; // ya existe

    const wrap = document.createElement('div');
    wrap.id = 'autoRefreshWrap';
    wrap.className = 'd-flex align-items-center gap-2';
    wrap.innerHTML = `
      <div class="form-check form-switch">
        <input class="form-check-input" type="checkbox" id="autoRefreshToggle">
        <label class="form-check-label" for="autoRefreshToggle">Auto-refresh (5 min)</label>
      </div>
      <span id="autoRefreshCountdown" class="badge bg-secondary"></span>
      <button id="forceRefreshBtn" class="btn btn-sm btn-outline-secondary">Actualizar</button>
    `;
    host.appendChild(wrap);

    document.getElementById('autoRefreshToggle').checked = enabled;
    document.getElementById('autoRefreshToggle').addEventListener('change', (e) => {
      enabled = e.target.checked;
      localStorage.setItem(KEY, enabled ? 'on' : 'off');
      restart();
    });

    document.getElementById('forceRefreshBtn').addEventListener('click', () => {
      location.reload();
    });
  }

  function startTimer() {
    stopTimer();
    if (!enabled) {
      updateCountdown('-');
      return;
    }
    nextAt = Date.now() + FIVE_MIN;
    tick();
    timer = setInterval(tick, 1000);
  }

  function stopTimer() {
    if (timer) clearInterval(timer);
    timer = null;
  }

  function tick() {
    // pausa si la pestaña no está visible
    if (document.hidden) return;

    const msLeft = Math.max(0, nextAt - Date.now());
    const s = Math.ceil(msLeft / 1000);
    const m = Math.floor(s / 60);
    const ss = String(s % 60).padStart(2, '0');
    updateCountdown(`${m}:${ss}`);

    if (msLeft <= 0) {
      // Recarga conservando ?fecha_inicio=...&fecha_fin=...&q=...
      location.reload();
    }
  }

  function updateCountdown(text) {
    const el = document.getElementById('autoRefreshCountdown');
    if (el) el.textContent = text;
  }

  function restart() {
    if (enabled) startTimer(); else stopTimer();
  }

  // visibility: al volver a la pestaña, re-programa el siguiente refresh
  document.addEventListener('visibilitychange', () => {
    if (!enabled) return;
    if (!document.hidden) {
      nextAt = Date.now() + FIVE_MIN;
      tick();
    }
  });

  // init
  injectControls();
  restart();
})();