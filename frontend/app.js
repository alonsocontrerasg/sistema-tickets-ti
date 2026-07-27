/*const API_URL = "http://127.0.0.1:8000/api/tickets";*/

const API_URL = "https://sistema-tickets-ti-mal6.onrender.com/api/tickets";

// 1. Obtener tickets cuando la página carga
document.addEventListener("DOMContentLoaded", fetchTickets);

// 2. Evento para crear un nuevo ticket (POST)
document.getElementById("ticketForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const nuevoTicket = {
        titulo: document.getElementById("titulo").value,
        descripcion: document.getElementById("descripcion").value,
        prioridad: document.getElementById("prioridad").value
    };

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(nuevoTicket)
        });

        if (res.ok) {
            document.getElementById("ticketForm").reset();
            fetchTickets(); // Actualiza la lista sin recargar la página
        } else {
            alert("Error al intentar levantar el ticket.");
        }
    } catch (error) {
        console.error("Error en petición POST:", error);
    }
});

// 3. Consultar la API para pintar las tarjetas en pantalla (GET)
async function fetchTickets() {
    const container = document.getElementById("ticketsContainer");

    try {
        const res = await fetch(API_URL);
        const tickets = await res.json();

        if (tickets.length === 0) {
            container.innerHTML = "<p>No hay tickets activos en el sistema.</p>";
            return;
        }

        container.innerHTML = tickets.map(ticket => `
            <div class="ticket-card prioridad-${ticket.prioridad}">
                <div class="ticket-info">
                    <h3>#${ticket.id} - ${escapeHtml(ticket.titulo)}</h3>
                    <p>${escapeHtml(ticket.descripcion)}</p>
                    <div class="badges">
                        <span class="badge badge-prioridad">Prioridad: ${ticket.prioridad}</span>
                        <span class="badge badge-estado">Estado: ${ticket.estado}</span>
                    </div>
                </div>
                <div class="ticket-actions">
                    <select class="status-select" onchange="cambiarEstado(${ticket.id}, this.value)">
                        <option value="ABIERTO" ${ticket.estado === 'ABIERTO' ? 'selected' : ''}>ABIERTO</option>
                        <option value="EN_PROCESO" ${ticket.estado === 'EN_PROCESO' ? 'selected' : ''}>EN_PROCESO</option>
                        <option value="RESUELTO" ${ticket.estado === 'RESUELTO' ? 'selected' : ''}>RESUELTO</option>
                    </select>
                    <button class="btn btn-danger" onclick="eliminarTicket(${ticket.id})">Eliminar</button>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error("Error al obtener tickets:", error);
        container.innerHTML = "<p style='color:red;'>⚠️ No se pudo conectar con la API. Verifica que el servidor Uvicorn esté corriendo.</p>";
    }
}

// 4. Cambiar el estado del ticket (PUT)
async function cambiarEstado(id, nuevoEstado) {
    try {
        const res = await fetch(`${API_URL}/${id}/estado`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ estado: nuevoEstado })
        });

        if (res.ok) {
            fetchTickets();
        } else {
            alert("No se pudo actualizar el estado.");
        }
    } catch (error) {
        console.error("Error al actualizar estado:", error);
    }
}

// 5. Eliminar ticket (DELETE)
async function eliminarTicket(id) {
    if (!confirm(`¿Estás seguro de eliminar el ticket #${id}?`)) return;

    try {
        const res = await fetch(`${API_URL}/${id}`, {
            method: "DELETE"
        });

        if (res.ok) {
            fetchTickets();
        } else {
            alert("No se pudo borrar el ticket.");
        }
    } catch (error) {
        console.error("Error al eliminar ticket:", error);
    }
}

// Función auxiliar para evitar ataques de inyección XSS
function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}