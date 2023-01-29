import pygame
from copy import deepcopy
from random import choice, randrange

# Defino las constantes
# num de filas y columnas
COLUMNAS, FILAS = 10, 20
TAMFILA = 45
TAMVENTANA = COLUMNAS * TAMFILA, FILAS * TAMFILA
RES = 750, 940
FPS = 60

pygame.init()
sc = pygame.display.set_mode(RES)
ventana_juego = pygame.Surface(TAMVENTANA)
refresco_pantalla = pygame.time.Clock()

lineasTablero = [pygame.Rect(x * TAMFILA, y * TAMFILA, TAMFILA, TAMFILA) for x in range(COLUMNAS) for y in range(FILAS)]

posicionFiguras = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],  # PALO
                   [(0, -1), (-1, -1), (-1, 0), (0, 0)],  # CUADRADO
                   [(-1, 0), (-1, 1), (0, 0), (0, -1)],  # ZETA
                   [(0, 0), (-1, 0), (0, 1), (-1, -1)],  # ZETA INVERTIDA
                   [(0, 0), (0, -1), (0, 1), (-1, -1)],  # L
                   [(0, 0), (0, -1), (0, 1), (1, -1)],  # J
                   [(0, 0), (0, -1), (0, 1), (-1, 0)]] # MINI T

