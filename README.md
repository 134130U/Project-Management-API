# Project Management API

A FastAPI-based REST API for project management, featuring user authentication, project tracking, updates, and file storage.

## Features

- **Authentication**: Secure JWT-based authentication for user login and registration.
- **Project Management**: Create, read, update, and delete projects.
- **Updates**: Track project progress with periodic updates.
- **File Storage**: Upload and manage project-related files using MinIO.
- **Database**: PostgreSQL for persistent data storage.
- **Containerization**: Fully Dockerized for easy setup and deployment.

## Technologies Used

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Storage**: [MinIO](https://min.io/)
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
- **API**: [http://localhost:8000](http://localhost:8000)
- **PostgreSQL**: `localhost:5432`
- **pgAdmin**: [http://localhost:5050](http://localhost:5050)
- **MinIO Console**: [http://localhost:9001](http://localhost:9001)

### 4. Stop the Application
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
├── app/
│   ├── api/            # API routes and dependencies
│   ├── core/           # Security, auth, and shared core logic
│   ├── db/             # Database session and base models
│   ├── models/         # SQLAlchemy models
│   ├── repositories/   # Data access layer
│   ├── schemas/        # Pydantic models (data validation)
│   ├── services/       # Business logic layer
│   └── main.py         # Application entry point
├── scripts/            # Database and storage initialization scripts
├── tests/              # Unit and integration tests
├── Dockerfile          # Container specification
├── docker-compose.yml  # Multi-container orchestration
├── Makefile            # Automation commands
└── requirements.txt    # Project dependencies
```
