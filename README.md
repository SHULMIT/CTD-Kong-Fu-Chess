# Kung Fu Chess

Kung Fu Chess is a real-time desktop chess game written in Python. Unlike
turn-based chess, pieces move over time, can jump, collide, capture, and enter
short recovery states while the simulation continues.

The project supports two modes:

- **Offline mode** runs the game engine and desktop interface in one process.
- **Multiplayer mode** uses an authoritative WebSocket server. Clients send
  commands, but only the server validates moves, advances the simulation, and
  publishes the resulting state.

Multiplayer includes desktop login and registration, persistent accounts and
ELO ratings, rating-based matchmaking, private rooms, temporary reconnects,
read-only spectators, and structured server logging.

## Main features

- Real-time offline Kung Fu Chess gameplay.
- Rule-based movement for all standard chess pieces.
- Timed movement, jumping, collisions, captures, promotion, and game-over
  detection.
- Server-authoritative WebSocket multiplayer on `ws://127.0.0.1:8765` by
  default.
- Desktop registration and login backed by SQLite.
- Scrypt password hashing with a random salt for every password.
- Persistent ELO ratings, starting at 1200, with atomic result updates.
- Matchmaking between players whose ratings differ by no more than 100 points.
- Private rooms using short server-generated room codes.
- A 20-second server-authoritative reconnect window for interrupted games.
- Read-only spectator access to active games.
- JSON-lines console and rotating-file server logging with sensitive-data
  filtering.
- Automated unit, integration, system, UI, and network tests.

## Architecture

The codebase separates state, rules, orchestration, transport, and rendering.
The main dependency direction is from application and UI code toward focused
game, rules, realtime, and model components.

- `GameEngine` is the gameplay facade. It coordinates game services but does
  not know about WebSockets, SQLite, authentication, or UI widgets.
- Movement rules remain in the `rules` package. Realtime motion and collision
  behavior remain in `realtime`.
- The internal `EventBus` publishes immutable domain events for moves, jumps,
  scores, and game completion. Multiplayer serialization and broadcasting are
  outside the domain model.
- `GameServer` is the WebSocket boundary and authoritative source of truth. It
  parses client intent, enforces ownership, invokes existing game APIs, and
  broadcasts authoritative snapshots and events.
- Authentication, persistent ratings, matchmaking, private rooms, reconnect
  sessions, spectators, and logging are implemented as focused services.
- Multiplayer clients do not run an authoritative local `GameEngine`. Their
  `RemoteGameState` is rebuilt from server snapshots and events on the UI
  thread.
- Dependencies are created at application entry points rather than stored in
  global singletons.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the core engine layer overview.

## Project structure

```text
app/             Application composition and desktop application factories
authentication/ Server-side accounts, password hashing, and repositories
board_io/        Board parsing, loading, and text formatting
controller/      Offline input-to-game command adapter
events/          EventBus and immutable domain events
game/            GameEngine facade and focused gameplay services
matchmaking/     Thread-safe ELO matchmaking service
model/           Board, piece, and position data
network/         Commands, serializers, WebSocket server/client, and remote state
rating/          ELO calculation and persistent rating updates
realtime/        Motion, timing, airborne state, and collision handling
rooms/           Private-room lifecycle service
rules/           Piece movement and move validation rules
spectators/      Active-game and spectator membership registry
tests/           Unit, game, integration, system, UI, and network tests
tools/           Development and local multiplayer launch helpers
view/            Desktop UI, rendering, input, animation, and authentication views
main.py          Offline desktop entry point
run_multiplayer.bat  Windows local multiplayer launcher
```

## Requirements

The repository does not currently declare a minimum Python version in a
`pyproject.toml` or equivalent package metadata. The current test environment
has been verified with Python 3.14.5. Use a Python version supported by the
exact dependency versions in [`requirements.txt`](requirements.txt):

- `numpy==2.5.1`
- `opencv-python==5.0.0.93`
- `pytest==9.1.1`
- `websockets==16.1.1`

