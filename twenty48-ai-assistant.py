"""
Script Name:    twenty48-ai-assistant.py
Description:    An AI Assistant to help you win the 2048 game in your smartwatch.
Author:         Mario Montoya <marioSGHT500@gmail.com>
Date:           2024-12-30

Version History:
- v0.1 (2024-12-30): It creates the Tw48AiAssistant class and uses niceGUI to use the class.

Copyright 2024 Mario Montoya

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from nicegui import ui
import random
import copy
import asyncio

class Tw48AiAssistant:
    "2048 AI Assistant. To help you win the 2048 game on your smartwatch."

    def __init__(self, board):
        "Initialize the 2048 AI Assistant with the current board."
        self.board = board

    def print_board(self):
        "Print the current board."
        print("\n".join(["\t".join(map(str, row)) for row in self.board]))
        print("-" * 20)

    def __slide_and_merge(self, row):
        "Slie and Merge one row to the left."
        "Returns: The merged row and the score for that merge."
        non_zero = [num for num in row if num != 0]  # Remove zeros
        new_row = []
        score = 0  # Initialize score for this row
        i = 0
        while i < len(non_zero):
            if i < len(non_zero) - 1 and non_zero[i] == non_zero[i + 1]:  # Check for a merge
                new_row.append(non_zero[i] * 2)  # Merge tiles
                score += new_row[-1]  # Add merged value to the score
                i += 2  # Skip the next tile since it was merged
            else:
                new_row.append(non_zero[i])  # No merge, just move the tile
                i += 1
        # Pad with zeros to maintain the row length
        new_row.extend([0] * (len(row) - len(new_row)))
        return new_row, score

    def __rotate_board(self, board, rotations):
        "Rotate a board clockwise by 'rotations' times"
        for _ in range(rotations % 4):
            board = [list(row) for row in zip(*board[::-1])]
        return board

    def __move_a_board(self, board, direction):
        "Slide a board in the direction provided"
        "Return: The new board and the score of that move"
        rotated_board = self.__rotate_board(board, direction)  # Rotate board based on direction.

        merged_score = 0  # Initialize the total score for the move.
        new_board = []
        for row in rotated_board:
            new_row, row_score = self.__slide_and_merge(row)  # Call slide_and_merge with score calculation.
            merged_score += row_score  # Accumulate the score from merged tiles.
            new_board.append(new_row)

        return self.__rotate_board(new_board, -direction), merged_score  # Rotate back to original orientation and return score.

    def valid_moves(self, board):
        "Return the valid moves of a board."
        directions = {"up": 3, "right": 2, "down": 1, "left": 0}
        valid = {}
        for dir_name, dir_val in directions.items():
            # Unpack the return value of move_board and compare only the board part
            if self.__move_a_board(board, dir_val)[0] != board:
                valid[dir_name] = dir_val
        return valid

    def __add_random_tile(self, board):
        empty_cells = [(r, c) for r in range(len(board)) for c in range(len(board[0])) if board[r][c] == 0]
        if not empty_cells:
            return False
        r, c = random.choice(empty_cells)
        board[r][c] = 2 if random.random() < 0.9 else 4
        return True

    def simulate_game(self, sims=349, depth=100):
        "Calculate the average score of every valid random move."
        directions = self.valid_moves(self.board)
        scores = {"up": [], "right": [], "down": [], "left": []}
        for _ in range(sims):
            sim_board = copy.deepcopy(self.board)
            first_move = None
            score = 0
            for _ in range(depth):
                valid = self.valid_moves(sim_board)
                if not valid:
                    break
                move = random.choice(list(valid.keys()))
                if first_move is None:
                    first_move = move
                sim_board, move_score = self.__move_a_board(sim_board, valid[move])
                score += move_score
                self.__add_random_tile(sim_board)
            if first_move:
                scores[first_move].append(score)
        return {move: sum(scores[move]) / len(scores[move]) if scores[move] else 0 for move in directions.keys()}

    def move_board(self, direction):
        "Move the real board and return the score of that move"
        self.board, move_score = self.__move_a_board(self.board, direction)
        return move_score

ROWS = 4
COLS = 4
MAX_ROWS = 7
MAX_COLS = 10
STAGE = 1  # 1=Setting up / 2=Moving / 3=Adding
# When adding a new tile: Which is the tile being toogled?
ROW = -1
COL = -1

lock = asyncio.Lock()  # To ensure atomic access to global variables
thinking = False  # Global variable to avoid double click issue
perfoming_move = False  # Global variable to avoid double click issue

# Global variables for exit conditions
GREETED = False # When a 2048 tile is found, display the congratulatory message only once.

# Define color mapping for the tiles based Daniel Huang's color pallet:
# https://github.com/daniel-huang-1230/Game-2048/blob/master/Gui2048.java
tile_colors = {
    0:'#BDAC97',
    2:'#eee4da',
    4:'#EBD8B6',
    8:'#F1AE72',
    16:'#F58F5A',
    32:'#F78063',
    64:'#F55934',
    128:'#edcf72',
    256:'#edcc61',
    512:'#edc850',
    1024:'#edc53f',
    2048:'#edc22e',
}

# Initialize the board state (ROWS x COLS grid)
board_state = [[0 for _ in range(COLS)] for _ in range(ROWS)]
tiles = [[None for _ in range(COLS)] for _ in range(ROWS)]

# Build the color mapping of the tiles
color_mapping = {
    f"r{row}c{col}": tile_colors[0]
    for row in range(MAX_ROWS) for col in range(MAX_COLS)
}
# Initialize the tile colors
ui.colors(**color_mapping)

# Function to create the board tiles
def create_tile(value, row, col):
    color = f'r{row}c{col}'
    return ui.button(f'{value}' if value != 0 else '',
                     color=color,
                     on_click=lambda: toggle_tile(row, col))

# Toggle the value of a tile when clicked
async def toggle_tile(row, col):
    if STAGE == 1:
        values = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 0]
    elif STAGE == 3:
        values = [2, 4, 0]
    else:
        return
    global ROW
    global COL
    current_value = board_state[row][col]
    if (STAGE == 1 or (STAGE == 3 and current_value == 0 and ROW == -1 and COL == -1) or \
        (STAGE == 3 and ROW == row and COL == col)):
        new_value = values[(values.index(current_value) + 1) % len(values)]
        board_state[row][col] = new_value
        if STAGE == 3:
            if new_value > 0:
                ROW=row
                COL=col
                continue_button.visible = True
                continue_button.enable()
            else:
                ROW=-1
                COL=-1
                continue_button.disable()
        await update_board()

# Update the board UI based on the board state
async def update_board():
    rows = int(rows_input.value)
    cols = int(cols_input.value)
    # Update the text of the tiles
    for row in range(rows):
        for col in range(cols):
            tiles[row][col].text = f'{board_state[row][col]}' if board_state[row][col] != 0 else ''
    await update_color_mapping()

async def update_color_mapping():
    rows = int(rows_input.value)
    cols = int(cols_input.value)
    # Dynamically build the color mapping of the tiles
    color_mapping = {
        f"r{row}c{col}": tile_colors[board_state[row][col]]
        for row in range(rows) for col in range(cols)
    }
    # Update all tile colors at once
    ui.colors(**color_mapping)
    ui.update() # Required in slower PCs.
    await asyncio.sleep(.25) # Required for ui self-refresh.

async def redraw_board():
    rows = int(rows_input.value)
    cols = int(cols_input.value)
    score_input.value = None
    board_row.clear()
    averages_column.clear()
    submit_button.visible = True
    global STAGE
    STAGE = 1
    global board_state
    board_state = [[0 for _ in range(cols)] for _ in range(rows)]
    global tiles
    tiles = [[None for _ in range(cols)] for _ in range(rows)]
    with board_row:
        for col in range(cols):
            with ui.column():
                for row in range(rows):
                    tiles[row][col] = create_tile(0, row, col)
    await update_color_mapping()

async def submit_board():
    global thinking
    async with lock:  # Protect access to variable
        if thinking:
            print("Already thinking. Ignoring click.")
            return
        thinking = True  # Mark as action in progress

    try:
        if score_input.value is None:
            ui.notify("Enter score first", type='negative')
            return
        if sum(sum(row) for row in board_state) == 0:
            ui.notify("Can't submit an empty board", type='negative')
            return
        submit_button.visible = False
        global t48
        t48 = Tw48AiAssistant(board_state)
        t48.print_board()
        averages_column.clear()
        with averages_column:
            with ui.card().tight():
                ui.label("Thinking...").style("background-color: #F3C546; padding: 7px; font-size: 16px; border-radius: 5px; text-align: center;")
        ui.update() # Required in slower PCs.
        await asyncio.sleep(.25) # Required for ui self-refresh.
        averages = t48.simulate_game()
        show_averages(averages)

    finally:
        async with lock:  # Ensure variable is reset, even if an exception occurs
            thinking = False

# Display move averages
def show_averages(averages):
    global STAGE
    STAGE = 2
    global ROW
    global COL
    ROW = -1
    COL = -1
    averages_column.clear()
    with averages_column:
        if not averages.keys():
            with ui.card().tight():
                ui.label("No more valid moves. Game over.").style( \
                    "background-color: #C00000; padding: 11px; font-size: 16px; color: white; border-radius: 5px; text-align: center;")
        else:
            with ui.row():
                with ui.column():
                    show_average_button(averages, 'dummy')
                    show_average_button(averages, 'left')
                with ui.column():
                    show_average_button(averages, 'up')
                    show_average_button(averages, 'down')
                with ui.column():
                    show_average_button(averages, 'dummy')
                    show_average_button(averages, 'right')

# Display an specific move average
def show_average_button(averages,move):
    arrows = {
        'up': '↑',
        'right': '→',
        'down': '↓',
        'left': '←',
    }
    if move in averages.keys():
        avg = averages[move]
        if avg == max(averages.values()):
            color = 'positive'
        elif avg == min(averages.values()):
            color = 'negative'
        else:
            color = 'dark'
        ui.button(f'{arrows[move]} {avg:.2f}', color=color, on_click=lambda m=move: perform_move(m))
    else:
        ui.button('* 000.00', color='dark_page').style('visibility: hidden;')

# Perform the chosen move and update the board
async def perform_move(direction):
    global perfoming_move
    async with lock:  # Protect access to performing_move
        if perfoming_move:
            print("Performing move. Ignoring click.")
            return
        perfoming_move = True  # Mark as action in progress

    try:
        global t48
        global board_state
        valid = t48.valid_moves(board_state)
        if direction not in valid:
            print("Direction", direction, "valid", valid)
            ui.notify(f'Move "{direction}" is not valid!', type='negative')
        else:
            move_score = t48.move_board(valid[direction])
            board_state = copy.copy(t48.board)
            await update_board()
            score_input.value += move_score
            averages_column.clear()
            global continue_button
            if move_score:
                ui.notify(f'+{move_score}', type='info')
            print(f'Moved "{direction}". Move score: {move_score}.')
            global STAGE
            STAGE=3
            with averages_column:
                continue_button = ui.button("Continue Game", color='secondary', \
                                            on_click=continue_game)
                continue_button.visible = False
                global GREETED
                if any(2048 in row for row in t48.board) and not GREETED:
                    with ui.card().tight():
                        ui.label("Congratulations! You reached 2048!").style( \
                            "background-color: #99FF66; padding: 11px; font-size: 16px; border-radius: 5px; text-align: center;")
                    GREETED = True
        ui.update() # Required in slower PCs.
        await asyncio.sleep(.25) # Required for ui self-refresh.

    finally:
        async with lock:  # Ensure performing_move is reset, even if an exception occurs
            perfoming_move = False

async def continue_game():
    global thinking
    async with lock:  # Protect access to variable
        if thinking:
            print("Already thinking. Ignoring click.")
            return
        thinking = True  # Mark as action in progress

    try:
        global t48
        t48.board = copy.copy(board_state)
        t48.print_board()
        averages_column.clear()
        with averages_column:
            with ui.card().tight():
                ui.label("Thinking...").style("background-color: #F3C546; padding: 7px; font-size: 16px; border-radius: 5px; text-align: center;")
        ui.update() # Required in slower PCs.
        await asyncio.sleep(.25) # Required for ui self-refresh.
        averages = t48.simulate_game()
        show_averages(averages)

    finally:
        async with lock:  # Ensure variable is reset, even if an exception occurs
            thinking = False

# Create the GUI using niceGUI
ui.page_title("Smartwatch 2048 AI Assistant")
with ui.card() as card:
    card.classes('w-full bg-[#756452] text-white')
    ui.label('Welcome to the Smartwatch 2048 AI Assistant').style(
        'border-radius: 0; font-size: 18px; font-weight: bold;')
with ui.row():
    with ui.column():
        rows_input = ui.number(label='Rows', value=ROWS, min=2, max=MAX_ROWS, on_change=redraw_board)
        cols_input = ui.number(label='Cols', value=COLS, min=2, max=MAX_COLS, on_change=redraw_board)
    with ui.column():
        score_input = ui.number(label='Score')
        # Create the ROWS x COLS board
        with ui.row() as board_row:
            for col in range(COLS):
                with ui.column():
                    for row in range(ROWS):
                        tiles[row][col] = create_tile(0, row, col)
        submit_button = ui.button('Submit Board', on_click=submit_board)
    averages_column = ui.column()

# Start the GUI
ui.run()

# The startup notice
print("""Smartwatch 2048 AI Assistant.
Copyright (C) 2024  Mario Montoya

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Mario Montoya <marioSGHT500@gmail.com>
""")