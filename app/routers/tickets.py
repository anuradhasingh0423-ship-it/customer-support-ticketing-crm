from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas


router = APIRouter(
    prefix="/api/tickets",
    tags=["Tickets"]
)


@router.post(
    "",
    status_code=201
)
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db)
):
    try:

        new_ticket = crud.create_ticket(
            db,
            ticket
        )

        return {
            "ticket_id": new_ticket.ticket_id,
            "created_at": new_ticket.created_at
        }

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to create ticket. Please try again."
        )


@router.get("")
def list_tickets(
    status: Optional[str] = Query(
        None,
        description="Filter by ticket status"
    ),

    search: Optional[str] = Query(
        None,
        description="Search tickets"
    ),

    db: Session = Depends(get_db)
):
    tickets = crud.get_tickets(
        db=db,
        status=status,
        search=search
    )

    return [
        {
            "ticket_id": ticket.ticket_id,
            "customer_name": ticket.customer_name,
            "subject": ticket.subject,
            "status": ticket.status,
            "created_at": ticket.created_at
        }
        for ticket in tickets
    ]


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    ticket = crud.get_ticket_by_id(
        db,
        ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return {
        "ticket_id": ticket.ticket_id,
        "customer_name": ticket.customer_name,
        "customer_email": ticket.customer_email,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": ticket.status,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "notes": [
            {
                "id": note.id,
                "note_text": note.note_text,
                "created_at": note.created_at
            }
            for note in ticket.notes
        ]
    }


@router.put("/{ticket_id}")
def update_ticket(
    ticket_id: str,
    update_data: schemas.TicketUpdate,
    db: Session = Depends(get_db)
):
    ticket = crud.get_ticket_by_id(
        db,
        ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    try:
        updated_ticket = crud.update_ticket(
            db,
            ticket,
            update_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
    
    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while updating the ticket."
        )

    return {
        "success": True,
        "updated_at": updated_ticket.updated_at
    }