# TI4Botten

A Discord bot for Twilight Imperium 4th Edition, featuring faction randomization and more.

## Features
- Randomly select TI4 factions, optionally filtered by expansion/source
- **Trivia Game**: Play TI4 trivia with custom questions and leaderboards
- Discord command interface
- Extensible bot architecture

## Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/fsharpasharp/TI4Botten.git
   cd TI4Botten
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Add your Discord bot token to a file named `.token` in the project root.

## Usage
Run the bot:
```sh
python app.py
```

### Commands

#### Trivia Game
- `!trivia` - Show trivia commands help
- `!trivia start` - Start a new trivia session in the current channel
- `!trivia next` - Get the next random question
- `!trivia answer <your_answer>` - Answer the current question
- `!trivia scores` - Show current session scores
- `!trivia add <question> | <answer> | [category]` - Add a custom question
- `!trivia list [category]` - List available questions
- `!trivia stop` - Stop the current session (creator only)

**Tip**: Use temporary channels or threads for trivia sessions to keep answers private and non-searchable!

## Database
This project uses SQLAlchemy ORM with SQLite (`app.db`). Tables are auto-created on first run. See `src/game/model.py` and `src/trivia/model.py` for models.

To seed the database with default TI4 trivia questions:
```sh
python src/trivia/seed_questions.py
```

## Testing
Run all tests:
```sh
pytest
```
Test coverage includes bot commands and faction logic. See `tests/` and `src/game/tests/` and `src/trivia/tests/`.

## Project Structure
- `app.py` — Main entrypoint for the bot
- `src/bot.py` — Bot and command definitions
- `src/game/commands.py` — Game-related Discord commands (uses ORM)
- `src/game/factions.py` — Faction logic and data loading
- `src/game/model.py` — SQLAlchemy ORM models
- `src/game/tests/` — Faction logic tests
- `src/trivia/commands.py` — Trivia game Discord commands
- `src/trivia/model.py` — Trivia database models
- `src/trivia/trivialogic.py` — Trivia game logic
- `src/trivia/tests/` — Trivia game tests
- `tests/` — Bot command tests

## Contributing
Pull requests and issues are welcome!