## Configurable Parameters

### 1. Board Dimensions
- **MAX_COLS** and **MAX_ROWS**
  - These define the maximum dimensions of the board.
  - By default, the board is 4x4, but you can change the dimensions through the GUI by setting new rows and columns.

### 2. Simulation Parameters
- **sims** (Default: 359)
  - The number of independent games to simulate with random moves.

- **depth** (Default: 100)
  - The maximum depth (number of moves) for each simulation.

You can override these defaults by providing parameters when calling the `simulate_game()` function from the `Tw48AiAssistant` class.

---
