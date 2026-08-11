# FastAPI Product API

A FastAPI-based REST API for managing products with PostgreSQL, SQLAlchemy, JWT authentication, password hashing, input validation, and protected product endpoints.

## Features

- User registration
- User login
- Password hashing using Argon2
- JWT-based authentication
- Protected product endpoints
- Product CRUD operations
- PATCH support for partial updates
- PostgreSQL database
- Async SQLAlchemy
- Pydantic input validation
- CORS configuration
- HTTP error responses
- Application logging

## Technologies Used

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- asyncpg
- Pydantic
- Argon2
- JWT
- Uvicorn

## Project Structure

```text
FastApi_prac/
│
├── main.py
├── models.py
├── database.py
├── database_models.py
├── auth.py
├── jwt_auth.py
├── bearer_auth.py
├── logging_config.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md