SQLite, `hashlib.scrypt`, `asyncio`, `tkinter`, and `logging` are used from the
Python standard library. A desktop environment is required for the OpenCV and
Tk GUI windows. The included `.bat` launcher is Windows-specific; the Python
module entry points can also be run directly on systems that provide the
required GUI support.

A virtual environment is strongly recommended.

## Installation

Clone the repository and enter its root directory:

```powershell
git clone https://github.com/SHULMIT/CTD-Kong-Fu-Chess.git
cd CTD-Kong-Fu-Chess
```

Create and activate a Windows virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell activation is restricted, the environment's Python executable
can be used directly without activation.

Install the pinned dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Running offline mode

From the repository root, with the virtual environment activated:

```powershell
python main.py
```

Without activation:

```powershell
.\.venv\Scripts\python.exe main.py
```

Offline mode does not require the WebSocket server or an account.

## Running multiplayer

### Windows launcher

The simplest local setup is to double-click `run_multiplayer.bat`, or run:

```powershell
.\run_multiplayer.bat
```

The launcher requires `.venv\Scripts\python.exe`. It starts one hidden local
server and two desktop clients, waits for both clients to close, and then stops
the server.

### Manual startup

Start the server in one terminal:

```powershell
.\.venv\Scripts\python.exe -m network.server_main
```

Start each client in a separate terminal. Repeat this command for additional
clients or spectators:

```powershell
.\.venv\Scripts\python.exe -m network.client_main
```

The default client URI is `ws://127.0.0.1:8765`. A different endpoint can be
selected with:

```powershell
.\.venv\Scripts\python.exe -m network.client_main --uri ws://127.0.0.1:8765
```

Restart existing server and client processes after changing the code; running
processes do not reload source files automatically.

## Multiplayer usage

1. Register a unique username with a password, or log in to an existing
   account.
2. After login, the multiplayer menu displays the authoritative username and
   current rating.
3. Select **Play** to enter ELO matchmaking. The search can be canceled while
   waiting. A match is created only for players within 100 rating points.
4. Select **Create Room** to receive a private room code. The creator can close
   the room before another player joins.
5. Select **Join Room** and enter a valid code to join its creator. The server
   supplies both player profiles, assigns white and black, and starts the game.
6. Select **Spectate Game** to request the active-game list and open a game by
   ID. Spectator clients receive updates but cannot issue game commands.
7. If a player connection is interrupted during a game, the server pauses new
   commands and allows 20 seconds for an automatic token-based resume. If the
   deadline expires, the connected opponent wins by forfeit and the existing
   ELO update flow runs once.

## Server command-line options

`network.server_main` supports the following options:

| Option | Default | Purpose |
| --- | --- | --- |
| `--host` | `127.0.0.1` | WebSocket bind address |
| `--port` | `8765` | WebSocket port |
| `--database` | `data/users.db` | SQLite database path |
| `--k-factor` | `32` | ELO K-factor |
| `--reconnect-timeout` | `20.0` | Resume window in seconds |
| `--log-level` | `INFO` | Server logging level |
| `--log-file` | `data/server.log` | Rotating log file path |
| `--log-max-bytes` | `2000000` | Maximum active log file size |
| `--log-backup-count` | `5` | Number of rotated files retained |

Example:

```powershell
.\.venv\Scripts\python.exe -m network.server_main `
  --host 127.0.0.1 `
  --port 8765 `
  --database data/users.db `
  --k-factor 32 `
  --reconnect-timeout 20 `
  --log-level INFO
```

## WebSocket protocol overview

Messages are JSON objects with a required `type`. The main categories are:

- **Authentication:** `register`, `login`, and structured success or failure
  responses.
- **Matchmaking:** start, queue status, cancellation, and `match_found`.
- **Private rooms:** create, join, cancel, room lifecycle responses, and room
  errors.
- **Gameplay:** move, jump, legal-destination requests, command responses,
  snapshots, and serialized game events.
- **Reconnect:** opaque resume-token delivery, `resume_session`, disconnect
  notices, resume responses, and timeout forfeits.
