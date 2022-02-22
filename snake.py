from textwrap import fill
import pygame, random, math, time, datetime, copy

SCALE = [15, 15]
RELSIZE = [40, 40]
FRAME_DELAY = 0
screenf = None
screen_width, screen_height = (RELSIZE[0]+1)*SCALE[0], (RELSIZE[1]+1)*SCALE[1]

def randcolor_bright():
    c = [random.random()*256, random.random()*256, random.random()*256]
    s = c.copy()
    s.sort()
    #print()
    #print(c)
    diff = 255 - s[-1]
    #print(diff)
    for i in range(len(c)):
        c[i] += diff
    c = (int(c[0]), int(c[1]), int(c[2]))
    #print(c)
    return c

COLORS = []
for y in range(RELSIZE[1]+1):
    COLORS.append([])
    for x in range(RELSIZE[0]+1):
        COLORS[-1].append(randcolor_bright())

LOST = False

d_time = 0
world_speed = 1
calc_time = [0, 0]

def distance(vec1, vec2):
    return math.sqrt((vec2[0] - vec1[0])**2 + (vec2[1] - vec1[1])**2)

def getMs():
    #print((datetime.datetime.now().microsecond + datetime.datetime.now().second*1000000 + datetime.datetime.now().minute*1000000*60 )/1000000)
    return (datetime.datetime.now().microsecond + datetime.datetime.now().second*1000000 + datetime.datetime.now().minute*1000000*60 + datetime.datetime.now().hour*10000000*60)/1000000

def getChange(dir):
    if dir == 0:
        return [1, 0]
    elif dir == 1:
        return [-1, 0]
    elif dir == 2:
        return [0, 1]
    else:
        return [0, -1]

def getDir(change):
    if change == [1, 0]:
        return 0
    elif change == [-1, 0]:
        return 1
    elif change == [0, 1]:
        return 2
    else:
        return 3

def getValue1(pos, pos2, tail):
    if pos in tail:
        #print('a')
        return -99999
    elif pos[0] < 0 or pos[1] < 0 or pos[0] > RELSIZE[0] or pos[1] > RELSIZE[1]:
        #print('b')
        return -99999
    try:
        #print('c')
        return 1/distance(pos, pos2)
    except:
        #print('d')
        return 99999

def inBound(pos):
    global RELSIZE
    if pos[0] < 0:
        return False
    elif pos[1] < 0:
        return False
    elif pos[0] > RELSIZE[0]:
        return False
    elif pos[1] > RELSIZE[1]:
        return False
    return True

def fillBound2(bound, check, checked=None):
    if checked==None:
        checked={f'{check}': True}
    if len(checked) >= (1/10)*RELSIZE[0]*RELSIZE[1]:
        while len(checked) > (1/10)*RELSIZE[0]*RELSIZE[1]:
            checked.pop(list(checked.keys())[-1])
        return checked
    dirs = []
    for i in [getChange(x) for x in range(4)]:
        new_pos = [check[0] + i[0], check[1] + i[1]]
        if f'{new_pos}' not in checked:
            if inBound(new_pos):
                if new_pos not in bound:
                    dirs.append(new_pos)
                    checked[f'{new_pos}'] = new_pos
    #checked += dirs
    if len(dirs) == 0:
        return checked
    for d in dirs:
        checked = fillBound2(bound, d, checked)
    return checked

def fillBound(bound, check, checked=None):
    if checked==None:
        checked=[check]
    if len(checked) >= (1/10)*RELSIZE[0]*RELSIZE[1]:
        while len(checked) > (1/10)*RELSIZE[0]*RELSIZE[1]:
            checked.pop(-1)
        return checked

    dirs = []
    for i in [getChange(x) for x in range(4)]:
        new_pos = [check[0] + i[0], check[1] + i[1]]
        if new_pos not in checked:
            if inBound(new_pos):
                if new_pos not in bound:
                    dirs.append(new_pos)
                    checked.append(new_pos)
    #dirs = [k for k in[[check[0] + i[0], check[1] + i[1]] for i in [getChange(x) for x in range(4)]] if k not in checked and inBound(k)]
    #dirs = [x for x in dirs if x not in bound]
    #checked += dirs
    if len(dirs) == 0:
        return checked
    for d in dirs:
        checked = fillBound(bound, d, checked)
    return checked

