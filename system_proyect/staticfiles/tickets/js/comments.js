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
  // ------ OBTIENE TICKET ID DE LA URL ------
  const ticketId = window.location.pathname.match(/(\d+)/)[0];

  // ------ FUNCIONES ------
  function scrollChatToBottom() {
    if (chatDiv) {
      chatDiv.scrollTop = chatDiv.scrollHeight;
    }
  }

  // Renderiza un mensaje instantáneo (para chat IA)
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
        </div>
        `;
  }

  // Cargar mensajes chat AJAX (solo para refresco)
  function cargarMensajes() {
    fetch(`/tickets/ticket_comments/ajax/${ticketId}/`, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((resp) => resp.json())
      .then((res) => {
        chatDiv.innerHTML = res.html;
        scrollChatToBottom();
      });
  }

  // Obtener status y comentarios generales en tiempo real
  function getTicketStatus() {
    fetch(`/tickets/ticket_status_get_ajax/${ticketId}/`, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((resp) => resp.json())
      .then((res) => {
        if (statusSelect && res.status) {
          statusSelect.value = res.status;
        }
        if (badgeStatus && res.status) {
          badgeStatus.innerText = res.status;
          // Cambia color según status
          let color = "bg-secondary";
          if (res.status === "Pendiente") color = "bg-warning text-dark";
          if (res.status === "En Proceso") color = "bg-info text-dark";
          if (res.status === "Resuelto") color = "bg-success";
          badgeStatus.className = `badge ${color}`;
        }
        if (commentsInput && res.comments !== undefined) {
          commentsInput.value = res.comments;
        }
        if (res.status === "Resuelto") {
          if (formIA) {
            let textarea = formIA.querySelector('textarea, [name="mensaje"]');
            let boton = formIA.querySelector('button[type="submit"]');
            if (textarea) textarea.disabled = true;
            if (boton) {
              boton.disabled = true;
              boton.innerText = "Ticket cerrado";
            }
          }
          if (form) {
            let textarea = form.querySelector('textarea, [name="mensaje"]');
            let boton = form.querySelector('button[type="submit"]');
            if (textarea) textarea.disabled = true;
            if (boton) {
              boton.disabled = true;
              boton.innerText = "Ticket cerrado";
            }
          }
          if (statusForm) {
            let btnStatus = statusForm.querySelector('button[type="submit"]');
            if (btnStatus) btnStatus.disabled = true;
          }
        } else {
          if (formIA) {
            let textarea = formIA.querySelector('textarea, [name="mensaje"]');
            let boton = formIA.querySelector('button[type="submit"]');
            if (textarea) textarea.disabled = false;
            if (boton) {
              boton.disabled = false;
              boton.innerText = "Preguntar a la IA";
            }
          }
          if (form) {
            let textarea = form.querySelector('textarea, [name="mensaje"]');
            let boton = form.querySelector('button[type="submit"]');
            if (textarea) textarea.disabled = false;
            if (boton) {
              boton.disabled = false;
              boton.innerText = "Enviar";
            }
          }
          if (statusForm) {
            let btnStatus = statusForm.querySelector('button[type="submit"]');
            if (btnStatus) btnStatus.disabled = false;
          }
        }
      });
  }

  // ------ AUTOSYNC ------
  setInterval(cargarMensajes, 2000);
  setInterval(getTicketStatus, 2000);
  cargarMensajes();
  getTicketStatus();

  // ------ ACTUALIZAR STATUS AJAX ------
  if (statusForm && statusSelect) {
    statusForm.addEventListener("submit", function (e) {
      e.preventDefault();
      fetch(`/tickets/ticket_status_update_ajax/${ticketId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
            .value,
          "X-Requested-With": "XMLHttpRequest",
        },
        body: new URLSearchParams({
          status: statusSelect.value,
          comments: commentsInput ? commentsInput.value : "",
        }),
      })
        .then((resp) => resp.json())
        .then((res) => {
          if (res.ok) {
            Swal.fire({
              toast: true,
              position: "top-end",
              timer: 1400,
              showConfirmButton: false,
              icon: "success",
              title: `Estado actualizado a "${statusSelect.value}"`,
            });
            getTicketStatus();
          } else {
            Swal.fire(
              "Error",
              res.error || "No se pudo actualizar el estado.",
              "error"
            );
          }
        });
    });
  }

  // ------ ENVÍO DE COMENTARIO CHAT (NORMAL) ------
  if (form && !formIA) {
    // Para los que usan solo el form normal
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      // Prevención si el ticket está cerrado
      if (statusSelect && statusSelect.value === "Resuelto") {
        Swal.fire(
          "Ticket Cerrado",
          "No se pueden agregar comentarios a un ticket resuelto.",
          "info"
        );
        return;
      }
      var data = new FormData(form);
      fetch(window.location.pathname, {
        method: "POST",
        body: data,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then((resp) => resp.json())
        .then((res) => {
          if (res.ok) {
            form.reset();
            cargarMensajes();
            Swal.fire({
              icon: "success",
              title: "Comentario enviado",
              timer: 1200,
              showConfirmButton: false,
            });
          } else {
            Swal.fire({
              icon: "error",
              title: "Error",
              text: res.error || "No se pudo enviar el comentario.",
            });
          }
        })
        .catch(() => {
          Swal.fire(
            "Error",
            "No se pudo enviar el comentario. Intenta de nuevo.",
            "error"
          );
        });
    });
  }

  // ------ ENVÍO DE COMENTARIO CHAT IA ------
  if (formIA) {
    formIA.addEventListener("submit", function (e) {
      e.preventDefault();
      const mensaje = formIA.querySelector("textarea").value.trim();
      if (!mensaje) return;

      fetch(`/tickets/ticket/${ticketId}/chat_ai/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": formIA.querySelector("[name=csrfmiddlewaretoken]")
            .value,
        },
        body: new URLSearchParams({ mensaje: mensaje }),
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.ok) {
            // Agrega mensaje usuario
            chatDiv.innerHTML += renderBubble(data.mensaje_usuario);
            // Agrega mensaje IA
            chatDiv.innerHTML += renderBubble(data.mensaje_ia);
            scrollChatToBottom();
            formIA.reset();
            if (iaOpciones) iaOpciones.style.display = "block";
          } else {
            Swal.fire(
              "Error",
              data.error || "No se pudo enviar el mensaje.",
              "error"
            );
          }
        })
        .catch((err) => {
          Swal.fire("Error", "Fallo de red o del servidor.", "error");
        });
    });
  }

  // ------ ESCALAR A TÉCNICO ------
  if (btnContactarTecnico) {
    btnContactarTecnico.addEventListener("click", function () {
      Swal.fire({
        icon: "info",
        title: "Notificar a un técnico humano",
        text: "Un técnico será notificado y dará seguimiento a tu ticket.",
        confirmButtonText: "OK",
      }).then(() => {
        location.reload(); // Por ahora, solo recarga para refrescar el chat
      });
    });
  }
});
