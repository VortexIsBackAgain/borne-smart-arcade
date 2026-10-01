#!/usr/bin/env python3
"""
Composant réutilisable : légende manette façon Recalbox (△ ✕ ○ □)
À appeler en toute fin de chaque fonction draw_*_screen, juste avant
pygame.display.flip().
"""
import pygame

LEGEND_BG = (25, 33, 45)
TEXT_WHITE = (240, 240, 240)
TEXT_MUTED = (150, 160, 180)

SYMBOL_COLORS = {
    "✕": (0, 162, 232),   # Bleu - Valider
    "○": (220, 60, 60),   # Rouge - Annuler/Retour
    "△": (40, 200, 100),  # Vert - Action secondaire
    "□": (220, 160, 40),  # Orange - Action tertiaire
    "◄►▲▼": (150, 160, 180),  # Gris - Navigation
}

def draw_legend(screen, font, actions):
    """
    Dessine une barre de légende en bas de l'écran.
    actions : liste de tuples (symbole, label), ex :
        [("◄►▲▼", "Naviguer"), ("✕", "Valider"), ("○", "Retour")]
    """
    WIDTH, HEIGHT = screen.get_size()
    bar_h = int(HEIGHT * 0.055)
    bar_y = HEIGHT - bar_h

    pygame.draw.rect(screen, LEGEND_BG, (0, bar_y, WIDTH, bar_h))

    spacing = int(WIDTH * 0.03)
    rendered = []
    total_w = 0
    for symbol, label in actions:
        color = SYMBOL_COLORS.get(symbol, TEXT_MUTED)
        sym_surf = font.render(symbol, True, color)
        lbl_surf = font.render(label, True, TEXT_WHITE)
        item_w = sym_surf.get_width() + 8 + lbl_surf.get_width()
        rendered.append((sym_surf, lbl_surf, item_w))
        total_w += item_w + spacing
    total_w -= spacing

    x = (WIDTH - total_w) // 2
    y_center = bar_y + bar_h // 2

    for sym_surf, lbl_surf, item_w in rendered:
        screen.blit(sym_surf, (x, y_center - sym_surf.get_height() // 2))
        screen.blit(lbl_surf, (x + sym_surf.get_width() + 8, y_center - lbl_surf.get_height() // 2))
        x += item_w + spacing


LEGEND_NAVIGATE_VALIDATE_BACK = [
    ("◄►▲▼", "Naviguer"),
    ("✕", "Valider"),
    ("○", "Retour"),
]

LEGEND_VALIDATE_BACK_ONLY = [
    ("✕", "Valider"),
    ("○", "Retour"),
]

LEGEND_BACK_ONLY = [
    ("○", "Retour"),
]

LEGEND_NAVIGATE_VALIDATE = [
    ("◄►▲▼", "Naviguer"),
    ("✕", "Valider"),
]
