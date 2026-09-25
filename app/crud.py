from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from . import models, schemas


ALLOWED_STATUSES = {
    "Open",
    "In Progress",
    "Closed"
}


def generate_ticket_id(db: Session) -> str:
    """
    Generate ticket IDs such as:
    TKT-001
    TKT-002
    TKT-003
    """

    last_ticket = (
        db.query(models.Ticket)
        .order_by(models.Ticket.id.desc())
        .first()
    )

    if not last_ticket:
        number = 1
    else:
        try:
            number = int(last_ticket.ticket_id.split("-")[1]) + 1
        except (IndexError, ValueError):
            number = last_ticket.id + 1

    return f"TKT-{number:03d}"


def create_ticket(
    db: Session,
    ticket_data: schemas.TicketCreate
):
    ticket = models.Ticket(
        ticket_id=generate_ticket_id(db),
        customer_name=ticket_data.customer_name,
        customer_email=ticket_data.customer_email,
        subject=ticket_data.subject,
        description=ticket_data.description,
        status="Open"
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def get_tickets(
    db: Session,
    status: str = None,
    search: str = None
):
    query = db.query(models.Ticket)

    if status:
        query = query.filter(
            models.Ticket.status == status
        )

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                models.Ticket.ticket_id.ilike(search_pattern),
                models.Ticket.customer_name.ilike(search_pattern),
                models.Ticket.customer_email.ilike(search_pattern),
                models.Ticket.description.ilike(search_pattern),
                models.Ticket.subject.ilike(search_pattern)
            )
        )

    return query.order_by(
        models.Ticket.created_at.desc()
    ).all()


def get_ticket_by_id(
    db: Session,
    ticket_id: str
):
    return (
        db.query(models.Ticket)
        .filter(models.Ticket.ticket_id == ticket_id)
        .first()
    )


def update_ticket(
    db: Session,
    ticket: models.Ticket,
    update_data: schemas.TicketUpdate
):
    if update_data.status is not None:

        if update_data.status not in ALLOWED_STATUSES:
            raise ValueError(
                "Invalid status. Use Open, In Progress, or Closed."
            )

        ticket.status = update_data.status

    if update_data.notes:
        new_note = models.Note(
            ticket_id=ticket.ticket_id,
            note_text=update_data.notes
        )

        db.add(new_note)

    ticket.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)

    return ticket