/* -------------------- 🔁 Redirección con mensaje -------------------- */
function redirectWithAlert(url, section) {
  Swal.fire({
    title: "Redirigiendo...",
    text: "Cargando " + section,
    icon: "info",
    showConfirmButton: false,
    timer: 1200,
  }).then(() => {
    window.location.href = url;
  });
}

/* -------------------- 🖨️ Botones de acción (Imprimir y Enviar) -------------------- */
function imprimirFormulario() {
  window.print();
}

function enviarPdfEmail() {
  Swal.fire("PDF Email", "Se enviará el PDF por correo", "success");
}

/* -------------------- 🏙️ Ciudad: actualizar ZIP y País automáticamente -------------------- */
const citySelect = document.getElementById("id_city");
const postalCodeInput = document.getElementById("postal_code");
const countryInput = document.getElementById("country");

citySelect.addEventListener("change", function () {
  const opt = this.options[this.selectedIndex];
  postalCodeInput.value = opt.getAttribute("data-zip") || "";
  countryInput.value = opt.getAttribute("data-country") || "";
});

document.addEventListener("DOMContentLoaded", function () {
  const opt = citySelect.options[citySelect.selectedIndex];
  postalCodeInput.value = opt.getAttribute("data-zip") || "";
  countryInput.value = opt.getAttribute("data-country") || "";
});

/* -------------------- 🧠 Botón Godfather: Activar/Desactivar -------------------- */
function toggleGodfatherButton() {
  const isSponsor = document.querySelector('[name="godfather"]').checked;
  document.getElementById("godfather_button").disabled = !isSponsor;
}

document.querySelector('[name="godfather"]').addEventListener("change", toggleGodfatherButton);

document.addEventListener("DOMContentLoaded", function () {
  toggleGodfatherButton();
});

/* -------------------- 🔍 Búsqueda de Sponsors: por Nombre, Apellido, ID -------------------- */
const searchName = document.getElementById("search_name");
const searchLastName = document.getElementById("search_lastname");
const searchId = document.getElementById("search_id");

searchName.addEventListener("change", () => loadSponsorData(searchName.value));
searchLastName.addEventListener("change", () => loadSponsorData(searchLastName.value));
searchId.addEventListener("change", () => loadSponsorData(searchId.value));

/* -------------------- 📥 Carga de datos del Sponsor desde la vista get_sponsor_data -------------------- */
function loadSponsorData(sponsorId) {
  if (!sponsorId) return;

  fetch(`/sponsors/get-sponsor-data/?id=${sponsorId}`)
    .then((resp) => resp.json())
    .then((data) => {
      if (data.error) {
        Swal.fire("Error", data.error, "error");
        return;
      }

      // TEXTOS Y SELECTS
      document.getElementById("id_title").value = data.title_id || "";
      document.getElementById("id_directed").value = data.directed_id || "";
      document.getElementById("id_last_name_1").value = data.last_name_1 || "";
      document.getElementById("id_last_name_2").value = data.last_name_2 || "";
      document.getElementById("id_first_name_1").value = data.first_name_1 || "";
      document.getElementById("id_first_name_2").value = data.first_name_2 || "";
      document.getElementById("id_contact").value = data.contact || "";
      document.getElementById("id_annex").value = data.annex || "";
      document.getElementById("id_address").value = data.address || "";
      document.getElementById("id_street").value = data.street || "";
      document.getElementById("id_email").value = data.email || "";
      document.getElementById("id_email_2").value = data.email_2 || "";
      document.getElementById("id_email_3").value = data.email_3 || "";
      document.getElementById("id_phone_1").value = data.phone_1 || "";
      document.getElementById("id_phone_2").value = data.phone_2 || "";
      document.getElementById("id_fax").value = data.fax || "";
      document.getElementById("id_language").value = data.language || "";
      document.getElementById("id_profession").value = data.profession || "";
      document.getElementById("id_addressed_to").value = data.addressed_to || "";
      document.getElementById("id_addressed_to_2").value = data.addressed_to_2 || "";
      document.getElementById("id_gender").value = data.gender || "";
      document.getElementById("id_nationality").value = data.nationality || "";
      document.getElementById("id_civil_status").value = data.civil_status || "";
      document.getElementById("id_note_1").value = data.note_1 || "";
      document.getElementById("id_note_2").value = data.note_2 || "";
      document.getElementById("id_padrino_ch_d").value = data.padrino_ch_d || "";

      // FECHAS
      document.getElementById("id_visitor_date").value = data.visitor_date || "";
      document.getElementById("id_volunt_dep_date").value = data.volunt_dep_date || "";
      document.getElementById("id_first_contact").value = data.first_contact || "";
      document.getElementById("id_last_contact").value = data.last_contact || "";
      document.getElementById("id_date_of_birth").value = data.date_of_birth || "";
      document.getElementById("id_date_of_birth_2").value = data.date_of_birth_2 || "";

      // CHECKBOXES
      document.getElementById("id_free_union").checked = data.free_union;
      document.getElementById("id_report_email").checked = data.report_email;
      document.getElementById("id_only_email").checked = data.only_email;
      document.getElementById("id_only_easter_rep").checked = data.only_easter_rep;
      document.getElementById("id_financial_report").checked = data.financial_report;
      document.getElementById("id_visitor").checked = data.visitor;
      document.getElementById("id_godfather").checked = data.godfather;
      document.getElementById("id_sponsor").checked = data.sponsor;
      document.getElementById("id_member").checked = data.member;
      document.getElementById("id_former_volunteer").checked = data.former_volunteer;
      document.getElementById("id_no_correspondence").checked = data.no_correspondence;
      document.getElementById("id_deceased").checked = data.deceased;
      document.getElementById("id_deactivated").checked = data.deactivated;
      document.getElementById("id_expect_reaction").checked = data.expect_reaction;
      document.getElementById("id_bad_address").checked = data.bad_address;
      document.getElementById("id_private").checked = data.private;
      document.getElementById("id_deactivate_soon").checked = data.deactivate_soon;
      document.getElementById("id_recog_2010").checked = data.recog_2010;
      document.getElementById("id_recog_2020_blanket").checked = data.recog_2020_blanket;
      document.getElementById("id_recog_2020_plate").checked = data.recog_2020_plate;

      // CIUDAD, ZIP y PAÍS
      if (data.city_id) {
        citySelect.value = data.city_id;
        const changeEvt = new Event("change");
        citySelect.dispatchEvent(changeEvt);

        postalCodeInput.value = data.zip_code || "";
        countryInput.value = data.country || "";
      }
    })
    .catch((err) => {
      console.error(err);
      Swal.fire("Error", "Ocurrió un error al cargar el Sponsor", "error");
    });
}

