import os
import sys
import pygame as pg
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

WIDTH, HEIGHT = 600,900 #サイズ

def main():  #main関数
    pg.display.set_caption("はじめてのPygame")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    image = pg.image.load("fig/game.png") # ゲームオーバー画像
    image_rect = image.get_rect()
    image_rect.center = WIDTH / 2, HEIGHT / 2
    screen.blit(image, image_rect) 
    pg.display.update()
    time.sleep(5)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()