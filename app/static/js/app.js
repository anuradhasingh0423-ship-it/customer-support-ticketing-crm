const API_URL = "/api/tickets";

let currentTicketId = null;
let currentTicket = null;


const ticketTableBody =
    document.getElementById("ticketTableBody");

const recentTicketTableBody =
    document.getElementById("recentTicketTableBody");

const searchInput =
    document.getElementById("searchInput");

const statusFilter =
    document.getElementById("statusFilter");

const createModal =
    document.getElementById("createModal");

const detailModal =
    document.getElementById("detailModal");

const createTicketForm =
    document.getElementById("createTicketForm");

const openCreateModalBtn =
    document.getElementById("openCreateModalBtn");

const refreshBtn =
    document.getElementById("refreshBtn");


    async function loadTickets() {

        try {
    
            const search =
                searchInput
                    ? searchInput.value.trim()
                    : "";
    
            const status =
                statusFilter
                    ? statusFilter.value
                    : "";
    
            const params =
                new URLSearchParams();
    
            if (search) {
    
                params.append(
                    "search",
                    search
                );
    
            }
    
            if (status) {
    
                params.append(
                    "status",
                    status
                );
    
            }
    
            let url = API_URL;
    
            if (params.toString()) {
    
                url +=
                    "?" +
                    params.toString();
    
            }
    
            const response =
                await fetch(url);
    
            if (!response.ok) {
    
                throw new Error(
                    "Failed to load tickets"
                );
    
            }
    
            const tickets =
                await response.json();
    
            if (ticketTableBody) {
    
                renderTickets(tickets);
    
            }
    
            if (recentTicketTableBody) {
    
                renderRecentTickets(tickets);
    
            }
    
            updateStatistics();
    
        } catch (error) {
    
            console.error(error);
    
            if (ticketTableBody) {
    
                ticketTableBody.innerHTML = `
                    <tr>
                        <td
                            colspan="6"
                            class="empty"
                        >
                            Unable to load tickets.
                            Please try again.
                        </td>
                    </tr>
                `;
    
            }
    
        }
    
    }


