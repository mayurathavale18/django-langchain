# Django Task Management System (REST + Celery + WebSockets)

A Django-based backend application demonstrating a **task management system** with:

- REST APIs for task creation and retrieval
- Asynchronous background processing using **Celery**
- Real-time task status updates using **WebSockets (Django Channels)**
- Redis as a message broker and channel layer
- PostgreSQL as the primary datastore

---

## Architecture Overview

The system is intentionally split into clear responsibilities:

- **Django + DRF**  
  Handles HTTP requests, validation, persistence, and orchestration.

- **Celery**  
  Executes long-running or asynchronous work outside the request-response cycle.

- **Redis**
  - Message broker for Celery tasks
  - Channel layer backend for WebSocket fan-out

- **Django Channels + Daphne**
  Enables ASGI support and WebSocket-based real-time updates.

- **PostgreSQL**
  Source of truth for task state.

---

## High-Level Flow

1. Client sends `POST /api/tasks/`
2. Django REST API:
   - Validates input
   - Persists a new task with status `PENDING`
   - Enqueues a Celery task
3. Celery worker:
   - Updates task status to `PROCESSING`
   - Executes background logic
   - Updates task status to `COMPLETED`
4. Each status transition is pushed to connected WebSocket clients in real time.

---

## Project Structure
config/
├── manage.py
├── config/
│ ├── init.py
│ ├── asgi.py
│ ├── celery.py
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
└── tasks/
├── init.py
├── admin.py
├── apps.py
├── consumers.py
├── models.py
├── routing.py
├── serializers.py
├── tasks.py
├── views.py
└── migrations/


---

## Core Concepts Demonstrated

- Django REST Framework `ModelViewSet`
- Explicit orchestration via `perform_create`
- Celery task discovery and execution
- Redis-backed message queues
- ASGI vs WSGI execution model
- WebSocket group-based fan-out
- Idempotent background task design
- Clear separation of persistence, orchestration, and execution

---

## Setup Instructions

### 1. Prerequisites

Ensure the following are installed and running:

- Python 3.10+
- PostgreSQL
- Redis
- Node.js (optional, for `wscat` testing)

---

### 2. Install Dependencies

```bash
pip install django djangorestframework channels channels-redis celery redis psycopg2-binary daphne
```

### 3. create a virutal env && activate it to use pip ( I use venv for it & I don't have python installed gloabally so I only use virutal envs whenever needed ):

```bash
python3 -m venv venv && source venv/bin/activate      # for linux and mac ( check equivalent commands for other systems )
```

### 4. Configure Database

Create a PostgreSQL database and update DATABASES in settings.py:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "task_db",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

### 5. Apply migrations

```python
python manage.py makemigrations
python manage.py migrate
```

### 6. Start Services (Separate Terminals)

- redis
```bash
redis-server
```

- celery worker
```bash
celery -A config worker -l info
```

- Django Server (ASGI via Daphne)
```bash
python manage.py runserver
```

---

## Api Usage

### 1. create a task :

```bash
curl -X POST http://127.0.0.1:8000/api/tasks/ -H "Content-Type: application/json" -d '{"title": "example task"}'
```

### response :
```json
{
  "id": 1,
  "title": "example task",
  "status": "PENDING",
  "created_at": "2026-01-12T06:30:00Z"
}
```

### 2. list tasks

```bash
curl http://127.0.0.1:8000/api/tasks/ -H "Content-Type: application/json"
```

---

## websocket usage

### 1. endpoint :

```bash
ws://localhost:8000/ws/tasks/<task_id>/
```

### 2. example client : ( check my basic client at [websocket_client.html](https://github.com/mayurathavale18/django-langchain/blob/master/config/websocket_client.html)

```bash
# can use this in any browser console ( make sure to be on a local server page first, else it will throw connection error. 
const ws = new WebSocket("ws://localhost:8000/ws/tasks/1/");

ws.onopen = () => console.log("CONNECTED");
ws.onmessage = e => console.log("MESSAGE:", e.data);
ws.onclose = () => console.log("DISCONNECTED");
```

### expected output :
```
MESSAGE: {"status":"PROCESSING"}
MESSAGE: {"status":"COMPLETED"}
```
---

## why websockets ?

- REST APIs expose state
- WebSockets expose events
- Clients fetch current state via REST
- Clients subscribe to real-time updates via WebSockets
WebSockets are treated as an optimization, not a source of truth.

---

## Celery Task Design

### Key properties of the background task:

- Explicitly enqueued via .delay()
- Idempotent
- Safe to retry
- Does not rely on global state
- Communicates progress via Redis-backed channel layers

---

## Common Failure Scenarios Covered

- Worker restarts
- Redis restarts
- Client reconnects
- Duplicate task execution
- Late WebSocket subscribers

---

## License
```
MIT License

Copyright (c) 2024 Kaustubh Patange

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
