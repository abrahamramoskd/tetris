# 🎮 Tetris en Python

Implementación completa del Tetris clásico en un **solo archivo Python** usando `pygame`.
Ideal para aprender cómo funciona un videojuego desde cero.

## ✨ Características

- 7 piezas Tetrimino (I, J, L, O, S, T, Z) con rotaciones completas
- Pieza fantasma (ghost piece) para apuntar la caída
- Wall Kick básico al rotar cerca de paredes
- Sistema de niveles: sube cada 10 líneas, aumenta la velocidad
- Puntuación clásica con bonificación por soft drop y hard drop
- Panel lateral con preview de la próxima pieza
- Pausa y pantalla de Game Over
- Código comentado línea a línea con fines didácticos

## 🚀 Requisitos e instalación

```bash
pip install pygame
python tetris.py
```

## 🕹️ Controles

| Tecla     | Acción              |
|-----------|---------------------|
| `← →`    | Mover izquierda/derecha |
| `↑`       | Rotar pieza         |
| `↓`       | Bajar (soft drop)   |
| `ESPACIO` | Caída instantánea   |
| `P`       | Pausar / reanudar   |
| `R`       | Reiniciar partida   |
| `ESC`     | Salir               |

## 📁 Estructura

Todo el juego vive en un solo archivo `tetris.py`, organizado en:

- `Board` — cuadrícula, colisiones y limpieza de líneas
- `Piece` — pieza activa, rotación y ghost piece
- `Game`  — lógica principal, puntuación y renderizado
- `main`  — loop de pygame (eventos → update → draw)

## 📄 Licencia

MIT — úsalo, modifícalo y compártelo libremente.
