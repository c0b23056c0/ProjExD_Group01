import os
import sys
import pygame as pg
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))


WIDTH, HEIGHT = 600,900


def main():  #main関数
    pg.display.set_caption("はじめてのPygame")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    #screen1 = pg.display.set_mode((WIDTH,HEIGHT))
    image = pg.image.load("fig/sougen.jpg")
    #image = pg.transform.flip(image,True,False)
    screen.blit(image,[150,400])
    pg.display.update()
    clock = pg.time.Clock()
    font = pg.font.Font(None, 80)

    enn = pg.Surface((20, 20))
    pg.draw.circle(enn, (255, 0, 0), (10, 10), 10)
    enn.set_colorkey((0, 0, 0))
    
    
    fonto = pg.font.Font(None,80)
    txt = fonto.render("Game Over",True,(255,0,0))   #GameOver表記
    screen.blit(txt,[WIDTH/2-150, HEIGHT/2])
    pg.display.update()
    time.sleep(5)
    
    

    tmr = 0
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
        
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