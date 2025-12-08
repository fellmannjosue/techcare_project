document.addEventListener("DOMContentLoaded", function () {
  // ------ SELECTORES ------
  const statusForm = document.getElementById("form-status-ticket");
  const statusSelect = document.getElementById("chat-status-select");
  const commentsInput = document.getElementById("ticket-comments");
  const badgeStatus = document.getElementById("badge-status");
  const chatDiv = document.getElementById("chat-mensajes");
  const formIA = document.getElementById("formComentarioIA");
  const form =
    document.getElementById("formComentario") ||
    document.getElementById("formComentarioTech");
  const btnContactarTecnico = document.getElementById("btn-contactar-tecnico");
  const iaOpciones = document.getElementById("chat-ia-opciones");

  // ------ OBTIENE TICKET ID ------
  const ticketId = window.location.pathname.match(/(\d+)/)[0];

  // ------ SCROLL ------
  function scrollChatToBottom() {
    if (chatDiv) chatDiv.scrollTop = chatDiv.scrollHeight;
  }

  // Renderiza mensaje del chat
  function renderBubble(data) {
    let icon = "";
    let autor = "";
    let clase = "";

    if (data.tipo === "usuario") {
      icon = '<i class="bi bi-person-circle"></i>';
      autor = `<span class="fw-semibold">${data.autor}</span>`;
      clase = "mine";
    } else if (data.tipo === "ia") {
      icon = '<i class="bi bi-robot"></i>';
      autor = `<span class="fw-semibold text-success">IA TechCare</span>`;
      clase = "ia-bubble";
    } else if (data.tipo === "tecnico") {
      icon = '<i class="bi bi-tools"></i>';
      autor = `<span class="fw-semibold text-primary">Técnico</span>`;
      clase = "tecnico-bubble";
    }

    return `
        <div class="chat-bubble ${clase}">
            ${data.mensaje.replace(/\n/g, "<br>")}
            <div class="chat-meta">
                ${icon} ${autor}
                <span class="text-secondary">${data.fecha}</span>
            </div>
        </div>`;
  }

  // ------ Cargar mensajes chat ------
  function cargarMensajes() {
    fetch(`/tickets/ticket_comments/ajax/${ticketId}/`, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((resp) => resp.json())
      .then((res) => {
        chatDiv.innerHTML = res.html;
      });
  }

  // ------ Obtener estado ------
  function getTicketStatus() {
    fetch(`/tickets/ticket_status_get_ajax/${ticketId}/`, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((resp) => resp.json())
      .then((res) => {
        // Status badge
        if (statusSelect && res.status) statusSelect.value = res.status;

        if (badgeStatus && res.status) {
          badgeStatus.innerText = res.status;
          let color = "bg-secondary";
          if (res.status === "Pendiente") color = "bg-warning text-dark";
          if (res.status === "En Proceso") color = "bg-info text-dark";
          if (res.status === "Resuelto") color = "bg-success";
          badgeStatus.className = `badge ${color}`;
        }

        // Deshabilitar campos si resuelto
        if (res.status === "Resuelto") {
          if (formIA) disableFormIA();
          if (form) disableFormNormal();
        }
      });
  }

  function disableFormIA() {
    let textarea = formIA.querySelector("textarea");
    let boton = formIA.querySelector('button[type="submit"]');
    if (textarea) textarea.disabled = true;
    if (boton) {
      boton.disabled = true;
      boton.innerText = "Ticket cerrado";
    }
  }

  function disableFormNormal() {
    let textarea = form.querySelector("textarea");
    let boton = form.querySelector('button[type="submit"]');
    if (textarea) textarea.disabled = true;
    if (boton) {
      boton.disabled = true;
      boton.innerText = "Ticket cerrado";
    }
  }

  // ------ AUTOSYNC ------
  setInterval(cargarMensajes, 2000);
  setInterval(getTicketStatus, 2000);
  cargarMensajes();
  getTicketStatus();

  // ============================================================
  // 🔥 CHAT IA
  // ============================================================
  if (formIA) {
    formIA.addEventListener("submit", function (e) {
      e.preventDefault();
      const mensaje = formIA.querySelector("textarea").value.trim();
      if (!mensaje) return;

      fetch(`/tickets/ticket/${ticketId}/chat_ai/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": formIA.querySelector("[name=csrfmiddlewaretoken]").value,
        },
        body: new URLSearchParams({ mensaje: mensaje }),
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.ok) {
            chatDiv.innerHTML += renderBubble(data.mensaje_usuario);
            chatDiv.innerHTML += renderBubble(data.mensaje_ia);
            scrollChatToBottom();
            formIA.reset();
          } else {
            Swal.fire("Atención", data.error, "info");
          }
        })
        .catch(() => Swal.fire("Error", "Fallo en IA", "error"));
    });
  }

  // ============================================================
  // 🔥 BOTÓN "NO ME AYUDÓ, CONTACTAR TÉCNICO"
  // ============================================================
  if (btnContactarTecnico) {
    btnContactarTecnico.addEventListener("click", function () {
      Swal.fire({
        icon: "warning",
        title: "¿Deseas contactar a un técnico?",
        text: "La IA dejará de responder y un técnico humano continuará con tu ticket.",
        showCancelButton: true,
        confirmButtonText: "Sí, contactar técnico",
        cancelButtonText: "Cancelar",
      }).then((result) => {
        if (!result.isConfirmed) return;

        // 🔥 Enviar solicitud al backend
        fetch(`/tickets/ticket/${ticketId}/contactar_tecnico/`, {
          method: "POST",
          headers: {
            "X-CSRFToken":
              document.querySelector("[name=csrfmiddlewaretoken]").value,
          },
        })
          .then((resp) => resp.json())
          .then((res) => {
            if (res.ok) {
              // 🔥 Ocultar IA y bloquear su uso
              if (formIA) {
                disableFormIA();
                formIA.style.display = "none";
              }
              if (iaOpciones) iaOpciones.style.display = "none";

              // 🔥 Mostrar confirmación
              Swal.fire({
                icon: "success",
                title: "Un técnico fue notificado",
                text: "La IA ya no responderá más en este ticket.",
                confirmButtonText: "Entendido",
              });

              cargarMensajes();
              scrollChatToBottom();
            }
          });
      });
    });
  }
});
