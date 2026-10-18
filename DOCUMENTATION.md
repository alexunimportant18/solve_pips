# solve_pips

A solver for the NYT Pip puzzles. This project implements a backtracking algorithm with constraint propagation to place dominoes on a grid such that all puzzle constraints are satisfied.

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [API Reference](#api-reference)
5. [Examples](#examples)
6. [Contributing](#contributing)

## Installation

\`\`\`bash
# Clone the repository
git clone <repository-url>
cd solve_pips

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate

# Install dependencies
pip install pydantic termcolor
\`\`\`

## Quick Start

You can run the solver by providing a puzzle definition in either TOML or CSV format.

**Using a TOML file:**
\`\`\`bash
python solve_pips.py --toml puzzle.toml
\`\`\`

**Using a CSV file:**
\`\`\`bash
python solve_pips.py --csv puzzle.csv
\`\`\`

## Architecture

### Project Structure
```
.
├── board.py          # Board state management and local constraint checks
├── combination.py    # Type definitions for number combinations
├── constraint.py     # Constraint types and definitions
├── direction.py      # Enumeration for domino placement directions
├── domino.py         # Domino representation and utilities
├── options.py        # CLI argument parsing
├── position.py       # Grid coordinate representation
├── readfile.py       # Puzzle file parsers (TOML/CSV)
├── solve.py          # Core recursive backtracking solver
└── solve_pips.py     # Main entry point
```

### Component Overview
- **Solver (`solve.py`)**: Implements a recursive backtracking search. It uses a fail-state cache (memoization) to avoid re-exploring identical board configurations.
- **Board (`board.py`)**: Manages the 2D grid, handles domino placement, and validates partial and full constraints. It also pre-calculates possible dominoes for each cell to prune the search space.
- **Constraints (`constraint.py`)**: Defines various puzzle rules such as `TOTAL` (sum of pips), `VALUE` (exact pip count), `EQUAL` (same value), `NE` (different values), and `LT/GT` (less than/greater than).
- **Parsing (`readfile.py`)**: Converts external puzzle descriptions into `Board` and `Domino` objects.

### Design Patterns
- **Strategy Pattern**: Used via `PipsPuzzleReader` to support multiple input formats (TOML, CSV).
- **Backtracking**: The core algorithm for exploring the state space of domino placements.
- **Constraint Satisfaction**: Pre-filtering possible dominoes for each cell based on constraints.

## API Reference

### Module: `board`
Manages the grid state and constraints.

#### Class `Board`
**Constructor:**
\`\`\`python
def __init__(self, width: int, height: int):
\`\`\`
- `width` (int): Board width.
- `height` (int): Board height.

**Key Methods:**
- `add_constraint(constraint: Constraint)`: Adds a rule to the board.
- `generate_possible_dominoes(available_dominoes: set[Domino])`: Pre-filters which dominoes can fit in which cells.
- `place_domino(domino: Domino, position: Position, direction: Direction) -> bool`: Attempts to place a domino and checks if partial constraints are still valid.

### Module: `solve`
Contains the recursive search logic.

#### Function `solve`
**Signature:**
\`\`\`python
def solve(board: Board, available_dominoes: set[Domino]) -> tuple[Board, set[Domino]] | None:
\`\`\`
- **Description**: Recursively attempts to fill the board.
- **Returns**: A tuple of the solved `Board` and remaining dominoes if a solution is found; otherwise `None`.

### Module: `readfile`
Parses puzzle files.

#### Function `get_puzzle_reader`
**Signature:**
\`\`\`python
def get_puzzle_reader(filename: str) -> PipsPuzzleReader:
\`\`\`
- **Returns**: An instance of `TomlPuzzleReader` or `CsvPuzzleReader` based on file extension.

## Examples

### Example 1: Basic Usage
Run the program with a CSV file:
\`\`\`bash
python solve_pips.py --csv test.csv
\`\`\`
The program will output the domino set used, a visualization of the constraints, and the final solved grid with colored dominoes.

## Troubleshooting

### Common Issues

**Issue**: "Unsupported file format"
**Solution**: Ensure your puzzle file ends with `.toml` or `.csv`.

**Issue**: "No solution found"
**Solution**: Verify the puzzle input is correct and that the set of provided dominoes can actually satisfy the constraints.

## License

Refer to the `LICENSE` file in the project root.
