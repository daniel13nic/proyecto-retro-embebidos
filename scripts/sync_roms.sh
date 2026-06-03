#!/bin/bash
USB_MOUNT="/media/usb"
ROM_DIR="/home/pi/roms"

# Montaje
mkdir -p $USB_MOUNT
mount /dev/sda1 $USB_MOUNT 2>/dev/null

# Sincronización con todas las extensiones de la consola
rsync -av --ignore-existing \
  --include='*/' \
  --include='*.[nN][eE][sS]' \
  --include='*.[sS][fF][cC]' \
  --include='*.[sS][mM][cC]' \
  --include='*.[gG][bB][aA]' \
  --exclude='*' \
  "$USB_MOUNT/" "$ROM_DIR/" | grep -iE '\.(nes|sfc|smc|gba)$' > /tmp/juegos_copiados.txt

# Devolver propiedad a Python
chown pi:pi /tmp/juegos_copiados.txt

# Desmontaje 
umount $USB_MOUNT 2>/dev/null
