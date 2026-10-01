#!/usr/bin/env python3
import os
import re
import subprocess
import pygame
from legend_view import draw_legend, LEGEND_NAVIGATE_VALIDATE_BACK

DARK_BG = (18, 22, 30)
CARD_BG = (30, 40, 55)
ACCENT_BLUE = (0, 162, 232)
TEXT_WHITE = (240, 240, 240)
TEXT_MUTED = (150, 160, 180)
GREEN_CONNECTED = (40, 200, 100)
RED_DISCONNECTED = (220, 60, 60)

# Chargement de l'icône manette pour le bouton appairer
GAMEPAD_IMG_PATH = "/media/hdd/media/gamepad_icon.png"
gamepad_img = None
if os.path.exists(GAMEPAD_IMG_PATH):
    try:
        raw_img = pygame.image.load(GAMEPAD_IMG_PATH)
        gamepad_img = pygame.transform.smoothscale(raw_img, (26, 26))
    except:
        gamepad_img = None

def get_paired_and_active_devices():
    """Récupère toutes les manettes BT enregistrées et croise leur statut actif/connecté."""
    paired_devices = []
    
    # 1. Manettes Bluetooth appairées sur le système (via bluetoothctl)
    try:
        out = subprocess.check_output(["bluetoothctl", "devices"], text=True)
        for line in out.strip().split('\n'):
            match = re.match(r'Device ([0-9A-FA-f:]+) (.*)', line)
            if match:
                mac, name = match.groups()
                paired_devices.append({"mac": mac, "name": name, "connected": False})
    except:
        pass

    # 2. Vérification des connexions actives via Pygame Joystick
    pygame.joystick.init()
    active_count = pygame.joystick.get_count()
    active_names = []
    for i in range(active_count):
        try:
            js = pygame.joystick.Joystick(i)
            js.init()
            active_names.append(js.get_name().lower())
        except:
            pass

    # Met à jour le statut 🟢/🔴 et trie pour mettre les connectées en tête
    for dev in paired_devices:
        dev_name_clean = dev["name"].lower()
        if any(act in dev_name_clean or dev_name_clean in act for act in active_names):
            dev["connected"] = True

    # Si aucune manette BT reconnue mais un joystick USB actif est branché
    if not paired_devices and active_count > 0:
        for i in range(active_count):
            js = pygame.joystick.Joystick(i)
            paired_devices.append({"mac": "USB", "name": js.get_name(), "connected": True})

    # Tri : Connectées en premier
    paired_devices.sort(key=lambda x: not x["connected"])
    return paired_devices

def draw_pair_button_icon(screen, x, y, is_selected):
    """Dessine visuellement : + 🎮 BT"""
    color = TEXT_WHITE if is_selected else ACCENT_BLUE
    
    # Dessin du '+' vectoriel
    plus_cx, plus_cy = x + 15, y + 15
    pygame.draw.line(screen, color, (plus_cx - 6, plus_cy), (plus_cx + 6, plus_cy), 3)
    pygame.draw.line(screen, color, (plus_cx, plus_cy - 6), (plus_cx, plus_cy + 6), 3)

    # Icône manette
    if gamepad_img:
        screen.blit(gamepad_img, (x + 28, y + 2))
    
    # Sigle Bluetooth (BT)
    font_bt = pygame.font.Font(None, 18)
    bt_txt = font_bt.render("BT", True, color)
    screen.blit(bt_txt, (x + 56, y + 2))

def draw_controllers_screen(screen, font_title, font_card, font_sub, selected_index, devices_list, status_msg=""):
    WIDTH, HEIGHT = screen.get_size()
    screen.fill(DARK_BG)

    title_surf = font_title.render("TABLEAU DE BORD DES MANETTES", True, TEXT_WHITE)
    screen.blit(title_surf, (int(WIDTH * 0.04), int(HEIGHT * 0.04)))

    # Tableau central des manettes
    table_x = int(WIDTH * 0.05)
    table_y = int(HEIGHT * 0.15)
    table_w = int(WIDTH * 0.90)
    table_h = int(HEIGHT * 0.60)
    
    pygame.draw.rect(screen, CARD_BG, (table_x, table_y, table_w, table_h), border_radius=12)

    # Navigation dans la liste des manettes (index 0 à len-1), Appairer (index N), Retour (index N+1)
    max_devices_shown = 5
    row_h = int(table_h / max_devices_shown)

    if not devices_list:
        no_dev = font_card.render("Aucune manette Bluetooth enregistrée.", True, TEXT_MUTED)
        screen.blit(no_dev, (table_x + 30, table_y + 40))
    else:
        for idx, dev in enumerate(devices_list[:max_devices_shown]):
            ry = table_y + idx * row_h
            is_selected = (selected_index == idx)

            if is_selected:
                pygame.draw.rect(screen, ACCENT_BLUE, (table_x + 5, ry + 4, table_w - 10, row_h - 8), border_radius=8)

            # Voyant 🟢 / 🔴
            dot_color = GREEN_CONNECTED if dev["connected"] else RED_DISCONNECTED
            pygame.draw.circle(screen, dot_color, (table_x + 30, ry + row_h // 2), 8)

            # Nom et MAC de la Manette
            lbl_name = font_card.render(f"Manette {idx+1} : {dev['name']}", True, TEXT_WHITE)
            lbl_mac = font_sub.render(f"[{dev['mac']}]", True, TEXT_WHITE if is_selected else TEXT_MUTED)
            
            screen.blit(lbl_name, (table_x + 50, ry + row_h // 2 - lbl_name.get_height() // 2))
            screen.blit(lbl_mac, (table_x + table_w - lbl_mac.get_width() - 30, ry + row_h // 2 - lbl_mac.get_height() // 2))

    # Zone inférieure des boutons
    bot_y = int(HEIGHT * 0.80)
    btn_w = int(WIDTH * 0.42)
    btn_h = int(HEIGHT * 0.11)

    # Index N : Bouton APPAIRER
    idx_appairer = len(devices_list)
    app_selected = (selected_index == idx_appairer)
    rect_app = pygame.Rect(table_x, bot_y, btn_w, btn_h)
    pygame.draw.rect(screen, ACCENT_BLUE if app_selected else CARD_BG, rect_app, border_radius=10)

    draw_pair_button_icon(screen, table_x + 20, bot_y + btn_h // 2 - 15, app_selected)
    txt_app = font_card.render("APPAIRER UNE MANETTE", True, TEXT_WHITE)
    screen.blit(txt_app, (table_x + 105, bot_y + btn_h // 2 - txt_app.get_height() // 2))

    # Index N+1 : Bouton RETOUR
    idx_retour = len(devices_list) + 1
    ret_selected = (selected_index == idx_retour)
    rect_ret = pygame.Rect(table_x + table_w - btn_w, bot_y, btn_w, btn_h)
    pygame.draw.rect(screen, ACCENT_BLUE if ret_selected else CARD_BG, rect_ret, border_radius=10)
    
    txt_ret = font_card.render("◄ RETOUR AU MENU", True, TEXT_WHITE)
    screen.blit(txt_ret, (rect_ret.x + btn_w // 2 - txt_ret.get_width() // 2, bot_y + btn_h // 2 - txt_ret.get_height() // 2))

    if status_msg:
        st_surf = font_sub.render(status_msg, True, ACCENT_BLUE)
        screen.blit(st_surf, (table_x, bot_y - 30))

    draw_legend(screen, font_sub, LEGEND_NAVIGATE_VALIDATE_BACK)
