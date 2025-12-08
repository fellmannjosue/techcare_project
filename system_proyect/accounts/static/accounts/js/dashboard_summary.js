/* ================================================================
   DASHBOARD SUMMARY (TechCare)
   ---------------------------------------------------------------
   Este script carga automáticamente los conteos de:
   - Tickets Pendientes
   - Citas Bilingüe
   - Citas Colegio/VOC
   - Coordinación BL
   - Coordinación Colegio
   - Reloj (Permisos / Compensatorio)

   Y los coloca en las tarjetas del Panel Principal.
   También prepara la apertura de modales (futuro).
   ================================================================ */

// ===============================
// 1. ENDPOINTS DEL BACKEND
// ===============================

const URL_TICKETS       = "/core/api/summary/tickets/";
const URL_CITAS_BL      = "/core/api/summary/citas_bl/";
const URL_CITAS_COL     = "/core/api/summary/citas_col/";
const URL_COORD_BL      = "/core/api/summary/coordinacion_bl/";
const URL_COORD_COL     = "/core/api/summary/coordinacion_col/";
const URL_RELOJ         = "/core/api/summary/reloj/";


// ===============================
// 2. ELEMENTOS HTML A ACTUALIZAR
// ===============================

// Cada tarjeta del dashboard tiene un <h3> donde mostramos el total
const cardTickets   = document.getElementById("card-tickets-total");
const cardCitasBL   = document.getElementById("card-citas-bl-total");
const cardCitasCOL  = document.getElementById("card-citas-col-total");
const cardCoordBL   = document.getElementById("card-coord-bl-total");
const cardCoordCOL  = document.getElementById("card-coord-col-total");
const cardReloj     = document.getElementById("card-reloj-total");

// Guardará los últimos datos (para abrir modales)
let resumenDatos = {
    tickets: [],
    citas_bl: [],
    citas_col: [],
    coord_bl: [],
    coord_col: [],
    reloj: [],
};


// ===============================
// 3. FUNCIÓN GENÉRICA PARA FETCH
// ===============================

async function cargarResumen(url) {
    try {
        const resp = await fetch(url);
        return await resp.json();
    } catch (err) {
        console.error("Error al obtener resumen:", url, err);
        return { total: 0, items: [] };
    }
}


// ===============================
// 4. CARGAR TODOS LOS MÓDULOS
// ===============================

async function actualizarDashboard() {

    // ---- Tickets ----
    const t = await cargarResumen(URL_TICKETS);
    if (cardTickets) cardTickets.innerText = t.total ?? 0;
    resumenDatos.tickets = t.items;

    // ---- Citas BL ----
    const bl = await cargarResumen(URL_CITAS_BL);
    if (cardCitasBL) cardCitasBL.innerText = bl.total ?? 0;
    resumenDatos.citas_bl = bl.items;

    // ---- Citas COL ----
    const col = await cargarResumen(URL_CITAS_COL);
    if (cardCitasCOL) cardCitasCOL.innerText = col.total ?? 0;
    resumenDatos.citas_col = col.items;

    // ---- Coordinación BL ----
    const cb = await cargarResumen(URL_COORD_BL);
    if (cardCoordBL) cardCoordBL.innerText = cb.total ?? 0;
    resumenDatos.coord_bl = cb.items;

    // ---- Coordinación Colegio ----
    const cc = await cargarResumen(URL_COORD_COL);
    if (cardCoordCOL) cardCoordCOL.innerText = cc.total ?? 0;
    resumenDatos.coord_col = cc.items;

    // ---- Reloj ----
    const r = await cargarResumen(URL_RELOJ);
    if (cardReloj) cardReloj.innerText = r.total ?? 0;
    resumenDatos.reloj = r.items;
}


// ===============================
// 5. AUTO-ACTUALIZACIÓN CADA 10s
// ===============================

document.addEventListener("DOMContentLoaded", actualizarDashboard);
setInterval(actualizarDashboard, 10000);


// ==================================================================
// 6. (FUTURO) FUNCIÓN PARA MOSTRAR MODALES AL CLICAR UNA TARJETA
// ==================================================================

window.abrirModalResumen = function (modulo) {

    let datos = resumenDatos[modulo] || [];

    let html = "";

    if (datos.length === 0) {
        html = "<p class='text-center text-muted'>No hay elementos recientes.</p>";
    } else {
        html = `
        <table class='table table-sm table-striped'>
            <thead>
                <tr>
                    <th>Título</th>
                    <th>Descripción</th>
                    <th>Fecha</th>
                </tr>
            </thead>
            <tbody>
                ${datos
                    .map(
                        (i) => `
                    <tr>
                        <td>${i.titulo}</td>
                        <td>${i.descripcion}</td>
                        <td>${i.fecha}</td>
                    </tr>`
                    )
                    .join("")}
            </tbody>
        </table>`;
    }

    Swal.fire({
        title: "Resumen del módulo",
        width: 700,
        html: html,
        confirmButtonText: "Cerrar",
    });
};
