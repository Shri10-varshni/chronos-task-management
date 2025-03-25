Smart Task Management System
Overview
The Smart Task Management System is a microservices-based web application designed to manage tasks, suggest priorities, and send notifications to users about upcoming tasks. It uses FastAPI for building the services, Docker for containerization, and Kubernetes for cloud deployment (though it's not actively deployed here). The project showcases various industry best practices, such as asynchronous communication, JWT authentication, and caching with Redis.

Key Features:
Task Management: Users can create, read, update, and delete tasks.

Priority Recommendations: The system intelligently suggests task priorities based on metadata (e.g., due dates).

Notifications: Sends reminders about upcoming tasks using RabbitMQ.

Microservices Architecture: Each feature is encapsulated in its own service.

Containerization with Docker: All services are containerized for easy local deployment.

Asynchronous Communication: Microservices communicate asynchronously using RabbitMQ and Redis.

JWT Authentication: Secure access using token-based authentication