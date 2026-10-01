#!/bin/bash

# ==============================================================================
# SCRIPT CENTRAL MAÎTRE — BORNE MULTI-APPLICATIONS
# ==============================================================================

MNT_HDD="/media/hdd"

show_menu() {
    clear
    echo "=========================================="
    echo "       BORNE INTERACTIVE MULTI-APPS       "
    echo "=========================================="
    echo "1. RETROGAMING (EmulationStation)"
    echo "2. KARAOKE (UltraStar Deluxe)"
    echo "3. DARTSCAB (Fléchettes)"
    echo "4. QUIZ SHOW (Serveur Smartphone)"
    echo "5. ARRÊTER LE SYSTÈME"
    echo "=========================================="
    echo -n "Choisissez une option [1-5] : "
}

start_retro() {
    echo "Lancement du mode Retrogaming..."
    sudo systemctl isolate arcade-retro.target
}

start_karaoke() {
    echo "Lancement du mode Karaoké..."
    sudo systemctl isolate arcade-karaoke.target
}

start_darts() {
    echo "Lancement de la DartsCab..."
    sudo systemctl isolate arcade-darts.target
}

start_quiz() {
    echo "Démarrage du Quiz Show..."
    python3 "$MNT_HDD/quiz/server.py" &
}

while true; do
    show_menu
    read -r choice
    case $choice in
        1) start_retro ;;
        2) start_karaoke ;;
        3) start_darts ;;
        4) start_quiz ;;
        5)
            echo "Arrêt propre du système..."
            sudo shutdown -h now
            exit 0
            ;;
        *) echo "Option invalide." && sleep 2 ;;
    esac
done
