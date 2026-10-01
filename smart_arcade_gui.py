import os
import sys
import time
import shutil
import threading
import urllib.request
import json
import pygame
from legend_view import draw_legend, LEGEND_NAVIGATE_VALIDATE

# Ajout de get_paired_and_active_devices manquant dans les imports
from manettes_view import draw_controllers_screen, get_paired_and_active_devices
from storage_view import draw_storage_screen, compute_hdd_breakdown
from settings_view import draw_settings_screen

pygame.init()
pygame.joystick.init()
pygame.mouse.set_visible(False)

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Smart Arcade Menu")

DARK_BG = (18, 22, 30)
CARD_BG = (30, 40, 55)
ACCENT_BLUE = (0, 162, 232)
TEXT_WHITE = (240, 240, 240)
TEXT_MUTED = (150, 160, 180)
RED_SHUTDOWN = (200, 50, 50)
PURPLE_STANDBY = (120, 60, 180)
PANEL_BG = (25, 33, 45)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = None

font_title = pygame.font.Font(FONT_PATH, int(HEIGHT * 0.045))
font_gear = pygame.font.Font(FONT_PATH, int(HEIGHT * 0.050))
font_clock = pygame.font.Font(FONT_PATH, int(HEIGHT * 0.045))
font_date = pygame.font.Font(FONT_PATH, int(HEIGHT * 0.025))
font_card = pygame.font.Font(FONT_PATH, int(HEIGHT * 0.030))
font_sub = pygame.font.Font(FONT_PATH, int(HEIGHT * 0.022))
font_storage = pygame.font.Font(FONT_PATH, int(HEIGHT * 0.019))

ACTIVITIES = [
    {"title": "RETROGAMING", "sub": "EmulationStation", "img_path": "/media/hdd/media/arcade.jpg", "cmd": "sudo systemctl isolate arcade-retro.target"},
    {"title": "KARAOKE", "sub": "UltraStar Deluxe", "img_path": "/media/hdd/media/karaoke.jpg", "cmd": "sudo systemctl isolate arcade-karaoke.target"},
    {"title": "DARTSCAB", "sub": "Cible Fléchettes", "img_path": "/media/hdd/media/darts.jpg", "cmd": "sudo systemctl isolate arcade-darts.target"},
    {"title": "QUIZ SHOW", "sub": "Serveur Smartphone", "img_path": "/media/hdd/media/quiz.jpg", "cmd": "python3 /media/hdd/quiz/server.py &"}
]

for act in ACTIVITIES:
    if os.path.exists(act["img_path"]):
        try:
            img = pygame.image.load(act["img_path"])
            act["surface"] = pygame.transform.smoothscale(img, (int(WIDTH * 0.20), int(HEIGHT * 0.32)))
        except:
            act["surface"] = None
    else:
        act["surface"] = None

def load_icon(path, size):
    if os.path.exists(path):
        try:
            img = pygame.image.load(path)
            return pygame.transform.smoothscale(img, size)
        except:
            return None
    return None

btn_h = int(HEIGHT * 0.10)
icon_size = (int(btn_h * 0.45), int(btn_h * 0.45))
sd_icon_img = load_icon("/media/hdd/media/sd_icon.png", (22, 22))
hdd_icon_img = load_icon("/media/hdd/media/hdd_icon.png", (22, 22))
standby_icon_img = load_icon("/media/hdd/media/standby_icon.png", icon_size)
power_icon_img = load_icon("/media/hdd/media/power_icon.png", icon_size)

settings_state = {
    "show_weather": True,
    "show_clock": True,
    "show_storage": True
}

weather_info = "Lallaing --°C"
def fetch_weather():
    global weather_info
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=50.39&longitude=3.17&current_weather=true"
        req = urllib.request.urlopen(url, timeout=5)
        data = json.loads(req.read().decode())
        temp = int(round(data["current_weather"]["temperature"]))
        code = data["current_weather"]["weathercode"]
        icon = "☀️" if code in [0, 1] else ("☁️" if code in [2, 3] else "🌧️")
        weather_info = f"{icon} Lallaing {temp}°C"
    except:
        weather_info = "☁️ Lallaing --°C"
