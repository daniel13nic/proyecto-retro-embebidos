#!/bin/bash

set -e

PROJECT_NAME="consola-retro"
INSTALL_DIR="/opt/$PROJECT_NAME"
SERVICE_USER="pi"

echo "Instalador de Consola Retro"
echo "==========================="
echo

if [ "$EUID" -eq 0 ]; then
    echo "Error: no ejecutes este script directamente como root."
    echo "Usa: ./install.sh"
    exit 1
fi

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
    echo "Advertencia: no existe el usuario '$SERVICE_USER'."
    echo "Se usará el usuario actual: $USER"
    SERVICE_USER="$USER"
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/8] Actualizando lista de paquetes"
sudo apt update

echo "[2/8] Instalando dependencias"
sudo apt install -y \
    python3 \
    python3-pygame \
    mednafen \
    joystick \
    evtest \
    mpv \
    rsync

echo "[3/8] Creando directorios de instalación"
sudo mkdir -p "$INSTALL_DIR"
sudo mkdir -p /home/"$SERVICE_USER"/roms

echo "[4/8] Copiando archivos del proyecto"
sudo rsync -av \
    --exclude ".git" \
    --exclude "__pycache__" \
    --exclude "*.pyc" \
    "$PROJECT_DIR/" "$INSTALL_DIR/"

echo "[5/8] Instalando archivos operativos en /home/$SERVICE_USER"
sudo cp "$INSTALL_DIR/src/menu.py" /home/"$SERVICE_USER"/menu.py
sudo cp "$INSTALL_DIR/scripts/start.sh" /home/"$SERVICE_USER"/start.sh
sudo cp "$INSTALL_DIR/scripts/boot_intro.sh" /home/"$SERVICE_USER"/boot_intro.sh
sudo cp "$INSTALL_DIR/assets/retro_font.ttf" /home/"$SERVICE_USER"/retro_font.ttf
sudo cp "$INSTALL_DIR/scripts/sync_roms.sh" /usr/local/bin/sync_roms.sh

if [ -f "$INSTALL_DIR/assets/intro.mp4" ]; then
    sudo cp "$INSTALL_DIR/assets/intro.mp4" /home/"$SERVICE_USER"/intro.mp4
fi

if [ -f "$INSTALL_DIR/assets/intro.png" ]; then
    sudo cp "$INSTALL_DIR/assets/intro.png" /home/"$SERVICE_USER"/intro.png
fi

if [ -f "$INSTALL_DIR/assets/intro.wav" ]; then
    sudo cp "$INSTALL_DIR/assets/intro.wav" /home/"$SERVICE_USER"/intro.wav
fi

echo "[6/8] Ajustando permisos"
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

sudo chown "$SERVICE_USER:$SERVICE_USER" /home/"$SERVICE_USER"/menu.py
sudo chown "$SERVICE_USER:$SERVICE_USER" /home/"$SERVICE_USER"/start.sh
sudo chown "$SERVICE_USER:$SERVICE_USER" /home/"$SERVICE_USER"/boot_intro.sh
sudo chown "$SERVICE_USER:$SERVICE_USER" /home/"$SERVICE_USER"/retro_font.ttf
sudo chown -R "$SERVICE_USER:$SERVICE_USER" /home/"$SERVICE_USER"/roms

if [ -f /home/"$SERVICE_USER"/intro.mp4 ]; then
    sudo chown "$SERVICE_USER:$SERVICE_USER" /home/"$SERVICE_USER"/intro.mp4
fi

if [ -f /home/"$SERVICE_USER"/intro.png ]; then
    sudo chown "$SERVICE_USER:$SERVICE_USER" /home/"$SERVICE_USER"/intro.png
fi

if [ -f /home/"$SERVICE_USER"/intro.wav ]; then
    sudo chown "$SERVICE_USER:$SERVICE_USER" /home/"$SERVICE_USER"/intro.wav
fi

sudo chmod +x /home/"$SERVICE_USER"/start.sh
sudo chmod +x /home/"$SERVICE_USER"/boot_intro.sh
sudo chmod +x /usr/local/bin/sync_roms.sh

echo "[7/8] Instalando servicio systemd y regla udev"
sudo sed "s/^User=pi$/User=$SERVICE_USER/" "$INSTALL_DIR/systemd/retromenu.service" | \
    sudo sed "s/^Group=pi$/Group=$SERVICE_USER/" | \
    sudo tee /etc/systemd/system/retromenu.service >/dev/null

sudo sed "s/^User=pi$/User=$SERVICE_USER/" "$INSTALL_DIR/systemd/splash.service" | \
    sudo sed "s/^Group=pi$/Group=$SERVICE_USER/" | \
    sudo tee /etc/systemd/system/splash.service >/dev/null

sudo cp "$INSTALL_DIR/udev/99-usb-sync.rules" /etc/udev/rules.d/99-usb-sync.rules

echo "[8/8] Recargando servicios"
sudo systemctl daemon-reload
sudo udevadm control --reload-rules
sudo systemctl enable splash.service
sudo systemctl enable retromenu.service

echo
echo "Instalación terminada."
echo
echo "Para iniciar manualmente la intro:"
echo "  sudo systemctl start splash.service"
echo
echo "Para iniciar manualmente el menú:"
echo "  sudo systemctl start retromenu.service"
echo
echo "Para revisar errores:"
echo "  journalctl -u splash.service -e"
echo "  journalctl -u retromenu.service -e"
echo
echo "Reinicia la Raspberry Pi para probar el arranque automático."