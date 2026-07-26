# Server Design

## Executive Summary

This document presents the proposed cloud architecture for scaling the Kung Fu Chess server.

The goal of the new architecture is to support:

- 100 million registered users.
- 10 million concurrent players.
- Horizontal scalability.
- High availability.
- Stateless services where possible.
- Fast deployment using Docker and Kubernetes.

The architecture separates the system into independent services that communicate using gRPC while clients communicate through WebSocket.

---

# Project Goals

- Support 100 million registered users.
- Support 10 million concurrent players.
- Scale horizontally by adding containers.
- Keep services loosely coupled.
- Isolate responsibilities between services.
- Reduce single points of failure.
- Support future cloud deployment.

---

# High Level Architecture

```text
                             Clients
                                │
                           WebSocket
                                │
                                ▼
                 API / WebSocket Gateway
                                │
                     gRPC Communication
                                │
      ┌─────────────────────────┼─────────────────────────┐
      │                         │                         │
      ▼                         ▼                         ▼
 Identity Service     Lobby & Matchmaking      Session Directory
                                                   &
                                            Game Allocation
                                                     │
                                                     ▼
                                              Game Service Pool
                                          ┌────────┬────────┬────────┐
                                          ▼        ▼        ▼
                                      Game 1   Game 2   Game N
                                                     │
                                                     ▼
                                              Rating Service

Infrastructure
──────────────
PostgreSQL
Redis
Kubernetes / K3s
```

---

# Game Flow

```text
Client
   │
   ▼
API / WebSocket Gateway
   │
   ▼
Identity Service
   │
   ▼
Lobby & Matchmaking
   │
   ▼
Session Directory
   │
   ▼
Game Service
   │
   ▼
Rating Service
   │
   ▼
PostgreSQL
```

---

# Database

## PostgreSQL

- Users
- Password Hashes
- Ratings
- Game Results
- Match History

## Redis

- Matchmaking Queue
- Private Rooms
- Active Sessions
- Game Routing
- Reconnect Tokens
- Worker Load

---

# Services

## API / WebSocket Gateway

### Responsibilities

### Replaces

### Communication

---

## Identity Service

### Responsibilities

### Replaces

### Communication

---

## Lobby & Matchmaking Service

### Responsibilities

### Replaces

### Communication

---

## Session Directory & Game Allocation

### Responsibilities

### Replaces

### Communication

---

## Game Service

### Responsibilities

### Replaces

### Communication

---

## Rating Service

### Responsibilities

### Replaces

### Communication

---

# Network Traffic

- 10 million concurrent players
- One move every two seconds
- Approximately 5 million moves per second
- Estimated incoming traffic
- Estimated outgoing traffic

---

# Docker Deployment

- Gateway Containers
- Identity Containers
- Lobby Containers
- Session Directory Containers
- Game Service Containers
- Rating Containers

---

# Kubernetes / K3s

- Container orchestration
- Auto scaling
- Load balancing
- Health checks
- Restart failed containers
- Service discovery

---

# Failure Scenarios

- Gateway failure
- Game Service failure
- Redis failure
- PostgreSQL failure

---

# Future Improvements

- Multi-region deployment
- Global load balancing
- Dedicated spectator service
- Replay service
