# CTD-Kong-Fu-Chess

# Chess Engine

A modular object-oriented chess engine developed in Python as part of an academic software engineering project.

## Overview

This project implements the core logic of a chess engine with a strong emphasis on clean architecture, object-oriented design, and separation of responsibilities. The system supports board parsing, move validation, real-time movement, piece promotion, capturing, and a command-based testing interface.

## Features

- Object-oriented architecture
- Rule-based move validation
- Real-time movement management
- Chess piece promotion
- Piece capturing
- Board parser and formatter
- Script-driven test runner
- Clean separation between Model, Rules, Controller, and Game Engine

## Project Structure

```
board_io/
config/
controller/
game/
model/
realtime/
rules/
runner/
```

## Technologies

- Python
- Object-Oriented Programming (OOP)
- SOLID Design Principles

## Design Principles

This project follows several software engineering best practices:

- Single Responsibility Principle (SRP)
- Separation of Concerns
- Factory Pattern
- Strategy Pattern
- Dependency Injection
- Modular Architecture

## Architecture Notes

Recent refactoring introduced thin facades and focused services:

- `realtime/real_time_arbiter.py`: orchestrates real-time flow only.
- `realtime/motion_timeline.py`: simulation clock and event slicing.
- `realtime/motion_step_planner.py`: selects and orders ready motion steps.
- `realtime/collision_resolver.py`: applies collision rules.
- `realtime/piece_lifecycle_service.py`: capture, promotion, and resolution flags.
- `realtime/airborne_manager.py`: jump timers and landing transitions.

- `game/game_engine.py`: stable facade for controller-facing API.
- `game/request_move_service.py`: move validation and motion scheduling.
- `game/game_state_service.py`: game-over state and wait/jump transitions.
- `game/game_query_service.py`: board query operations.

This keeps responsibilities separated while preserving external behavior.

## Running

Run the project with:

```bash
python main.py
```

## Status

This project is actively developed as part of a university chess engine assignment.

## Author

Developed by Shulamit s
