# 🔍 Visualizador de Procesos Importantes en Windows

Este script en Python analiza un árbol de procesos de Windows y visualiza solo los procesos **más importantes**, omitiendo el ruido de procesos secundarios.

## 🚀 ¿Qué hace?

- Carga un árbol de procesos desde un archivo `pstree.json`
- Filtra procesos importantes como `chrome.exe`, `code.exe`, `discord.exe`, etc.
- Construye un grafo visual mostrando relaciones entre procesos
- Dibuja el grafo con un diseño jerárquico y limpio
- Muestra estadísticas finales

## 🧠 Procesos incluidos

### Procesos importantes:
- `explorer.exe`
- `chrome.exe`
- `firefox.exe`
- `notepad.exe`
- `cmd.exe`
- `powershell.exe`
- `python.exe`
- `code.exe`
- `discord.exe`
- `teams.exe`
- `steam.exe`
- `winrar.exe`

### Procesos raíz básicos (siempre incluidos para la estructura):
- `system`
- `services.exe`
- `wininit.exe`
- `smss.exe`

## 📁 Requisitos

- Python 3.x
- `networkx`
- `matplotlib`

Instálalos con:

```bash
pip install networkx matplotlib
