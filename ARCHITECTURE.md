# Architecture

## Overview

This project implements a real-time Kung Fu Chess engine. Responsibilities are
split into focused layers, and dependencies point toward the domain rather than
toward UI or transport implementations.

## High-level layers

- **Application** creates dependencies and owns process lifecycle.
- **Controller** maps offline user input to game operations.
- **Game** coordinates gameplay through the `GameEngine` facade.
- **Rules** validates chess movement independently of rendering and animation.
- **Realtime** owns simulation, timing, motion, airborne state, and collisions.
- **Model** stores board, piece, and position data.
- **Network** adapts commands and domain events to the WebSocket protocol.
- **UI** renders state and collects user input without deciding game rules.

## Offline startup flow

```text
main.py
  -> DesktopApplicationFactory
       -> GameEngineFactory -> GameEngine
       -> Controller
       -> GameSceneFactory -> GameScene
       -> GameApplication -> GameLoop
```

## Multiplayer server startup flow

```text
network/server/main.py
  -> GameEngineFactory -> GameEngine
  -> authentication, rating, and reconnect services
  -> GameServer
       -> WebSocket lifecycle
       -> ClientMessageRouter
       -> GameRuntime
       -> GameEventPublisher
```

`GameServer` is a thin lifecycle facade. It composes focused handlers and
services but delegates authentication, lobby operations, command handling,
match sessions, event publication, messaging, and simulation to those
components.

## Offline input flow

```text
Mouse
  -> Controller
  -> GameEngine
  -> RequestMoveService
  -> RuleEngine
  -> RealTimeArbiter
```

## Rendering flow

```text
GameLoop
  -> GameScene
  -> BoardRenderer
  -> PieceRenderer
  -> PieceAnimationService
  -> Canvas
```

Multiplayer clients render a `RemoteGameState` reconstructed from authoritative
server snapshots and events. They do not run a second authoritative simulation.

## Multiplayer command flow

```text
NetworkClient
  -> WebSocket
  -> GameServer.handle_message
  -> ClientMessageRouter
  -> CommandParser
  -> GameCommandHandler
  -> GameEngine
  -> authoritative snapshot or command response
```

The transport parser validates external message shape and primitive types.
Ownership and gameplay legality remain server-side responsibilities.

## Multiplayer event flow

The game layer publishes immutable domain events without depending on network
code. The transport layer converts supported events into JSON-safe payloads:

```text
GameEngine / Realtime
  -> EventBus
  -> GameEventPublisher
  -> GameEventSerializer
  -> ClientMessenger
  -> players and spectators
  -> RemoteGameState
  -> UI activity and status displays
```

`GameEventType` lives in the shared `network` package because its values are
wire-protocol discriminators, not domain state. Both `GameEventSerializer` and
`RemoteGameState` use it. The domain event classes remain in
`events/game_events.py`, preserving the boundary between gameplay and
transport.

The supported network game-event types are:

- `move_started`
- `move_completed`
- `jump_started`
- `jump_completed`
- `score_changed`
- `game_over`

## Layer responsibilities

### Application

Starts the application, creates dependencies, and owns the main loop or server
lifecycle.

### Controller

Receives offline user input, maps screen coordinates, and requests actions from
`GameEngine`. It contains no game rules.

### Game

Acts as the gameplay facade and coordinates focused services. It does not
perform rendering or depend on a UI implementation.

### Rules

Calculates legal moves. It is independent from rendering, animation, and
network transport.

### Realtime

Owns simulation timing, collisions, airborne logic, and active motions.

### Model

Stores game state without rendering or transport behavior.

### Network

Owns WebSocket lifecycle, external command parsing, JSON serialization,
authoritative publication, and remote client state reconstruction. It adapts
the domain rather than moving transport concerns into it.

### UI

Draws game state, displays animations, and collects input. It never decides
game rules.

## Important principles

- Game coordination belongs to Game.
- Movement validation belongs to Rules.
- Simulation belongs to Realtime.
- Data belongs to Model.
- Protocol adaptation belongs to Network.
- Rendering belongs to UI.
- Application entry points create dependencies.

## Design goals

- High cohesion
- Low coupling
- Single Responsibility Principle
- Encapsulation
- Small public APIs
- Composition over inheritance
- Readability
- Testability
