# Customer Support Ticketing CRM

A simple customer support ticket management system built as part of an AI & Tech internship assessment.

The application allows support teams to create, search, view, and update customer support tickets from a web-based dashboard.

## Features

- Create customer support tickets
- Automatically generate ticket IDs
- View all support tickets
- Search tickets by ID, customer name, email, subject, or description
- Filter tickets by status
- View complete ticket details
- Update ticket status
- Add notes and comments to tickets
- Dashboard with ticket statistics
- Responsive web interface
- AI Assistant for ticket summary, priority, and suggested replies
- Local AI processing using Ollama

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

### Frontend
- HTML
- CSS
- JavaScript

### AI
- Ollama
- Gemma 3 1B

## Project Structure

```text
customer-support-ticketing-crm/
│
├── app/
│   ├── routers/
│   │   ├── ai.py
│   │   └── tickets.py
│   │
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── test/
│
├── .gitignore
├── requirements.txt
└── README.md