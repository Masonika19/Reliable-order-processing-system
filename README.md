# Reliable Order Processing System (ROPS)

A fault-tolerant REST API designed to demonstrate reliable order processing under duplicate requests, temporary failures, permanent failures, and transaction errors.

## Problem

Order-processing systems must handle failures safely without creating duplicate transactions or leaving partially processed data.

ROPS addresses this using:

- Request validation
- Idempotency
- Database transactions
- Automatic retries
- Transaction rollback
- Failure simulation
- Audit logging
- Automated testing
- CI using GitHub Actions
- Docker-based deployment

## System Architecture

```text
                    Client / Swagger UI
                            |
                            v
                    +----------------+
                    |    FastAPI     |
                    |    REST API    |
                    +-------+--------+
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
        Validation    Idempotency    Reliability
                                      Controls
                                           |
                              +------------+------------+
                              |                         |
                              v                         v
                           Retry                    Rollback
                              |                         |
                              +------------+------------+
                                           |
                                           v
                                  Database Transaction
                                           |
                                           v
                                    +-------------+
                                    |    MySQL    |
                                    +-------------+
                                     /           \
                                    /             \
                                   v               v
                              Orders Table    Audit Logs
```

## Reliability Features

### 1. Request Validation

Incoming orders are validated using Pydantic before processing.

### 2. Idempotency

Each request requires an idempotency key. Repeating the same request with the same key returns the previously created order instead of creating a duplicate order.

### 3. Transaction Management

Database operations are committed only after successful processing. Failures trigger transaction rollback.

### 4. Automatic Retry

Temporary processing failures are retried up to three times.

### 5. Failure Simulation

The API supports controlled failure modes for testing reliability and recovery behavior.

### 6. Audit Logging

Important events such as successful processing, retries, and permanent failures are stored in the audit log.

### 7. Automated Testing

The system includes tests for successful orders, idempotency, retries, permanent failures, validation errors, and rollback behavior.

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check service health |
| POST | `/orders` | Create and process an order |

### Create Order

Example request:

```json
{
  "product": "Laptop",
  "side": "BUY",
  "quantity": 2,
  "price": 50000
}
```

Each order request requires an `idempotency-key` header.

Example:

```text
idempotency-key: order-demo-001
```

### Failure Simulation

The order endpoint supports controlled failure testing.

Temporary failure:

```text
POST /orders?failure_mode=temporary
```

Temporary failures trigger the retry mechanism.

Permanent failure:

```text
POST /orders?failure_mode=permanent
```

Permanent failures trigger retries followed by transaction rollback and an `ORDER_FAILED` audit event.

## Testing

The project contains automated tests covering:

- Successful order creation
- Idempotent duplicate requests
- Temporary failure recovery
- Permanent failure handling
- Invalid quantity validation
- Invalid order side validation
- Database rollback

All automated tests pass successfully.

## Docker

The application is containerized using Docker Compose.

The environment contains:

- FastAPI application container
- MySQL database container

The API is exposed on:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

MySQL runs internally on port `3306` and is exposed to the host through port `3308`.

## CI/CD

GitHub Actions is configured to automatically install dependencies and execute the automated test suite whenever changes are pushed to the `main` branch or submitted through a pull request.

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- Pydantic
- Pytest
- HTTPX
- Docker
- Docker Compose
- GitHub Actions
- Git / GitHub

## Project Structure

```text
ROPS/
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── database.py
│   └── main.py
├── tests/
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```