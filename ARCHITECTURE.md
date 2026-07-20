# Architecture

## Overview

This project implements a real-time Kung Fu Chess engine.

The architecture intentionally separates responsibilities into independent layers.

Each layer owns a single responsibility.

---

# High-Level Layers

Application
Controller
Game
Realtime
Rules
Model
UI

Dependencies always point downward.

UI never contains game logic.

Rules never know about rendering.

Realtime never performs rendering.

---

# Startup Flow

```text
main.py
  -> DesktopApplicationFactory
       -> GameEngineFactory -> GameEngine
       -> Controller
       -> GameSceneFactory -> GameScene
       -> GameApplication -> GameLoop
```

---

# Input Flow

Mouse

↓

Controller

↓

GameEngine

↓

RequestMoveService

↓

RuleEngine

↓

RealTimeArbiter

---

# Rendering Flow

GameLoop

↓

GameScene

↓

BoardRenderer

↓

PieceRenderer

↓

PieceAnimationService

↓

Canvas

---

# Layer Responsibilities

## Application

Starts the application.

Creates dependencies.

Owns the main loop.

---

## Controller

Receives user input.

Maps screen coordinates.

Requests actions from GameEngine.

Contains no game rules.

---

## Game

Acts as the facade of the gameplay.

Coordinates services.

Does not perform rendering.

Does not know UI implementation.

---

## Rules

Calculates legal moves.

Contains chess rules only.

Independent from rendering.

Independent from animation.

---

## Realtime

Owns simulation.

Owns timing.

Owns collisions.

Owns airborne logic.

Owns active motions.

---

## Model

Stores game state.

Contains no gameplay logic.

Contains no rendering logic.

---

## UI

Draws everything.

Shows animations.

Displays game state.

Never decides game rules.

---

# Important Principles

Game logic belongs to Game.

Rendering belongs to UI.

Movement validation belongs to Rules.

Simulation belongs to Realtime.

Data belongs to Model.

---

# Dependency Direction

UI
↓

Game
↓

Realtime

↓

Model

Rules are used by Game.

Application creates everything.

---

# Design Goals

- High cohesion
- Low coupling
- Single Responsibility Principle
- Encapsulation
- Small public APIs
- Composition over inheritance
- Readability
- Testability