threading.Thread(target=fetch_weather, daemon=True).start()

def get_storage_info():
    try:
        sd_stat = shutil.disk_usage("/")
        sd_free_gb = sd_stat.free / (1024**3)
        sd_pct = (sd_stat.free / sd_stat.total) * 100
        sd_str = f"{sd_free_gb:.1f}Go ({sd_pct:.0f}%)"
    except:
        sd_str = "N/A"
    try:
        hdd_stat = shutil.disk_usage("/media/hdd")
        hdd_free_gb = hdd_stat.free / (1024**3)
        hdd_pct = (hdd_stat.free / hdd_stat.total) * 100
        hdd_str = f"{hdd_free_gb:.1f}Go ({hdd_pct:.0f}%)"
    except:
        hdd_str = "N/A"
    return sd_str, hdd_str

# =========================================================
# 🎮 GESTIONNAIRE DE MANETTES (Correctif Pygame 2)
# =========================================================
active_joysticks = {}

for i in range(pygame.joystick.get_count()):
    try:
        j = pygame.joystick.Joystick(i)
        j.init()
        active_joysticks[j.get_instance_id()] = j
    except:
        pass

def get_joysticks_info():
    """Lit le dictionnaire actif pour éviter la déconnexion inopinée"""
    info_list = []
    joys = list(active_joysticks.values())
    for i in range(4):
        if i < len(joys):
            info_list.append({"id": i+1, "name": joys[i].get_name(), "type": "BT/USB", "active": True})
        else:
            info_list.append({"id": i+1, "active": False})
    return info_list
# =========================================================

current_view = "MAIN"
selected_index = 0
sub_selected_index = 0
clock = pygame.time.Clock()
running = True
hdd_breakdown_cache = None

