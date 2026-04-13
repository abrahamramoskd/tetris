"""
╔══════════════════════════════════════════════════════════════╗
║                     TETRIS EN PYTHON                        ║
║              Desarrollado con pygame                        ║
╚══════════════════════════════════════════════════════════════╝

CÓMO EJECUTAR:
    1. Instala pygame:  pip install pygame
    2. Ejecuta:         python tetris.py

CONTROLES:
    ← →     Mover pieza izquierda / derecha
    ↑       Rotar pieza
    ↓       Bajar pieza más rápido (soft drop)
    ESPACIO Caída instantánea (hard drop)
    P       Pausar / reanudar
    R       Reiniciar partida
    ESC     Salir
"""

import pygame          # Librería principal para gráficos y eventos
import random          # Para seleccionar piezas al azar
import sys             # Para cerrar el programa limpiamente

# ─────────────────────────────────────────────────────────────
# CONSTANTES DEL JUEGO
# Centralizar los valores aquí facilita ajustar el juego.
# ─────────────────────────────────────────────────────────────

# Tamaño de cada celda del tablero en píxeles
CELL_SIZE = 30

# Dimensiones del tablero (columnas × filas)
COLS = 10
ROWS = 20

# Dimensiones de la ventana
# El panel lateral (200 px) muestra: próxima pieza, puntaje y nivel
PANEL_WIDTH = 200
SCREEN_WIDTH  = COLS * CELL_SIZE + PANEL_WIDTH  # 500 px
SCREEN_HEIGHT = ROWS * CELL_SIZE                # 600 px

# Fotogramas por segundo — controla la suavidad de la animación
FPS = 60

# ─────────────────────────────────────────────────────────────
# COLORES  (R, G, B)
# Paleta estilo "neon oscuro" para un look retro-moderno.
# ─────────────────────────────────────────────────────────────
COLOR_BG          = (10,  10,  25)   # Fondo del tablero
COLOR_PANEL       = (18,  18,  40)   # Fondo del panel lateral
COLOR_GRID        = (30,  30,  60)   # Líneas de la cuadrícula
COLOR_TEXT        = (220, 220, 255)  # Texto general
COLOR_TITLE       = (120, 220, 255)  # Texto de títulos
COLOR_GHOST       = (255, 255, 255)  # Pieza fantasma (guía de caída)
COLOR_BORDER      = (60,  60, 120)   # Borde del tablero

# Colores de cada tipo de pieza (índice 0 = vacío)
PIECE_COLORS = [
    (10,  10,  25),    # 0 – vacío (mismo que el fondo)
    (0,  240, 240),    # 1 – I  cian
    (0,   0, 240),     # 2 – J  azul
    (240, 160,  0),    # 3 – L  naranja
    (240, 240,  0),    # 4 – O  amarillo
    (0,  240,  0),     # 5 – S  verde
    (160,  0, 240),    # 6 – T  púrpura
    (240,  0,  0),     # 7 – Z  rojo
]

# ─────────────────────────────────────────────────────────────
# DEFINICIÓN DE LAS 7 PIEZAS TETRIMINO
#
# Cada pieza es una lista de rotaciones.
# Cada rotación es una lista de coordenadas (fila, col) relativas
# al centro de la pieza. Así la rotación es solo elegir el
# siguiente elemento de la lista.
# ─────────────────────────────────────────────────────────────
PIECES = [
    # ── I ──  (color índice 1)
    [
        [(0,0),(0,1),(0,2),(0,3)],   # horizontal
        [(0,0),(1,0),(2,0),(3,0)],   # vertical
    ],
    # ── J ──  (color índice 2)
    [
        [(0,0),(1,0),(1,1),(1,2)],
        [(0,0),(0,1),(1,0),(2,0)],
        [(0,0),(0,1),(0,2),(1,2)],
        [(0,1),(1,1),(2,0),(2,1)],
    ],
    # ── L ──  (color índice 3)
    [
        [(0,2),(1,0),(1,1),(1,2)],
        [(0,0),(1,0),(2,0),(2,1)],
        [(0,0),(0,1),(0,2),(1,0)],
        [(0,0),(0,1),(1,1),(2,1)],
    ],
    # ── O ──  (color índice 4)  — no rota (cuadrado)
    [
        [(0,0),(0,1),(1,0),(1,1)],
    ],
    # ── S ──  (color índice 5)
    [
        [(0,1),(0,2),(1,0),(1,1)],
        [(0,0),(1,0),(1,1),(2,1)],
    ],
    # ── T ──  (color índice 6)
    [
        [(0,1),(1,0),(1,1),(1,2)],
        [(0,0),(1,0),(1,1),(2,0)],
        [(0,0),(0,1),(0,2),(1,1)],
        [(0,1),(1,0),(1,1),(2,1)],
    ],
    # ── Z ──  (color índice 7)
    [
        [(0,0),(0,1),(1,1),(1,2)],
        [(0,1),(1,0),(1,1),(2,0)],
    ],
]

