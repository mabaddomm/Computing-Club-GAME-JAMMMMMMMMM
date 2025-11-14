# Computing-Club-GAME-JAMMMMMMMMM

A simple 2D game framework built with Python and pygame-ce.

## Quick Start

### 1. Create and activate virtual environment

```bash
python -m venv .venv
```

**Windows:**
```bash
.venv\Scripts\activate.bat        # Command Prompt
.\.venv\Scripts\Activate.ps1     # PowerShell
source .venv/Scripts/activate    # Git Bash
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the game

```bash
python main.py
```

## Project Structure

- `game/` - Core framework
- `game_objects/` - Game entities (players, enemies, items, etc.)
- `ui_elements/` - UI components (buttons, text, HUD, etc.)
- `scenes/` - Game scenes
- `levels/` - Game levels
- `config/` - Settings and constants
- `assets/` - Images, sounds, fonts

See `STRUCTURE.md` for detailed organization guide.

## Troubleshooting

**PowerShell activation fails:** Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**SSL errors:** Update pip with `python -m pip install --upgrade pip`
