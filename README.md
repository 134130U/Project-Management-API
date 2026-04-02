# Project Management API & Frontend

A full-stack project management application featuring a FastAPI-based REST API and a Dash-based interactive frontend. Track project progress, manage tasks, and handle file attachments in a Jira/Asana style interface.

## Features

- **Interactive Dashboard**: View project summaries, filter by status/priority, and see real-time progress.
- **Project Detail View (Jira-style)**:
    - **Update Progress**: Live updates for project completion percentage and status.
    - **Comments & Updates**: Post updates with rich text and file attachments.
    - **File Management**: Upload and download project-related files directly from the UI.
- **Authentication**: Secure JWT-based authentication for user login and registration.
- **Project Management**: Create, read, update, and delete projects with ease.
- **File Storage**: Persistent storage for attachments using MinIO.
- **Database**: PostgreSQL for robust data management.
- **Containerization**: Fully Dockerized for seamless setup and deployment.

## Technologies Used

- **Frontend**: [Dash](https://dash.plotly.com/) (Plotly), [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)
- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Storage**: [MinIO](https://min.io/) (S3 Compatible)
- **Orchestration**: [Docker Compose](https://docs.docker.com/compose/)
- **Language**: Python 3.9+

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Make](https://www.gnu.org/software/make/) (optional, but recommended)

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/134130U/Project-Management-API.git
cd project-management-api
```

### 2. Configure Environment Variables
Copy the example environment file and adjust values as needed (a default `.env` is already provided for local development).

### 3. Run the Application
Use the provided `Makefile` to build and start all services:
```bash
make run
```
This will start:
- **Frontend**: [http://localhost:8050](http://localhost:8050)
- **API (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL**: `localhost:5432`
- **pgAdmin**: [http://localhost:5050](http://localhost:5050)
- **MinIO Console**: [http://localhost:9001](http://localhost:9001)

### 4. Default Login Credentials
Use the following credentials to explore the application:
- **Email**: `test@test.com`
- **Password**: `newpassword123`

### 5. Stop the Application
```bash
make down
```

## API Documentation

Once the application is running, you can access the interactive API documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Core Endpoints
- `/auth`: Registration and login.
- `/projects`: Manage projects.
- `/updates`: Manage project updates.
- `/files`: Upload and retrieve project files.
- `/health`: API health check status.

## Running Tests

To run the automated tests using `pytest`, use the following command:
```bash
make test
```

## Project Structure

```text
├── app/                # Backend FastAPI application
│   ├── api/            # API routes and dependencies
│   ├── core/           # Security, auth, and shared core logic
│   ├── db/             # Database session and base models
│   ├── models/         # SQLAlchemy models
│   ├── repositories/   # Data access layer
│   ├── schemas/        # Pydantic models (data validation)
│   ├── services/       # Business logic layer
│   └── main.py         # Application entry point
├── frontend/           # Frontend Dash application
│   ├── pages/          # Dash pages (Dashboard, Projects, Login, etc.)
│   ├── components/     # Reusable UI components (Navbar, Cards, etc.)
│   ├── services/       # Frontend-to-Backend API client services
│   └── app.py          # Dash application initialization
├── scripts/            # Database and storage initialization scripts
├── tests/              # Unit and integration tests
├── Dockerfile          # Backend container specification
├── docker-compose.yml  # Multi-container orchestration
├── Makefile            # Automation commands
└── requirements.txt    # Project dependencies
```