def getValue2(pos, pos2, tail):
    global calc_time
    #if move recusrive full area is less than tail length then -1 (or check all make area a component)
    if pos in tail:
        #print('a')
        return -99999
    elif pos[0] < 0 or pos[1] < 0 or pos[0] > RELSIZE[0] or pos[1] > RELSIZE[1]:
        #print('b')
        return -99999
    try:
        #print('c')

        #start_time = getMs()
        checked = fillBound2(tail, pos)
        #calc_time[0] += getMs() - start_time
        #calc_time[1] += 1
        #print(len(checked))
        if len(checked) < 10:
            #print(len(checked))
            return len(checked)/1000
        return 1/distance(pos, pos2) + len(checked)/1000
    except:
        #print('d')
        return 99999

def simulateSnake(snake, apple):
    global LOST

    s = copy.deepcopy(snake)
    s.sim = True
    a = copy.deepcopy(apple)

    while True:
        s.update(a)
        if s.score > snake.score:
            #print('win')
            return True
        elif LOST == True:
            #print('lose')
            LOST = False
            return False

class Snake():
    def __init__(self, pos, color, valueFunc):
        self.pos = pos
        self.color = color
        self.tail = []
        self.direction = 0
        self.score = 0
        self.sim = False
        self.mValue = valueFunc
        self.lost = False

    def collideTail(self):
        if self.pos in self.tail:
            return True
        else:
            return False

    def collideApple(self, apple):
        if self.pos == apple.pos:
            if not self.sim:
                apple.newPos(self)
            else:
                apple.pos = [-1,-1]
            self.score += 1
            self.tail.append(self.pos.copy())
            return True
        return False

    def update(self, apple, move=-1):
        global LOST, screenf, RELSIZE, screen_width,screen_height
        if move != -1:
            self.direction = move
        else:
            dirs = [getChange(x) for x in range(4)]
            #print()
            #print(dirs)
            d_tail = self.tail.copy()
            d_tail.append(self.pos)
            dirs.sort(key=lambda x : self.mValue([self.pos[0] + x[0], self.pos[1] + x[1]], apple.pos, d_tail), reverse=True)
            #print(dirs)
            self.direction = getDir(dirs[0])
        prev = self.tail.copy()

        #print(dirs)

        for i in range(len(self.tail)):
            if i == 0:
                self.tail[i] = self.pos.copy()
            else:
                self.tail[i] = prev[i-1].copy()

        vel = getChange(self.direction)
        self.pos[0] += vel[0]
        self.pos[1] += vel[1]

        if self.collideTail():
            self.lost = True

        if not inBound(self.pos):
            self.lost = True
        '''if not self.sim:
            if self.pos[0] < 0:
                RELSIZE = [RELSIZE[0]+1, RELSIZE[1]]
                screen_width, screen_height = (RELSIZE[0]+1)*SCALE[0], (RELSIZE[1]+1)*SCALE[1]
                screenf = pygame.display.set_mode([screen_width, screen_height])
                self.pos[0] += 1
                for i,t in enumerate(self.tail):
                    self.tail[i][0] += 1
            elif self.pos[1] < 0:
                RELSIZE = [RELSIZE[0], RELSIZE[1]+1]
                screen_width, screen_height = (RELSIZE[0]+1)*SCALE[0], (RELSIZE[1]+1)*SCALE[1]
                screenf = pygame.display.set_mode([screen_width, screen_height])
                self.pos[1] += 1
                for i,t in enumerate(self.tail):
                    self.tail[i][1] += 1
            elif self.pos[0] > RELSIZE[0]:
                RELSIZE = [RELSIZE[0]+1, RELSIZE[1]]
                screen_width, screen_height = (RELSIZE[0]+1)*SCALE[0], (RELSIZE[1]+1)*SCALE[1]
                screenf = pygame.display.set_mode([screen_width, screen_height])
            elif self.pos[1] > RELSIZE[1]:
                RELSIZE = [RELSIZE[0], RELSIZE[1]+1]
                screen_width, screen_height = (RELSIZE[0]+1)*SCALE[0], (RELSIZE[1]+1)*SCALE[1]
                screenf = pygame.display.set_mode([screen_width, screen_height])'''

        self.collideApple(apple)

    def draw(self, surf):
        for t in self.tail:
            pygame.draw.rect(surf, self.color, (t[0]*SCALE[0], t[1]*SCALE[1], SCALE[0], SCALE[1]))
            #pygame.draw.rect(surf, COLORS[t[1]][t[0]], (t[0]*SCALE[0], t[1]*SCALE[1], SCALE[0], SCALE[1]))
        pygame.draw.rect(surf, self.color, (self.pos[0]*SCALE[0], self.pos[1]*SCALE[1], SCALE[0], SCALE[1]))

