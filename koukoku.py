import os
import sys
import pygame as pg

 
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    pg.display.set_caption("はじめてのPygame")
    screen = pg.display.set_mode((600, 900))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 80)

    enn = pg.Surface((20, 20))
    pg.draw.circle(enn, (255, 0, 0), (10, 10), 10)
    enn.set_colorkey((0, 0, 0))
    gamemood = 0
    tmr = 0
    fonto = pg.font.Font(None, 120)
    txt = fonto.render("Start", True, (255,0,0)) #start文字
    image1 = pg.image.load("fig/2.png") #こうかとん
    image2 = pg.image.load("fig/9.png") #こうかとん
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and pg.K_KP_ENTER:
                gamemood = 1
        if gamemood == 0: #start画面
            screen.blit(txt,[600/2 - 120, 900/2 - 70])
            screen.blit(image1,[100, 380])
            screen.blit(image2,[400, 380])
            pg.display.update()
        elif gamemood == 1:
            txt = font.render(str(tmr), True, (255, 255, 255))
            screen.fill((50, 50, 50))
            screen.blit(txt, [300, 200])
            screen.blit(enn, [100, 400])
            pg.display.update()
            tmr += 1        
            clock.tick(1)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()