import pygame, random, math, time, datetime

SCALE = [10, 10]
RELSIZE = [50, 50]
screen_width, screen_height = (RELSIZE[0]+1)*SCALE[1], (RELSIZE[1]+1)*SCALE[0]

LOST = False

d_time = 0
world_speed = 1

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

def getValue(pos, pos2, tail):
    if pos in tail:
        return -1
    elif pos[0] < 0 or pos[1] < 0 or pos[0] > RELSIZE[0] or pos[1] > RELSIZE[1]:
        return -1
    try:
        return 1/math.dist(pos, pos2)
    except:
        return 9999

class Snake():
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
        self.tail = []
        self.direction = 0
        self.score = 0

    def collideTail(self):
        if self.pos in self.tail:
            return True
        else:
            return False

    def collideApple(self, apple):
        if self.pos == apple.pos:
            apple.newPos(self.tail)
            self.score += 1
            self.tail.append(self.pos.copy())
            return True
        return False

    def update(self, apple, move=-1):
        global LOST
        if move != -1:
            self.direction = move
        else:
            dirs = [getChange(x) for x in range(4)]
            #print()
            #print(dirs)
            dirs.sort(key=lambda x : getValue([self.pos[0] + x[0], self.pos[1] + x[1]], apple.pos, self.tail), reverse=True)
            #print(dirs)
            self.direction = getDir(dirs[0])
        prev = self.tail.copy()

        self.collideApple(apple)
        for i in range(len(self.tail)):
            if i == 0:
                self.tail[i] = self.pos.copy()
            else:
                self.tail[i] = prev[i-1].copy()

        vel = getChange(self.direction)
        self.pos[0] += vel[0]
        self.pos[1] += vel[1]

        if self.collideTail():
            LOST = True
        elif self.pos[0] < 0 or self.pos[1] < 0 or self.pos[0] > RELSIZE[0] or self.pos[1] > RELSIZE[1]:
            LOST = True

    def draw(self, surf):
        for t in self.tail:
            pygame.draw.rect(surf, self.color, (t[0]*SCALE[0], t[1]*SCALE[1], SCALE[0], SCALE[1]))
        pygame.draw.rect(surf, self.color, (self.pos[0]*SCALE[0], self.pos[1]*SCALE[1], SCALE[0], SCALE[1]))

class Apple():
    def __init__(self, color):
        self.pos = [(int)(random.random()*RELSIZE[0]), (int)(random.random()*RELSIZE[1])]
        self.color = color

    def newPos(self, tail):
        new_pos = [(int)(random.random()*RELSIZE[0]), (int)(random.random()*RELSIZE[1])]
        while new_pos in tail:
            new_pos = [(int)(random.random()*RELSIZE[0]), (int)(random.random()*RELSIZE[1])]
        self.pos = new_pos

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
    global d_time, world_speed, LOST

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

    apple = Apple((255,0,0))
    snake = Snake([0,0], (0,255,0))

    move = -1

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
                if event.key == pygame.K_w:
                    move = 3
                if event.key == pygame.K_s:
                    move = 2
                if event.key == pygame.K_a:
                    move = 1
                if event.key == pygame.K_d:
                    move = 0

        #print(getMs() - last_time)
        if getMs() - last_time >= 0.0:
            #print(move)
            screenf.fill(0)

            if not LOST:
                textSurf = myfont.render(f'Score: {snake.score}', True, (0,255,0))
                screenf.blit(textSurf, ( int(screen_width/2 - textSurf.get_size()[0]/2), 0 ))
                snake.update(apple, move)
            else:
                textSurf = myfont.render(f'Score: {snake.score}', True, (0,255,0))
                screenf.blit(textSurf, ( int(screen_width/2 - textSurf.get_size()[0]/2), 0 ))
                textSurf = myfont.render('Gamer Over', True, (0,255,0))
                screenf.blit(textSurf, ( int(screen_width/2 - textSurf.get_size()[0]/2), int(screen_height/2 - textSurf.get_size()[1]/2) ))
            snake.draw(screenf)
            apple.draw(screenf)

            d_time = (time.time_ns() - last_time)/target_fps
            last_time = getMs()

            if LOST:
                pygame.display.flip()
                time.sleep(1)
                LOST = False
                apple = Apple((255,0,0))
                snake = Snake([0,0], (0,255,0))

            move = -1
        pygame.display.flip()

if __name__ == "__main__":
    main()