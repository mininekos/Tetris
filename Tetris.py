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
game_sc = pygame.Surface(TAMVENTANA)
clock = pygame.time.Clock()

lineasTablero = [pygame.Rect(x * TAMFILA, y * TAMFILA, TAMFILA, TAMFILA) for x in range(COLUMNAS) for y in range(FILAS)]

posicionFiguras = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],  #asd
                   [(0, -1), (-1, -1), (-1, 0), (0, 0)],  #asd
                   [(-1, 0), (-1, 1), (0, 0), (0, -1)],  #asd
                   [(0, 0), (-1, 0), (0, 1), (-1, -1)],  #asd
                   [(0, 0), (0, -1), (0, 1), (-1, -1)],  #asd
                   [(0, 0), (0, -1), (0, 1), (1, -1)],  #asd
                   [(0, 0), (0, -1), (0, 1), (-1, 0)]] #asd

figuras = [[pygame.Rect(x + COLUMNAS // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in posicionFiguras]
figure_rect = pygame.Rect(0, 0, TAMFILA - 2, TAMFILA - 2)
tablero = [[0 for i in range(COLUMNAS)] for j in range(FILAS)]

anim_count, anim_speed, anim_limit = 0, 60, 2000

bg = pygame.image.load('imagenes/1700.jpg').convert()
game_bg = pygame.image.load('imagenes/1700.jpg').convert()

main_font = pygame.font.SysFont('arial', 65)
font = pygame.font.SysFont('arial', 45)
# definir textos
titulo = main_font.render('TETRIS', True, pygame.Color('darkorange'))
txtScore = font.render('score: ', True, pygame.Color('green'))
txtRecord = font.render('record: ', True, pygame.Color('purple'))

get_color = lambda : (randrange(30, 256), randrange(30, 256), randrange(30, 256))

figure, next_figure = deepcopy(choice(figuras)), deepcopy(choice(figuras))
color, next_color = get_color(), get_color()

score, comboLineas = 0, 0
puntosCombo = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


def check_borders():
    if figure[i].x < 0 or figure[i].x > COLUMNAS - 1:
        return False
    elif figure[i].y > FILAS - 1 or tablero[figure[i].y][figure[i].x]:
        return False
    return True

# quitar record
def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')


def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))


while True:
    record = get_record()
    dx, rotate = 0, False
    sc.blit(bg, (0, 0))
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game_bg, (0, 0))
    # delay for full lines
    for i in range(comboLineas):
        pygame.time.wait(200)
    # control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True
    # move x
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break
    # move y
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    tablero[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figuras)), get_color()
                anim_limit = 2000
                break
    # rotate
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not check_borders():
                figure = deepcopy(figure_old)
                break
    # check lines
    line, comboLineas = FILAS - 1, 0
    for row in range(FILAS - 1, -1, -1):
        count = 0
        for i in range(COLUMNAS):
            if tablero[row][i]:
                count += 1
            tablero[line][i] = tablero[row][i]
        if count < COLUMNAS:
            line -= 1
        else:
            anim_speed += 3
            comboLineas += 1
    # compute score
    score += puntosCombo[comboLineas]
    # draw grid
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in lineasTablero]
    # draw figure
    for i in range(4):
        figure_rect.x = figure[i].x * TAMFILA
        figure_rect.y = figure[i].y * TAMFILA
        pygame.draw.rect(game_sc, color, figure_rect)
    # draw field
    for y, raw in enumerate(tablero):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TAMFILA, y * TAMFILA
                pygame.draw.rect(game_sc, col, figure_rect)
    # draw next figure
    for i in range(4):
        figure_rect.x = next_figure[i].x * TAMFILA + 380
        figure_rect.y = next_figure[i].y * TAMFILA + 185
        pygame.draw.rect(sc, next_color, figure_rect)
    # draw titles
    sc.blit(titulo, (485, -10))
    sc.blit(txtScore, (535, 780))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (550, 840))
    sc.blit(txtRecord, (525, 650))
    sc.blit(font.render(record, True, pygame.Color('gold')), (550, 710))
    # game over
    for i in range(COLUMNAS):
        if tablero[0][i]:
            # quitar record
            set_record(record, score)
            tablero = [[0 for i in range(COLUMNAS)] for i in range(FILAS)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score = 0
            for i_rect in lineasTablero:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20, 20))
                pygame.display.flip()
                clock.tick(200)

    pygame.display.flip()
    clock.tick(FPS)