function renderTickets(tickets) {

    if (!tickets.length) {

        ticketTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty">
                    No tickets found.
                </td>
            </tr>
        `;

        return;
    }


    ticketTableBody.innerHTML =
        tickets.map(ticket => {

            return `
                <tr>

                    <td>
                        <span class="ticket-id">
                            ${escapeHtml(ticket.ticket_id)}
                        </span>
                    </td>

                    <td>
                        <span class="customer-name">
                            ${escapeHtml(ticket.customer_name)}
                        </span>
                    </td>

                    <td>
                        <span class="subject">
                            ${escapeHtml(ticket.subject)}
                        </span>
                    </td>

                    <td>
                        ${getStatusBadge(ticket.status)}
                    </td>

                    <td>
                        ${formatDate(ticket.created_at)}
                    </td>

                    <td>
                        <button
                            class="view-btn"
                            onclick="openTicket(
                                '${ticket.ticket_id}'
                            )"
                        >
                            View
                        </button>
                    </td>

                </tr>
            `;

        }).join("");
}


function renderRecentTickets(tickets) {

    if (!recentTicketTableBody) {
        return;
    }

    if (!tickets.length) {

        recentTicketTableBody.innerHTML = `
            <tr>
                <td
                    colspan="6"
                    class="empty"
                >
                    No tickets found.
                </td>
            </tr>
        `;

        return;
    }


    const recentTickets =
        tickets.slice(0, 5);


    recentTicketTableBody.innerHTML =
        recentTickets.map(ticket => {

            return `
                <tr>

                    <td>
                        <span class="ticket-id">
                            ${escapeHtml(ticket.ticket_id)}
                        </span>
                    </td>

                    <td>
                        <span class="customer-name">
                            ${escapeHtml(ticket.customer_name)}
                        </span>
                    </td>

                    <td>
                        <span class="subject">
                            ${escapeHtml(ticket.subject)}
                        </span>
                    </td>

                    <td>
                        ${getStatusBadge(ticket.status)}
                    </td>

                    <td>
                        ${formatDate(ticket.created_at)}
                    </td>

                    <td>

                        <button
                            class="view-btn"
                            onclick="openTicket(
                                '${ticket.ticket_id}'
                            )"
                        >
                            View
                        </button>

                    </td>

                </tr>
            `;

        }).join("");

}


function getStatusBadge(status) {

    let className =
        "status-open";


    if (status === "In Progress") {

        className =
            "status-progress";
    }


    if (status === "Closed") {

        className =
            "status-closed";
    }


    return `
        <span class="status-badge ${className}">
            ${escapeHtml(status)}
        </span>
    `;
}



async function updateStatistics() {

    try {

        const response =
            await fetch(API_URL);

        const tickets =
            await response.json();
        

        const total =
            tickets.length;


        const open =
            tickets.filter(
                t => t.status === "Open"
            ).length;


        const progress =
            tickets.filter(
                t => t.status === "In Progress"
            ).length;


        const closed =
            tickets.filter(
                t => t.status === "Closed"
            ).length;


        document.getElementById(
            "totalTickets"
        ).textContent = total;


        document.getElementById(
            "openTickets"
        ).textContent = open;


        document.getElementById(
            "progressTickets"
        ).textContent = progress;


        document.getElementById(
            "closedTickets"
        ).textContent = closed;


    } catch (error) {

        console.error(
            "Statistics error:",
            error
        );
    }
}



createTicketForm.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        const ticketData = {

            customer_name:
                document.getElementById(
                    "customerName"
                ).value.trim(),

            customer_email:
                document.getElementById(
                    "customerEmail"
                ).value.trim(),

            subject:
                document.getElementById(
                    "ticketSubject"
                ).value.trim(),

            description:
                document.getElementById(
                    "ticketDescription"
                ).value.trim()
        };


        try {

            const response =
                await fetch(
                    API_URL,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                ticketData
                            )
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                let message =
                    "Unable to create ticket.";

                if (data.detail) {

                    if (
                        Array.isArray(
                            data.detail
                        )
                    ) {

                        message =
                            data.detail
                                .map(
                                    error =>
                                        error.msg
                                )
                                .join(", ");

                    } else {

                        message =
                            data.detail;
                    }
                }


                throw new Error(
                    message
                );
            }


            closeModal("createModal");


            createTicketForm.reset();


            showToast(
                `Ticket ${data.ticket_id} created successfully!`
            );


            await loadTickets();


        } catch (error) {

            console.error(error);

            showToast(
                error.message,
                true
            );
        }

    }
);



async function openTicket(ticketId) {

    try {

        currentTicketId =
            ticketId;


        const response =
            await fetch(
                `${API_URL}/${ticketId}`
            );


        if (!response.ok) {

            throw new Error(
                "Ticket not found."
            );
        }


        const ticket =
            await response.json();
        currentTicket = ticket;



        document.getElementById(
            "detailTitle"
        ).textContent =
            ticket.subject;


        document.getElementById(
            "detailTicketId"
        ).textContent =
            ticket.ticket_id;


        renderTicketDetails(ticket);


        openModal("detailModal");


    } catch (error) {

        console.error(error);

        showToast(
            error.message,
            true
        );
    }
}



function renderTicketDetails(ticket) {

    const notesHtml =
        ticket.notes.length

            ? ticket.notes.map(note => `
                <div class="note">

                    <div class="note-text">
                        ${escapeHtml(
                            note.note_text
                        )}
                    </div>

                    <span class="note-date">
                        ${formatDate(
                            note.created_at
                        )}
                    </span>

                </div>
            `).join("")

            : `
                <p
                    style="
                        color:#9ca3af;
                        font-size:13px;
                        margin-bottom:15px;
                    "
                >
                    No notes added yet.
                </p>
            `;


    document.getElementById(
        "ticketDetails"
    ).innerHTML = `

        <div class="detail-grid">

            <div class="detail-item">
                <label>Customer</label>

                <p>
                    ${escapeHtml(
                        ticket.customer_name
                    )}
                </p>
            </div>


            <div class="detail-item">
                <label>Email</label>

                <p>
                    ${escapeHtml(
                        ticket.customer_email
                    )}
                </p>
            </div>


            <div class="detail-item">
                <label>Created</label>

                <p>
                    ${formatDate(
                        ticket.created_at
                    )}
                </p>
            </div>


            <div class="detail-item">
                <label>Last Updated</label>

                <p>
                    ${formatDate(
                        ticket.updated_at
                    )}
                </p>
            </div>

        </div>


        <div class="detail-item">

            <label>Description</label>

            <div class="description-box">
                ${escapeHtml(
                    ticket.description
                )}
            </div>

        </div>

        <div style="
            margin-top: 20px;
            margin-bottom: 20px;
            
        ">
        </div>

        <div
            id="aiResult"
            style="
                display:none;
                margin-top: 10px;
                margin-bottom: 25px;
                padding: 18px;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                background: #f8fafc;
                "

        ></div>

        <h3 class="detail-section-title">
            Update Status
        </h3>


        <div class="status-update">

            <select id="detailStatus">

                <option
                    value="Open"
                    ${ticket.status === "Open"
                        ? "selected"
                        : ""}
                >
                    Open
                </option>

                <option
                    value="In Progress"
                    ${ticket.status === "In Progress"
                        ? "selected"
                        : ""}
                >
                    In Progress
                </option>

                <option
                    value="Closed"
                    ${ticket.status === "Closed"
                        ? "selected"
                        : ""}
                >
                    Closed
                </option>

            </select>


            <button
                class="primary-btn"
                onclick="updateTicketStatus()"
            >
                Save Status
            </button>

        </div>


        <h3 class="detail-section-title">
            Notes & Comments
        </h3>


        <div class="notes-list">
            ${notesHtml}
        </div>


        <div class="note-form">

            <textarea
                id="newNote"
                placeholder="Add a note or comment..."
            ></textarea>


            <button
                class="primary-btn"
                onclick="addNote()"
            >
                Add Note
            </button>

        </div>
    `;
}



async function updateTicketStatus() {

    const status =
        document.getElementById(
            "detailStatus"
        ).value;


    try {

        const response =
            await fetch(
                `${API_URL}/${currentTicketId}`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            status: status
                        })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to update ticket."
            );
        }


        showToast(
            "Ticket status updated."
        );


        await loadTickets();


        await openTicket(
            currentTicketId
        );


    } catch (error) {

        console.error(error);

        showToast(
            error.message,
            true
        );
    }
}





async function addNote() {

    const noteElement =
        document.getElementById(
            "newNote"
        );


    const note =
        noteElement.value.trim();


    if (!note) {

        showToast(
            "Please enter a note.",
            true
        );

        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/${currentTicketId}`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            notes: note
                        })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to add note."
            );
        }


        showToast(
            "Note added successfully."
        );


        await openTicket(
            currentTicketId
        );


    } catch (error) {

        console.error(error);

        showToast(
            error.message,
            true
        );
    }
}



