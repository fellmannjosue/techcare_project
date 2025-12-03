document.addEventListener("DOMContentLoaded", function () {
  // ---------- Lógica para mostrar/ocultar "Cargo" según área ----------
  const areaField = document.getElementById("id_area");
  const divCargo = document.getElementById("divCargo");
  function mostrarCargo() {
    if (!areaField) return;
    const area = areaField.value;
    if (area === "bilingue" || area === "colegio") {
      divCargo.style.display = "";
    } else {
      divCargo.style.display = "none";
      if (document.getElementById("id_cargo")) {
        document.getElementById("id_cargo").selectedIndex = 0;
      }
    }
  }
  if (areaField) {
    mostrarCargo();
    areaField.addEventListener("change", mostrarCargo);
  }

  // ---------- Modal de búsqueda de correos institucionales ----------
  const btnBuscarCorreo = document.getElementById("btnBuscarCorreo");
  const modal = new bootstrap.Modal(
    document.getElementById("modalBuscarCorreo")
  );
  const listaCorreos = document.getElementById("listaCorreos");
  const inputBuscarCorreo = document.getElementById("inputBuscarCorreo");
  const emailInput = document.getElementById("id_email");

  // Array de ejemplo: cámbialo por AJAX si lo deseas
  const correosDisponibles = [
    "acanales@ana-hn.org",
    "acarrillo@ana-hn.org",
    "acruz@ana-hn.org",
    "admin2@ana-hn.org",
    "admin3@ana-hn.org",
    "avalladares@ana-hn.org",
    "azuniga@ana-hn.org",
    "bespino@ana-hn.org",
    "cmatute@ana-hn.org",
    "coordinacion_bl@ana-hn.org",
    "coordinacion_col@ana-hn.org",
    "cvalle@ana-hn.org",
    "dcaceres@ana-hn.org",
    "dfigueroa@ana-hn.org",
    "dlopez@ana-hn.org",
    "druiz@ana-hn.org",
    "eestrada@ana-hn.org",
    "efellmann@ana-hn.org",
    "flicona@ana-hn.org",
    "glorenzo@ana-hn.org",
    "grivera@ana-hn.org",
    "gsaravia@ana-hn.org",
    "gvivas@ana-hn.org",
    "ialcerro@ana-hn.org",
    "jcantor@ana-hn.org",
    "jchirinos@ana-hn.org",
    "juandavidcanales2bachb@ana-hn.org",
    "jfellmann@ana-hn.org",
    "jrodriguez@ana-hn.org",
    "jvivas@ana-hn.org",
    "kescoto@ana-hn.org",
    "kespinoza@ana-hn.org",
    "kgarcia@ana-hn.org",
    "lchavez@ana-hn.org",
    "lflores@ana-hn.org",
    "llopez@ana-hn.org",
    "lvalladares@ana-hn.org",
    "mariafernandavalle2bacha@ana-hn.org",
    "malvarado@ana-hn.org",
    "mcarias@ana-hn.org",
    "mcastro@ana-hn.org",
    "mmedina@ana-hn.org",
    "mrodriguez@ana-hn.org",
    "ogonzalez@ana-hn.org",
    "posorto@ana-hn.org",
    "pserrano@ana-hn.org",
    "rdiaz@ana-hn.org",
    "rflores@ana-hn.org",
    "rlagos@ana-hn.org",
    "rmercado@ana-hn.org",
    "rsanchez@ana-hn.org",
    "sbarrientos@ana-hn.org",
    "smidence@ana-hn.org",
    "spadillas@ana-hn.org",
    "tzuniga@ana-hn.org",
    "vfigueroa@ana-hn.org",
    "yzavala@ana-hn.org",
  ];

  function filtrarCorreos() {
    const filtro = inputBuscarCorreo.value.toLowerCase();
    listaCorreos.innerHTML = "";
    let encontrados = 0;
    correosDisponibles.forEach((correo) => {
      if (correo.toLowerCase().includes(filtro)) {
        const li = document.createElement("li");
        li.classList.add("list-group-item");
        li.textContent = correo;
        li.onclick = function () {
          emailInput.value = correo;
          modal.hide();
        };
        listaCorreos.appendChild(li);
        encontrados++;
      }
    });
    if (encontrados === 0) {
      const li = document.createElement("li");
      li.classList.add("list-group-item", "disabled");
      li.textContent = "No se encontraron correos";
      listaCorreos.appendChild(li);
    }
  }

  if (btnBuscarCorreo) {
    btnBuscarCorreo.addEventListener("click", function () {
      inputBuscarCorreo.value = "";
      filtrarCorreos();
      modal.show();
    });
  }

  if (inputBuscarCorreo) {
    inputBuscarCorreo.addEventListener("input", filtrarCorreos);
  }
});
