// static/citas_billingue/js/select-date_bl.js
document.addEventListener('DOMContentLoaded', function () {
    const teacherId = document.getElementById('js-data').dataset.teacherId;
    const csrfToken = document.getElementById('js-data').dataset.csrfToken;
    const calendar = document.querySelector('#calendar tbody');
    const timeSlots = document.querySelector('#time-slots');
    const form = document.querySelector('#appointment-form');
    const today = new Date();
    const currentYear = today.getFullYear();
    const currentMonth = today.getMonth();
    generateCalendar(currentYear, currentMonth);

    function generateCalendar(year, month) {
        const monthNames = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"];
        document.getElementById("monthLabel").innerText = `${monthNames[month]} ${year}`;
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        let date = 1;
        calendar.innerHTML = '';
        for (let i = 0; i < 6; i++) {
            const row = document.createElement('tr');
            for (let j = 0; j < 7; j++) {
                const cell = document.createElement('td');
                if (i === 0 && j < firstDay) {
                    cell.innerHTML = '';
                } else if (date > daysInMonth) {
                    break;
                } else {
                    const fullDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(date).padStart(2, '0')}`;
                    cell.innerHTML = date;
                    cell.classList.add('selectable-date');
                    cell.style.cursor = 'pointer';
                    if (today.getFullYear() === year && today.getMonth() === month && today.getDate() === date) {
                        cell.style.backgroundColor = '#90caf9';
                    }
                    cell.onclick = () => {
                        clearSelection();
                        cell.style.backgroundColor = '#4CAF50';
                        cell.style.color = 'white';
                        loadTimeSlots(fullDate);
                    };
                    date++;
                }
                row.appendChild(cell);
            }
            calendar.appendChild(row);
        }
    }

    function clearSelection() {
        document.querySelectorAll('.selectable-date').forEach(cell => {
            cell.style.backgroundColor = '';
            cell.style.color = '';
            const cellDate = new Date(currentYear, currentMonth, parseInt(cell.innerHTML));
            if (cellDate.toDateString() === today.toDateString()) {
                cell.style.backgroundColor = '#90caf9';
            }
        });
    }

    function loadTimeSlots(date) {
        document.getElementById('selected-date').value = date;
        fetch(`/citas_billingue/get-available-slots/?teacher_id=${teacherId}&date=${date}`)
            .then(response => response.json())
            .then(data => {
                timeSlots.innerHTML = '';
                if (data.slots && data.slots.length > 0) {
                    data.slots.forEach(slot => {
                        const li = document.createElement('li');
                        li.textContent = slot.time;
                        li.classList.add('list-group-item');
                        if (slot.available) {
                            li.style.cursor = 'pointer';
                            li.onclick = () => {
                                document.querySelectorAll('#time-slots .selected-time')
                                    .forEach(sel => sel.classList.remove('selected-time'));
                                li.classList.add('selected-time');
                                selectTime(date, slot.time);
                            };
                        } else {
                            li.classList.add('unavailable');
                            li.onclick = () => {
                                Swal.fire({
                                    title: 'Horario no disponible',
                                    text: 'Este horario ya está reservado. Por favor, seleccione otro.',
                                    icon: 'error',
                                    confirmButtonText: 'Aceptar',
                                });
                            };
                        }
                        timeSlots.appendChild(li);
                    });
                } else {
                    timeSlots.innerHTML = '<li class="list-group-item text-danger">No hay horarios disponibles</li>';
                }
            })
            .catch(() => {
                timeSlots.innerHTML = '<li class="list-group-item text-danger">Error al cargar los horarios</li>';
            });
    }

    function selectTime(date, time) {
        document.getElementById('selected-time').value = time;
        Swal.fire({
            title: 'Selección realizada',
            html: `<p><strong>Fecha:</strong> ${date}</p><p><strong>Hora:</strong> ${time}</p>`,
            icon: 'info',
            confirmButtonText: 'Aceptar',
        });
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const date = document.getElementById('selected-date').value;
        const time = document.getElementById('selected-time').value;
        if (!date || !time) {
            Swal.fire({
                title: 'Error',
                text: 'Seleccione una fecha y hora antes de continuar',
                icon: 'error',
                confirmButtonText: 'Aceptar',
            });
            return;
        }
        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-CSRFToken': csrfToken,
            },
        })
        .then(response => {
            if (response.ok) {
                Swal.fire({
                    title: '¡Cita agendada!',
                    html: `<p><strong>Fecha:</strong> ${date}</p>
                           <p><strong>Hora:</strong> ${time}<br>Esperar la confirmación del encargado<br>GRACIAS POR ESPERAR</p>`,
                    icon: 'success',
                    confirmButtonText: 'Aceptar',
                }).then(() => {
                    window.location.href = '/citas_billingue/user-data_bl/';
                });
            } else {
                throw new Error();
            }
        })
        .catch(() => {
            Swal.fire({
                title: 'Error',
                text: 'Ocurrió un error al agendar la cita. Por favor, inténtelo de nuevo.',
                icon: 'error',
                confirmButtonText: 'Aceptar',
            });
        });
    });
});
