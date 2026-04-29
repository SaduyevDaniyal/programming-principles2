# TSIS4 Snake Game

Minimal Snake implementation with PostgreSQL leaderboard and advanced gameplay.

## Features

- Username entry in Pygame menu
- PostgreSQL tables: players and game_sessions
- Save result after game over
- Top 10 leaderboard screen
- Personal best during gameplay
- Weighted food with timeout
- Poison food shortens snake by 2
- Power-ups: speed, slow, shield
- Obstacles from level 3
- Settings saved in settings.json
- Main Menu, Game Over, Leaderboard, Settings screens

## Setup

Create PostgreSQL database:

```sql
CREATE DATABASE snake;
```

Create `database.ini` from `database.ini.example`:

```ini
[postgresql]
host=localhost
database=snake
user=your_user
password=
port=5432
```

## Run

```bash
pip install pygame psycopg2-binary
python3 main.py
```

## Controls

- Arrow keys: move snake
- Menu: type username, press Enter or Play
