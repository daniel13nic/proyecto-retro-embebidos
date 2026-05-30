#!/bin/bash

# udev nos pasará el nombre de la partición como parámetro (ej. sda1)
DEVICE="/dev/$1"
MOUNT_POINT="/mnt/usb_roms"
ROM_DIR="/home/pi/roms"
LOG="/home/pi/usb_sync.log"

echo "--- USB Detectado: $DEVICE ---" >> $LOG
date >> $LOG

# 1. Encontrar los PIDs del emulador y del menú de Python
MENU_PID=$(pgrep -f "python3 /home/pi/menu.py")
EMU_PID=$(pgrep -x "mednafen")

# Pausar los procesos si existen (señal STOP)
if [ -n "$MENU_PID" ]; then kill -STOP $MENU_PID >> $LOG 2>&1; fi
if [ -n "$EMU_PID" ]; then kill -STOP $EMU_PID >> $LOG 2>&1; fi

# 2. Montar la memoria USB en una carpeta temporal
mkdir -p $MOUNT_POINT
mount $DEVICE $MOUNT_POINT >> $LOG 2>&1

# 3. Copiar las ROMS (ignorando las que ya existen)
# Solo copiamos archivos con las extensiones válidas de las carpetas de la USB
rsync -avm --ignore-existing \
    --include="*/" \
    --include="*.nes" --include="*.sfc" --include="*.smc" --include="*.gba" \
    --exclude="*" \
    "$MOUNT_POINT/" "$ROM_DIR/" >> $LOG 2>&1

# 4. Ajustar permisos (Como el script corre como root, los archivos deben pertenecer al usuario pi)
chown -R pi:pi $ROM_DIR

# 5. Desmontar de forma segura
umount $MOUNT_POINT >> $LOG 2>&1
rmdir $MOUNT_POINT

# 6. Reanudar procesos (señal CONT)
if [ -n "$MENU_PID" ]; then kill -CONT $MENU_PID >> $LOG 2>&1; fi
if [ -n "$EMU_PID" ]; then kill -CONT $EMU_PID >> $LOG 2>&1; fi

echo "Sincronización terminada de forma segura." >> $LOG
