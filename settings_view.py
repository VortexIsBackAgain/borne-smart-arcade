#!/usr/bin/env python3
import os
import pygame
from legend_view import draw_legend, LEGEND_NAVIGATE_VALIDATE_BACK

DARK_BG = (18, 22, 30)
CARD_BG = (30, 40, 55)
ACCENT_BLUE = (0, 162, 232)
TEXT_WHITE = (240, 240, 240)
TEXT_MUTED = (150, 160, 180)

# Chargement sécurisé de l'icône manette
GAMEPAD_IMG_PATH = "/media/hdd/media/gamepad_icon.png"
gamepad_img = None
if os.path.exists(GAMEPAD_IMG_PATH):
    try:
        raw_img = pygame.image.load(GAMEPAD_IMG_PATH)
        gamepad_img = pygame.transform.smoothscale(raw_img, (28, 28))
    except:
        gamepad_img = None

def draw_settings_screen(screen, font_title, font_card, font_sub, selected_index, settings_state):
    WIDTH, HEIGHT = screen.get_size()
    screen.fill(DARK_BG)

    title_surf = font_title.render("PARAMÈTRES ET CONFIGURATION", True, TEXT_WHITE)
    screen.blit(title_surf, (int(WIDTH * 0.04), int(HEIGHT * 0.04)))

    options = [
        ("Afficher la Météo en haut", settings_state.get("show_weather", True)),
        ("Afficher l'Horloge en haut", settings_state.get("show_clock", True)),
        ("Afficher le Widget Stockage", settings_state.get("show_storage", True)),
        ("Gérer et Tester les Manettes", "MANETTES"),
        ("◄ RETOUR AU MENU PRINCIPAL", "RETOUR")
    ]

    start_y = int(HEIGHT * 0.18)
    opt_h = int(HEIGHT * 0.11)
    spacing = int(HEIGHT * 0.02)
    panel_w = int(WIDTH * 0.90)

    for i, (label, val) in enumerate(options):
        y = start_y + i * (opt_h + spacing)
        rect = pygame.Rect(int(WIDTH * 0.05), y, panel_w, opt_h)

        is_selected = (selected_index == i)
        bg_color = ACCENT_BLUE if is_selected else CARD_BG
        pygame.draw.rect(screen, bg_color, rect, border_radius=10)

        # Affichage du libellé avec l'icône manette pour la ligne d'appairage
        if i == 3 and gamepad_img:
            screen.blit(gamepad_img, (int(WIDTH * 0.08), y + opt_h // 2 - 14))
            lbl_surf = font_card.render(label, True, TEXT_WHITE)
            screen.blit(lbl_surf, (int(WIDTH * 0.08) + 38, y + opt_h // 2 - lbl_surf.get_height() // 2))
        else:
            lbl_surf = font_card.render(label, True, TEXT_WHITE)
            screen.blit(lbl_surf, (int(WIDTH * 0.08), y + opt_h // 2 - lbl_surf.get_height() // 2))

        if isinstance(val, bool):
            status_txt = "OUI [ON]" if val else "NON [OFF]"
            st_color = (100, 255, 100) if val else (255, 100, 100)
            st_surf = font_card.render(status_txt, True, st_color)
            screen.blit(st_surf, (int(WIDTH * 0.05) + panel_w - st_surf.get_width() - 30, y + opt_h // 2 - st_surf.get_height() // 2))

    draw_legend(screen, font_sub, LEGEND_NAVIGATE_VALIDATE_BACK)