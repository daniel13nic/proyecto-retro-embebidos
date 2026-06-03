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
AUDIO_USB = "/home/pi/assets/moneda.wav"

os.environ["SDL_VIDEODRIVER"] = "kmsdrm"

# --- NUEVA PALETA DE COLORES SYNTHWAVE ---
COLOR_FONDOBASICO = (10, 0, 30)   # Azul oscuro
COLOR_FONDOALTO = (40, 0, 80)     # Púrpura oscuro (para gradiente)
COLOR_GRID = (150, 0, 255)         # Púrpura neón para la cuadrícula
COLOR_TEXTO_TITULO = (255, 0, 255) # Magenta (brillante)
COLOR_TEXTO_SELECCION = (0, 255, 255) # Cian (neón)
COLOR_TEXTO_NORMAL = (200, 200, 200) # Gris claro/blanco opaco
COLOR_ERROR = (255, 50, 50)       # Rojo neón

def formatear_nombre_juego(nombre_archivo):
    # 1. Quitar la extensión buscando el último punto (ej. '.nes', '.sfc')
    nombre_sin_ext = nombre_archivo.rsplit('.', 1)[0]
    
    # 2. Reemplazar guiones bajos y medios por espacios
    nombre_limpio = nombre_sin_ext.replace('_', ' ').replace('-', ' ')
    
    # 3. Primera letra mayúscula
    return nombre_limpio.title()

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
    horizonte_y = int(height * 0.7)
    ground_height = height - horizonte_y
    
    fuga_x = width // 2
    fuga_y = horizonte_y - int(height * 0.1) 
    
    num_lineas_fuga = 14
    for i in range(num_lineas_fuga + 1):
        x_final = (width / num_lineas_fuga) * i
        pygame.draw.line(screen, COLOR_GRID, (fuga_x, fuga_y), (x_final, height), 2)

    num_lineas_horiz = 8
    for i in range(num_lineas_horiz):
        ratio = (i / num_lineas_horiz) ** 2
        y_horiz = horizonte_y + int(ground_height * ratio)
        pygame.draw.line(screen, COLOR_GRID, (0, y_horiz), (width, y_horiz), 1)
        
    pygame.draw.line(screen, COLOR_GRID, (0, horizonte_y), (width, horizonte_y), 3)