# ─────────────────────────────────────────────────────────────
# VELOCIDADES POR NIVEL
#
# Cada valor es el número de ticks (a 60 FPS) que tarda la
# pieza en bajar una fila automáticamente. Menos = más rápido.
# ─────────────────────────────────────────────────────────────
LEVEL_SPEEDS = [48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5]

# ─────────────────────────────────────────────────────────────
# SISTEMA DE PUNTUACIÓN
#
# Puntos otorgados por eliminar N líneas de una vez.
# Multiplicado por el nivel actual para incentivar subir.
# ─────────────────────────────────────────────────────────────
LINE_POINTS = {1: 100, 2: 300, 3: 500, 4: 800}

# ─────────────────────────────────────────────────────────────
# CLASE: Tablero
#
# Representa la cuadrícula del juego como una lista de listas.
# board[fila][columna] == 0  → celda vacía
# board[fila][columna] == N  → celda ocupada por color N
# ─────────────────────────────────────────────────────────────
class Board:
    def __init__(self):
        # Inicializa un tablero vacío (todas las celdas en 0)
        self.grid = [[0] * COLS for _ in range(ROWS)]

    def is_valid(self, cells):
        """
        Verifica si una lista de celdas (fila, col) es válida:
        - Dentro de los límites del tablero
        - No superpuesta con celdas ya ocupadas
        """
        for r, c in cells:
            if c < 0 or c >= COLS:   # Fuera de límites horizontales
                return False
            if r >= ROWS:             # Por debajo del fondo
                return False
            if r >= 0 and self.grid[r][c]:  # Celda ya ocupada
                return False
        return True

    def lock(self, cells, color_idx):
        """
        Fija una pieza en el tablero asignando el índice de color
        a cada celda que ocupa. Se llama cuando la pieza aterriza.
        """
        for r, c in cells:
            if 0 <= r < ROWS:
                self.grid[r][c] = color_idx

    def clear_lines(self):
        """
        Elimina las filas completas (sin celdas a 0).
        Retorna cuántas filas fueron eliminadas.

        Algoritmo:
          1. Filtra las filas incompletas (las conserva).
          2. Cuenta cuántas filas se eliminaron.
          3. Agrega filas vacías arriba para mantener ROWS filas.
        """
        full_rows = [r for r in range(ROWS) if all(self.grid[r])]
        cleared   = len(full_rows)

        if cleared:
            # Conservar sólo las filas no completas
            self.grid = [row for r, row in enumerate(self.grid)
                         if r not in full_rows]
            # Añadir filas vacías en la parte superior
            empty_rows = [[0] * COLS for _ in range(cleared)]
            self.grid  = empty_rows + self.grid

        return cleared

    def draw(self, surface):
        """
        Dibuja el tablero completo:
          1. Fondo
          2. Celdas ocupadas (piezas fijas)
          3. Cuadrícula decorativa
          4. Borde exterior
        """
        # 1. Fondo
        pygame.draw.rect(surface, COLOR_BG,
                         (0, 0, COLS * CELL_SIZE, ROWS * CELL_SIZE))

        # 2. Celdas con color
        for r in range(ROWS):
            for c in range(COLS):
                color_idx = self.grid[r][c]
                if color_idx:
                    draw_cell(surface, r, c, PIECE_COLORS[color_idx])

        # 3. Líneas de la cuadrícula
        for r in range(ROWS + 1):
            pygame.draw.line(surface, COLOR_GRID,
                             (0, r * CELL_SIZE),
                             (COLS * CELL_SIZE, r * CELL_SIZE))
        for c in range(COLS + 1):
            pygame.draw.line(surface, COLOR_GRID,
                             (c * CELL_SIZE, 0),
                             (c * CELL_SIZE, ROWS * CELL_SIZE))

        # 4. Borde exterior
        pygame.draw.rect(surface, COLOR_BORDER,
                         (0, 0, COLS * CELL_SIZE, ROWS * CELL_SIZE), 2)


