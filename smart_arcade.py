#!/usr/bin/env python3
import curses
import os
import sys

def draw_menu(stdscr, selected_row_idx):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    title = "=== BORNE INTERACTIVE SMART-ARCADE ==="
    stdscr.addstr(2, w//2 - len(title)//2, title, curses.A_BOLD)

    options = [
        "1. RETROGAMING  (EmulationStation)",
        "2. KARAOKE      (UltraStar Deluxe)",
        "3. DARTSCAB     (Fléchettes)",
        "4. QUIZ SHOW    (Serveur Smartphone)",
        "5. VEILLE       (Diaporama & Météo)",
        "6. ETEINDRE LA BORNE"
    ]

    for idx, row in enumerate(options):
        x = w//2 - len(row)//2
        y = h//2 - len(options)//2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, row)

    footer = "Utilisez les flèches HAUT/BAS et ENTREE pour valider"
    stdscr.addstr(h-3, w//2 - len(footer)//2, footer, curses.A_DIM)
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    current_row = 0

    while True:
        draw_menu(stdscr, current_row)
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < 5:
            current_row += 1
        elif key in [10, 13, curses.KEY_ENTER]:
            stdscr.clear()
            if current_row == 0:
                stdscr.addstr(10, 10, "Mode Retrogaming non encore installe (Test OK)")
            elif current_row == 1:
                stdscr.addstr(10, 10, "Mode Karaoke non encore installe (Test OK)")
            elif current_row == 2:
                stdscr.addstr(10, 10, "Mode DartsCab non encore installe (Test OK)")
            elif current_row == 3:
                stdscr.addstr(10, 10, "Mode Quiz non encore installe (Test OK)")
            elif current_row == 4:
                stdscr.addstr(10, 10, "Lancement Ecran de veille Météo/Photos...")
            elif current_row == 5:
                os.system("sudo shutdown -h now")
                break
            stdscr.refresh()
            stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
