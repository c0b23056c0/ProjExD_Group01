import os
import sys
import pygame as pg

os.chdir(os.path.dirname(os.path.abspath(__file__)))

WITDH, HEIGHT = 600, 900
def main():
    pg.display.set_caption("広告ゲーム")
    screen = pg.display.set_mode((WITDH, HEIGHT))
    bg_img = pg.image.load(f"fig/sabaku.jpg")
    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
        
        screen.fill((50, 50, 50))
        screen.blit(bg_img, [0, 0])
        pg.display.update()      
        clock.tick(1)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()