- **Spectators:** active-game listing, start/stop spectating, and read-only
  errors.
- **Ratings and profiles:** both player profiles and authoritative rating
  updates after a decisive completed game.

The protocol is intentionally server-authoritative. A client-provided username,
rating, color, game result, or board state is never accepted as authoritative.

## Database

The default SQLite database is `data/users.db`. Its parent directory and tables
are created safely when the server starts.

The schema contains:

- `users`: unique username, scrypt password hash, persistent rating, and
  creation timestamp. New accounts start at rating 1200.
- `game_results`: unique `game_id`, winner and loser user IDs, their resulting
  ratings, and completion timestamp.

Passwords are never stored as plaintext. `game_results.game_id` is the primary
key, so the same authoritative game result cannot update ratings more than
once. Both users' rating changes and the game-result insertion occur in one
SQLite transaction.

## Logging

The server writes structured JSON-lines records to both the console and
`data/server.log` by default. The file handler rotates at 2,000,000 bytes and
retains five backups.

Logged events include authentication outcomes, connections, matchmaking,
rooms, spectators, game lifecycle, reconnects, forfeits, rating updates, and
unexpected exceptions. Context such as `game_id`, `user_id`, `username`, and
`room_code` is included when available.

A logging filter redacts password, password-hash, token, and resume-token
values, including sensitive values embedded in nested mappings or common
inline text formats. Passwords and tokens are not intentionally passed to log
calls.

## Testing

Run the complete configured test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Run unit tests only:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit -q
```

Run multiplayer and WebSocket tests only:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\network -q
```

The repository's `pytest.ini` also includes game, integration, system, tools,
and UI test directories in the full suite. Test counts are intentionally not
hardcoded here because they change as coverage grows.

## Manual multiplayer test checklist

- [ ] Register two unique users and log in from both clients.
- [ ] Confirm that each menu shows the correct username and persistent rating.
- [ ] Start and cancel a normal matchmaking search.
- [ ] Match two users within 100 rating points and verify both profiles.
- [ ] Create a private room, join it by code, and start exactly one game.
- [ ] Complete a decisive game and confirm both ELO values refresh.
- [ ] Disconnect one active player and confirm the opponent sees the countdown.
- [ ] Reconnect within 20 seconds and confirm the same game and color resume.
- [ ] Let a reconnect deadline expire and confirm one forfeit and one ELO update.
- [ ] Open a third client, spectate the active game, and confirm move commands
      are rejected.
- [ ] Confirm the spectator view closes when the game ends.
- [ ] Inspect console output and `data/server.log` for structured lifecycle
      records without credentials or tokens.

## Security notes

- Passwords use the standard-library scrypt KDF with random salts and
  constant-time digest comparison.
- Authentication records, ratings, color ownership, room membership, resume
  identity, game state, and game results are controlled by the server.
- Resume tokens are opaque, generated with `secrets.token_urlsafe(32)`, rotated
  after a successful resume, and invalidated when the session is cleaned up.
- Spectators are rejected before their gameplay messages reach `GameEngine`.
- Server logging filters sensitive fields and inline secret patterns.
- Clients send intent only; they are not trusted to determine legality,
  captures, scores, winners, or rating changes.

## Known limitations

- The current server composition owns one authoritative `GameEngine`, so it
  supports one active game at a time rather than multiple concurrent game
  rooms.
- Reconnect state is held in server memory and is not recovered after a server
  restart.
- Matchmaking uses a fixed 100-point rating range; it does not expand over time.
- There is no chat, bot play, invitation system, or long-term abandoned-game
  recovery.
- Multiple-device ownership of the same active participant is not supported.
- The supplied all-in-one launcher is Windows-specific and starts exactly two
  clients; additional clients must be launched manually.

## Development status

The major offline and local multiplayer features described above are
implemented and covered by automated tests. The project remains under active
development and should not be described as production-ready without additional
deployment, operational, and security review.

## License

No license file or license declaration is currently included in this
repository. No usage or redistribution license has been specified yet.