def main():
    time.sleep(1)
    pygame.init()
    pygame.mixer.init()
    pygame.joystick.init()

    # Obtener info de pantalla para centrado dinámico
    try:
        screen_info = pygame.display.Info()
        sw = screen_info.current_w
        sh = screen_info.current_h
    except:
        sw, sh = 1920, 1080 

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
    # --- CARGAR FUENTE RETRO  ---
    try:
        font_main = pygame.font.Font(FONT_FILE, 30)
        font_title = pygame.font.Font(FONT_FILE, 50)
    except:
        print("AVISO: No se encontró retro_font.ttf. Usando fuente default.")
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
        sonido_alerta = pygame.mixer.Sound(AUDIO_USB)
        sonido_alerta.set_volume(0.8) 
    except:
        print("AVISO: No se encontró el archivo de audio para la USB.")
        sonido_alerta = None

    try:
        while corriendo:
            
            # --- INTERRUPCIÓN: VERIFICACIÓN DE USB ---
            if os.path.exists('/tmp/usb_pending'):
                # 1. Aumentamos las dimensiones: Ancho a 1100 y Alto a 650
                rect_w, rect_h = 1100, 650
                rect_x, rect_y = (sw - rect_w) // 2, (sh - rect_h) // 2
                
                pygame.draw.rect(screen, COLOR_FONDOBASICO, (rect_x, rect_y, rect_w, rect_h))
                pygame.draw.rect(screen, COLOR_TEXTO_TITULO, (rect_x, rect_y, rect_w, rect_h), 5)
                
                texto_aviso = font_main.render("USB DETECTADA. ¿COPIAR ROMS?", True, (255, 255, 255))
                texto_opciones = font_main.render("[X] SÍ   /   [O] NO", True, COLOR_TEXTO_SELECCION)
                
                # 2. Centramos dinámicamente el texto de aviso según el nuevo ancho
                screen.blit(texto_aviso, (rect_x + (rect_w - texto_aviso.get_width()) // 2, rect_y + 100))
                screen.blit(texto_opciones, (rect_x + (rect_w - texto_opciones.get_width()) // 2, rect_y + 200))
                pygame.display.flip()

                # --- REPRODUCIR SONIDO AQUÍ ---
                if sonido_alerta:
                    sonido_alerta.play()
                
                esperando_respuesta = True
                while esperando_respuesta:
                    for event in pygame.event.get():
                        if event.type == pygame.JOYBUTTONDOWN:
                            if event.button == 0: # Botón X (SÍ)
                                # Pantalla de carga
                                pygame.draw.rect(screen, COLOR_FONDOBASICO, (rect_x, rect_y, rect_w, rect_h))
                                pygame.draw.rect(screen, COLOR_TEXTO_TITULO, (rect_x, rect_y, rect_w, rect_h), 5)
                                texto_trabajando = font_main.render("COPIANDO ARCHIVOS...", True, (255, 255, 255))
                                screen.blit(texto_trabajando, (rect_x + (rect_w - texto_trabajando.get_width()) // 2, rect_y + 250))
                                pygame.display.flip()
                                
                                # Ejecutar copia real
                                subprocess.run(["sudo", "/usr/local/bin/sync_roms.sh"])
                                
                                # Leer resultados
                                juegos_nuevos = []
                                if os.path.exists('/tmp/juegos_copiados.txt'):
                                    with open('/tmp/juegos_copiados.txt', 'r') as f:
                                        juegos_nuevos = f.readlines()
                                
                                # Mostrar resumen
                                pygame.draw.rect(screen, COLOR_FONDOBASICO, (rect_x, rect_y, rect_w, rect_h))
                                pygame.draw.rect(screen, COLOR_TEXTO_TITULO, (rect_x, rect_y, rect_w, rect_h), 5)
                                
                                if len(juegos_nuevos) > 0:
                                    resumen = font_main.render(f"¡SE COPIARON {len(juegos_nuevos)} JUEGOS!", True, (0, 255, 0))
                                    screen.blit(resumen, (rect_x + 50, rect_y + 50))
                                    
                                    y_pos = rect_y + 110
                                    # 3. Ampliamos el rango a 10 juegos
                                    for juego_txt in juegos_nuevos[:10]:
                                        # Recortar el nombre si es excesivamente largo para no salir de la ventana
                                        nombre_juego = juego_txt.strip()
                                        if len(nombre_juego) > 55:
                                            nombre_juego = nombre_juego[:52] + "..."
                                            
                                        txt_juego = font_main.render("- " + nombre_juego, True, (255, 255, 255))
                                        screen.blit(txt_juego, (rect_x + 50, y_pos))
                                        y_pos += 40
                                        
                                    if len(juegos_nuevos) > 10:
                                        txt_mas = font_main.render(f"...y {len(juegos_nuevos)-10} más.", True, COLOR_TEXTO_NORMAL)
                                        screen.blit(txt_mas, (rect_x + 50, y_pos))
                                else:
                                    resumen = font_main.render("NO SE ENCONTRARON JUEGOS NUEVOS.", True, COLOR_ERROR)
                                    screen.blit(resumen, (rect_x + (rect_w - resumen.get_width()) // 2, rect_y + 250))
                                
                                # 4. Bajamos el texto de continuar para que no se empalme con la lista
                                continuar = font_main.render("PRESIONA [X] PARA CONTINUAR", True, COLOR_TEXTO_TITULO)
                                screen.blit(continuar, (rect_x + (rect_w - continuar.get_width()) // 2, rect_y + 580))
                                pygame.display.flip()
                                
                                esperando_resumen = True
                                while esperando_resumen:
                                    for ev in pygame.event.get():
                                        if ev.type == pygame.JOYBUTTONDOWN and ev.button == 0:
                                            esperando_resumen = False
                                
                                esperando_respuesta = False
                                
                            elif event.button == 1: # Botón O (NO)
                                esperando_respuesta = False

                # Limpiar banderas y recargar lista de ROMs
                try:
                    if os.path.exists('/tmp/usb_pending'):
                        os.remove('/tmp/usb_pending')
                    if os.path.exists('/tmp/juegos_copiados.txt'):
                        os.remove('/tmp/juegos_copiados.txt')
                except PermissionError:
                       pass
                
                juegos = obtener_juegos()
                indice_seleccionado = 0
                continue # Reiniciar el ciclo principal para limpiar la pantalla

            # --- LÓGICA NORMAL DEL MENÚ ---
            
            # Escaneo forzado cada 2 segundos (por si acaso)
            frames_desde_revision += 1
            if frames_desde_revision >= 60: 
                frames_desde_revision = 0
                juegos_nuevos = obtener_juegos()
                if juegos_nuevos != juegos:
                    juegos = juegos_nuevos
                    indice_seleccionado = 0

            # 1. Fondo Synthwave (Gradiente + Cuadrícula)
            draw_synthwave_background(screen, sw, sh)

            # 2. Dibujar Título (Centrado arriba)
            text_title = "SYSTEM MENU"
            title_surf = font_title.render(text_title, True, COLOR_TEXTO_TITULO)
            title_rect = title_surf.get_rect(center=(sw // 2, int(sh * 0.15)))
            
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
                start_y_list = int(sh * 0.20)
                spacing_y = 40 
                max_visibles = 12
                
                inicio_lista = 0
                if len(juegos) > max_visibles:
                    inicio_lista = max(0, indice_seleccionado - (max_visibles // 2))
                    if inicio_lista > len(juegos) - max_visibles:
                        inicio_lista = len(juegos) - max_visibles

                juegos_visibles = juegos[inicio_lista : inicio_lista + max_visibles]
                
                for i, juego in enumerate(juegos_visibles):
                    indice_real = i + inicio_lista
                    nombre_estetico = formatear_nombre_juego(juego)
                    
                    if indice_real == indice_seleccionado:
                        texto_completo = f"> {nombre_estetico} <"
                        color_render = COLOR_TEXTO_SELECCION
                    else:
                        texto_completo = nombre_estetico
                        color_render = COLOR_TEXTO_NORMAL
                        
                    texto_surf = font_main.render(texto_completo, True, color_render)
                    
                    curr_y = start_y_list + (i * spacing_y)
                    texto_rect = texto_surf.get_rect(center=(sw // 2, curr_y))
                    
                    if int(sh * 0.7) > curr_y + 20:
                        screen.blit(texto_surf, texto_rect)

            # 4. Decoraciones extras 
            small_font = pygame.font.Font(FONT_FILE, 18) if os.path.exists(FONT_FILE) else pygame.font.Font(None, 24)
            
            controles_txt = "[FLECHAS]: NAVEGAR | [X]: JUGAR | [OPTIONS]: SALIR"
            surf_controles = small_font.render(controles_txt, True, COLOR_TEXTO_NORMAL)
            screen.blit(surf_controles, (20, sh - 35))
            
            usb_txt = "INSERTA UNA USB PARA AUTO-COPIAR NUEVOS JUEGOS"
            surf_usb = small_font.render(usb_txt, True, COLOR_TEXTO_NORMAL)
            usb_rect = surf_usb.get_rect(topright=(sw - 20, sh - 35))
            screen.blit(surf_usb, usb_rect)

            pygame.display.flip()

            # --- MANEJO DE EVENTOS  ---
            for evento in pygame.event.get():
                if evento.type == pygame.JOYHATMOTION:
                    x, y = evento.value
                    if juegos: 
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

                    elif evento.button == 9: 
                        screen.fill(COLOR_FONDOBASICO)
                        msg_apagando = font_title.render("APAGANDO SISTEMA...", True, COLOR_ERROR)
                        msg_rect = msg_apagando.get_rect(center=(sw // 2, sh // 2))
                        screen.blit(msg_apagando, msg_rect)
                        pygame.display.flip()
                        
                        time.sleep(1.5)
                        pygame.quit()
                        
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
