import os
import sys
import pygame as pg

os.chdir(os.path.dirname(os.path.abspath(__file__)))

WITDH, HEIGHT = 600, 900


class Stage(pg.sprite.Sprite):
    """
    ステージの描写に関するクラス
    """
    def __init__(self) -> None:
        """
        ステージSurfaceを生成する
        """
        super().__init__()
        self.image_yoko = pg.Surface((WITDH, HEIGHT)) # 横長の枠組みのSurface
        self.image_tate = pg.Surface((WITDH, HEIGHT)) # 縦長の枠組みのSurface
        pg.draw.rect(self.image_yoko, (180,82,45), [0, 0, 100, 50])
        pg.draw.rect(self.image_tate, (180,82,45), [0, 0, 50, 100])
        pg.draw.rect(self.image_yoko, (255, 255, 255), [0, 0, 100, 50], 2) # 横向きの四角形の枠組みの描写
        pg.draw.rect(self.image_tate, (255, 255, 255), [0, 0, 50, 100], 2) # 縦向きの四角形の枠組みの描写
        self.image_tate.set_colorkey((0, 0, 0))
        self.image_yoko.set_colorkey((0, 0, 0))
        self.rect_yoko = self.image_yoko.get_rect()
        self.rect_tate = self.image_tate.get_rect()

    def update(self,screen: pg.Surface):
        """
        二重のfor文を使ってステージの描写をする
        引数 screen：画面Surface
        """
        x, y = 0, 0
        for x in range(6):
            screen.blit(self.image_yoko, [(100 * x) , 0])
            screen.blit(self.image_yoko, [(100 * x), 850])
            for y in range(9):
                if x == 0:
                    screen.blit(self.image_tate, [0, (100 * y)])
                if x == 5:
                    screen.blit(self.image_tate, [550, (100 * y)])


class Kokaton(pg.sprite.Sprite):
    """
    主人公こうかとんに関する関数
    """
    def __init__(self):
        """
        こうかとん画像Surfaceを生成する
        """
        super().__init__()
        self.image = pg.transform.flip(pg.image.load(f"fig/0.png"), True, False) # こうかとんの画像を読み込む
        self.image_kao = pg.transform.rotozoom(pg.image.load(f"fig/kao.png"), 0, 0.15) # 顔の画像を読み込む
        self.vx, self.vy = +2, 0
        self.rect = self.image.get_rect()
        self.rect_kao = self.image_kao.get_rect()
        self.rect.centerx = 100 # こうかとんの位置の調整
        self.rect.bottom = 850
        self.rect_kao.center = (505, 810)
    
    def update(self, screen: pg.Surface):
        """
        クリア後にこうかとんを移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.vx, self.vy)
        screen.blit(self.image, self.rect)
        if self.rect.centerx == 500:
            self.vx = 0
            screen.blit(self.image_kao, self.rect_kao) #クリア時に顔を表示する


def main():
    pg.display.set_caption("広告ゲーム")
    screen = pg.display.set_mode((WITDH, HEIGHT))
    bg_img = pg.image.load(f"fig/sabaku.jpg")
    kokaton = Kokaton()
    stage = Stage()
    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
        
        screen.blit(bg_img, [0, 0])
    
        stage.update(screen)
        kokaton.update(screen)
        pg.display.update()
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()