# Consola Retro Embebida

Proyecto final de la asignatura **Fundamentos de Sistemas Embebidos**.

Este proyecto implementa una consola retro embebida utilizando Raspberry Pi OS Lite, Python, Pygame, Mednafen, systemd, udev y scripts Bash. El sistema está diseñado para iniciar automáticamente sin escritorio gráfico, mostrar una interfaz gráfica propia con temática Synthwave, permitir la selección de juegos mediante gamepad o joystick, ejecutar ROMS retro mediante emulación y detectar memorias USB para la importación interactiva de nuevos juegos.

## Objetivo

Implementar una consola de videojuegos retro como sistema embebido, capaz de arrancar directamente a una interfaz de usuario propia, operar sin teclado ni mouse, emular juegos de NES, SNES y Game Boy Advance, e importar ROMS desde una memoria USB al almacenamiento local de la Raspberry Pi de forma amigable e interactiva.

## Características principales

* Arranque automático mediante systemd.
* Interfaz gráfica fluida estilo Synthwave (cuadrícula de perspectiva y colores neón) desarrollada con Python y Pygame.
* Operación completa mediante gamepad o joystick.
* Ejecución de juegos mediante Mednafen.
* Soporte para ROMS de NES, SNES y Game Boy Advance.
* Menú en pantalla completa sin entorno de escritorio.
* **Detección de USB e importación interactiva**: Alerta sonora y ventana emergente que consulta al usuario antes de copiar archivos.
* Visualización en pantalla de los juegos copiados (mostrando hasta 10 juegos recientes y truncando nombres largos para mantener la estética).
* Copia inteligente de ROMS usando rsync para evitar sobrescribir archivos existentes.
* Intro personalizada de arranque con soporte para video o imagen con audio.
* Scripts de instalación y configuración para Raspberry Pi OS.

## Estructura del repositorio

```text
.
├── assets/              Archivos de recursos: fuente retro, intro personalizada y alerta_usb.wav
├── doc/                 Documentación técnica y tutorial individual
├── roms/                Carpeta local para ROMS; no se suben ROMS al repositorio
├── scripts/             Scripts Bash de arranque, intro y sincronización USB
├── src/                 Código fuente principal del menú (menu.py)
├── systemd/             Servicios systemd del proyecto
├── udev/                Regla udev para detección de USB
├── vid/                 Archivo con URL del video demostrativo
├── install.sh           Instalador automatizado del proyecto
├── LICENSE              Licencia del proyecto
└── README.md            Descripción e instrucciones del proyecto
```

## Requisitos de hardware

* Raspberry Pi compatible con Raspberry Pi OS Lite.
* Tarjeta microSD.
* Fuente de alimentación adecuada para Raspberry Pi.
* Pantalla HDMI.
* Gamepad o joystick USB.
* Memoria USB para importar ROMS.
* Bocinas o salida de audio por HDMI.

## Requisitos de software

El proyecto está pensado para ejecutarse sobre Raspberry Pi OS Lite o un sistema base compatible con Debian. El instalador configura las dependencias principales:

* Python 3.
* Pygame.
* Mednafen.
* joystick.
* evtest.
* mpv.
* rsync.
* systemd.
* udev.

## Instalación

Clonar el repositorio en la Raspberry Pi:

```bash
git clone https://github.com/daniel13nic/proyecto-retro-embebidos.git
cd proyecto-retro-embebidos
```

Ejecutar el instalador:

```bash
chmod +x install.sh
./install.sh
```

El script instala dependencias, copia los archivos necesarios, configura los servicios systemd, instala la regla udev y habilita el arranque automático del menú.

Para iniciar manualmente la intro:

```bash
sudo systemctl start splash.service
```

Para iniciar manualmente el menú:

```bash
sudo systemctl start retromenu.service
```

Para revisar errores:

```bash
journalctl -u splash.service -e
journalctl -u retromenu.service -e
```

## Organización de ROMS

Las ROMS deben colocarse localmente en:

```text
/home/pi/roms
```

Extensiones soportadas:

```text
NES:  .nes
SNES: .sfc, .smc
GBA:  .gba
```

Las ROMS no se incluyen en el repositorio. Para pruebas y demostración se recomienda utilizar ROMS homebrew, demos o juegos de libre distribución.

## Formato de USB para importar ROMS

La memoria USB puede contener ROMS en su raíz o dentro de carpetas. El script de sincronización busca archivos con extensiones válidas y los copia al directorio local de ROMS.

Extensiones aceptadas:

```text
.nes
.sfc
.smc
.gba
```

El sistema utiliza `rsync --ignore-existing`, por lo que no sobrescribe archivos ya existentes con el mismo nombre.

## Flujo de funcionamiento

1. La Raspberry Pi se energiza.
2. Raspberry Pi OS Lite inicia sin escritorio gráfico.
3. systemd ejecuta el servicio de intro personalizada.
4. systemd ejecuta el menú retro (interfaz Synthwave).
5. El usuario navega la lista de juegos con el gamepad o joystick.
6. Al seleccionar un juego, el menú escribe la ruta en /tmp/next_game.txt y se cierra.
7. El script start.sh orquesta la ejecución lanzando Mednafen con la ROM seleccionada.
8. Al terminar el juego, el sistema vuelve automáticamente al menú.
9. Si se inserta una USB, udev genera una bandera en el sistema (/tmp/usb_pending).
10. El menú de Pygame detecta la bandera, emite un efecto de sonido y despliega una ventana emergente interactiva preguntando si se desean copiar los juegos.
11. Si el usuario presiona [X], el menú llama internamente al script de sincronización, muestra el progreso, y finalmente despliega una lista de confirmación con los juegos transferidos (leyendo /tmp/juegos_copiados.txt).

## Archivos principales

### `src/menu.py`

Implementa la interfaz gráfica principal con Pygame. Dibuja el fondo Synthwave, centra dinámicamente los textos, reproduce el sonido de alerta, maneja la ventana emergente de confirmación de USB, procesa los inputs del gamepad y genera el archivo temporal para que el orquestador ejecute el emulador.

### `scripts/start.sh`

Actúa como orquestador del sistema. Ejecuta el menú, espera la selección de una ROM y después lanza Mednafen. Al cerrar el emulador, regresa al menú.

### `scripts/sync_roms.sh`

Invocado por el menu.py tras la confirmación del usuario. Monta el dispositivo USB, copia las ROMS válidas al almacenamiento local usando rsync, escribe los nombres de los archivos copiados en un .txt temporal para que la interfaz los muestre, y desmonta la USB de forma segura.

### `systemd/retromenu.service`

Servicio systemd encargado de iniciar automáticamente el menú retro en la terminal TTY1.

### `udev/99-usb-sync.rules`

Regla udev que detecta la conexión de una memoria USB y detona la señal (bandera) que el menú intercepta para iniciar el proceso de copia.


## Video demostrativo

```text
URL del video: https://youtu.be/Xch_X6m8AQw
```

## Repositorio

```text
https://github.com/daniel13nic/proyecto-retro-embebidos
```

## Autores

Proyecto desarrollado en equipo para la asignatura Fundamentos de Sistemas Embebidos.

Integrantes:

* Daniel Nicolás Feregrino
* Cesar Romualdo Ramírez Cervantes
* Luis Enrique Monter González

## Licencia

Este proyecto se distribuye bajo licencia MIT. Consultar el archivo `LICENSE`.
