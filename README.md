# Customer Support Ticketing CRM

A simple web-based Customer Support Ticketing CRM developed as part of an AI & Tech internship assessment.

The application helps support teams create, manage, search, and track customer support tickets through a clean and responsive dashboard.

## Features

- Create customer support tickets
- Automatically generate ticket IDs
- View all support tickets
- Search tickets by:
  - Ticket ID
  - Customer name
  - Customer email
  - Subject
  - Description
- Filter tickets by status
- View complete ticket details
- Update ticket status
- Add notes and comments
- Dashboard with ticket statistics
- Responsive web interface
- REST API for ticket management
- SQLite database for local development

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

### Frontend

- HTML
- CSS
- JavaScript

## Project Structure

```text
customer-support-ticketing-crm/
│
├── app/
│   ├── routers/
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



## How to Run

1. Clone the repository

git clone https://github.com/anuradhasingh0423-ship-it/customer-support-ticketing-crm.git

2. Open the project
cd customer-support-ticketing-crm

3. Create a virtual environment

For Windows:

python -m venv .venv

Activate the virtual environment:

.venv\Scripts\activate

4. Install dependencies
pip install -r requirements.txt

5. Start the application
uvicorn app.main:app --reload

6. Open the application

Open the following URL in your browser:

http://127.0.0.1:8000
API Endpoints
Tickets
Method	Endpoint	Description
POST	/api/tickets	Create a new ticket
GET	/api/tickets	Get all tickets
GET	/api/tickets/{ticket_id}	Get ticket details
PUT	/api/tickets/{ticket_id}	Update a ticket
Ticket Status

Tickets can have one of the following statuses:

Open
In Progress
Closed
Database

The application uses SQLite for local development.

The database is created automatically when the application starts.

SQLite was selected to keep the project simple and easy to run during development and evaluation.

## Testing

Basic API validation tests are included in the test directory.

The application validates:

Required ticket fields
Customer email format
Ticket status values
Empty notes
Ticket creation and updates
Deployment

The application is deployed using Render.

The deployed application can be accessed through the Render deployment URL.

Screenshots
Dashboard

Add a screenshot of the CRM dashboard here.

Create Ticket

Add a screenshot of the ticket creation form here.

Ticket Details

Add a screenshot of the ticket details page here.

Future Improvements

Possible improvements for future versions include:

User authentication
Role-based access control
Email notifications
Ticket assignment to support agents
Customer self-service portal
PostgreSQL for production deployment
Advanced ticket analytics
File and image attachments
Support agent activity tracking
Author

Anuradha Singh

Bachelor of Engineering
Artificial Intelligence & Machine Learning

GitHub:

https://github.com/anuradhasingh0423-ship-it