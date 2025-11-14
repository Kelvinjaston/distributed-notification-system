# Distributed Notification System

A highly scalable and fault-tolerant Distributed Notification System built on a Microservices architecture. The core objective is to decouple synchronous API calls from asynchronous notification processing (Email and Push) using a Message Queue (RabbitMQ).

The system is designed to meet strict performance targets, including handling over 1,000 notifications per minute with high reliability and low latency.

## Architecture and Services

The system is composed of five specialized microservices, communicating synchronously via REST and asynchronously via RabbitMQ.

| Service | Responsibility | Communication | Data Storage |
|---------|----------------|---------------|--------------|
| **API Gateway** | Entry point, Authentication, Request Validation, and Message Routing to RabbitMQ. | Synchronous (REST) | None |
| **User Service** | Manages user data (preferences, tokens) and handles authentication/permissions. | Synchronous (REST) | PostgreSQL, Redis (Cache) |
| **Template Service** | Stores, manages, and performs variable substitution on notification templates. | Synchronous (REST) | PostgreSQL |
| **Email Service** | Consumes messages from email.queue, fills templates, and sends emails (SMTP/API). | Asynchronous (RabbitMQ) | None |
| **Push Service** | Consumes messages from push.queue and delivers mobile/web push notifications. | Asynchronous (RabbitMQ) | None |

## Infrastructure Components

- **Queue**: RabbitMQ (for asynchronous communication and failure handling)
- **Database**: PostgreSQL (for persistent user and template data)
- **Cache**: Redis (for high-speed lookups of user preferences and rate limiting)

## Service Communication Strategy

All services run inside a dedicated Docker network created by Docker Compose. This means service-to-service communication uses the service name (e.g., `user-service`) and the internal port (e.g., 8081).

### Internal Communication (Service-to-Service)
- Email Service uses `http://user-service:8081` and `http://template-service:8082`
- The service name (`user-service`) is used as the hostname for DNS resolution within the Docker network
- No `localhost` or `127.0.0.1` is used for inter-service calls

### External Access (Client-to-System)
- Only the API Gateway is exposed externally via the host machine's port 8080
- The User Service is not directly exposed but is accessible through the API Gateway
- The client (browser, mobile app) accesses the system via `http://localhost:8080`

## Asynchronous Messaging Flow (RabbitMQ)

The system uses a `notifications.direct` exchange to route messages reliably.

| Component | Purpose |
|-----------|---------|
| `notifications.direct` (Exchange) | Direct exchange used by the API Gateway to send notification requests |
| `email.queue` | Bound to the exchange for messages requiring the Email Service |
| `push.queue` | Bound to the exchange for messages requiring the Push Service |
| `failed.queue` | Acts as the Dead Letter Queue (DLQ) for messages that permanently fail after retries |

## Key Technical Concepts & Fault Tolerance

The system incorporates advanced distributed concepts to ensure stability and resilience:

| Concept | Implementation Focus |
|---------|---------------------|
| **CI/CD Workflow** | Automated build, testing, Docker image creation, and deployment via GitHub Actions and Docker Compose |
| **Circuit Breaker** | Implemented to prevent cascading failure when external dependencies (e.g., SMTP servers, FCM) go down |
| **Retry System** | Automatic retries with exponential backoff for transient message processing failures before routing to the Dead Letter Queue |
| **Idempotency** | Unique request IDs are used to prevent duplicate notifications from being sent due to retries or network issues |
| **Health Checks** | Each service exposes a dedicated `/health` endpoint for status monitoring |

## Deployment and Local Setup

This project is containerized using Docker and deployed using Docker Compose.

### Requirements
- Docker and Docker Compose
- Java Development Kit (JDK 17 or higher)
- Maven

### Local Development

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Kelvinjaston/distributed-notification-system.git
   cd distributed-notification-system
   ```
   Build Docker Images:
The project uses Maven to build executable JARs, which are then packaged into the final Docker images defined by Dockerfile.prod.
 # Build all services using Maven
   mvn clean package -DskipTests

Start the System (Docker Compose):
Ensure your .env file is configured with PostgreSQL and RabbitMQ credentials.

  docker compose up --build -d


   
   
