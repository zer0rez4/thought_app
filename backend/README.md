<h1 align='center'>
   Thoughts API
</h1>

<p align="center">
    Backend service for creating, managing, and sharing personal and public thoughts.
</p>

<p align="center">
    Built with FastAPI, PostgreSQL, and SQLAlchemy.
</p>

<p align="center">
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12">
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

## 📖 About

This directory contains the backend implementation of Thoughts API.

The application provides a REST API for managing thoughts and user accounts, with JWT authentication, access control, email-based account workflows, and asynchronous database operations.

See the [root README](../README.md) for an overview of the entire project and instructions for running it with Docker Compose.


## ✨ Features

### Authentication & Security

- User registration and email verification
- JWT-based authentication with access and refresh tokens
- Refresh token rotation and revocation
- Logout from the current session or all devices
- Password hashing and password reset via email
- Token expiration and validation
- User-level authorization and access control

### User Management

- User profile retrieval and updates
- Soft account deletion
- Account restoration via email
- Email-based verification and recovery workflows

### Thought Management

- Create, retrieve, update and delete thoughts
- Public and private thought visibility
- Access-controlled thought operations
- Paginated thought retrieval
- Text search
- Random public thought retrieval

### Database & Infrastructure

- PostgreSQL relational database
- Asynchronous database operations with SQLAlchemy
- Schema migrations with Alembic
- Dockerized application and PostgreSQL setup using Docker Compose
- Automatic database migrations on application startup

### Testing

- Automated tests with Pytest and pytest-asyncio
- Asynchronous API testing with HTTPX AsyncClient
- Separate test database
- Tests covering authentication, email workflows, user management and thought operations

## 🛠️ Technology stack

| Technology | Usage |
|-|-|
| Python | Main programming language |
| FastAPI | REST API development and dependency injection |
| SQLAlchemy | Async ORM and database interaction |
| PostgreSQL | Relational database |
| Alembic | Database schema migrations |
| Docker | Application containerization |
| Docker Compose | Multi-container application orchestration |
| Pydantic | Data validation and serialization |
| Pytest | Automated testing |
| pytest-asyncio | Asynchronous test execution |
| Pydantic Settings | Application configuration management |
| Uvicorn | ASGI server for running the application |
| python-jose | JWT token generation and validation |
| Passlib + bcrypt | Secure password hashing |

## 🚀 Local Development
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

## 🧪 Testing

The project contains 97 automated tests covering authentication, users and thoughts.

Tests use pytest, pytest-asyncio, HTTPX AsyncClient and an asynchronous SQLAlchemy session.

Run the following commands from the `backend/` directory:

```bash
python -m pytest
```

## 🏗️ Architecture

The project follows a layered architecture approach:
```text
Client
   │
FastAPI Router
   │
Service Layer
   │
Async SQLAlchemy
   │
PostgreSQL
```
The application separates HTTP handling, business logic, database operations and request/response validation. SQLAlchemy is used with asynchronous database sessions, while Alembic manages schema migrations.

## 📁 Project Structure
```text
backend/
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
│   │   ├── email.py
│   │   ├── jwt.py
│   │   ├── security.py
│   │   └── settings.py
│   │
│   ├── database/            # Database connection and SQLAlchemy models
│   │   ├── models.py
│   │   └── database.py
│   │
│   ├── schemas/             # Pydantic schemas for validation
│   │   ├── email.py
│   │   ├── response.py
│   │   ├── thoughts.py
│   │   ├── token.py
│   │   └── user.py
│   │
│   ├── services/            # Business logic
│   │   ├── auth.py
│   │   ├── email_token.py
│   │   ├── email.py
│   │   ├── thought.py
│   │   └── user.py
│   │
│   ├── templates/            # Templates
│   │   └── email/            # Email templates
│   │      ├── reset_password_email.html
│   │      ├── reset_password_email.txt
│   │      ├── restore_email.html
│   │      ├── restore_email.txt
│   │      ├── verify_email.html
│   │      └── verify_email.txt
│   │
│   ├── utils/            # Shared utility functions
│   │   ├── templates.py
│   │   └── validators.py
│   │
│   └── main.py
│
├── tests/
│   │
│   ├── factories/
│   │   ├── thought.py
│   │   └── user.py
│   │
│   ├── helpers/
│   │   ├── assertions.py
│   │   ├── data.py
│   │   └── requests.py
│   │
│   ├── utils/
│   │   ├── db.py
│   │   └── tokens.py
│   │
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_thought.py
│   └── test_user.py
│
├── .dockerignore
├── alembic.ini
├── Dockerfile
├── pytest.ini
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
| POST | /auth/register | Register a new account |
| POST | /auth/resend-verification | Request another verification email |
| GET | /auth/verify-email | Verify email |
| POST | /auth/login | Login user |
| POST | /auth/refresh | Generate new access token using refresh token |
| POST | /auth/logout | Revoke current refresh token |
| POST | /auth/logout/all | Revoke all user's refresh tokens |
| POST | /auth/reset-password | Request a password reset email |
| POST | /auth/resend-reset-password | Request another password reset email |
| POST | /auth/set-new-password | Set a new password using a reset token |

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
| POST | /users/restore | Request an account restoration email |
| GET | /users/restore | Restore an account using a token |
| GET | /users/{user_id} | Get user and user's thoughts by id |

## 🔐 Security

The application implements the following security mechanisms:

- Password hashing using Passlib and bcrypt
- JWT-based access and refresh tokens
- Refresh token rotation
- Refresh token revocation during logout
- Refresh token hashing before database storage
- Token validation and expiration checks
- Protected endpoints and user-level access control
- Email verification
- Password reset through email tokens
- Account restoration through email tokens
- Soft account deletion

## 🔄 Token Flow

The application uses JWT-based authentication with access and refresh tokens.

- Access tokens are used for API authorization.
- Refresh tokens are stored in the database as SHA-256 hashes rather than plain-text tokens.
- Each refresh request revokes the current refresh token and issues a new access/refresh token pair.
- Refresh tokens can be revoked during logout, either for the current session or all sessions.