#!/usr/bin/env python3
import os
import math
import shutil
import pygame
from legend_view import draw_legend, LEGEND_BACK_ONLY

DARK_BG = (18, 22, 30)
CARD_BG = (30, 40, 55)
ACCENT_BLUE = (0, 162, 232)
TEXT_WHITE = (240, 240, 240)
TEXT_MUTED = (150, 160, 180)
BAR_BG = (45, 55, 75)

PIE_COLORS = {
    "Rétrogaming": (0, 162, 232),
    "Karaoké": (200, 60, 200),
    "Dartscab": (230, 160, 40),
    "Quiz": (60, 200, 140),
    "Médias & Autres": (150, 160, 180),
    "Libre": (45, 55, 75),
}

HDD_ROOT = "/media/hdd"

CATEGORY_FOLDERS = {
    "Rétrogaming": ["roms", "bios", "saves"],
    "Karaoké": ["ultrastar"],
    "Dartscab": ["darts"],
    "Quiz": ["quiz"],
    "Médias & Autres": ["media", "backups", "scores"],
}

def get_dir_size(path):
    total = 0
    if not os.path.isdir(path):
        return 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            try:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total

def compute_hdd_breakdown():
    """Calcul lourd (parcourt les dossiers) : à appeler UNE SEULE FOIS
    à l'entrée de l'écran Storage, jamais dans la boucle d'affichage."""
    breakdown = {}
    for category, folders in CATEGORY_FOLDERS.items():
        total = 0
        for folder in folders:
            total += get_dir_size(os.path.join(HDD_ROOT, folder))
        breakdown[category] = total

    try:
        hdd_stat = shutil.disk_usage(HDD_ROOT)
        breakdown["Libre"] = hdd_stat.free
    except OSError:
        breakdown["Libre"] = 0

    return breakdown

def draw_pie_chart(screen, center, radius, breakdown):
    total = sum(breakdown.values())
    if total == 0:
        return
    start_angle = -90  # démarre en haut
    for category, value in breakdown.items():
        if value <= 0:
            continue
        sweep = (value / total) * 360
        color = PIE_COLORS.get(category, TEXT_MUTED)

        points = [center]
        steps = max(2, int(sweep / 2))
        for i in range(steps + 1):
            angle = math.radians(start_angle + sweep * i / steps)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(screen, color, points)
        start_angle += sweep

def draw_pie_legend(screen, font_sub, breakdown, x, y, line_h):
    total = sum(breakdown.values())
    for i, (category, value) in enumerate(breakdown.items()):
        color = PIE_COLORS.get(category, TEXT_MUTED)
        gb = value / (1024**3)
        pct = (value / total * 100) if total > 0 else 0

        swatch_y = y + i * line_h
        pygame.draw.rect(screen, color, (x, swatch_y, 18, 18), border_radius=4)

        label = f"{category} : {gb:.1f} Go ({pct:.0f}%)"
        lbl_surf = font_sub.render(label, True, TEXT_WHITE)
        screen.blit(lbl_surf, (x + 28, swatch_y - 2))

def draw_storage_screen(screen, font_title, font_card, font_sub, selected_index, hdd_breakdown=None):
    WIDTH, HEIGHT = screen.get_size()
    screen.fill(DARK_BG)

    title_surf = font_title.render("ANALYSE DU STOCKAGE DISQUE", True, TEXT_WHITE)
    screen.blit(title_surf, (int(WIDTH * 0.04), int(HEIGHT * 0.04)))

    sd_stat = shutil.disk_usage("/")
    sd_used_gb = (sd_stat.total - sd_stat.free) / (1024**3)
    sd_total_gb = sd_stat.total / (1024**3)

    panel_w = int(WIDTH * 0.40)
    panel_h = int(HEIGHT * 0.55)

    # Carte SD (inchangé)
    rect_sd = pygame.Rect(int(WIDTH * 0.04), int(HEIGHT * 0.16), panel_w, panel_h)
    pygame.draw.rect(screen, CARD_BG, rect_sd, border_radius=12)

    t_sd = font_card.render("Carte SD (Système)", True, ACCENT_BLUE)
    screen.blit(t_sd, (int(WIDTH * 0.06), int(HEIGHT * 0.20)))

    sd_txt = font_sub.render(f"Occupation : {sd_used_gb:.1f} Go / {sd_total_gb:.1f} Go", True, TEXT_WHITE)
    screen.blit(sd_txt, (int(WIDTH * 0.06), int(HEIGHT * 0.28)))

    pygame.draw.rect(screen, BAR_BG, (int(WIDTH * 0.06), int(HEIGHT * 0.35), panel_w - 50, 20), border_radius=5)
    pct_sd = sd_used_gb / sd_total_gb
    pygame.draw.rect(screen, ACCENT_BLUE, (int(WIDTH * 0.06), int(HEIGHT * 0.35), int((panel_w - 50) * pct_sd), 20), border_radius=5)

    # Camembert SSD par module
    rect_hdd = pygame.Rect(int(WIDTH * 0.50), int(HEIGHT * 0.16), int(WIDTH * 0.46), panel_h)
    pygame.draw.rect(screen, CARD_BG, rect_hdd, border_radius=12)

    t_hdd = font_card.render("SSD — Répartition par module", True, ACCENT_BLUE)
    screen.blit(t_hdd, (int(WIDTH * 0.52), int(HEIGHT * 0.19)))

    if hdd_breakdown:
        pie_center = (int(WIDTH * 0.60), int(HEIGHT * 0.45))
        pie_radius = int(HEIGHT * 0.13)
        draw_pie_chart(screen, pie_center, pie_radius, hdd_breakdown)
        draw_pie_legend(screen, font_sub, hdd_breakdown,
                         int(WIDTH * 0.72), int(HEIGHT * 0.26), int(HEIGHT * 0.045))
    else:
        loading_txt = font_sub.render("Calcul en cours...", True, TEXT_MUTED)
        screen.blit(loading_txt, (int(WIDTH * 0.52), int(HEIGHT * 0.45)))

    # Bouton RETOUR
    btn_ret_w = int(WIDTH * 0.20)
    btn_ret_h = int(HEIGHT * 0.09)
    btn_ret_x = WIDTH - int(WIDTH * 0.05) - btn_ret_w
    btn_ret_y = int(HEIGHT * 0.78)
    rect_ret = pygame.Rect(btn_ret_x, btn_ret_y, btn_ret_w, btn_ret_h)

    color_ret = ACCENT_BLUE if selected_index == 0 else CARD_BG
    pygame.draw.rect(screen, color_ret, rect_ret, border_radius=10)
    txt_ret = font_card.render("◄ RETOUR (B)", True, TEXT_WHITE)
    screen.blit(txt_ret, (btn_ret_x + btn_ret_w // 2 - txt_ret.get_width() // 2, btn_ret_y + btn_ret_h // 2 - txt_ret.get_height() // 2))

    draw_legend(screen, font_sub, LEGEND_BACK_ONLY)