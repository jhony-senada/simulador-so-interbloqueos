# Simulador de Administración de Recursos e Interbloqueos (SO)

Este proyecto es un simulador desarrollado en Python que representa la administración de recursos realizada por un Sistema Operativo. El sistema gestiona memoria, procesos, archivos y dispositivos exclusivos, además de detectar y resolver interbloqueos (deadlocks) analizando las cuatro condiciones de Coffman mediante la teoría de grafos.

## Características Principales
* **Administración de Memoria:** Asignación, validación y liberación de memoria RAM.
* **Gestión de Archivos:** Creación, lectura y eliminación de archivos lógicos (Syscalls).
* **Detección de Interbloqueos:** Uso de grafos dirigidos para detectar esperas circulares.
* **Tirador de Paro Inteligente:** Estrategia heurística de recuperación (expropiación táctica o terminación forzosa).
* **Monitoreo Real:** Telemetría del hardware físico del equipo utilizando `psutil`.
* **Registro de Eventos:** Generación automática de historial en `simulacion.log`.

---

## Requisitos Previos

Asegúrate de tener instalado **Python 3.8 o superior** en tu sistema.

Las librerías externas necesarias para el funcionamiento del simulador (análisis de grafos, interfaz gráfica y monitoreo de hardware) se encuentran listadas en el archivo `requirements.txt`.

---

## Instrucciones de Instalación

1. **Clonar o descargar el repositorio**
   Abre una terminal, navega hasta la carpeta donde descargaste el proyecto y extrae los archivos.

2. **Instalar las dependencias**
   Ejecuta el siguiente comando en la terminal para instalar todas las librerías necesarias:
   
   pip install -r requirements.txt
   
## Instrucciones de Ejecución
El simulador cuenta con dos interfaces disponibles: una Interfaz de Línea de Comandos (CLI) y una Interfaz Gráfica de Usuario (GUI).

### Opción 1: Ejecución vía Menú CLI (Recomendado)
El menú CLI permite cargar los escenarios JSON dinámicamente, ejecutar la simulación en modo paso a paso o automático, y observar el monitoreo en tiempo real.
Para iniciarlo, ejecuta:

python menu_cli.py
Nota: Asegúrate de escribir el nombre exacto del archivo JSON cuando el menú te lo solicite, incluyendo la extensión, por ejemplo: ejemplo2.json.

### Opción 2: Ejecución vía Interfaz Gráfica (GUI)
Para observar el panel de control gráfico con el estado en tiempo real de los procesos [WIP]:

python gui.py

## Estructura de los Escenarios de Prueba
Los escenarios de simulación están configurados en formato JSON y deben colocarse en la misma carpeta que los archivos ejecutables. Estos archivos definen la memoria total, las políticas de expropiación, los recursos exclusivos y las acciones de los procesos.

## Autores (Equipo de Desarrollo)
[Cabello Silva José Carlos / 333306]

[Nombre de tu compañero / Matrícula]

[Nombre de tu compañero / Matrícula]