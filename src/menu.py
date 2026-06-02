import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import subprocess
import sys
import time

# --- CONFIGURACIÓN ---
ROM_DIR = "/home/pi/roms"
EMULATOR = "mednafen"
# Ruta a la fuente
FONT_FILE = "/home/pi/retro_font.ttf" 

os.environ["SDL_VIDEODRIVER"] = "kmsdrm"

# --- NUEVA PALETA DE COLORES SYNTHWAVE ---
COLOR_FONDOBASICO = (10, 0, 30)   # Azul oscuro
COLOR_FONDOALTO = (40, 0, 80)     # Púrpura oscuro (para gradiente)
COLOR_GRID = (150, 0, 255)         # Púrpura neón para la cuadrícula
COLOR_TEXTO_TITULO = (255, 0, 255) # Magenta (brillante)
COLOR_TEXTO_SELECCION = (0, 255, 255) # Cian (neón)
COLOR_TEXTO_NORMAL = (200, 200, 200) # Gris claro/blanco opaco
COLOR_ERROR = (255, 50, 50)       # Rojo neón

def obtener_juegos():
    if not os.path.exists(ROM_DIR):
        return []
    return sorted([f for f in os.listdir(ROM_DIR) if f.endswith(('.nes', '.sfc', '.smc', '.gba'))])

