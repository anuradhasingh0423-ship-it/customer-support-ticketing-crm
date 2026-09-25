from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class TicketCreate(BaseModel):
    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    customer_email: EmailStr

    subject: str = Field(
        ...,
        min_length=3,
        max_length=255
    )

    description: str = Field(
        ...,
        min_length=5,
        max_length=5000
    )

    @field_validator("customer_name", "subject", "description")
    @classmethod
    def validate_text_fields(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class NoteResponse(BaseModel):
    id: int
    note_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    ticket_id: str
    customer_name: str
    subject: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketDetailResponse(BaseModel):
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    notes: List[NoteResponse] = []

    class Config:
        from_attributes = True


class TicketUpdate(BaseModel):
    status: Optional[
        Literal["Open", "In Progress", "Closed"]
    ] = None

    notes: Optional[str] = Field(
        default=None,
        max_length=2000
    )

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError(
                "Note cannot be empty."
            )

        return value