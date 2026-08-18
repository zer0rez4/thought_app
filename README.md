<h1 align='center'>
Thoughts API
</h1>

<p align="center">
REST API for creating, managing and sharing personal and public thoughts with authentication and access control.
</p>

<p align="center">

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-green)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-red)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue)](https://www.postgresql.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2-blue)](https://docs.pydantic.dev/)
[![Docker](https://img.shields.io/badge/Docker-blue)](https://www.docker.com/)
[![Alembic](https://img.shields.io/badge/Alembic-red)](https://alembic.sqlalchemy.org/)
[![Pytest](https://img.shields.io/badge/Pytest-blue)](https://docs.pytest.org/)

</p>

## 📌 About

Thoughts API is a backend application for creating, managing and sharing personal and public thoughts.

The project includes user authentication, access control, token management, data validation, search, pagination, automated testing and database migrations.


## ✨ Features

- User registration and login
- JWT-based authentication
- Access and refresh token management
- Refresh token rotation
- Logout and logout from all devices
- Secure password hashing
- Thought creation and management
- Public and private thought visibility control
- User authorization and access control
- Pagination
- Text search
- Request validation
- Soft account deletion
- User restoration
- PostgreSQL database
- Dockerized application with PostgreSQL
- Alembic database migrations
- Automated tests with Pytest

## 🛠 Technologies

| Technology | Usage |
|-|-|
| Python | Main programming language |
| FastAPI | REST API development and dependency injection |
| SQLAlchemy | ORM and database interaction |
| PostgreSQL | Relational database |
| Alembic | Database schema migrations |
| Docker | Application containerization |
| Docker Compose | Multi-container application orchestration |
| Pydantic | Data validation and serialization |
| Pytest | Automated testing |
| Pydantic Settings | Application configuration management |
| Uvicorn | ASGI server for running the application |
| python-jose | JWT token generation and validation |
| Passlib + bcrypt | Secure password hashing |

## 🚀 Getting Started
### Prerequisites

- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/zer0rez4/thought_app.git
cd thought_app
```

### 2. Configure environment variables
Create a .env file in the project root based on .env.example:

```bash
On Windows:
   copy .env.example .env

On Linux/macOS:
   cp .env.example .env
```
Then fill in the required values.

### 3. Start the application
Build and start the containers:
```bash
docker compose up --build
```
The API will be available at:
```text
http://localhost:8000
```
Interactive API documentation:
```text
http://localhost:8000/docs
```

### 4. Stop the application
To stop the containers:
```bash
docker compose down
```
The PostgreSQL data is stored in a Docker volume and will persist after stopping or recreating the containers.

To remove the containers and the database data:
```bash
docker compose down -v
```

## 🏗 Architecture

The project follows a layered architecture approach:
```text
Client
   │
FastAPI Router
   │
Service Layer
   │
SQLAlchemy ORM
   │
PostgreSQL
```
The application separates API handling, business logic, data models, validation schemas and database migrations.

## 📁 Project Structure
```text
thought_app/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   │
│   ├── api/                 # API routes and HTTP handlers
│   │   ├── auth.py
│   │   ├── thought.py
│   │   └── user.py
│   │
│   ├── core/                # Application configuration and security
│   │   ├── dependencies.py
│   │   ├── jwt.py
│   │   ├── security.py
│   │   └── settings.py
│   │
│   ├── database/            # Database connection and SQLAlchemy models
│   │   ├── models.py
│   │   └── database.py
│   │
│   ├── schemas/             # Pydantic schemas for validation
│   │   ├── thoughts.py
│   │   ├── token.py
│   │   └── user.py
│   │
│   ├── services/            # Business logic
│   │   ├── auth.py
│   │   ├── thought.py
│   │   └── user.py
│   │
│   └── main.py
│
├── tests/
│   │
│   ├── conftest.py
│   ├── helpers.py
│   ├── test_auth.py
│   └── test_user.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── compose.yaml
├── Dockerfile
├── README.md
└── requirements.txt
```

The project structure is organized into separate layers with clear responsibilities:

- API layer handles HTTP communication
- Service layer contains business logic
- Database layer manages persistence
- Schema layer handles validation and serialization
- Alembic manages database schema migrations
- Tests verify application behavior

## 📡 API Overview

### 🔐 Authentication

| Method | Endpoint | Description |
|-|-|-|
| POST | /register | Create account |
| POST | /login | Login user |
| POST | /refresh | Generate new access token using refresh token |
| POST | /logout | Revoke current refresh token |
| POST | /logout/all | Revoke all user's refresh tokens |

### 💭 Thoughts

| Method | Endpoint | Description |
|-|-|-|
| POST | /thoughts | Create thought |
| GET | /thoughts/random | Get random public thought |
| GET | /thoughts/my | Get user's thoughts |
| GET | /thoughts/{thought_id} | Get thought by id |
| GET | /thoughts | Get available thoughts for current user |
| PATCH | /thoughts/{thought_id} | Update thought |
| DELETE | /thoughts/{thought_id} | Delete thought |

### 👤 Users

| Method | Endpoint | Description |
|-|-|-|
| GET | /users/me | Get user's profile |
| PATCH | /users/me | Update user |
| DELETE | /users/me | Delete user |
| POST | /users/restore | Restore user |
| GET | /users/{user_id} | Get user and user's thoughts by id |

## 🔐 Security

Implemented:

- Password hashing using Passlib and bcrypt
- JWT authentication
- Access and refresh token system
- Refresh token rotation
- Token revocation
- Protected endpoints
- User authorization and access control
- Soft account deletion
- Password verification

## 🔄 Token Flow

The application uses JWT-based authentication with access and refresh tokens.

- Access tokens are used for API authorization
- Refresh tokens are stored in the database
- Refresh tokens can be revoked during logout
- Refresh token rotation is used to improve security