function openModal(id) {

    document
        .getElementById(id)
        .classList.add("show");
}


function closeModal(id) {

    document
        .getElementById(id)
        .classList.remove("show");
}



document.querySelectorAll(
    "[data-close]"
).forEach(button => {

    button.addEventListener(
        "click",
        () => {

            closeModal(
                button.dataset.close
            );

        }
    );
});



document.querySelectorAll(
    ".modal-overlay"
).forEach(overlay => {

    overlay.addEventListener(
        "click",
        function(event) {

            if (
                event.target === overlay
            ) {

                overlay.classList.remove(
                    "show"
                );
            }

        }
    );
});



document
    .getElementById(
        "openCreateModalBtn"
    )
    .addEventListener(
        "click",
        () => {

            openModal(
                "createModal"
            );

        }
    );



let searchTimeout;


if (searchInput) {

    searchInput.addEventListener(
        "input",
        function() {

            clearTimeout(searchTimeout);

            searchTimeout =
                setTimeout(
                    () => {
                        loadTickets();
                    },
                    250
                );

        }
    );

}




if (statusFilter) {

    statusFilter.addEventListener(
        "change",
        () => {
            loadTickets();
        }
    );

}



if (refreshBtn) {

    refreshBtn.addEventListener(
        "click",
        () => {

            loadTickets();

            showToast(
                "Tickets refreshed."
            );

        }
    );

}



function showToast(
    message,
    isError = false
) {

    const toast =
        document.getElementById(
            "toast"
        );


    const messageElement =
        document.getElementById(
            "toastMessage"
        );


    messageElement.textContent =
        message;


    toast.style.background =
        isError
            ? "#dc2626"
            : "#111827";


    toast.classList.add(
        "show"
    );


    setTimeout(
        () => {

            toast.classList.remove(
                "show"
            );

        },
        3000
    );
}


function formatDate(dateString) {

    if (!dateString) {
        return "-";
    }


    const date =
        new Date(dateString);


    return date.toLocaleString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric",

            hour: "2-digit",
            minute: "2-digit"
        }
    );
}



function escapeHtml(value) {

    if (value === null ||
        value === undefined) {

        return "";
    }


    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}



document.querySelectorAll(".nav-item").forEach(item => {

    item.addEventListener("click", function(event) {

        event.preventDefault();

        // Remove active from all navigation items
        document.querySelectorAll(".nav-item").forEach(nav => {
            nav.classList.remove("active");
        });

        // Make clicked item active
        this.classList.add("active");

        const target = this.getAttribute("href");

        // Dashboard
        if (target === "#") {
            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        }

        // Tickets
        else if (target === "#tickets") {

            const ticketsSection =
                document.getElementById("tickets");

            if (ticketsSection) {
                ticketsSection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        }

    });

});

loadTickets();