#!/bin/bash

# Aseguramos el driver de video y le enseñamos dónde están los programas
export SDL_VIDEODRIVER=kmsdrm
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games

while true; do
    rm -f /tmp/next_game.txt
    
    #  Limpiamos por completo la pantalla y el texto viejo
    clear
    sleep 1
    
    python3 /home/pi/menu.py
    
    if [ -f /tmp/next_game.txt ]; then
        JUEGO=$(cat /tmp/next_game.txt)
        
        #  Volvemos a limpiar antes de arrancar el juego
        clear
        
        #  El "> /dev/null 2>&1" absorbe todo el texto de Mednafen para que no se vea
        mednafen "$JUEGO" > /dev/null 2>&1
        
    else
        clear
        break
    fi
done