# ─────────────────────────────────────────────────────────────
# CLASE: Piece
#
# Representa la pieza activa que el jugador controla.
# ─────────────────────────────────────────────────────────────
class Piece:
    def __init__(self, piece_type=None):
        """
        piece_type: índice en la lista PIECES (0–6).
        Si no se especifica, se elige uno al azar.
        """
        if piece_type is None:
            piece_type = random.randint(0, len(PIECES) - 1)

        self.type      = piece_type
        self.color_idx = piece_type + 1        # Color: índice 1–7
        self.rotations = PIECES[piece_type]    # Lista de rotaciones
        self.rot_idx   = 0                     # Rotación actual
        # Posición inicial: centrada en la parte superior
        self.row = 0
        self.col = COLS // 2 - 2

    def cells(self):
        """
        Devuelve las coordenadas absolutas (fila, col) de los
        4 bloques de la pieza en su posición y rotación actuales.
        """
        shape = self.rotations[self.rot_idx]
        return [(self.row + dr, self.col + dc) for dr, dc in shape]

    def rotated_cells(self, direction=1):
        """
        Devuelve las celdas si se rotara en la dirección indicada
        (1 = horario, -1 = antihorario), sin aplicar el cambio.
        Útil para verificar si la rotación es válida antes de ejecutarla.
        """
        new_idx = (self.rot_idx + direction) % len(self.rotations)
        shape   = self.rotations[new_idx]
        return [(self.row + dr, self.col + dc) for dr, dc in shape]

    def ghost_cells(self, board):
        """
        Calcula la posición más baja posible de la pieza actual
        (donde caería si se soltara). Dibujada como silueta transparente
        para ayudar al jugador a apuntar.
        """
        ghost_row = self.row
        # Desplazamos hacia abajo de a 1 hasta que deje de ser válido
        while True:
            shape    = self.rotations[self.rot_idx]
            test_cells = [(ghost_row + 1 + dr, self.col + dc)
                          for dr, dc in shape]
            if board.is_valid(test_cells):
                ghost_row += 1
            else:
                break
        shape = self.rotations[self.rot_idx]
        return [(ghost_row + dr, self.col + dc) for dr, dc in shape]

    def draw(self, surface, board):
        """
        Dibuja:
          1. La pieza fantasma (ghost) con borde blanco semitransparente
          2. La pieza activa con su color sólido
        """
        # 1. Pieza fantasma
        for r, c in self.ghost_cells(board):
            if r >= 0:
                draw_cell(surface, r, c, COLOR_BG,
                          border_color=COLOR_GHOST, border_width=2)

        # 2. Pieza activa
        for r, c in self.cells():
            if r >= 0:
                draw_cell(surface, r, c, PIECE_COLORS[self.color_idx])


# ─────────────────────────────────────────────────────────────
# FUNCIÓN AUXILIAR: draw_cell
#
# Dibuja una sola celda cuadrada en la posición (row, col).
# El borde interior más oscuro da un efecto 3D sutil.
# ─────────────────────────────────────────────────────────────
def draw_cell(surface, row, col, color,
              border_color=None, border_width=1):
    x = col * CELL_SIZE
    y = row * CELL_SIZE
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    if border_color:
        # Solo borde (pieza fantasma)
        pygame.draw.rect(surface, border_color, rect, border_width)
    else:
        # Relleno sólido
        pygame.draw.rect(surface, color, rect)
        # Borde interior oscuro para efecto 3D
        dark = tuple(max(0, v - 60) for v in color)
        pygame.draw.rect(surface, dark, rect, 1)