# --- FONDO ESTILO SYNTHWAVE ---
def draw_synthwave_background(screen, width, height):
    # 1. Gradiente simulado (de púrpura a azul profundo)
    for y in range(height):
        # Calculamos el color interpolado para cada línea horizontal
        ratio = y / height
        r = int(COLOR_FONDOALTO[0] * (1 - ratio) + COLOR_FONDOBASICO[0] * ratio)
        g = int(COLOR_FONDOALTO[1] * (1 - ratio) + COLOR_FONDOBASICO[1] * ratio)
        b = int(COLOR_FONDOALTO[2] * (1 - ratio) + COLOR_FONDOBASICO[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

    # 2. Dibujar Cuadrícula de Perspectiva (Suelo)
    # Definimos dónde empieza el horizonte 
    horizonte_y = int(height * 0.7)
    ground_height = height - horizonte_y
    
    # Líneas de profundidad (fugas) que convergen en el centro del horizonte
    fuga_x = width // 2
    fuga_y = horizonte_y - int(height * 0.1) # Punto de fuga ligeramente arriba del horizonte visible
    
    num_lineas_fuga = 14
    for i in range(num_lineas_fuga + 1):
        # Calculamos puntos en el borde inferior de la pantalla
        x_final = (width / num_lineas_fuga) * i
        # Dibujamos línea desde el horizonte hasta el borde inferior
        pygame.draw.line(screen, COLOR_GRID, (fuga_x, fuga_y), (x_final, height), 2)

    # Líneas horizontales con espacio creciente (perspectiva)
    num_lineas_horiz = 8
    for i in range(num_lineas_horiz):
        # Usamos una función exponencial simple para separar las líneas más abajo
        ratio = (i / num_lineas_horiz) ** 2
        y_horiz = horizonte_y + int(ground_height * ratio)
        pygame.draw.line(screen, COLOR_GRID, (0, y_horiz), (width, y_horiz), 1)
        
    # Dibujar línea del horizonte neón
    pygame.draw.line(screen, COLOR_GRID, (0, horizonte_y), (width, horizonte_y), 3)


def main():
    time.sleep(1)
    pygame.init()
    pygame.joystick.init()

    # Obtener info de pantalla para centrado dinámico
    try:
        screen_info = pygame.display.Info()
        sw = screen_info.current_w
        sh = screen_info.current_h
    except:
        # Failsafe por si KMSDRM no reporta bien el tamaño inicialmente
        sw, sh = 1920, 1080 

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
    # --- CARGAR FUENTE RETRO  ---
    try:
        # Fuente más pequeña para el menú centrado 
        font_main = pygame.font.Font(FONT_FILE, 30)
        # Fuente más grande para el título 
        font_title = pygame.font.Font(FONT_FILE, 50)
    except:
        print("AVISO: No se encontró retro_font.ttf. Usando fuente default (se verá mal).")
        font_main = pygame.font.Font(None, 40)
        font_title = pygame.font.Font(None, 70)

    reloj = pygame.time.Clock()

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    juegos = obtener_juegos()
    indice_seleccionado = 0
    corriendo = True
    
    frames_desde_revision = 0

    try:
        while corriendo:
            
            # Escaneo forzado cada 2 segundos
            frames_desde_revision += 1
            if frames_desde_revision >= 60: 
                frames_desde_revision = 0
                juegos_nuevos = obtener_juegos()
                if juegos_nuevos != juegos:
                    juegos = juegos_nuevos
                    indice_seleccionado = 0

            # --- NUEVA LÓGICA DE DIBUJO ---
            
            # 1. Fondo Synthwave (Gradiente + Cuadrícula)
            draw_synthwave_background(screen, sw, sh)

            # 2. Dibujar Título (Centrado arriba)
            # Como la imagen, usemos un nombre más corto y cool
            text_title = "SYSTEM MENU"
            title_surf = font_title.render(text_title, True, COLOR_TEXTO_TITULO)
            title_rect = title_surf.get_rect(center=(sw // 2, int(sh * 0.15)))
            
            # Efecto de brillo simple (dibujar Magenta oscuro detrás)
            title_glow = font_title.render(text_title, True, (100, 0, 100))
            glow_rect = title_glow.get_rect(center=(sw // 2 + 3, int(sh * 0.15) + 3))
            screen.blit(title_glow, glow_rect)
            
            screen.blit(title_surf, title_rect)

            # 3. Dibujar Lista de Juegos (Centrada con Scroll)
            if not juegos:
                mensaje = font_main.render("> INSERT USB / NO ROMS <", True, COLOR_ERROR)
                msg_rect = mensaje.get_rect(center=(sw // 2, sh // 2))
                screen.blit(mensaje, msg_rect)
            else:
                # Ajustamos la altura inicial y el espacio para que quepan 12 cómodamente
                start_y_list = int(sh * 0.20)
                spacing_y = 40 
                max_visibles = 12
                
                # --- Lógica de Scroll (Cámara) ---
                inicio_lista = 0
                if len(juegos) > max_visibles:
                    # Centramos el cursor para que la lista suba o baje al navegar
                    inicio_lista = max(0, indice_seleccionado - (max_visibles // 2))
                    # Evitamos que la cámara baje más allá del último juego
                    if inicio_lista > len(juegos) - max_visibles:
                        inicio_lista = len(juegos) - max_visibles

                # Cortamos la lista solo a los juegos que caben en la pantalla
                juegos_visibles = juegos[inicio_lista : inicio_lista + max_visibles]
                
                for i, juego in enumerate(juegos_visibles):
                    # Recuperamos su índice real para saber si está seleccionado
                    indice_real = i + inicio_lista
                    
                    if indice_real == indice_seleccionado:
                        texto_completo = f"> {juego} <"
                        color_render = COLOR_TEXTO_SELECCION
                    else:
                        texto_completo = juego
                        color_render = COLOR_TEXTO_NORMAL
                        
                    texto_surf = font_main.render(texto_completo, True, color_render)
                    
                    # Calculamos posición
                    curr_y = start_y_list + (i * spacing_y)
                    texto_rect = texto_surf.get_rect(center=(sw // 2, curr_y))
                    
                    # Dibujamos siempre y cuando no pise el suelo de neón
                    if int(sh * 0.7) > curr_y + 20:
                        screen.blit(texto_surf, texto_rect)

            # 4. Decoraciones extras 
            # Texto pequeño en esquinas
            small_font = pygame.font.Font(FONT_FILE, 18) if os.path.exists(FONT_FILE) else pygame.font.Font(None, 24)
            
            # Esquina inferior izquierda: instrucciones del control
            controles_txt = "[FLECHAS]: NAVEGAR | [X]: JUGAR | [OPTIONS]: SALIR"
            surf_controles = small_font.render(controles_txt, True, COLOR_TEXTO_NORMAL)
            screen.blit(surf_controles, (20, sh - 35))
            
            # Esquina inferior derecha: instrucción de la USB
            usb_txt = "INSERTA UNA USB PARA AUTO-COPIAR NUEVOS JUEGOS"
            surf_usb = small_font.render(usb_txt, True, COLOR_TEXTO_NORMAL)
            usb_rect = surf_usb.get_rect(topright=(sw - 20, sh - 35))
            screen.blit(surf_usb, usb_rect)

            pygame.display.flip()

            # --- MANEJO DE EVENTOS  ---
            for evento in pygame.event.get():
                if evento.type == pygame.JOYHATMOTION:
                    x, y = evento.value
                    if juegos: # Failsafe si la lista está vacía
                        if y == 1:
                            indice_seleccionado = (indice_seleccionado - 1) % len(juegos)
                        elif y == -1:
                            indice_seleccionado = (indice_seleccionado + 1) % len(juegos)

                if evento.type == pygame.JOYBUTTONDOWN:
                    if evento.button == 0 and juegos: 
                        ruta_juego = os.path.join(ROM_DIR, juegos[indice_seleccionado])

                        with open("/tmp/next_game.txt", "w") as f:
                            f.write(ruta_juego)

                        pygame.quit()
                        sys.exit(0)

                    elif evento.button == 9: # Botón Options para apagar
                        # 1. Pantalla de despedida
                        screen.fill(COLOR_FONDOBASICO)
                        msg_apagando = font_title.render("APAGANDO SISTEMA...", True, COLOR_ERROR)
                        msg_rect = msg_apagando.get_rect(center=(sw // 2, sh // 2))
                        screen.blit(msg_apagando, msg_rect)
                        pygame.display.flip()
                        
                        # 2. 1.5 segundos para que el usuario lea el mensaje
                        time.sleep(1.5)
                        pygame.quit()
                        
                        # 3. Se manda la orden a nivel de hardware a la Raspberry Pi
                        subprocess.run(["sudo", "poweroff"])
                        sys.exit(0)

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP and juegos:
                        indice_seleccionado = (indice_seleccionado - 1) % len(juegos)
                    elif evento.key == pygame.K_DOWN and juegos:
                        indice_seleccionado = (indice_seleccionado + 1) % len(juegos)
                    elif evento.key == pygame.K_RETURN and juegos:
                        ruta_juego = os.path.join(ROM_DIR, juegos[indice_seleccionado])

                        with open("/tmp/next_game.txt", "w") as f:
                            f.write(ruta_juego)

                        pygame.quit()
                        sys.exit(0)

                    elif evento.key == pygame.K_ESCAPE:
                        screen.fill(COLOR_FONDOBASICO)
                        msg_apagando = font_title.render("APAGANDO SISTEMA...", True, COLOR_ERROR)
                        msg_rect = msg_apagando.get_rect(center=(sw // 2, sh // 2))
                        screen.blit(msg_apagando, msg_rect)
                        pygame.display.flip()
                        
                        time.sleep(1.5)
                        pygame.quit()
                        subprocess.run(["sudo", "poweroff"])
                        sys.exit(0)

            reloj.tick(30)
            
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
