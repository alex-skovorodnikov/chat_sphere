# Chat Sphere WebSocket

A real-time chat application using WebSocket, built with FastAPI, Alembic for database migrations, Docker for containerization, and Redis for message brokering.

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)


## Features

- Real-time messaging using WebSocket.
- User authentication and management.
- Message history retrieval.
- Scalable architecture using Redis for message brokering.
- Dockerized application for easy deployment.

## Technologies

- **FastAPI**: A modern web framework for building APIs with Python 3.6+ based on standard Python type hints.
- **Alembic**: A lightweight database migration tool for use with SQLAlchemy.
- **Docker**: A platform for developing, shipping, and running applications in containers.
- **Redis**: An in-memory data structure store used as a database, cache, and message broker.

## Installation

Follow these steps to set up the project locally:

1.**Install Poetry** (if you haven't already):
```bash
  curl -sSL https://install.python-poetry.org | python3 -
```
2.**Clone the repository:**
```bash
   https://github.com/alex-skovorodnikov/chat_sphere.git
```
3.**Navigate the project directory:**
```bash
  cd chat-sphere
```
4.**Install the required dependencies:**
```bash
  poetry install
```
5.**Build and run the application using Docker Compose:**
```bash
  docker-compose up --build
```
6.**Run database migrations using Alembic.** You can do this by executing a command in the running container. First, find the container name or ID:
```bash
  docker-compose ps
```
7.**Then, run the migration command:**
```bash
  docker-compose exec app poetry run alembic upgrade head
```
---
## Contact

If you have any questions, suggestions, or feedback, feel free to reach out!

- **Aleksey Skovorodnikov**
- **Email**: [alexSkovorodnikov@yandex.ru](mailto:alexskovorodnikov@yandex.ru)
- **Project Link**: https://github.com/alex-skovorodnikov/chat_sphere