def draw_main_interface():
    screen.fill(DARK_BG)
    title_surf = font_title.render("BORNE SMART-ARCADE", True, TEXT_WHITE)
    screen.blit(title_surf, (int(WIDTH * 0.04), int(HEIGHT * 0.04)))
    
    if settings_state["show_clock"]:
        current_time = time.strftime("%H:%M")
        current_date = time.strftime("%d/%m/%Y")
        time_surf = font_clock.render(current_time, True, ACCENT_BLUE)
        date_surf = font_date.render(current_date, True, TEXT_MUTED)
        clock_x = WIDTH - int(WIDTH * 0.04) - time_surf.get_width()
        screen.blit(time_surf, (clock_x, int(HEIGHT * 0.03)))
        screen.blit(date_surf, (WIDTH - int(WIDTH * 0.04) - date_surf.get_width(), int(HEIGHT * 0.03) + time_surf.get_height()))
        
    if settings_state["show_weather"]:
        w_surf = font_date.render(weather_info, True, TEXT_WHITE)
        w_x = WIDTH - int(WIDTH * 0.22) - w_surf.get_width()
        screen.blit(w_surf, (w_x, int(HEIGHT * 0.04)))
        
    card_w = int(WIDTH * 0.20)
    card_h = int(HEIGHT * 0.48)
    spacing = int(WIDTH * 0.03)
    start_x = (WIDTH - (4 * card_w + 3 * spacing)) // 2
    card_y = int(HEIGHT * 0.18)
    
    for i, act in enumerate(ACTIVITIES):
        x = start_x + i * (card_w + spacing)
        rect = pygame.Rect(x, card_y, card_w, card_h)
        if selected_index == i:
            pygame.draw.rect(screen, ACCENT_BLUE, rect.inflate(10, 10), border_radius=15)
            pygame.draw.rect(screen, CARD_BG, rect, border_radius=12)
        else:
            pygame.draw.rect(screen, CARD_BG, rect, border_radius=12)
        if act["surface"]:
            screen.blit(act["surface"], (x, card_y + 12))
        else:
            placeholder = pygame.Rect(x + 10, card_y + 12, card_w - 20, int(card_h * 0.65))
            pygame.draw.rect(screen, (45, 55, 75), placeholder, border_radius=8)
        t_surf = font_card.render(act["title"], True, TEXT_WHITE)
        s_surf = font_sub.render(act["sub"], True, TEXT_MUTED)
        screen.blit(t_surf, (x + card_w // 2 - t_surf.get_width() // 2, card_y + card_h - 60))
        screen.blit(s_surf, (x + card_w // 2 - s_surf.get_width() // 2, card_y + card_h - 32))
        
    bot_y = int(HEIGHT * 0.78)
    btn_w = int(WIDTH * 0.08)
    btn_spacing = int(WIDTH * 0.02)
    sd_free, hdd_free = get_storage_info()
    stg_w = int(WIDTH * 0.32)
    stg_x = int(WIDTH * 0.04)
    rect_stg = pygame.Rect(stg_x, bot_y, stg_w, btn_h)
    
    if settings_state["show_storage"]:
        if selected_index == 4:
            pygame.draw.rect(screen, ACCENT_BLUE, rect_stg.inflate(6, 6), border_radius=12)
        pygame.draw.rect(screen, PANEL_BG, rect_stg, border_radius=10)
        if sd_icon_img:
            screen.blit(sd_icon_img, (stg_x + 12, bot_y + 14))
        if hdd_icon_img:
            screen.blit(hdd_icon_img, (stg_x + 12, bot_y + btn_h - 34))
        offset_x = 42 if (sd_icon_img or hdd_icon_img) else 15
        t_sd = font_storage.render(f"SD : {sd_free}", True, TEXT_WHITE)
        t_hdd = font_storage.render(f"HDD : {hdd_free}", True, ACCENT_BLUE)
        screen.blit(t_sd, (stg_x + offset_x, bot_y + 15))
        screen.blit(t_hdd, (stg_x + offset_x, bot_y + btn_h - 33))
        
    right_start_x = stg_x + stg_w + int(WIDTH * 0.04)
    p_x = right_start_x
    rect_p = pygame.Rect(p_x, bot_y, btn_w, btn_h)
    color_p = ACCENT_BLUE if selected_index == 5 else CARD_BG
    pygame.draw.rect(screen, color_p, rect_p, border_radius=10)
    txt_p = font_gear.render("⚙", True, TEXT_WHITE)
    screen.blit(txt_p, (p_x + btn_w // 2 - txt_p.get_width() // 2, bot_y + btn_h // 2 - txt_p.get_height() // 2))
    
    v_x = p_x + btn_w + btn_spacing
    rect_v = pygame.Rect(v_x, bot_y, btn_w, btn_h)
    color_v = ACCENT_BLUE if selected_index == 6 else PURPLE_STANDBY
    pygame.draw.rect(screen, color_v, rect_v, border_radius=10)
    if standby_icon_img:
        screen.blit(standby_icon_img, (v_x + btn_w // 2 - icon_size[0] // 2, bot_y + btn_h // 2 - icon_size[1] // 2))
        
    e_x = v_x + btn_w + btn_spacing
    rect_e = pygame.Rect(e_x, bot_y, btn_w, btn_h)
    color_e = ACCENT_BLUE if selected_index == 7 else RED_SHUTDOWN
    pygame.draw.rect(screen, color_e, rect_e, border_radius=10)
    if power_icon_img:
        screen.blit(power_icon_img, (e_x + btn_w // 2 - icon_size[0] // 2, bot_y + btn_h // 2 - icon_size[1] // 2))
        
    draw_legend(screen, font_sub, LEGEND_NAVIGATE_VALIDATE)
    pygame.display.flip()

# --- BOUCLE PRINCIPALE ---
while running:
    if current_view == "MAIN":
        draw_main_interface()
    elif current_view == "STORAGE":
        draw_storage_screen(screen, font_title, font_card, font_sub, sub_selected_index, hdd_breakdown_cache)
        pygame.display.flip()
    elif current_view == "SETTINGS":
        draw_settings_screen(screen, font_title, font_card, font_sub, sub_selected_index, settings_state)
        pygame.display.flip()
    elif current_view == "MANETTES":
        devices_list = get_paired_and_active_devices()
        draw_controllers_screen(screen, font_title, font_card, font_sub, sub_selected_index, devices_list)
        pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Détection à chaud des manettes ajoutées/retirées (Hotplug)
        elif event.type == pygame.JOYDEVICEADDED:
            try:
                j = pygame.joystick.Joystick(event.device_index)
                j.init()
                active_joysticks[j.get_instance_id()] = j
            except: pass
        elif event.type == pygame.JOYDEVICEREMOVED:
            if event.instance_id in active_joysticks:
                del active_joysticks[event.instance_id]
                
        elif event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYHATMOTION:
            is_validate = (event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE]) or \
                          (event.type == pygame.JOYBUTTONDOWN and event.button == 0)
            is_back = (event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]) or \
                      (event.type == pygame.JOYBUTTONDOWN and event.button == 1)

            if current_view == "MAIN":
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT) or \
                   (event.type == pygame.JOYHATMOTION and event.value == (1, 0)):
                    if selected_index < 3: selected_index += 1
                    elif selected_index >= 4 and selected_index < 7: selected_index += 1
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT) or \
                     (event.type == pygame.JOYHATMOTION and event.value == (-1, 0)):
                    if selected_index > 0 and selected_index <= 3: selected_index -= 1
                    elif selected_index > 4: selected_index -= 1
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN) or \
                     (event.type == pygame.JOYHATMOTION and event.value == (0, -1)):
                    if selected_index <= 3: selected_index = 4
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_UP) or \
                     (event.type == pygame.JOYHATMOTION and event.value == (0, 1)):
                    if selected_index >= 4: selected_index = 0
                elif is_validate:
                    if selected_index < 4:
                        cmd = ACTIVITIES[selected_index]["cmd"]
                        pygame.quit()
                        os.system(cmd)
                        sys.exit(0)
                    elif selected_index == 4:
                        current_view = "STORAGE"
                        sub_selected_index = 0
                        hdd_breakdown_cache = compute_hdd_breakdown()
                    elif selected_index == 5:
                        current_view = "SETTINGS"
                        sub_selected_index = 0
                    elif selected_index == 6:
                        pygame.quit()
                        os.system("python3 /home/pi/screensaver.py")
                        sys.exit(0)
                    elif selected_index == 7:
                        pygame.quit()
                        os.system("sudo shutdown -h now")
                        sys.exit(0)

            elif current_view == "SETTINGS":
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN) or \
                   (event.type == pygame.JOYHATMOTION and event.value == (0, -1)):
                    if sub_selected_index < 4: sub_selected_index += 1
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_UP) or \
                     (event.type == pygame.JOYHATMOTION and event.value == (0, 1)):
                    if sub_selected_index > 0: sub_selected_index -= 1
                elif is_back or (is_validate and sub_selected_index == 4):
                    current_view = "MAIN"
                elif is_validate:
                    if sub_selected_index == 0: settings_state["show_weather"] = not settings_state["show_weather"]
                    elif sub_selected_index == 1: settings_state["show_clock"] = not settings_state["show_clock"]
                    elif sub_selected_index == 2: settings_state["show_storage"] = not settings_state["show_storage"]
                    elif sub_selected_index == 3:
                        current_view = "MANETTES"
                        sub_selected_index = 0

            elif current_view == "MANETTES":
                devices_list = get_paired_and_active_devices()
                max_idx = len(devices_list) + 1
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN) or \
                   (event.type == pygame.JOYHATMOTION and event.value == (0, -1)):
                    if sub_selected_index < max_idx:
                        sub_selected_index += 1
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_UP) or \
                     (event.type == pygame.JOYHATMOTION and event.value == (0, 1)):
                    if sub_selected_index > 0:
                        sub_selected_index -= 1
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT) or \
                     (event.type == pygame.JOYHATMOTION and event.value == (1, 0)):
                    if sub_selected_index == len(devices_list):
                        sub_selected_index = len(devices_list) + 1
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT) or \
                     (event.type == pygame.JOYHATMOTION and event.value == (-1, 0)):
                    if sub_selected_index == len(devices_list) + 1:
                        sub_selected_index = len(devices_list)
                elif is_back or (is_validate and sub_selected_index == len(devices_list) + 1):
                    current_view = "SETTINGS"
                elif is_validate and sub_selected_index == len(devices_list):
                    pass

            elif current_view == "STORAGE":
                if is_back or is_validate:
                    current_view = "MAIN"
                    
    clock.tick(30)
pygame.quit()