figuras = [[pygame.Rect(x + COLUMNAS // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in posicionFiguras]
tam_linea_figura = pygame.Rect(0, 0, TAMFILA - 2, TAMFILA - 2)
tablero = [[0 for i in range(COLUMNAS)] for j in range(FILAS)]

contador_velocidad, velocidad_animacion, velocidad_limite = 0, 60, 2000

bg = pygame.image.load('imagenes/1700.jpg').convert()
game_bg = pygame.image.load('imagenes/1700.jpg').convert()

main_font = pygame.font.SysFont('arial', 65)
font = pygame.font.SysFont('arial', 45)
# definir textos
titulo = main_font.render('TETRIS', True, pygame.Color('darkorange'))
txtScore = font.render('score: ', True, pygame.Color('green'))
txtRecord = font.render('record: ', True, pygame.Color('purple'))

colores=[(255, 0,   0  ),
            (0,   150, 0  ),
            (0,   0,   255),
            (255, 120, 0  ),
            (255, 255, 0  ),
            (180, 0,   255),
            (0,   220, 220)]

get_color = lambda : (randrange(30, 256), randrange(30, 256), randrange(30, 256))

figura_actual, siguiente_figura =deepcopy(choice(figuras)), deepcopy(choice(figuras))
color_actual, siguiente_color = get_color(), get_color()

score, record, comboLineas = 0, 0, 0

puntosCombo = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


# Comprobar si la pieza sale del tablero
def comprobar_bordes():
    if figura_actual[i].x < 0 or figura_actual[i].x > COLUMNAS - 1:
        return False
    elif figura_actual[i].y > FILAS - 1 or tablero[figura_actual[i].y][figura_actual[i].x]:
        return False
    return True

while True:

    mover_eje_x, rotar = 0, False
    sc.blit(bg, (0, 0))
    sc.blit(ventana_juego, (20, 20))
    ventana_juego.blit(game_bg, (0, 0))
    # retraso para puntuar
    for i in range(comboLineas):
        pygame.time.wait(200)
    # EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                mover_eje_x = -1
            elif event.key == pygame.K_RIGHT:
                mover_eje_x = 1
            elif event.key == pygame.K_DOWN:
                # Cambio la velocidad para que caiga rapido
                velocidad_limite = 100
            elif event.key == pygame.K_SPACE:
                velocidad_limite = 100
            elif event.key == pygame.K_UP:
                rotar = True
        if event.type == pygame.KEYUP:
            if event.key==pygame.K_DOWN:
                # Cambio la velocidad para que reinicie su velocidad normal
                velocidad_limite=2000
    # Movimiento de la figura eje x
    figura_anterior = deepcopy(figura_actual)
    for i in range(4):
        figura_actual[i].x += mover_eje_x
        if not comprobar_bordes():
            figura_actual = deepcopy(figura_anterior)
            break
    # Movimiento de la figura eje y
    contador_velocidad += velocidad_animacion
    if contador_velocidad > velocidad_limite:
        contador_velocidad = 0
        figura_anterior = deepcopy(figura_actual)
        for i in range(4):
            figura_actual[i].y += 1
            if not comprobar_bordes():
                for i in range(4):
                    tablero[figura_anterior[i].y][figura_anterior[i].x] = color_actual
                figura_actual, color_actual = siguiente_figura, siguiente_color
                siguiente_figura, siguiente_color = deepcopy(choice(figuras)), get_color()
                velocidad_limite = 2000
                break
    # Girar
    centro_rotacion = figura_actual[0]
    figura_anterior = deepcopy(figura_actual)
    if rotar:
        for i in range(4):
            x = figura_actual[i].y - centro_rotacion.y
            y = figura_actual[i].x - centro_rotacion.x
            figura_actual[i].x = centro_rotacion.x - x
            figura_actual[i].y = centro_rotacion.y + y
            if not comprobar_bordes():
                figura_actual = deepcopy(figura_anterior)
                break
    # Comprobar lineas
    linea, comboLineas = FILAS - 1, 0
    for fila_comprobar in range(FILAS - 1, -1, -1):
        # contador de columnas
        num_filas = 0
        for i in range(COLUMNAS):
            if tablero[fila_comprobar][i]:
                # sumo 1 al contador si coincide
                num_filas += 1
            # paso a la siguiente linea
            tablero[linea][i] = tablero[fila_comprobar][i]
        # Si hay la misma cantidad de columnas en el contador que en total hay una linea completa
        # no coincide
        if num_filas < COLUMNAS:
            linea -= 1
        # Coincide y sumo para luego puntuar
        else:
            velocidad_animacion += 3
            comboLineas += 1
    # Puntuo acorde a la cantidad de lineas que se hayan hecho
    score += puntosCombo[comboLineas]
    # Pintar pantalla
    [pygame.draw.rect(ventana_juego, (40, 40, 40), i_rect, 1) for i_rect in lineasTablero]
    # dibujar figura
    for i in range(4):
        tam_linea_figura.x = figura_actual[i].x * TAMFILA
        tam_linea_figura.y = figura_actual[i].y * TAMFILA
        pygame.draw.rect(ventana_juego, color_actual, tam_linea_figura)
    # Pintar tablero
    for y, raw in enumerate(tablero):
        for x, col in enumerate(raw):
            if col:
                tam_linea_figura.x, tam_linea_figura.y = x * TAMFILA, y * TAMFILA
                pygame.draw.rect(ventana_juego, col, tam_linea_figura)
    # Visualizar siguiente figura
    for i in range(4):
        tam_linea_figura.x = siguiente_figura[i].x * TAMFILA + 380
        tam_linea_figura.y = siguiente_figura[i].y * TAMFILA + 185
        pygame.draw.rect(sc, siguiente_color, tam_linea_figura)
    # Pintar textos
    sc.blit(titulo, (485, -10))
    sc.blit(txtScore, (535, 780))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (550, 840))
    sc.blit(txtRecord, (525, 650))
    sc.blit(font.render(str(record), True, pygame.Color('gold')), (550, 710))
    # Perder
    for i in range(COLUMNAS):
        if tablero[0][i]:
            # Cambio el record si se supera
            if record < score:
                record=score
            tablero = [[0 for i in range(COLUMNAS)] for i in range(FILAS)]
            # Reset de variables
            contador_velocidad, velocidad_animacion, velocidad_limite = 0, 60, 2000
            score = 0
            # Redibujo el tablero y pongo una animazion to wapa para cada cuadrado
            for i_rect in lineasTablero:
                pygame.draw.rect(ventana_juego, get_color(), i_rect)
                sc.blit(ventana_juego, (20, 20))
                pygame.display.flip()
                refresco_pantalla.tick(200)

    pygame.display.flip()
    refresco_pantalla.tick(FPS)