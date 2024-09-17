import pgzrun
import pygame
import random
import math
import os


font = pygame.font.SysFont('simHei',20)

TITLE = '金铲铲之战1.0' 
WIDTH = 1200
HEIGHT = 800

timer=300 #游戏倒计时

logo=Actor('logo')
logo.pos=600,300

logo2=Actor('logo2')
logo2.pos=700,600

beginbutton=Actor('star')
beginbutton.pos=1060,500

storebutton=Actor('store')
storebutton.pos=1060,600

exitbutton=Actor('exit')
exitbutton.pos=1060,700

timebutton=Actor('addtime')
timebutton.pos=1060,400

playagain=Actor('playagain')
playagain.pos=1000,600

gamestatus=0
seat=7
remain=7
score=0
# 自定义游戏常量
T_WIDTH = 60
T_HEIGHT = 66
 
# 下方牌堆的位置
DOCK = Rect((120, 700), (T_WIDTH*seat, T_HEIGHT))

# 上方的所有牌
tiles = []
# 牌堆里的牌
docks = []

# 初始化牌组，13*18张牌随机打乱
ts = list(range(1, 14))*18
random.shuffle(ts)
n = 0
for k in range(8):    # 7层
    for i in range(8-k):    #每层减1行
        for j in range(8-k):
            t = ts[n]        #获取排种类
            n += 1
            tile = Actor(f'tile{t}')       #使用tileX图片创建Actor对象
            tile.pos = 250 + (k * 0.5 + j) * tile.width, 100 + (k * 0.5 + i) * tile.height * 0.9    #设定位置
            tile.tag = t            #记录种类
            tile.layer = k          #记录层级
            tile.status = 1 if k == 7 else 0        #除了最顶层，状态都设置为0（不可点）这里是个简化实现
            tiles.append(tile)
for i in range(13):        #剩余牌放下面（为了凑整能通关）
    t = ts[n] 
    n += 1
    tile = Actor(f'tile{t}')
    tile.pos = 100+i * tile.width, 580
    tile.tag = t
    tile.layer = 0
    tile.status = 1
    tiles.append(tile)

for i in range(13):        #剩余牌放下面（为了凑整能通关）
    t = ts[n] 
    n += 1
    tile = Actor(f'tile{t}')
    tile.pos = 100+i * tile.width, 40
    tile.tag = t
    tile.layer = 0
    tile.status = 1
    tiles.append(tile)

def update():
    global gamestatus
    global timer
    if timer <=0:
        return 
    timer-=1/60

# 游戏帧绘制函数
def draw():
    if gamestatus==1:
        global score
        screen.clear()
        screen.blit('back1', (0, 0))      #背景图
        timebutton.draw()
        screen.draw.text('time: ' + str(round(timer, 0)), (900,10), color=(255,255,255),fontsize=40)
        screen.draw.text('seats: ' , (50,700), color=(255,255,255),fontsize=30)
        remain=seat-len(docks)
        screen.draw.text('remains:' + str(round(remain, 0)), (250,640), color=(255,255,255),fontsize=30)
        screen.draw.text('scores:' + str(round(score, 0))+'+'+str(round(timer, 0)), (900,50), color=(255,255,255),fontsize=50)
        for tile in tiles:
            #绘制上方牌组
            tile.draw()
            if tile.status == 0:
                screen.blit('mask', tile.topleft)     #不可点的添加遮罩
        for i, tile in enumerate(docks):
            #绘制排队，先调整一下位置（因为可能有牌被消掉）
            tile.left = (DOCK.x + i * T_WIDTH)
            tile.top = DOCK.y
            tile.draw()

        # 超过7张，失败
        if len(docks) >= seat:
            screen.clear()
            screen.blit('end', (0, 0))
            screen.draw.text('your scores:' + str(round(score, 0)), (900,50), color=(255,255,255),fontsize=50)
            screen.draw.text('you lost!!!!' , (100,50), color=(255,255,255),fontsize=90)
            playagain.draw()
        if timer <= 0:
            screen.clear()
            screen.blit('end', (0, 0))
            screen.draw.text('your scores:' + str(round(score, 0)), (900,50), color=(255,255,255),fontsize=50)
            screen.draw.text('you lost!!!!' , (100,50), color=(255,255,255),fontsize=90)
            playagain.draw()
        # 没有剩牌，胜利
        if len(tiles) == 0:
            screen.blit('win', (0, 0))
            score+=timer
    if gamestatus==0:
        screen.clear()
        screen.blit('back1',(0,0))
        beginbutton.draw()
        storebutton.draw()
        exitbutton.draw()
        logo.draw()
        logo2.draw()

# 鼠标点击响应
def on_mouse_down(pos):

    if beginbutton.collidepoint(pos):
        global gamestatus
        gamestatus=1

    if timebutton.collidepoint(pos):
        global timer
        global seat
        global remain
        global score
        timer+=60
        seat+=2
        remain+=2
        score-=60
    
    if exitbutton.collidepoint(pos):
        pygame.quit()

    if playagain.collidepoint(pos):
        gamestatus=0
        
    global docks
    
    if len(docks) >= seat or len(tiles) == 0:      #游戏结束不响应
        return
    for tile in reversed(tiles):    #逆序循环是为了先判断上方的牌，如果点击了就直接跳出，避免重复判定
        if tile.status == 1 and tile.collidepoint(pos):
            # 状态1可点，并且鼠标在范围内
            tile.status = 2
            tiles.remove(tile)
            diff = [t for t in docks if t.tag != tile.tag]    #获取牌堆内不相同的牌
            if len(docks) - len(diff) < 2:    #如果相同的牌数量<2，就加进牌堆
                docks.append(tile)
            else:             #否则用不相同的牌替换牌堆（即消除相同的牌）
                docks = diff
                score+=10
            for down in tiles:      #遍历所有的牌
                if down.layer == tile.layer - 1 and down.colliderect(tile):   #如果在此牌的下一层，并且有重叠
                    for up in tiles:      #那就再反过来判断这种被覆盖的牌，是否还有其他牌覆盖它
                        if up.layer == down.layer + 1 and up.colliderect(down):     #如果有就跳出
                            break
                    else:      #如果全都没有，说明它变成了可点状态
                        down.status = 1
            return



pgzrun.go()


