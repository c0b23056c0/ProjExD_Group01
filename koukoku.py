import os
import sys
import pygame as pg
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

WIDTH = 600
HEIGTH = 900


class Clear():
    def __init__(self, screen):
        font = pg.font.Font(None, 80)
        self.img = pg.image.load("fig/sora.jpg")
        self.txt = font.render("CLEAR", True, (0, 0, 255))
        #screen.fill(0, 255, 0)
        screen.blit(self.img, [0, 0])
        screen.blit(self.txt, [200, 350])
        pg.display.update()
        time.sleep(1)




def main():
    pg.display.set_caption("広告ゲーム")
    screen = pg.display.set_mode((600, 900))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 80)

    enn = pg.Surface((20, 20))
    pg.draw.circle(enn, (255, 0, 0), (10, 10), 10)
    enn.set_colorkey((0, 0, 0))

    tmr = 0
    # def __init__(self, font):
    #     self.font = pg.font.Font(None, 80)
    #     txt = font.render("Game Clear", True, (255, 255, 0))
    #     screen.blit(txt,[WIDTH/2-150, HEIGTH/2])
    #     pg.display.update()
    #     time.sleep(2)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
        
        txt = font.render(str(tmr), True, (255, 255, 255))
        if tmr == 5:
            Clear(screen)
            return
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