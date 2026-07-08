# main.py

import sys
# URL: https://github.com/your-username/kong-fu-chess-repo

from board_io.text_board_parser import TextBoardParser
from board_io.text_board_formatter import TextBoardFormatter
from core.game import Game

def _parse_input_sections(input_lines):
    # מחלקת את שורות הקלט לחלק של הלוח ולחלק של הפקודות
    board_lines = []
    command_lines = []
    mode = None

    for line in input_lines:
        stripped_line = line.strip()
        if stripped_line == "Board:":
            mode = "board"
            continue
        elif stripped_line == "Commands:":
            mode = "commands"
            continue
        
        if mode == "board" and stripped_line:
            board_lines.append(stripped_line)
        elif mode == "commands" and stripped_line:
            command_lines.append(stripped_line)
            
    return board_lines, command_lines

def _execute_command(game, command_line):
    # מפענחת ומבצעת פקודה בודדת
    tokens = command_line.split()
    if not tokens:
        return

    action = tokens[0]
    
    if action == "click" and len(tokens) == 3:
        game.click(int(tokens[1]), int(tokens[2]))
        
    elif action == "wait" and len(tokens) == 2:
        game.wait(int(tokens[1]))
        
    elif action == "print" and len(tokens) == 2 and tokens[1] == "board":
        print(TextBoardFormatter.format(game.board))

def main():
    # 1. קריאת קלט
    input_data = sys.stdin.read().strip().splitlines()
    board_lines, command_lines = _parse_input_sections(input_data)

    # 2. אתחול הלוח
    try:
        board = TextBoardParser.parse(board_lines)
    except ValueError as e:
        print(str(e))
        return

    # 3. יצירת המשחק והרצת הפקודות
    game = Game(board)
    for cmd_line in command_lines:
        _execute_command(game, cmd_line)

if __name__ == "__main__":
    main()