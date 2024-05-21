import os
import sys
import pygame as pg

os.chdir(os.path.dirname(os.path.abspath(__file__)))
circle_speed_y = 0  # 垂直速度


class Rakka:
    def __init__(self,screen, x, y, rad, col):
        self.x = x
        self.y = y
        self.rad = rad
        self.col = col
        self.speed_y = 0
        self.img = pg.Surface((2*rad, 2*rad))
        self.img.set_colorkey((0,0,0))
        pg.draw.circle(self.img, col, (rad, rad), self.rad)
        self.rct = self.img.get_rect()
        self.rct.center = (x, y)
        self.speed_x, self.speed_y = 0, +5

    def update(self, screen):
        # self.y += self.speed_y
        print(self.rct.centery)
        if self.rct.centery >= 850:
            self.rct.centery = self.rct.centery
            self.speed_y = 0
        self.rct.move_ip(self.speed_x, self.speed_y)
        screen.blit(self.img, self.rct)
    
        

def main():
    pg.display.set_caption("広告のゲーム")
    screen = pg.display.set_mode((600, 900))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    clock = pg.time.Clock()
    enn = pg.Surface((20, 20))
    pg.draw.circle(enn, (255, 0, 0), (10, 10), 10)
    enn.set_colorkey((0, 0, 0))
    rakka = Rakka(screen, 200, 50, 20, (255, 255, 0))    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        screen.blit(bg_img, [0, 0]) 
        rakka.update(screen)
        # rakka.draw(screen)

        pg.display.update()
        pg.display.flip()
        clock.tick(60) 

if __name__=="__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

