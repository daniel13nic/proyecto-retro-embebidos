# Consola Retro Embebida

Proyecto final de la asignatura **Fundamentos de Sistemas Embebidos**.

Este proyecto implementa una consola retro embebida utilizando Raspberry Pi OS Lite, Python, Pygame, Mednafen, systemd, udev y scripts Bash. El sistema está diseñado para iniciar automáticamente sin escritorio gráfico, mostrar una interfaz propia tipo menú, permitir la selección de juegos mediante gamepad o joystick, ejecutar ROMS retro mediante emulación y copiar nuevas ROMS desde una memoria USB.

## Objetivo

Implementar una consola de videojuegos retro como sistema embebido, capaz de arrancar directamente a una interfaz de usuario propia, operar sin teclado ni mouse, emular juegos de NES, SNES y Game Boy Advance, e importar ROMS desde una memoria USB al almacenamiento local de la Raspberry Pi.

## Características principales

* Arranque automático mediante systemd.
* Interfaz gráfica propia desarrollada con Python y Pygame.
* Operación mediante gamepad o joystick.
* Ejecución de juegos mediante Mednafen.
* Soporte para ROMS de NES, SNES y Game Boy Advance.
* Menú en pantalla completa sin entorno de escritorio.
* Importación automática de ROMS desde memoria USB.
* Pausa temporal del menú o emulador durante la sincronización USB.
* Copia inteligente de ROMS usando rsync para evitar sobrescribir archivos existentes.
* Intro personalizada de arranque con soporte para video o imagen con audio.
* Scripts de instalación y configuración para Raspberry Pi OS.

## Estructura del repositorio

```text
.
├── assets/              Archivos de recursos: fuente retro e intro personalizada
├── doc/                 Documentación técnica y tutorial individual
├── roms/                Carpeta local para ROMS; no se suben ROMS al repositorio
├── scripts/             Scripts Bash de arranque, intro y sincronización USB
├── src/                 Código fuente principal del menú
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
4. systemd ejecuta el menú retro.
5. El usuario navega con gamepad o joystick.
6. Al seleccionar un juego, el menú escribe la ruta en `/tmp/next_game.txt`.
7. El script `start.sh` ejecuta Mednafen con la ROM seleccionada.
8. Al terminar el juego, el sistema vuelve al menú.
9. Si se inserta una USB, udev ejecuta el script de sincronización.
10. El script pausa el menú o emulador, copia ROMS válidas, desmonta la USB y reanuda el sistema.

## Archivos principales

### `src/menu.py`

Implementa la interfaz gráfica principal con Pygame. Muestra la lista de ROMS disponibles, permite navegar con gamepad o joystick, selecciona juegos y genera el archivo temporal usado por el orquestador para ejecutar el emulador.

### `scripts/start.sh`

Actúa como orquestador del sistema. Ejecuta el menú, espera la selección de una ROM y después lanza Mednafen. Al cerrar el emulador, regresa al menú.

### `scripts/sync_roms.sh`

Se ejecuta cuando udev detecta una memoria USB. Monta el dispositivo, pausa temporalmente el menú o emulador, copia las ROMS válidas al almacenamiento local y reanuda el sistema.

### `systemd/retromenu.service`

Servicio systemd encargado de iniciar automáticamente el menú retro en la terminal TTY1.

### `udev/99-usb-sync.rules`

Regla udev que detecta la conexión de una memoria USB y lanza el script de sincronización de ROMS.


## Video demostrativo

El enlace al video demostrativo debe colocarse en:

```text
vid/video.txt
```

También debe agregarse aquí cuando esté disponible:

```text
URL del video: pendiente
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
