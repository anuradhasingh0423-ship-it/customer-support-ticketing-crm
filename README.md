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




How to Run

1. Clone the repository
git clone https://github.com/anuradhasingh0423-ship-it/customer-support-ticketing-crm.git

2. Open the project
cd customer-support-ticketing-crm

3. Create a virtual environment

Windows:

python -m venv .venv

Activate it:

.venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt
5. Start the application
uvicorn app.main:app --reload

Open the application in your browser:

http://127.0.0.1:8000
AI Assistant

The project includes an optional local AI Assistant.

It uses Ollama instead of a paid API.

Install Ollama and download the model:

ollama pull gemma3:1b

Make sure Ollama is running before using the AI Assistant.

The AI Assistant can provide:

Ticket summary
Ticket priority
Suggested customer reply

The application also applies status-based rules so that the AI does not claim that a closed ticket is being investigated or resolved when that information is not available.

The main CRM works independently of the AI Assistant.

API Endpoints
Tickets
Method	Endpoint	Description
POST	/api/tickets	Create a ticket
GET	/api/tickets	Get tickets
GET	/api/tickets/{ticket_id}	Get ticket details
PUT	/api/tickets/{ticket_id}	Update ticket
AI
Method	Endpoint	Description
POST	/api/ai/ticket-assist	Generate AI assistance for a ticket
Ticket Status

Tickets can have one of three statuses:

Open
In Progress
Closed
Database

The application uses SQLite for local development.

The database is created automatically when the application is started.

Testing

Basic API validation tests are included in the test directory.

The project also includes validation for:

Invalid email addresses
Invalid ticket statuses
Empty notes
Required ticket fields
Screenshots

Add screenshots of the application here after deployment.

Future Improvements

Some possible improvements for future versions:

User authentication
Role-based access
Email notifications
Ticket assignment to support agents
Customer portal
Production database such as PostgreSQL
Hosted AI service for the deployed version
Author

Anuradha Singh

Bachelor of Engineering - Artificial Intelligence & Machine Learning

GitHub:
https://github.com/anuradhasingh0423-ship-it