# ─────────────────────────────────────────────────────────────
# CLASE: Game
#
# Orquesta toda la lógica del juego:
#   - Estado (tablero, pieza activa, puntuación…)
#   - Loop de actualización (física, colisiones, limpieza)
#   - Renderizado (tablero + panel lateral + pantallas)
# ─────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        """Reinicia el estado completo para una nueva partida."""
        self.board       = Board()
        self.score       = 0
        self.lines       = 0       # Total de líneas eliminadas
        self.level       = 1
        self.piece       = Piece() # Pieza activa
        self.next_piece  = Piece() # Próxima pieza (se muestra en panel)
        self.paused      = False
        self.game_over   = False
        self.tick        = 0       # Contador de frames para la caída automática

    # ── Propiedades de velocidad ──────────────────────────────

    @property
    def fall_speed(self):
        """
        Devuelve cuántos ticks (frames) tarda la pieza en caer 1 fila.
        Usa la tabla LEVEL_SPEEDS; al pasar el nivel 10 queda en 5.
        """
        idx = min(self.level - 1, len(LEVEL_SPEEDS) - 1)
        return LEVEL_SPEEDS[idx]

    # ── Lógica de movimiento ──────────────────────────────────

    def move(self, d_col):
        """
        Desplaza la pieza activa horizontalmente.
        d_col: +1 (derecha) o -1 (izquierda)
        """
        test = [(r, c + d_col) for r, c in self.piece.cells()]
        if self.board.is_valid(test):
            self.piece.col += d_col

    def rotate(self, direction=1):
        """
        Rota la pieza en la dirección indicada (1=horario).
        Si la posición rotada es inválida, intenta desplazarla
        1 o 2 columnas a cada lado (Wall Kick básico).
        """
        test = self.piece.rotated_cells(direction)
        if self.board.is_valid(test):
            self.piece.rot_idx = (self.piece.rot_idx + direction) % \
                                  len(self.piece.rotations)
            return

        # Wall kick: probar pequeños desplazamientos laterales
        for d_col in [1, -1, 2, -2]:
            kicked = [(r, c + d_col) for r, c in test]
            if self.board.is_valid(kicked):
                self.piece.col    += d_col
                self.piece.rot_idx = (self.piece.rot_idx + direction) % \
                                      len(self.piece.rotations)
                return
        # Si ningún kick funciona, la rotación se cancela

    def soft_drop(self):
        """
        Baja la pieza 1 fila manualmente (tecla ↓).
        Si no puede bajar, la fija en el tablero.
        Suma 1 punto por cada fila de soft drop.
        """
        test = [(r + 1, c) for r, c in self.piece.cells()]
        if self.board.is_valid(test):
            self.piece.row += 1
            self.score     += 1  # Bonificación por soft drop
        else:
            self._lock_piece()

    def hard_drop(self):
        """
        Caída instantánea (tecla ESPACIO).
        Suma 2 puntos por cada fila caída.
        """
        ghost = self.piece.ghost_cells(self.board)
        # Calculamos cuántas filas desciende comparando ghost con posición actual
        if ghost:
            drop_rows = ghost[0][0] - self.piece.cells()[0][0]
            self.piece.row += drop_rows
            self.score     += drop_rows * 2
        self._lock_piece()

    def _lock_piece(self):
        """
        Fija la pieza activa en el tablero y prepara la siguiente.

        Secuencia:
          1. Escribir la pieza en el grid.
          2. Limpiar filas completas y actualizar puntaje.
          3. Actualizar nivel cada 10 líneas.
          4. Hacer que la próxima pieza se vuelva la activa.
          5. Detectar Game Over si la nueva pieza ya colisiona.
        """
        # 1. Fijar en el tablero
        self.board.lock(self.piece.cells(), self.piece.color_idx)

        # 2. Limpiar líneas
        cleared = self.board.clear_lines()
        if cleared:
            self.lines += cleared
            self.score += LINE_POINTS.get(cleared, 0) * self.level

        # 3. Subir de nivel cada 10 líneas eliminadas
        self.level = max(1, self.lines // 10 + 1)

        # 4. Avanzar a la próxima pieza
        self.piece      = self.next_piece
        self.next_piece = Piece()
        self.tick       = 0   # Reinicia el contador de caída

        # 5. Game Over: la nueva pieza colisiona al aparecer
        if not self.board.is_valid(self.piece.cells()):
            self.game_over = True

    # ── Loop de actualización ─────────────────────────────────

    def update(self):
        """
        Llamada cada frame. Incrementa el tick y, cuando alcanza
        la velocidad del nivel, baja la pieza automáticamente.
        """
        if self.paused or self.game_over:
            return

        self.tick += 1
        if self.tick >= self.fall_speed:
            self.tick = 0
            test = [(r + 1, c) for r, c in self.piece.cells()]
            if self.board.is_valid(test):
                self.piece.row += 1
            else:
                self._lock_piece()

    # ── Renderizado ───────────────────────────────────────────

    def draw(self, surface, font_big, font_med, font_small):
        """
        Dibuja toda la pantalla:
          1. Tablero con piezas fijas y activa
          2. Panel lateral derecho (next, score, level, líneas)
          3. Overlay de pausa o Game Over si corresponde
        """
        # 1. Tablero
        self.board.draw(surface)
        if not self.game_over:
            self.piece.draw(surface, self.board)

        # 2. Panel lateral
        self._draw_panel(surface, font_big, font_med, font_small)

        # 3. Overlays
        if self.paused:
            self._draw_overlay(surface, font_big, "PAUSA",
                               "(P) para continuar")
        elif self.game_over:
            self._draw_overlay(surface, font_big, "GAME OVER",
                               f"Puntaje: {self.score}  (R) reiniciar")

    def _draw_panel(self, surface, font_big, font_med, font_small):
        """Panel lateral con información del juego."""
        px = COLS * CELL_SIZE + 10  # X de inicio del panel
        py = 10                     # Y de inicio

        # Fondo del panel
        pygame.draw.rect(surface, COLOR_PANEL,
                         (COLS * CELL_SIZE, 0, PANEL_WIDTH, SCREEN_HEIGHT))

        # ── Título ──
        txt = font_big.render("TETRIS", True, COLOR_TITLE)
        surface.blit(txt, (px, py))
        py += 40

        # ── Próxima pieza ──
        lbl = font_small.render("Siguiente:", True, COLOR_TEXT)
        surface.blit(lbl, (px, py))
        py += 20
        self._draw_next(surface, px, py)
        py += 90

        # ── Puntaje ──
        surface.blit(font_small.render("Puntaje", True, COLOR_TEXT), (px, py))
        py += 18
        surface.blit(font_med.render(str(self.score), True, COLOR_TITLE), (px, py))
        py += 35

        # ── Nivel ──
        surface.blit(font_small.render("Nivel", True, COLOR_TEXT), (px, py))
        py += 18
        surface.blit(font_med.render(str(self.level), True, COLOR_TITLE), (px, py))
        py += 35

        # ── Líneas eliminadas ──
        surface.blit(font_small.render("Líneas", True, COLOR_TEXT), (px, py))
        py += 18
        surface.blit(font_med.render(str(self.lines), True, COLOR_TITLE), (px, py))
        py += 50

        # ── Controles ──
        controls = [
            ("←→", "Mover"),
            ("↑",  "Rotar"),
            ("↓",  "Bajar"),
            ("SPC","Caída"),
            ("P",  "Pausa"),
            ("R",  "Restart"),
        ]
        surface.blit(font_small.render("Controles:", True, COLOR_TEXT), (px, py))
        py += 20
        for key, action in controls:
            line = font_small.render(f"{key:>3} {action}", True,
                                     (160, 160, 200))
            surface.blit(line, (px, py))
            py += 18

    def _draw_next(self, surface, px, py):
        """
        Muestra la próxima pieza centrada dentro de una caja 4×4
        en el panel lateral.
        """
        # Fondo de la caja de preview
        box_size = CELL_SIZE * 4
        pygame.draw.rect(surface, COLOR_BG, (px, py, box_size, box_size))
        pygame.draw.rect(surface, COLOR_BORDER, (px, py, box_size, box_size), 1)

        shape = self.next_piece.rotations[0]
        color = PIECE_COLORS[self.next_piece.color_idx]

        # Centramos la pieza dentro de la caja
        rows_used = max(r for r, c in shape) - min(r for r, c in shape) + 1
        cols_used = max(c for r, c in shape) - min(c for r, c in shape) + 1
        min_r     = min(r for r, c in shape)
        min_c     = min(c for r, c in shape)

        offset_r = (4 - rows_used) // 2 - min_r
        offset_c = (4 - cols_used) // 2 - min_c

        for dr, dc in shape:
            x = px + (dc + offset_c) * CELL_SIZE
            y = py + (dr + offset_r) * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, color, rect)
            dark = tuple(max(0, v - 60) for v in color)
            pygame.draw.rect(surface, dark, rect, 1)

    def _draw_overlay(self, surface, font, title, subtitle):
        """
        Dibuja un rectángulo semitransparente sobre el tablero
        con el título y subtítulo indicados (pausa / game over).
        """
        # Superficie semitransparente
        overlay = pygame.Surface((COLS * CELL_SIZE, ROWS * CELL_SIZE),
                                  pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Título centrado
        t1 = font.render(title, True, (255, 80, 80))
        surface.blit(t1, (COLS * CELL_SIZE // 2 - t1.get_width() // 2,
                          ROWS * CELL_SIZE // 2 - 40))

        # Subtítulo
        t2 = pygame.font.SysFont("monospace", 14).render(subtitle, True, COLOR_TEXT)
        surface.blit(t2, (COLS * CELL_SIZE // 2 - t2.get_width() // 2,
                          ROWS * CELL_SIZE // 2 + 10))


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL: main
#
# Inicializa pygame, crea las fuentes, el juego y ejecuta
# el loop principal (captura eventos → actualiza → dibuja).
# ─────────────────────────────────────────────────────────────
def main():
    pygame.init()
    pygame.display.set_caption("Tetris – Python")

    # Crear ventana principal
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock  = pygame.time.Clock()

    # Fuentes — se usan 3 tamaños para jerarquía visual
    font_big   = pygame.font.SysFont("monospace", 24, bold=True)
    font_med   = pygame.font.SysFont("monospace", 20, bold=True)
    font_small = pygame.font.SysFont("monospace", 13)

    game = Game()

    # ── Loop principal ────────────────────────────────────────
    # El loop corre a FPS constantes; en cada iteración:
    #   1. Procesa eventos del teclado/ventana
    #   2. Actualiza la lógica (caída automática)
    #   3. Dibuja todo en pantalla
    # ─────────────────────────────────────────────────────────
    while True:

        # ── 1. Eventos ────────────────────────────────────────
        for event in pygame.event.get():

            if event.type == pygame.QUIT:          # Cerrar ventana
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:   # Salir con ESC
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_r:        # Reiniciar
                    game.reset()

                if event.key == pygame.K_p:        # Pausar / reanudar
                    if not game.game_over:
                        game.paused = not game.paused

                # Controles de movimiento (solo si el juego está activo)
                if not game.paused and not game.game_over:
                    if event.key == pygame.K_LEFT:
                        game.move(-1)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1)
                    elif event.key == pygame.K_UP:
                        game.rotate(1)
                    elif event.key == pygame.K_DOWN:
                        game.soft_drop()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()

        # ── 2. Actualización lógica ───────────────────────────
        game.update()

        # ── 3. Renderizado ────────────────────────────────────
        screen.fill(COLOR_BG)                      # Limpiar pantalla
        game.draw(screen, font_big, font_med, font_small)
        pygame.display.flip()                      # Mostrar el frame

        clock.tick(FPS)                            # Limitar a FPS constantes


# ─────────────────────────────────────────────────────────────
# Punto de entrada estándar de Python
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
