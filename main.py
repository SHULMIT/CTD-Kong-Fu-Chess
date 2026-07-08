# main.py

import sys
# TODO: Update with actual repository URL as required by reviewer
# Repository URL: https://github.com/your-username/kong-fu-chess-repo

from io.text_board_parser import TextBoardParser
from io.text_board_formatter import TextBoardFormatter

def main():
    # קריאת כל הקלט מה-Standard Input
    input_data = sys.stdin.read().strip().splitlines()
    
    board_lines = []
    command_lines = []
    parsing_mode = None

    # הפרדת הקלט לחלק של הלוח ולחלק של הפקודות
    for line in input_data:
        stripped_line = line.strip()
        if stripped_line == "Board:":
            parsing_mode = "board"
            continue
        elif stripped_line == "Commands:":
            parsing_mode = "commands"
            continue
        
        if parsing_mode == "board" and stripped_line:
            board_lines.append(stripped_line)
        elif parsing_mode == "commands" and stripped_line:
            command_lines.append(stripped_line)

    # ניסיון לפענח את הלוח (זריקת שגיאות במקרה של קלט לא תקין)
    try:
        board = TextBoardParser.parse(board_lines)
    except ValueError as e:
        print(str(e))
        return

    # ביצוע הפקודות
    for cmd in command_lines:
        if cmd == "print board":
            print(TextBoardFormatter.format(board))

if __name__ == "__main__":
    main()