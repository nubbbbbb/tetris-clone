# Tetris

A Python implementation of the classic Tetris game using pygame, featuring modern Tetris mechanics including SRS+ from Tetr.io, All-mini+ spin detection from Tetr.io, Hold functionality and a 5 piece next queue (adjustable in code).

## Features

- **7 Tetromino Pieces**: All standard Tetris pieces (I, O, T, S, Z, J, L) with proper rotation mechanics
- **Super Rotation System+ (SRS+)**: Authentic rotation kicks based on Tetr.io's system
- **Piece Hold**: Hold a piece and swap it with the next falling piece
- **Next Queue**: Preview the next pieces to be played
- **Line Clear Detection**: Automatic detection of cleared lines with visual feedback
- **Back-to-Back Tracking**: B2B counter for consecutive line clears
- **Spin Detection**: Recognition of T-spins and other rotation-based placements
- **Configurable Settings**: Adjust DAS, ARR, and frame rate via `settings.json`
- **Custom UI**: Clean game board with held piece display, next queue preview, and line clear statistics

## Requirements

- Python 3.7+
- pygame

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Tetris.git
cd Tetris
```

2. Install dependencies:
```bash
pip install pygame
```

3. Run the game:
```bash
python tetris.py
```

## Configuration

Edit `settings.json` to customize game settings:

```json
{
    "Framerate": 60,
    "DAS": 167,
    "ARR": 33,
    "SDF": 33
}
```

- **Framerate**: Game update frequency (frames per second)
- **DAS** (Delayed Auto Shift): Milliseconds before horizontal movement repeats
- **ARR** (Auto Repeat Rate): Milliseconds between repeated horizontal movements
- **SDF** (Soft Drop Factor): Soft drop speed multiplier

## Game Controls

| Action | Key |
|--------|-----|
| Move Left | ← |
| Move Right | → |
| Soft Drop | ↓ |
| Rotate Clockwise | X or Up |
| Rotate Counter-Clockwise | Z |
| Rotate 180 degrees | A |
| Hard drop | Space |
| Hold Piece | C |
| Reset game | R |

*Note: Actual controls may vary based on implementation. Check the code for exact keybindings.*

## Project Structure

- `tetris.py` - Main game file containing all game logic and rendering
- `settings.json` - Configuration file for game parameters
- `README.md` - This file

## How to Play

1. Start the game by running `python tetris.py`
2. Tetromino pieces appear at the top of the board
3. Use arrow keys to move pieces left/right/down and rotate them
4. Complete horizontal lines to clear them
5. The game ends when pieces reach the top of the playing field

## Technical Details

### Piece Rotation
The game implements the Standard Tetris Rotation System+ (SRS+) with rotation kicks, allowing pieces to rotate in confined spaces when a direct rotation would cause a collision.

### Board Dimensions
- Width: 10 columns
- Height: 23 rows (with 20 rows as the playable area)

### Color Scheme
Each piece has a distinct color:
- I: Cyan
- O: Yellow
- T: Purple
- S: Green
- Z: Red
- J: Blue
- L: Orange

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests with improvements.
