import math
import os
import sys
import time
from pygame.locals import *
import pygame as pg

os.chdir(os.path.dirname(os.path.abspath(__file__)))
WIDTH, HEIGHT = 600, 900
STAGE_NUM = 1


def check_bound(obj_rct:pg.Rect) -> tuple[bool, bool]:
    """
    Rectの画面内外判定用の関数
    引数：こうかとんRect，または，爆弾Rect，またはビームRect
    戻り値：横方向判定結果，縦方向判定結果（True：画面内／False：画面外）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:  # 横方向のはみ出し判定
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Yoko_Stage(pg.sprite.Sprite):
    """
    ステージの描写に関するクラス
    """
    def __init__(self, xy: tuple[int, int]) -> None:
        """
        ステージSurfaceを生成する
        """
        super().__init__()
        self.image = pg.Surface((100, 25)) # 横長の枠組みのSurface
        pg.draw.rect(self.image, (180,82,45), [0, 0, 100, 25])
        pg.draw.rect(self.image, (255, 255, 255), [0, 0, 100, 25], 2) # 横向きの四角形の枠組みの描写
        self.rect = self.image.get_rect()
        self.rect.topleft = xy
        
    def update(self):
        pass


class Tate_Stage(pg.sprite.Sprite):
    """
    ステージの描写に関するクラス
    """
    def __init__(self, xy: tuple[int, int]) -> None:
        """
        ステージSurfaceを生成する
        """
        super().__init__()
        self.image = pg.Surface((25, 100)) # 縦長の枠組みのSurface
        pg.draw.rect(self.image, (180,82,45), [0, 0, 25, 100])
        pg.draw.rect(self.image, (255, 255, 255), [0, 0, 25, 100], 2) # 縦向きの四角形の枠組みの描写
        self.rect = self.image.get_rect()
        self.rect.topleft = xy
    
    def update(self):
        pass
        

class Kao():
    """
    おふざけ用のクラス
    こうかとんがクリアしたり，マグマなどに衝突したら呼び出されるクラス
    """
    def __init__(self):
        """
        顔のSurfaceを生成する
        """
        self.image = self.image_kao = pg.transform.rotozoom(pg.image.load(f"fig/kao.png"), 0, 0.15) # 顔の画像を読み込む
        self.rect = self.image.get_rect()

    def update(self, ko: "Kokaton", screen: pg.Surface):
        """
        こうかとんの位置に基づいて顔を表示する
        引数１ ko：こうかとんのインスタンスの取得
        引数２ screen：画面Surface
        """
        self.rect.center = ko.rect.center
        screen.blit(self.image, self.rect)


class Kokaton(pg.sprite.Sprite):
    """
    主人公こうかとんに関する関数
    """
    def __init__(self, x, y):
        """
        こうかとん画像Surfaceを生成する
        """
        super().__init__()
        self.image = pg.transform.flip(pg.image.load(f"fig/0.png"), True, False) # こうかとんの画像を読み込む
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.vx, self.vy = 0, 0
        self.speed = 5
    
    def update(self, screen: pg.Surface):
        """
        スペースを押したらこうかとんを移動させる
        引数 screen：画面Surface
        """
        if self.vy < 0:
            self.vy = 0
        self.rect.move_ip(self.speed * self.vx, self.speed * self.vy)
        screen.blit(self.image, self.rect)


class Yoko_Pin(pg.sprite.Sprite): # 横用のピンのクラス
    """
    横長用のピンのクラス
    リストにあらかじめ図形左上の座標タプルを入れておくことで呼び出しを簡単にしている
    """
    yoko_topleft_xy = [(50, 165), (50, 290), (300, 165), (300, 290)] # ピンの座標タプルのリスト

    def __init__(self, ytl):
        """
        横長用のピンのSurface
        引数１：座標タプルの引数
        """
        super().__init__()
        self.image = pg.Surface((250, 20)) # ピンの横用のSurface
        pg.draw.rect(self.image, (255, 215, 0), [0, 0, 250, 20])
        pg.draw.rect(self.image, (0, 0, 0), [0, 0, 250, 20], 2) # ピンの枠線
        self.rect = self.image.get_rect()
        # ステージごとに配置を変えれるようにする
        self.rect.topleft = __class__.yoko_topleft_xy[ytl]
        self.vx, self.vy = 0, 0

    def update(self):
        """
        マウスがピンの半分より壁側にあるとき左クリックするとピンを動かす
        画面外に出たらGroupオブジェクトから消去される
        """
        # マウスの処理
        if pg.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pg.mouse.get_pos() # マウスのｘ座標とｙ座標の取得
            if self.rect.centerx > (WIDTH / 2): # ピンが画面の右側にあったら
                if (self.rect.centerx <= mouse_x <= self.rect.right and self.rect.top <= mouse_y <= self.rect.bottom): # マウスがピンの半分より右側にあったら
                    self.vx = +2
            elif self.rect.centerx < (WIDTH / 2): # ピンが画面の左側にあったら
                if (self.rect.left <= mouse_x <= self.rect.centerx and self.rect.top <= mouse_y <= self.rect.bottom): # マウスがピンの半分より左側にあったら
                    self.vx = -2
        
        self.rect.move_ip(self.vx, self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill() # 画面外にでたらGroupオブジェクトから消去される


class Tate_Pin(pg.sprite.Sprite): # 縦用のピンのクラス
    """
    縦長用のピンのクラス
    リストにあらかじめ図形左上の座標タプルを入れておくことで呼び出しを簡単にしている
    """
    tate_topleft_xy = [(290, 50), (290, 600)] # 座標タプルのリスト

    def __init__(self, ttl):
        """
        縦長用のピンのSurface
        引数１：座標タプルの引数
        """
        super().__init__()
        self.image = pg.Surface((20, 250)) # ピンの縦用のSurface
        pg.draw.rect(self.image, (255, 215, 0), [0, 0, 20, 250])
        pg.draw.rect(self.image, (0, 0, 0), [0, 0, 20, 250], 2)
        self.rect = self.image.get_rect()
        # ステージごとに変えることのできる配置
        self.rect.topleft = __class__.tate_topleft_xy[ttl]
        self.vx, self.vy = 0, 0

    def update(self):
        """
        マウスがピンの半分より壁側にあるとき左クリックするとピンを動かす
        画面外に出たらGroupオブジェクトから消去される
        """
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            if self.rect.centery > (HEIGHT / 2):
                if (self.rect.left <= mouse_x <= self.rect.right and self.rect.centery <= mouse_y <= self.rect.bottom):
                    self.vy = +2
            elif self.rect.centery < (HEIGHT / 2):
                if (self.rect.left <= mouse_x <= self.rect.right and self.rect.top <= mouse_y <= self.rect.centery):
                    self.vy = -2
        
        self.rect.move_ip(self.vx, self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill() # 画面外にでたらGroupオブジェクトから消去される


class Obj(pg.sprite.Sprite):
    """
    マグマなどの描写に関するクラス
    """
    colors = [(232, 57, 41), (255, 239, 108), (188, 226, 232)]
    def __init__(self, num, xy: tuple[int, int]):
        """
        マグマなどの円Surface
        引数２：色タプルリストを指定するための引数
        引数３：物体の位置タプル
        """
        super().__init__()
        rad = 30
        self.image = pg.Surface((2*rad, 2*rad))
        self.color = __class__.colors[num]
        pg.draw.circle(self.image, self.color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.vx, self.vy = 0, 0
    
    def update(self):
        self.rect.move_ip(self.vx, self.vy)


class Stone(pg.sprite.Sprite):
    """
    マグマと水が当たった時の黒曜石を表示させるクラス
    """
    def __init__(self, obj: "Obj"):
        """
        石の表示のSUrface
        引数1：マグマなどのインスタンス
        """
        super().__init__()
        self.image = pg.Surface((250, 50))
        pg.draw.rect(self.image, (0, 0, 0), [0, 0, 250, 50])
        self.rect = self.image.get_rect()
        self.rect.center = obj.rect.center
    
    def update(self):
        pass


def main():
    pg.display.set_caption("広告ゲーム")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/sabaku.jpg")

    kao = Kao()
    ysts = pg.sprite.Group()
    tsts = pg.sprite.Group() 
    mgms = pg.sprite.Group()
    wtrs = pg.sprite.Group()
    trs = pg.sprite.Group()
    sixtones = pg.sprite.Group()
    pins = pg.sprite.Group()

    clock = pg.time.Clock()

    #ここはステージ毎に数値を変更することができる
    kokaton = Kokaton(100, 800)
    # ステージの座標をfor文で指定する
    for x in range(7):
        ysts.add(Yoko_Stage((100 * x, 0)))
        ysts.add(Yoko_Stage((100 * x -50, 25)))
        ysts.add(Yoko_Stage((100 * x, 875)))
        ysts.add(Yoko_Stage((100 * x -50, 850)))
        if x < 3:
            ysts.add(Yoko_Stage((100 * x, 800)))
            ysts.add(Yoko_Stage((100 * x, 825)))
    for y in range(10):
        tsts.add(Tate_Stage((0, 100 * y)))
        tsts.add(Tate_Stage((25, 100 * y -50)))
        tsts.add(Tate_Stage((575, 100 * y)))
        tsts.add(Tate_Stage((550, 100 * y -50)))

    #ステージによって変えれる
    mgms.add(Obj(0, (425, 260)))
    wtrs.add(Obj(2, (425, 820)))
    trs.add(Obj(1, (425, 135)))

    # 使いたい棒の座標タプルが入ったリストを指定する
    pins.add(Yoko_Pin(2))
    pins.add(Yoko_Pin(3))
    pins.add(Tate_Pin(0))

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
        
        screen.blit(bg_img, [0, 0])

        # 何にも衝突がなければobj.vyは+2になる
        for mgm in mgms:
            mgm.vy = +2
        for wtr in wtrs:
            wtr.vy = +2
        for tre in trs:
            tre.vy = +2
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            # マウスがこうかとんに重なっていたら
            if (kokaton.rect.topleft[0] <= mouse_x <= kokaton.rect.bottomright[0]) and (kokaton.rect.topleft[1] <= mouse_y <= kokaton.rect.bottomright[1]):
                kokaton.vx, kokaton.vy = calc_orientation(kokaton.rect, tre.rect)
        
        # こうかとんとステージの当たり判定
        if len(pg.sprite.spritecollide(kokaton, ysts, False)) != 0:
            kokaton.vy = 0
        if len(pg.sprite.spritecollide(kokaton, tsts, False)) != 0:
            kokaton.vx = 0
            if kokaton.rect.centerx < WIDTH / 2:
                kokaton.rect.left += 1
            elif kokaton.rect.centerx > WIDTH / 2:
                kokaton.rect.right -= 1
        
        # こうかとんとピンの当たり判定
        if len(pg.sprite.spritecollide(kokaton, pins, False)) != 0:
            kokaton.vx, kokaton.vy = 0, 0
        
        # こうかとんとマグマと水で出来た石の当たり判定
        if len(pg.sprite.spritecollide(kokaton, sixtones, False)) != 0:
            kokaton.vy = 0

        # ピンとobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, pins, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, pins, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, pins, False, False).keys():
            tre.vy = 0
        
        # 床とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ysts, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ysts, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ysts, False, False).keys():
            tre.vy = 0
        
        # 水とマグマの当たり判定
        for wtr in pg.sprite.groupcollide(wtrs, mgms, True, True).keys():
            sixtones.add(Stone(wtr))
        
        # マグマと宝物の当たり判定
        for mgm in pg.sprite.groupcollide(mgms, trs, False, True).keys():
            pass

        # 宝とマグマと水で出来た石の当たり判定
        for tre in pg.sprite.groupcollide(trs, sixtones, False, False).keys():
            tre.vy = 0
        
        # こうかとんとマグマの当たり判定，ゲームオーバー
        if len(pg.sprite.spritecollide(kokaton, mgms, False)) != 0:
            kokaton.update(screen)
            kao.update(kokaton, screen)
            sixtones.draw(screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
            return "gameover"
        
        # こうかとんと宝の当たり判定，クリアー！！
        if len(pg.sprite.spritecollide(kokaton, trs, True)) != 0:
            kokaton.update(screen)
            kao.update(kokaton, screen)
            sixtones.draw(screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
            return "clear"

        kokaton.update(screen)
        pins.update()
        pins.draw(screen)
        mgms.update()
        mgms.draw(screen)
        wtrs.update()
        wtrs.draw(screen)
        trs.update()
        trs.draw(screen)
        sixtones.update()
        sixtones.draw(screen)
        ysts.draw(screen)
        tsts.draw(screen)
        pg.display.update()
        clock.tick(60)


def main2():
    pg.display.set_caption("広告ゲーム2")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/sizen.jpg")

    kao = Kao()
    ysts = pg.sprite.Group()
    tsts = pg.sprite.Group() 
    mgms = pg.sprite.Group()
    wtrs = pg.sprite.Group()
    trs = pg.sprite.Group()
    sixtones = pg.sprite.Group()
    pins = pg.sprite.Group()

    clock = pg.time.Clock()

    #ここはステージ毎に数値を変更することができる
    kokaton = Kokaton(100, 800)
    # ステージの座標をfor文で指定する
    for x in range(7):
        ysts.add(Yoko_Stage((100 * x, 0)))
        ysts.add(Yoko_Stage((100 * x -50, 25)))
        ysts.add(Yoko_Stage((100 * x, 875)))
        ysts.add(Yoko_Stage((100 * x -50, 850)))
        if x < 3:
            ysts.add(Yoko_Stage((100 * x, 800)))
            ysts.add(Yoko_Stage((100 * x, 825)))
    for y in range(10):
        tsts.add(Tate_Stage((0, 100 * y)))
        tsts.add(Tate_Stage((25, 100 * y -50)))
        tsts.add(Tate_Stage((575, 100 * y)))
        tsts.add(Tate_Stage((550, 100 * y -50)))

    #ステージによって変えれる
    mgms.add(Obj(0, (425, 260)))
    wtrs.add(Obj(2, (425, 820)))
    trs.add(Obj(1, (425, 135)))

    game_stats = None

    # 使いたい棒の座標タプルが入ったリストを指定する
    pins.add(Yoko_Pin(2))
    pins.add(Yoko_Pin(3))
    pins.add(Tate_Pin(0))

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
        
        screen.blit(bg_img, [0, 0])

        # 何にも衝突がなければobj.vyは+2になる
        for mgm in mgms:
            mgm.vy = +2
        for wtr in wtrs:
            wtr.vy = +2
        for tre in trs:
            tre.vy = +2
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            # マウスがこうかとんに重なっていたら
            if (kokaton.rect.topleft[0] <= mouse_x <= kokaton.rect.bottomright[0]) and (kokaton.rect.topleft[1] <= mouse_y <= kokaton.rect.bottomright[1]):
                kokaton.vx, kokaton.vy = calc_orientation(kokaton.rect, tre.rect)
        
        # こうかとんとステージの当たり判定
        if len(pg.sprite.spritecollide(kokaton, ysts, False)) != 0:
            kokaton.vy = 0
        if len(pg.sprite.spritecollide(kokaton, tsts, False)) != 0:
            kokaton.vx = 0
            if kokaton.rect.centerx < WIDTH / 2:
                kokaton.rect.left += 1
            elif kokaton.rect.centerx > WIDTH / 2:
                kokaton.rect.right -= 1
        
        # こうかとんとピンの当たり判定
        if len(pg.sprite.spritecollide(kokaton, pins, False)) != 0:
            kokaton.vx, kokaton.vy = 0, 0
        
        # こうかとんとマグマと水で出来た石の当たり判定
        if len(pg.sprite.spritecollide(kokaton, sixtones, False)) != 0:
            kokaton.vy = 0

        # ピンとobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, pins, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, pins, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, pins, False, False).keys():
            tre.vy = 0
        
        # 床とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ysts, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ysts, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ysts, False, False).keys():
            tre.vy = 0
        
        # 水とマグマの当たり判定
        for wtr in pg.sprite.groupcollide(wtrs, mgms, True, True).keys():
            sixtones.add(Stone(wtr))
        
        # マグマと宝物の当たり判定
        for mgm in pg.sprite.groupcollide(mgms, trs, False, True).keys():
            pass

        # 宝とマグマと水で出来た石の当たり判定
        for tre in pg.sprite.groupcollide(trs, sixtones, False, False).keys():
            tre.vy = 0
        
        # こうかとんとマグマの当たり判定，ゲームオーバー
        if len(pg.sprite.spritecollide(kokaton, mgms, False)) != 0:
            kokaton.update(screen)
            kao.update(kokaton, screen)
            sixtones.draw(screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
            return "gameover"
        
        # こうかとんと宝の当たり判定，クリアー！！
        if len(pg.sprite.spritecollide(kokaton, trs, True)) != 0:
            kokaton.update(screen)
            kao.update(kokaton, screen)
            sixtones.draw(screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
            return "clear"

        kokaton.update(screen)
        pins.update()
        pins.draw(screen)
        mgms.update()
        mgms.draw(screen)
        wtrs.update()
        wtrs.draw(screen)
        trs.update()
        trs.draw(screen)
        sixtones.update()
        sixtones.draw(screen)
        ysts.draw(screen)
        tsts.draw(screen)
        pg.display.update()
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    game_stats = None
    # ステージの変化とゲームオーバーなどの処理
    while True:
        game_stats = main() # main関数内でreturnしてくる文字列を変数に格納する
        if game_stats == "clear":
            STAGE_NUM += 1
            game_stats = main2()
            break
        elif game_stats == "gameover":
            print("continue")
            continue
        elif game_stats == "retire":
            break
    pg.quit()
    sys.exit()