class Apple():
    def __init__(self, color):
        self.pos = [(int)(random.random()*RELSIZE[0]), (int)(random.random()*RELSIZE[1])]
        self.color = color

    def newPos(self, snake):
        global LOST
        #print()
        start_time = getMs()
        invalid_pos = snake.tail.copy()

        new_pos = [(int)(random.random()*RELSIZE[0]), (int)(random.random()*RELSIZE[1])]
        while new_pos in invalid_pos:
            #print('no')
            new_pos = [(int)(random.random()*RELSIZE[0]), (int)(random.random()*RELSIZE[1])]

        self.pos = new_pos
        #print(len(invalid_pos) - len(snake.tail))

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, (self.pos[0]*SCALE[0], self.pos[1]*SCALE[1], SCALE[0], SCALE[1]))

def tint(surf, tint_color):
    """ adds tint_color onto surf.
    """
    surf = surf.copy()
    # surf.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    surf.fill(tint_color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    return surf

def main():
    global d_time, world_speed, LOST, screenf

    pygame.init()
    clock = pygame.time.Clock()

    pygame.display.set_caption("Snake")

    icon = pygame.Surface((100,100))
    icon.fill((255, 255, 255))
    pygame.display.set_icon(icon)

    screenf = pygame.display.set_mode([screen_width, screen_height])
    # = pygame.Surface((screen_width,screen_height), pygame.SRCALPHA)

    text_size = 48
    myfont = pygame.font.SysFont('arial', text_size)
    last_time = time.time_ns()

    game_run = True
    target_fps = ((1/60)*1000000000)
    last_time = getMs()

    #apples = [Apple((255,0,0)), Apple((0,0,255))]
    apples = [Apple((255,0,0))]
    #snakes = [Snake([0,0], (0,255,0), getValue1), Snake([0,0], (255,0,255), getValue2)]
    snakes = [Snake([0,0], (0,255,0), getValue2)]

    move = -1

    transparent = pygame.Surface((screen_width,screen_height), pygame.SRCALPHA)

    while game_run:
        '''if self.direction == 0:
                self.pos[0] += 1
            elif self.direction == 1:
                self.pos[0] -= 1
            elif self.direction == 2:
                self.pos[1] += 1
            else:
                self.pos[1] -= 1'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_run = False
                pygame.display.quit()
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                apples = [Apple((255,0,0)), Apple((0,0,255))]
                snakes = [Snake(snakes[0].pos, (0,255,0), getValue1), Snake(snakes[1].pos, (255,0,255), getValue2)]
                if event.key == pygame.K_w:
                    move = 3
                if event.key == pygame.K_s:
                    move = 2
                if event.key == pygame.K_a:
                    move = 1
                if event.key == pygame.K_d:
                    move = 0

        #print(getMs() - last_time)
        #if getMs() - last_time >= FRAME_DELAY:
        if True:
            #print(move)
            #transparent.blit(screenf, (0,0))
            #transparent.set_alpha(253)
            screenf.fill(0)
            #screenf.blit(transparent, (0,0))

            textSurf = myfont.render(f'Score: {snakes[0].score}', True, (0,255,0))
            screenf.blit(textSurf, ( int(screen_width/2 - textSurf.get_size()[0]/2), 0 ))

            #textSurf = myfont.render(f'Score: {snakes[1].score}', True, snakes[1].color)
            #screenf.blit(textSurf, ( int(screen_width/2 - textSurf.get_size()[0]/2), screen_height - textSurf.get_size()[1] ))
            for i,s in enumerate(snakes):
                if not s.lost:
                    s.update(apples[i], move)
                s.draw(screenf)
                apples[i].draw(screenf)

            #d_time = (time.time_ns() - last_time)/target_fps
            last_time = getMs()
            #print(calc_time[0]/calc_time[1])

            move = -1
        pygame.display.flip()

if __name__ == "__main__":
    main()