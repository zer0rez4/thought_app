<h1 align='center'>
   Thoughts API
</h1>

<p align='center'>
A REST API for creating, managing, and sharing personal and public thoughts.
</p>

<p align="center">
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12">
    </a>
    <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript">
        <img src="https://img.shields.io/badge/Frontend-Vanilla%20JS-F7DF1E?logo=javascript&logoColor=black" alt="Vanilla JavaScript">
    </a>
    <a href="https://fastapi.tiangolo.com/">
        <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
    </a>
    <a href="https://www.sqlalchemy.org/">
        <img src="https://img.shields.io/badge/SQLAlchemy-ORM-D71F00" alt="SQLAlchemy">
    </a>
    <a href="https://www.postgresql.org/">
        <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
    </a>
    <a href="https://docs.pydantic.dev/">
        <img src="https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white" alt="Pydantic v2">
    </a>
    <a href="https://www.docker.com/">
        <img src="https://img.shields.io/badge/Docker-Containerization-2496ED?logo=docker&logoColor=white" alt="Docker">
    </a>
    <a href="https://alembic.sqlalchemy.org/">
        <img src="https://img.shields.io/badge/Alembic-Migrations-6BAA75" alt="Alembic">
    </a>
    <a href="https://docs.pytest.org/">
        <img src="https://img.shields.io/badge/Pytest-Testing-0A9EDC?logo=pytest&logoColor=white" alt="Pytest">
    </a>
</p>

## Overview

Thoughts is a full-stack application for creating, managing, and sharing personal and public thoughts. It consists of a robust FastAPI backend and a lightweight, vanilla JavaScript frontend with JWT authentication and email verification flows.

## Features

- **Authentication:** registration, email verification, JWT access and refresh tokens.
- **Session management:** refresh token rotation, session revocation, and logout from all devices.
- **Account management:** profile updates, soft deletion, and account restoration.
- **Thoughts:** CRUD operations, public and private visibility, text search, and pagination.
- **Security:** password hashing, token validation, and user-level access control.
- **Email workflows:** email verification, password recovery, and account restoration.
- **Testing:** automated API tests with Pytest, pytest-asyncio, and HTTPX.
- **Database:** PostgreSQL with asynchronous SQLAlchemy and Alembic migrations.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Programming language |
| FastAPI | REST API and dependency injection |
| SQLAlchemy | Asynchronous ORM and database access |
| PostgreSQL | Relational database |
| Pydantic | Data validation and serialization |
| Alembic | Database migrations |
| Pytest | Automated testing |
| Docker Compose | Local development environment |

## Architecture

```text
Client
  |
  v
FastAPI Routers
  |
  v
Service Layer
  |
  v
Async SQLAlchemy
  |
  v
PostgreSQL
```

The application separates HTTP handling, business logic, data validation, and persistence into distinct layers.

## Project Structure

```text
thought_app/
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   ├── css/
│   ├── js/
│   └── index.html
├── compose.yaml
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Git
- Docker Desktop with Docker Compose, or Docker Engine with the Compose plugin

### 1. Clone the repository

```bash
git clone https://github.com/zer0rez4/thought_app.git
cd thought_app
```

### 2. Configure environment variables

Create a `.env` file from the example:

**Windows PowerShell**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS**
```bash
cp .env.example .env
```

Fill in the required environment variables before starting the application.

### 3. Start the application

```bash
docker compose up --build
```

The API will be available at:

- API: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs

### 4. Run the Frontend (Optional)
The frontend is a standalone Single Page Application (SPA). To run it locally alongside the backend:

1. Open the `frontend/` directory in your code editor.
2. Use a local development server. For example, with VS Code "Live Server" extension, or Python:
   
From the root of the project
```bash
python -m http.server 5500 --directory frontend
```

### 5. Stop the application

```bash
docker compose down
```

Docker volumes preserve database data when containers are stopped or recreated. To also remove the database volume:

```bash
docker compose down -v
```

**Warning:** `docker compose down -v` deletes the database volume and its stored data.

## Testing

The backend includes an automated test suite built with Pytest, pytest-asyncio, and HTTPX.

For test setup and execution instructions, see [`backend/README.md`](backend/README.md).

## Documentation
- For detailed information about the backend architecture, API endpoints, and database, see [`backend/README.md`](backend/README.md).
- For details on the frontend architecture, module structure, and local setup, see [`frontend/README.md`](frontend/README.md).

## Project Status

The project is under active development.
