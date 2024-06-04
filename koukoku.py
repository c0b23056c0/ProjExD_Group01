import math
import os
import sys
import time
from pygame.locals import *
import pygame as pg
import time

 
os.chdir(os.path.dirname(os.path.abspath(__file__)))
WIDTH, HEIGHT = 600, 900
STAGE_NUM = 0


def check_bound(obj_rct:pg.Rect) -> tuple[bool, bool]:
    """
    Rectの画面内外判定用の関数
    引数：こうかとんRect，または，爆弾Rect，またはビームRect
    戻り値：横方向判定結果，縦方向判定結果（True：画面内／False：画面外）
    """
    yoko, tate = True, True
    if obj_rct.right < 0 or WIDTH < obj_rct.left:  # 横方向のはみ出し判定
        yoko = False
    if obj_rct.bottom < 0 or HEIGHT < obj_rct.top:  # 縦方向のはみ出し判定
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


class Asiba(pg.sprite.Sprite):
    def __init__(self, xy: tuple[int, int]):
        super().__init__()
        self.image = pg.image.load("fig/renga.png")
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
        こうかとんをクリックしたらこうかとんを動かす
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed * self.vx, self.speed * self.vy)
        screen.blit(self.image, self.rect)


class Yoko_Pin(pg.sprite.Sprite): # 横用のピンのクラス
    """
    横長用のピンのクラス
    リストにあらかじめ図形左上の座標タプルを入れておくことで呼び出しを簡単にしている
    """
    yoko_topleft_xy = [(50, 165), (50, 300), (50, 575), (300, 250), (300, 450), (300, 775), (50, 230), (300, 230), ] # ピンの座標タプルのリスト

    def __init__(self, xy: tuple[int, int]):
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
        self.rect.topleft = xy
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
            elif self.rect.centerx == WIDTH / 2:
                if (self.rect.centerx <= mouse_x <= self.rect.right and self.rect.top <= mouse_y <= self.rect.bottom): # マウスがピンの半分より右側にあったら
                    self.vx = +2
                elif (self.rect.left <= mouse_x <= self.rect.centerx and self.rect.top <= mouse_y <= self.rect.bottom): # マウスがピンの半分より左側にあったら
                    self.vx = -2
        self.rect.move_ip(self.vx, self.vy)

        if check_bound(self.rect) != (True, True):
            self.kill() # 画面外にでたらGroupオブジェクトから消去される


class Tate_Pin(pg.sprite.Sprite): # 縦用のピンのクラス
    """
    縦長用のピンのクラス
    リストにあらかじめ図形左上の座標タプルを入れておくことで呼び出しを簡単にしている
    """
    def __init__(self, xy:tuple[int, int]):
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
        self.rect.topleft = xy
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


class Yoko_Take(pg.sprite.Sprite): # 横用の竹のクラス
    def __init__(self, xy: tuple[int, int]):
        super().__init__()
        self.image = pg.Surface((250, 20))
        pg.draw.rect(self.image, (124, 252, 0), [0, 0, 250, 20])
        self.rect = self.image.get_rect()
        self.rect.topleft = xy
    
    def update(self):
        self.kill()


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
        rad = 10
        self.image = pg.Surface((2*rad, 2*rad))
        self.color = __class__.colors[num]
        pg.draw.circle(self.image, self.color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.vx, self.vy = 0, 0
        self.speed = 3
    
    def update(self):
        self.rect.move_ip(self.vx * self.speed, self.vy * self.speed)


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
        self.image = pg.Surface((20, 20))
        pg.draw.rect(self.image, (0, 0, 0), [0, 0, 20, 20])
        self.rect = self.image.get_rect()
        self.rect.center = obj.rect.center
        self.vx, self.vy = 0, 0
        self.speed = 3
    
    def update(self):
        self.rect.move_ip(self.vx * self.speed, self.vy * self.speed)


class BlackHole(pg.sprite.Sprite):
    def __init__(self, xy: tuple[int, int]):
        super().__init__()
        self.image = pg.image.load("fig/blackhole.png")
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.vx, self.vy = 0, 0
    
    def update(self, screen: pg.Surface):
        self.rect.move_ip(self.vx, self.vy)
        screen.blit(self.image, self.rect)


class Senpuki(pg.sprite.Sprite):
    def __init__(self, angle, xy: tuple[int, int], m):
        super().__init__()
        if m:
            self.image = pg.transform.rotozoom(pg.image.load("fig/senpuki.png"), angle, 1.0)
        elif not m:
            self.image = pg.transform.rotozoom(pg.image.load("fig/nm_senpuki.png"), angle, 1.0)
        self.rect = self.image.get_rect()
        self.rect.center = xy
    
    def update(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class Yoko_Kaze(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.image.load("fig/yokokaze.png")
        self.rect = self.image.get_rect()
        self.rect.centery = y
        if x < WIDTH / 2:
            self.rect.centerx = x + 62
        elif x > WIDTH / 2:
            self.rect.centerx = x - 62
    
    def update(self, count, sen):
        self.rect.centery = sen.rect.centery
        if count > 3:
            self.kill()


class Tate_Kaze(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.image.load("fig/tatekaze.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        if y < HEIGHT / 2:
            self.rect.centery = y + 62
        elif y > HEIGHT / 2:
            self.rect.centery = y - 62
    
    def update(self):
        self.kill()


class Start:
    def __init__(self, stage_num):
        self.fonto = pg.font.Font(None, 120)
        self.image = pg.Surface((250, 80))
        self.txt = self.fonto.render("Start", True, (0,0,0)) #start文字
        pg.draw.rect(self.image, (255, 255, 255), [0, 0, 250, 80], 2) # startの周りの四角
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.txt_rect = self.txt.get_rect()
        self.s_font = pg.font.Font(None, 100)
        self.font_image = self.s_font.render(f"{stage_num + 1}", 0, (0, 0, 0))
        self.font_rect = self.font_image.get_rect()
        self.font_rect.center = WIDTH / 2, HEIGHT / 4
        self.image3 = pg.image.load("fig/mura1.png")
        self.image1 = pg.image.load("fig/2.png") #こうかとん
        self.image2 = pg.image.load("fig/9.png") #こうかとん
        self.rect1 = self.image1.get_rect()
        self.rect2 = self.image2.get_rect()
        self.rect3 = self.image3.get_rect()
        self.txt_rect.center = WIDTH / 2, HEIGHT / 2
        self.rect.center = self.txt_rect.center
    
    def update(self, screen: pg.Surface):
        screen.blit(self.image3,[0,0])
        screen.blit(self.txt,self.txt_rect)
        screen.blit(self.image1,[100, 380])
        screen.blit(self.image2,[450, 380])
        screen.blit(self.image, self.rect)
        screen.blit(self.font_image, self.font_rect)


class Gameover:
    def __init__(self):
        #ゲームオーバーの文字列
        self.image = pg.image.load("fig/game.png") # ゲームオーバー画像
        self.image_rect = self.image.get_rect()
        self.image_rect.center = 300, 200
        #コンチヌー
        self.con = pg.font.Font(None, 50)
        self.con_image = self.con.render(f"CONTINUE ???", 1, (255, 255, 255), (255, 0, 0))
        self.con_rect = self.con_image.get_rect()
        self.con_rect.center = 300, 500
        #リタイア
        self.ret = pg.font.Font(None, 50)
        self.ret_image = self.ret.render(f"RETIRE ???", 1, (255, 255, 255), (0, 0, 255))
        self.ret_rect = self.ret_image.get_rect()
        self.ret_rect.center = 300, 650
    
    def update(self, screen: pg.Surface):
        # screen.blit(self.go_image, self.go_rect)
        screen.blit(self.con_image, self.con_rect)
        screen.blit(self.ret_image, self.ret_rect)
        screen.blit(self.image, self.image_rect) 


class Clear:
    def __init__(self):
        #クリアの文字列
        font = pg.font.Font(None, 80)
        self.img = pg.image.load("fig/宇宙.png")
        self.txt = font.render("CLEAR", True, (255, 255, 0))
        self.txt_rect = self.txt.get_rect()
        self.img1 = pg.image.load("fig/2.png")
        self.img2 = pg.image.load("fig/5.png")
        self.img3 = pg.image.load("fig/2.png")
        self.img4 = pg.image.load("fig/5.png")
        self.img5 = pg.image.load("fig/ペンギン.png")
        self.img6 = pg.image.load("fig/アボカド.png")
        self.txt_rect.center = 300, 200
        #コンチヌー
        self.next = pg.font.Font(None, 50)
        self.next_image = self.next.render(f"NEXT STAGE", 1, (255, 255, 255), (255, 0, 0))
        self.next_rect = self.next_image.get_rect()
        self.next_rect.center = 300, 500
        #リタイア
        self.con = pg.font.Font(None, 50)
        self.con_image = self.con.render(f"CONTINUE ???", 1, (255, 255, 255), (0, 0, 255))
        self.con_rect = self.con_image.get_rect()
        self.con_rect.center = 300, 650
    
    def update(self, screen: pg.Surface):
        #
        screen.blit(self.img, [0, 0])
        # screen.blit(self.txt, [200, 400])
        screen.blit(self.img1,[100, 150])
        screen.blit(self.img2,[450, 150])
        screen.blit(self.img3,[100, 750])
        screen.blit(self.img4,[450, 750])
        screen.blit(self.img5,[450, 400])
        screen.blit(self.img6,[75, 400])
        
        screen.blit(self.txt, self.txt_rect)
        screen.blit(self.next_image, self.next_rect)
        screen.blit(self.con_image, self.con_rect)


def main(stage_num):
    game_stats = None
    pg.display.set_caption(f"広告ゲーム{stage_num}")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/bg_img{stage_num}.jpg")

    start = Start(stage_num)
    go = Gameover()
    cl = Clear()

    kao = Kao()
    ysts = pg.sprite.Group()
    tsts = pg.sprite.Group() 
    asis = pg.sprite.Group()
    mgms = pg.sprite.Group()
    wtrs = pg.sprite.Group()
    trs = pg.sprite.Group()
    sixtones = pg.sprite.Group()
    ypins = pg.sprite.Group()
    tpins = pg.sprite.Group()

    clock = pg.time.Clock()

    # 基本ステージの描写(周りの壁)
    for x in range(7):
        ysts.add(Yoko_Stage((100 * x, 0)))
        ysts.add(Yoko_Stage((100 * x -50, 25)))
        ysts.add(Yoko_Stage((100 * x, 875)))
        ysts.add(Yoko_Stage((100 * x -50, 850)))
    for y in range(10):
        tsts.add(Tate_Stage((0, 100 * y)))
        tsts.add(Tate_Stage((25, 100 * y -50)))
        tsts.add(Tate_Stage((575, 100 * y)))
        tsts.add(Tate_Stage((550, 100 * y -50)))

    #ここはステージ毎に数値を変更することができる
    kokaton = Kokaton(100, 750)
    
    # 追加ステージの座標をfor文で指定する
    for y in range(9):
        asis.add(Asiba((50, 50 + 50 * y)))
        if y <= 1:
            asis.add(Asiba((50, 775 + 50 * y)))

    #ステージによって変えれる
    for x in range(11):
        mgms.add(Obj(0, (325 + 20 * x, 400)))
        wtrs.add(Obj(2, (325  + 20 * x, 820)))
        trs.add(Obj(1, (325  + 20 * x, 200)))

    # 使いたい棒の座標タプルが入ったリストを指定する
    ypins.add(Yoko_Pin((300, 250)))
    ypins.add(Yoko_Pin((300, 450)))
    ypins.add(Yoko_Pin((300, 775)))

    while True:
        start.update(screen)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
            # 一ステージとばすチート
            if event.type == pg.KEYDOWN and event.key == pg.K_g:
                return "clear"
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            if (start.rect.topleft[0] <= mouse_x <= start.rect.bottomright[0]) and (start.rect.topleft[1] <= mouse_y <= start.rect.bottomright[1]):
                break

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
            if event.type == pg.KEYDOWN and event.key == pg.K_r:
                return "continue"
        
        screen.blit(bg_img, [0, 0])

        kokaton.vy = +1
        # 何にも衝突がなければobj.vyは+2になる
        for mgm in mgms:
            mgm.vy = +2
        for wtr in wtrs:
            wtr.vy = +2
        for tre in trs:
            tre.vy = +2
        for stone in sixtones:
            stone.vy = +2
            stone.vx = 0
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            # マウスがこうかとんに重なっていたら
            if (kokaton.rect.topleft[0] <= mouse_x <= kokaton.rect.bottomright[0]) and (kokaton.rect.topleft[1] <= mouse_y <= kokaton.rect.bottomright[1]):
                kokaton.vx, emp = calc_orientation(kokaton.rect, tre.rect)
        
        # こうかとんとステージの当たり判定
        if len(pg.sprite.spritecollide(kokaton, ysts, False)) != 0:
            kokaton.vy = 0
        for tst in pg.sprite.spritecollide(kokaton, tsts, False):
            if tst.rect.left <= kokaton.rect.right <= tst.rect.right:
                kokaton.vx = 0
                kokaton.rect.right -= 10
            elif tst.rect.left <= kokaton.rect.left <= tst.rect.right:
                kokaton.vx = 0
                kokaton.rect.centerx += 10
        
        # こうかとんと足場の当たり判定
        for asi in pg.sprite.spritecollide(kokaton, asis, False):
            kokaton.vy = 0
            if asi.rect.top +5 < kokaton.rect.bottom and asi.rect.bottom > kokaton.rect.top:
                if asi.rect.left <= kokaton.rect.right <= asi.rect.right:
                    kokaton.vx = 0
                    kokaton.rect.right -= 10
                elif asi.rect.left <= kokaton.rect.left <= asi.rect.right:
                    kokaton.vx = 0
                    kokaton.rect.centerx += 10
        
        # こうかとんとピンの当たり判定
        if len(pg.sprite.spritecollide(kokaton, tpins, False)) != 0:
            kokaton.vx = 0
        if len(pg.sprite.spritecollide(kokaton, ypins, False)) != 0:
            kokaton.vy = 0
        
        # こうかとんとマグマと水で出来た石の当たり判定
        for stone in pg.sprite.spritecollide(kokaton, sixtones, False):
            kokaton.vy = 0
            if kokaton.rect.bottom > stone.rect.top +5:
                if kokaton.rect.centerx <= stone.rect.centerx:
                    stone.vx = +2
                elif kokaton.rect.centerx >= stone.rect.centerx:
                    stone.vx = -2
                else:
                    stone.vx = +2
    
        # ピンとobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ypins, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ypins, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ypins, False, False).keys():
            tre.vy = 0
        
        # 床とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ysts, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ysts, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ysts, False, False).keys():
            tre.vy = 0
        
        # 足場とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, asis, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, asis, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, asis, False, False).keys():
            tre.vy = 0
        
        # 水とマグマの当たり判定 ... ステージごとに下においてある方を基準とする
        for wtr in pg.sprite.groupcollide(wtrs, mgms, True, True).keys():
            sixtones.add(Stone(wtr))
        
        # 宝とマグマと水で出来た石の当たり判定
        for tre in pg.sprite.groupcollide(trs, sixtones, False, False).keys():
            tre.vy = 0
        
        # 石と床の当たり判定
        for stone in pg.sprite.groupcollide(sixtones, ysts, False, False).keys():
            stone.vy = 0
        
        # 縦のピンと横のピンの当たり判定 -> 縦ピンのy座標移動量を0にする
        for tpin in pg.sprite.groupcollide(tpins, ypins, False, False).keys():
            tpin.vy = 0
        
        # 横のピンと縦のピンの当たり判定 -> 横ピンのx座標移動量を0にする
        for ypin in pg.sprite.groupcollide(ypins, tpins, False, False).keys():
            ypin.vx = 0
        
        # マグマと宝物の当たり判定
        if len(pg.sprite.groupcollide(mgms, trs, False, True).values()) != 0:
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
        
        # こうかとんとマグマの当たり判定，ゲームオーバー
        if len(pg.sprite.spritecollide(kokaton, mgms, False)) != 0:
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
        
        # こうかとんと宝の当たり判定，クリアー！！
        if len(pg.sprite.spritecollide(kokaton, trs, True)) != 0:
            if len(trs) == 0:
                game_stats = "clear"
                kokaton.update(screen)
                kao.update(kokaton, screen)
                ysts.draw(screen)
                tsts.draw(screen)
                pg.display.update()
                time.sleep(2)

        if game_stats != None:
            break

        kokaton.update(screen)
        ypins.update()
        ypins.draw(screen)
        tpins.update()
        tpins.draw(screen)
        mgms.update()
        mgms.draw(screen)
        wtrs.update()
        wtrs.draw(screen)
        trs.update()
        trs.draw(screen)
        sixtones.update()
        sixtones.draw(screen)
        asis.draw(screen)
        ysts.draw(screen)
        tsts.draw(screen)
        pg.display.update()
        clock.tick(60)
    
    while True:
        if game_stats == "gameover":
            go.update(screen)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "retire"
            if pg.mouse.get_pressed()[0]: # マウスの処理
                mouse_x, mouse_y = pg.mouse.get_pos()
                if (go.con_rect.topleft[0] <= mouse_x <= go.con_rect.bottomright[0]) and (go.con_rect.topleft[1] <= mouse_y <= go.con_rect.bottomright[1]):
                    return "continue"
                elif (go.ret_rect.topleft[0] <= mouse_x <= go.ret_rect.bottomright[0]) and (go.ret_rect.topleft[1] <= mouse_y <= go.ret_rect.bottomright[1]):
                    return "retire"
        
        elif game_stats == "clear":
            cl.update(screen)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "retire"
            if pg.mouse.get_pressed()[0]: # マウスの処理
                mouse_x, mouse_y = pg.mouse.get_pos()
                if (cl.next_rect.topleft[0] <= mouse_x <= cl.next_rect.bottomright[0]) and (cl.next_rect.topleft[1] <= mouse_y <= cl.next_rect.bottomright[1]):
                    return "clear"
                elif (cl.con_rect.topleft[0] <= mouse_x <= cl.con_rect.bottomright[0]) and (cl.con_rect.topleft[1] <= mouse_y <= cl.con_rect.bottomright[1]):
                    return "continue"


def main2(stage_num):
    game_stats = None
    pg.display.set_caption(f"広告ゲーム{stage_num}")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/bg_img{stage_num}.jpg")

    start = Start(stage_num)
    go = Gameover()
    cl = Clear()

    kao = Kao()
    ysts = pg.sprite.Group()
    tsts = pg.sprite.Group() 
    asis = pg.sprite.Group()
    mgms = pg.sprite.Group()
    wtrs = pg.sprite.Group()
    trs = pg.sprite.Group()
    sixtones = pg.sprite.Group()
    ypins = pg.sprite.Group()
    tpins = pg.sprite.Group()

    clock = pg.time.Clock()

    # 基本ステージの描写(周りの壁)
    for x in range(7):
        ysts.add(Yoko_Stage((100 * x, 0)))
        ysts.add(Yoko_Stage((100 * x -50, 25)))
        ysts.add(Yoko_Stage((100 * x, 875)))
        ysts.add(Yoko_Stage((100 * x -50, 850)))
    for y in range(10):
        tsts.add(Tate_Stage((0, 100 * y)))
        tsts.add(Tate_Stage((25, 100 * y -50)))
        tsts.add(Tate_Stage((575, 100 * y)))
        tsts.add(Tate_Stage((550, 100 * y -50)))

    #ここはステージ毎に数値を変更することができる
    kokaton = Kokaton(175, 550)
    # 追加ステージの座標をfor文で指定する
    for y in range(11):
        asis.add(Asiba((300, 50 + 50 * y)))

    #ステージによって変えれる
    for x in range(11):
        mgms.add(Obj(0, (75 + 20 * x, 800)))
        wtrs.add(Obj(2, (75  + 20 * x, 250)))
        trs.add(Obj(1, (325  + 20 * x, 800)))

    # 使いたい棒の座標タプルが入ったリストを指定する
    ypins.add(Yoko_Pin((50, 300)))
    ypins.add(Yoko_Pin((50, 575)))
    tpins.add(Tate_Pin((290, 600)))

    while True:
        start.update(screen)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
            # 一ステージとばすチート
            if event.type == pg.KEYDOWN and event.key == pg.K_g:
                return "clear"
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            if (start.rect.topleft[0] <= mouse_x <= start.rect.bottomright[0]) and (start.rect.topleft[1] <= mouse_y <= start.rect.bottomright[1]):
                break

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
            if event.type == pg.KEYDOWN and event.key == pg.K_r:
                return "continue"
        
        screen.blit(bg_img, [0, 0])

        kokaton.vy = +1
        # 何にも衝突がなければobj.vyは+2になる
        for mgm in mgms:
            mgm.vy = +2
        for wtr in wtrs:
            wtr.vy = +2
        for tre in trs:
            tre.vy = +2
        for stone in sixtones:
            stone.vy = +2
            stone.vx = 0
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            # マウスがこうかとんに重なっていたら
            if (kokaton.rect.topleft[0] <= mouse_x <= kokaton.rect.bottomright[0]) and (kokaton.rect.topleft[1] <= mouse_y <= kokaton.rect.bottomright[1]):
                kokaton.vx, emp = calc_orientation(kokaton.rect, tre.rect)
        
        # こうかとんとステージの当たり判定
        if len(pg.sprite.spritecollide(kokaton, ysts, False)) != 0:
            kokaton.vy = 0
        for tst in pg.sprite.spritecollide(kokaton, tsts, False):
            if tst.rect.left <= kokaton.rect.right <= tst.rect.right:
                kokaton.vx = 0
                kokaton.rect.right -= 10
            elif tst.rect.left <= kokaton.rect.left <= tst.rect.right:
                kokaton.vx = 0
                kokaton.rect.centerx += 10
        
        # こうかとんと足場の当たり判定
        for asi in pg.sprite.spritecollide(kokaton, asis, False):
            kokaton.vy = 0
            if asi.rect.top +5 < kokaton.rect.bottom and asi.rect.bottom > kokaton.rect.top:
                if asi.rect.left <= kokaton.rect.right <= asi.rect.right:
                    kokaton.vx = 0
                    kokaton.rect.right -= 10
                elif asi.rect.left <= kokaton.rect.left <= asi.rect.right:
                    kokaton.vx = 0
                    kokaton.rect.centerx += 10
        
        # こうかとんとピンの当たり判定
        if len(pg.sprite.spritecollide(kokaton, tpins, False)) != 0:
            kokaton.vx = 0
        if len(pg.sprite.spritecollide(kokaton, ypins, False)) != 0:
            kokaton.vy = 0
        
        # こうかとんとマグマと水で出来た石の当たり判定
        for stone in pg.sprite.spritecollide(kokaton, sixtones, False):
            kokaton.vy = 0
            if kokaton.rect.bottom > stone.rect.top +5:
                if kokaton.rect.centerx <= stone.rect.centerx:
                    stone.vx = +2
                elif kokaton.rect.centerx >= stone.rect.centerx:
                    stone.vx = -2
                else:
                    stone.vx = +2

        # ピンとobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ypins, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ypins, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ypins, False, False).keys():
            tre.vy = 0
        
        # 床とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ysts, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ysts, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ysts, False, False).keys():
            tre.vy = 0
        
        # 足場とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, asis, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, asis, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, asis, False, False).keys():
            tre.vy = 0
        
        # 水とマグマの当たり判定 ... ステージごとに下においてある方を基準とする
        for mgm in pg.sprite.groupcollide(mgms, wtrs, True, True).keys():
            sixtones.add(Stone(mgm))
        
        # 宝とマグマと水で出来た石の当たり判定
        for tre in pg.sprite.groupcollide(trs, sixtones, False, False).keys():
            tre.vy = 0
        
        # 石と床の当たり判定
        for stone in pg.sprite.groupcollide(sixtones, ysts, False, False).keys():
            stone.vy = 0
        
        # 縦のピンと横のピンの当たり判定 -> 縦ピンのy座標移動量を0にする
        for tpin in pg.sprite.groupcollide(tpins, ypins, False, False).keys():
            tpin.vy = 0
        
        # 横のピンと縦のピンの当たり判定 -> 横ピンのx座標移動量を0にする
        for ypin in pg.sprite.groupcollide(ypins, tpins, False, False).keys():
            ypin.vx = 0
        
        # マグマと宝物の当たり判定
        if len(pg.sprite.groupcollide(mgms, trs, False, True).values()) != 0:
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
        
        # こうかとんとマグマの当たり判定，ゲームオーバー
        if len(pg.sprite.spritecollide(kokaton, mgms, False)) != 0:
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
        
        # こうかとんと宝の当たり判定，クリアー！！
        if len(pg.sprite.spritecollide(kokaton, trs, True)) != 0:
            if len(trs) == 0:
                game_stats = "clear"
                kokaton.update(screen)
                kao.update(kokaton, screen)
                ysts.draw(screen)
                tsts.draw(screen)
                pg.display.update()
                time.sleep(2)

        if game_stats != None:
            break

        kokaton.update(screen)
        ypins.update()
        ypins.draw(screen)
        tpins.update()
        tpins.draw(screen)
        mgms.update()
        mgms.draw(screen)
        wtrs.update()
        wtrs.draw(screen)
        trs.update()
        trs.draw(screen)
        sixtones.update()
        sixtones.draw(screen)
        asis.draw(screen)
        ysts.draw(screen)
        tsts.draw(screen)
        pg.display.update()
        clock.tick(60)
    
    while True:
        if game_stats == "gameover":
            go.update(screen)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "retire"
            if pg.mouse.get_pressed()[0]: # マウスの処理
                mouse_x, mouse_y = pg.mouse.get_pos()
                if (go.con_rect.topleft[0] <= mouse_x <= go.con_rect.bottomright[0]) and (go.con_rect.topleft[1] <= mouse_y <= go.con_rect.bottomright[1]):
                    return "continue"
                elif (go.ret_rect.topleft[0] <= mouse_x <= go.ret_rect.bottomright[0]) and (go.ret_rect.topleft[1] <= mouse_y <= go.ret_rect.bottomright[1]):
                    return "retire"
        
        elif game_stats == "clear":
            cl.update(screen)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "retire"
            if pg.mouse.get_pressed()[0]: # マウスの処理
                mouse_x, mouse_y = pg.mouse.get_pos()
                if (cl.next_rect.topleft[0] <= mouse_x <= cl.next_rect.bottomright[0]) and (cl.next_rect.topleft[1] <= mouse_y <= cl.next_rect.bottomright[1]):
                    return "clear"
                elif (cl.con_rect.topleft[0] <= mouse_x <= cl.con_rect.bottomright[0]) and (cl.con_rect.topleft[1] <= mouse_y <= cl.con_rect.bottomright[1]):
                    return "continue"


def main3(stage_num):
    game_stats = None
    pg.display.set_caption(f"広告ゲーム{stage_num + 1}")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/bg_img{stage_num}.jpg")

    start = Start(stage_num)
    go = Gameover()
    cl = Clear()

    kao = Kao()
    ysts = pg.sprite.Group()
    tsts = pg.sprite.Group()
    asis = pg.sprite.Group()
    mgms = pg.sprite.Group()
    wtrs = pg.sprite.Group()
    trs = pg.sprite.Group()
    sixtones = pg.sprite.Group()
    ypins = pg.sprite.Group()
    tpins = pg.sprite.Group()
    ytks = pg.sprite.Group()

    clock = pg.time.Clock()

    # 基本ステージの描写(周りの壁)
    for x in range(7):
        ysts.add(Yoko_Stage((100 * x, 0)))
        ysts.add(Yoko_Stage((100 * x -50, 25)))
        ysts.add(Yoko_Stage((100 * x, 875)))
        ysts.add(Yoko_Stage((100 * x -50, 850)))
    for y in range(10):
        tsts.add(Tate_Stage((0, 100 * y)))
        tsts.add(Tate_Stage((25, 100 * y -50)))
        tsts.add(Tate_Stage((575, 100 * y)))
        tsts.add(Tate_Stage((550, 100 * y -50)))

    #ここはステージ毎に数値を変更することができる
    kokaton = Kokaton(300, 600)

    # 追加ステージの座標をfor文で指定する
    asis.add(Asiba((175, 650)))

    #ステージによって変えれる
    for i in range(24):
        mgms.add(Obj(0, (70 + 20 * i, 400)))
        wtrs.add(Obj(2, (70  + 20 * i, 200)))
        if i <= 11:
            trs.add(Obj(1, (190  + 20 * i, 800)))

    # 使いたい棒の座標タプルが入ったリストを指定する
    ypins.add(Yoko_Pin((50, 240)))
    ypins.add(Yoko_Pin((300, 240)))
    ypins.add(Yoko_Pin((50, 430)))
    ypins.add(Yoko_Pin((300, 430)))

    # 使いたい竹の座標をタプルで指定する
    ytks.add(Yoko_Take((50, 700)))
    ytks.add(Yoko_Take((300, 700)))

    while True:
        start.update(screen)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
            # 一ステージとばすチート
            if event.type == pg.KEYDOWN and event.key == pg.K_g:
                return "clear"
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            if (start.rect.topleft[0] <= mouse_x <= start.rect.bottomright[0]) and (start.rect.topleft[1] <= mouse_y <= start.rect.bottomright[1]):
                break

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
            if event.type == pg.KEYDOWN and event.key == pg.K_r:
                return "continue"
        
        screen.blit(bg_img, [0, 0])

        kokaton.vy = +1
        # 何にも衝突がなければobj.vyは+2になる
        for mgm in mgms:
            mgm.vy = +2
        for wtr in wtrs:
            wtr.vy = +2
        for tre in trs:
            tre.vy = +2
        for stone in sixtones:
            stone.vy = +2
            stone.vx = 0
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            # マウスがこうかとんに重なっていたら
            if (kokaton.rect.topleft[0] <= mouse_x <= kokaton.rect.bottomright[0]) and (kokaton.rect.topleft[1] <= mouse_y <= kokaton.rect.bottomright[1]):
                kokaton.vx, emp = calc_orientation(kokaton.rect, tre.rect)
        
        # こうかとんとステージの当たり判定
        if len(pg.sprite.spritecollide(kokaton, ysts, False)) != 0:
            kokaton.vy = 0
        for tst in pg.sprite.spritecollide(kokaton, tsts, False):
            if tst.rect.left <= kokaton.rect.right <= tst.rect.right:
                kokaton.vx = 0
                kokaton.rect.right -= 10
            elif tst.rect.left <= kokaton.rect.left <= tst.rect.right:
                kokaton.vx = 0
                kokaton.rect.centerx += 10
        
        # こうかとんと足場の当たり判定
        for asi in pg.sprite.spritecollide(kokaton, asis, False):
            kokaton.vy = 0
            if asi.rect.top +5 < kokaton.rect.bottom and asi.rect.bottom > kokaton.rect.top:
                if asi.rect.left <= kokaton.rect.right <= asi.rect.right:
                    kokaton.vx = 0
                    kokaton.rect.right -= 10
                elif asi.rect.left <= kokaton.rect.left <= asi.rect.right:
                    kokaton.vx = 0
                    kokaton.rect.centerx += 10
        
        # こうかとんとピンの当たり判定
        if len(pg.sprite.spritecollide(kokaton, tpins, False)) != 0:
            kokaton.vx = 0
        if len(pg.sprite.spritecollide(kokaton, ypins, False)) != 0:
            kokaton.vy = 0
        
        #こうかとんと竹の当たり判定
        if len(pg.sprite.spritecollide(kokaton, ytks, False)) != 0:
            kokaton.vy = 0
        
        # こうかとんとマグマと水で出来た石の当たり判定
        for stone in pg.sprite.spritecollide(kokaton, sixtones, False):
            kokaton.vy = 0
            if kokaton.rect.bottom > stone.rect.top +5:
                if kokaton.rect.centerx <= stone.rect.centerx:
                    stone.vx = +2
                elif kokaton.rect.centerx >= stone.rect.centerx:
                    stone.vx = -2
                else:
                    stone.vx = +2

        # ピンとobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ypins, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ypins, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ypins, False, False).keys():
            tre.vy = 0
        
        # 竹とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ytks, False, True).keys():
            pass
        for wtr in pg.sprite.groupcollide(wtrs, ytks, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ytks, False, False).keys():
            tre.vy = 0
        
        # 床とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ysts, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ysts, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ysts, False, False).keys():
            tre.vy = 0
        
        # 足場とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, asis, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, asis, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, asis, False, False).keys():
            tre.vy = 0
        
        # 水とマグマの当たり判定 ... ステージごとに下においてある方を基準とする
        for mgm in pg.sprite.groupcollide(mgms, wtrs, True, True).keys():
            sixtones.add(Stone(mgm))
        
        # 宝とマグマと水で出来た石の当たり判定
        for tre in pg.sprite.groupcollide(trs, sixtones, False, False).keys():
            tre.vy = 0
        
        # ピンと石の当たり判定
        for stone in pg.sprite.groupcollide(sixtones, ypins, False, False).keys():
            stone.vy = 0
        
        # 石と足場の当たり判定
        for stone in pg.sprite.groupcollide(sixtones, asis, False, False).keys():
            stone.vy = 0

        # 石と竹の当たり判定
        if len(pg.sprite.groupcollide(sixtones, ytks, False, True)) != 0:
            pass

        # 石と床の当たり判定
        for stone in pg.sprite.groupcollide(sixtones, ysts, False, False).keys():
            stone.vy = 0

        # 縦のピンと横のピンの当たり判定 -> 縦ピンのy座標移動量を0にする
        for tpin in pg.sprite.groupcollide(tpins, ypins, False, False).keys():
            tpin.vy = 0
        
        # 横のピンと縦のピンの当たり判定 -> 横ピンのx座標移動量を0にする
        for ypin in pg.sprite.groupcollide(ypins, tpins, False, False).keys():
            ypin.vx = 0
        
        # マグマと宝物の当たり判定
        if len(pg.sprite.groupcollide(mgms, trs, False, True).values()) != 0:
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
        
        # こうかとんとマグマの当たり判定，ゲームオーバー
        if len(pg.sprite.spritecollide(kokaton, mgms, False)) != 0:
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
        
        # こうかとんと宝の当たり判定，クリアー！！
        if len(pg.sprite.spritecollide(kokaton, trs, True)) != 0:
            if len(trs) == 0:
                game_stats = "clear"
                kokaton.update(screen)
                kao.update(kokaton, screen)
                ysts.draw(screen)
                tsts.draw(screen)
                pg.display.update()
                time.sleep(2)

        if game_stats != None:
            break

        kokaton.update(screen)
        ypins.update()
        ypins.draw(screen)
        tpins.update()
        tpins.draw(screen)
        mgms.update()
        mgms.draw(screen)
        wtrs.update()
        wtrs.draw(screen)
        trs.update()
        trs.draw(screen)
        sixtones.update()
        sixtones.draw(screen)
        asis.draw(screen)
        ysts.draw(screen)
        tsts.draw(screen)
        ytks.draw(screen)
        pg.display.update()
        clock.tick(60)
    
    while True:
        if game_stats == "gameover":
            go.update(screen)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "retire"
            if pg.mouse.get_pressed()[0]: # マウスの処理
                mouse_x, mouse_y = pg.mouse.get_pos()
                if (go.con_rect.topleft[0] <= mouse_x <= go.con_rect.bottomright[0]) and (go.con_rect.topleft[1] <= mouse_y <= go.con_rect.bottomright[1]):
                    return "continue"
                elif (go.ret_rect.topleft[0] <= mouse_x <= go.ret_rect.bottomright[0]) and (go.ret_rect.topleft[1] <= mouse_y <= go.ret_rect.bottomright[1]):
                    return "retire"
        
        elif game_stats == "clear":
            cl.update(screen)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "retire"
            if pg.mouse.get_pressed()[0]: # マウスの処理
                mouse_x, mouse_y = pg.mouse.get_pos()
                if (cl.next_rect.topleft[0] <= mouse_x <= cl.next_rect.bottomright[0]) and (cl.next_rect.topleft[1] <= mouse_y <= cl.next_rect.bottomright[1]):
                    return "clear"
                elif (cl.con_rect.topleft[0] <= mouse_x <= cl.con_rect.bottomright[0]) and (cl.con_rect.topleft[1] <= mouse_y <= cl.con_rect.bottomright[1]):
                    return "continue"


def main4(stage_num):
    game_stats = None
    pg.display.set_caption(f"広告ゲーム{stage_num + 1}")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/bg_img{stage_num}.jpg")

    start = Start(stage_num)
    go = Gameover()
    cl = Clear()

    kao = Kao()
    ysts = pg.sprite.Group()
    tsts = pg.sprite.Group()
    asis = pg.sprite.Group()
    mgms = pg.sprite.Group()
    wtrs = pg.sprite.Group()
    trs = pg.sprite.Group()
    sixtones = pg.sprite.Group()
    ypins = pg.sprite.Group()
    tpins = pg.sprite.Group()
    ytks = pg.sprite.Group()

    clock = pg.time.Clock()

    # 基本ステージの描写(周りの壁)
    for x in range(7):
        ysts.add(Yoko_Stage((100 * x, 0)))
        ysts.add(Yoko_Stage((100 * x -50, 25)))
        ysts.add(Yoko_Stage((100 * x, 875)))
        ysts.add(Yoko_Stage((100 * x -50, 850)))
    for y in range(10):
        tsts.add(Tate_Stage((0, 100 * y)))
        tsts.add(Tate_Stage((25, 100 * y -50)))
        tsts.add(Tate_Stage((575, 100 * y)))
        tsts.add(Tate_Stage((550, 100 * y -50)))

    #ここはステージ毎に数値を変更することができる
    kokaton = Kokaton(300, 150)

    #ステージによって変えれる
    for i in range(24):
        mgms.add(Obj(0, (70 + 20 * i, 400)))
        wtrs.add(Obj(2, (70  + 20 * i, 200)))
        trs.add(Obj(1, (70  + 20 * i, 800)))
    
    # ブラックホール
    blackhole = BlackHole((300, 600))

    # 使いたい棒の座標タプルが入ったリストを指定する
    ypins.add(Yoko_Pin((50, 240)))
    ypins.add(Yoko_Pin((300, 240)))
    ypins.add(Yoko_Pin((50, 430)))
    ypins.add(Yoko_Pin((300, 430)))

    # 使いたい竹の座標をタプルで指定する
    ytks.add(Yoko_Take((50, 770)))
    ytks.add(Yoko_Take((300, 770)))

    while True:
        start.update(screen)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
            # 一ステージとばすチート
            if event.type == pg.KEYDOWN and event.key == pg.K_g:
                return "clear"
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            if (start.rect.topleft[0] <= mouse_x <= start.rect.bottomright[0]) and (start.rect.topleft[1] <= mouse_y <= start.rect.bottomright[1]):
                break

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
            if event.type == pg.KEYDOWN and event.key == pg.K_r:
                return "continue"
        
        screen.blit(bg_img, [0, 0])

        kokaton.vy = +1
        # objはブラックホールに吸い込まれる
        for mgm in mgms:
            try:
                mgm.vx, mgm.vy = calc_orientation(mgm.rect, blackhole.rect)
            except ZeroDivisionError:
                pass
        for wtr in wtrs:
            try:
                wtr.vx, wtr.vy = calc_orientation(wtr.rect, blackhole.rect)
            except ZeroDivisionError:
                pass
        for tre in trs:
            try:
                tre.vx, tre.vy = calc_orientation(tre.rect, blackhole.rect)
            except ZeroDivisionError:
                game_stats = "gameover"
                kokaton.update(screen)
                kao.update(kokaton, screen)
                ysts.draw(screen)
                tsts.draw(screen)
                pg.display.update()
                time.sleep(2)
        
        for stone in sixtones:
            stone.vy = +2
            stone.vx = 0
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            # マウスがこうかとんに重なっていたら
            if (kokaton.rect.topleft[0] <= mouse_x <= kokaton.rect.bottomright[0]) and (kokaton.rect.topleft[1] <= mouse_y <= kokaton.rect.bottomright[1]):
                kokaton.vx, emp = calc_orientation(kokaton.rect, tre.rect)
            # ブラックホールの移動処理
            if (blackhole.rect.topleft[0] <= mouse_x <= blackhole.rect.bottomright[0]) and (blackhole.rect.topleft[1] <= mouse_y <= blackhole.rect.bottomright[1]):
                if (50 <= mouse_x <= 550) and (50 <= mouse_y <= 850):
                    blackhole.rect.center = (mouse_x, mouse_y)
        
        # こうかとんとステージの当たり判定
        if len(pg.sprite.spritecollide(kokaton, ysts, False)) != 0:
            kokaton.vy = 0
        for tst in pg.sprite.spritecollide(kokaton, tsts, False):
            if tst.rect.left <= kokaton.rect.right <= tst.rect.right:
                kokaton.vx = 0
                kokaton.rect.right -= 10
            elif tst.rect.left <= kokaton.rect.left <= tst.rect.right:
                kokaton.vx = 0
                kokaton.rect.centerx += 10
        
        # こうかとんと足場の当たり判定
        for asi in pg.sprite.spritecollide(kokaton, asis, False):
            kokaton.vy = 0
            if asi.rect.top +5 < kokaton.rect.bottom and asi.rect.bottom > kokaton.rect.top:
                if asi.rect.left <= kokaton.rect.right <= asi.rect.right:
                    kokaton.vx = 0
                    kokaton.rect.right -= 10
                elif asi.rect.left <= kokaton.rect.left <= asi.rect.right:
                    kokaton.vx = 0
                    kokaton.rect.centerx += 10
        
        # こうかとんとピンの当たり判定
        if len(pg.sprite.spritecollide(kokaton, tpins, False)) != 0:
            kokaton.vx = 0
        if len(pg.sprite.spritecollide(kokaton, ypins, False)) != 0:
            kokaton.vy = 0
        
        #こうかとんと竹の当たり判定
        if len(pg.sprite.spritecollide(kokaton, ytks, False)) != 0:
            kokaton.vy = 0
        
        # こうかとんとマグマと水で出来た石の当たり判定
        for stone in pg.sprite.spritecollide(kokaton, sixtones, False):
            kokaton.vy = 0
            if kokaton.rect.bottom > stone.rect.top +5:
                if kokaton.rect.centerx <= stone.rect.centerx:
                    stone.vx = +2
                elif kokaton.rect.centerx >= stone.rect.centerx:
                    stone.vx = -2
                else:
                    stone.vx = +2

        # こうかとんとブラックホールの当たり判定
        if kokaton.rect.colliderect(blackhole.rect):
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)

        # ピンとobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ypins, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ypins, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ypins, False, False).keys():
            tre.vy = 0
        
        # 竹とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ytks, False, True).keys():
            pass
        for wtr in pg.sprite.groupcollide(wtrs, ytks, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ytks, False, False).keys():
            tre.vy = 0
        
        # 床とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ysts, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ysts, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ysts, False, False).keys():
            tre.vy = 0
        
        # 足場とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, asis, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, asis, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, asis, False, False).keys():
            tre.vy = 0
        
        # ブラックホールとobjの当たり判定
        if len(pg.sprite.spritecollide(blackhole, mgms, True)) != 0:
            pass
        if len(pg.sprite.spritecollide(blackhole, wtrs, True)) != 0:
            pass
        if len(pg.sprite.spritecollide(blackhole, trs, True)) != 0:
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
        
        # 水とマグマの当たり判定 ... ステージごとに下においてある方を基準とする
        for mgm in pg.sprite.groupcollide(mgms, wtrs, True, True).keys():
            sixtones.add(Stone(mgm))
        
        # 宝とマグマと水で出来た石の当たり判定
        for tre in pg.sprite.groupcollide(trs, sixtones, False, False).keys():
            tre.vy = 0
        
        # ピンと石の当たり判定
        for stone in pg.sprite.groupcollide(sixtones, ypins, False, False).keys():
            stone.vy = 0
        
        # 石と足場の当たり判定
        for stone in pg.sprite.groupcollide(sixtones, asis, False, False).keys():
            stone.vy = 0

        # 石と竹の当たり判定
        if len(pg.sprite.groupcollide(sixtones, ytks, False, True)) != 0:
            pass

        # 石と床の当たり判定
        for stone in pg.sprite.groupcollide(sixtones, ysts, False, False).keys():
            stone.vy = 0

        # 縦のピンと横のピンの当たり判定 -> 縦ピンのy座標移動量を0にする
        for tpin in pg.sprite.groupcollide(tpins, ypins, False, False).keys():
            tpin.vy = 0
        
        # 横のピンと縦のピンの当たり判定 -> 横ピンのx座標移動量を0にする
        for ypin in pg.sprite.groupcollide(ypins, tpins, False, False).keys():
            ypin.vx = 0
        

        
        # マグマと宝物の当たり判定
        if len(pg.sprite.groupcollide(mgms, trs, False, True).values()) != 0:
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
        
        # こうかとんとマグマの当たり判定，ゲームオーバー
        if len(pg.sprite.spritecollide(kokaton, mgms, False)) != 0:
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
        
        # こうかとんと宝の当たり判定，クリアー！！
        if len(pg.sprite.spritecollide(kokaton, trs, True)) != 0:
            if len(trs) == 0:
                game_stats = "clear"
                kokaton.update(screen)
                kao.update(kokaton, screen)
                ysts.draw(screen)
                tsts.draw(screen)
                pg.display.update()
                time.sleep(2)

        if game_stats != None:
            break

        kokaton.update(screen)
        ypins.update()
        ypins.draw(screen)
        tpins.update()
        tpins.draw(screen)
        mgms.update()
        mgms.draw(screen)
        wtrs.update()
        wtrs.draw(screen)
        trs.update()
        trs.draw(screen)
        sixtones.update()
        sixtones.draw(screen)
        asis.draw(screen)
        ytks.draw(screen)
        blackhole.update(screen)
        ysts.draw(screen)
        tsts.draw(screen)
        pg.display.update()
        clock.tick(60)
    
    while True:
        if game_stats == "gameover":
            go.update(screen)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "retire"
            if pg.mouse.get_pressed()[0]: # マウスの処理
                mouse_x, mouse_y = pg.mouse.get_pos()
                if (go.con_rect.topleft[0] <= mouse_x <= go.con_rect.bottomright[0]) and (go.con_rect.topleft[1] <= mouse_y <= go.con_rect.bottomright[1]):
                    return "continue"
                elif (go.ret_rect.topleft[0] <= mouse_x <= go.ret_rect.bottomright[0]) and (go.ret_rect.topleft[1] <= mouse_y <= go.ret_rect.bottomright[1]):
                    return "retire"
        
        elif game_stats == "clear":
            cl.update(screen)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "retire"
            if pg.mouse.get_pressed()[0]: # マウスの処理
                mouse_x, mouse_y = pg.mouse.get_pos()
                if (cl.next_rect.topleft[0] <= mouse_x <= cl.next_rect.bottomright[0]) and (cl.next_rect.topleft[1] <= mouse_y <= cl.next_rect.bottomright[1]):
                    return "clear"
                elif (cl.con_rect.topleft[0] <= mouse_x <= cl.con_rect.bottomright[0]) and (cl.con_rect.topleft[1] <= mouse_y <= cl.con_rect.bottomright[1]):
                    return "continue"


def main5(stage_num):
    game_stats = None
    pg.display.set_caption(f"広告ゲーム{stage_num}")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/bg_img{stage_num}.jpg")
    countl = 0
    countr = 0

    start = Start(stage_num)
    go = Gameover()
    cl = Clear()

    kao = Kao()
    ysts = pg.sprite.Group()
    tsts = pg.sprite.Group() 
    asis = pg.sprite.Group()
    mgms = pg.sprite.Group()
    wtrs = pg.sprite.Group()
    trs = pg.sprite.Group()
    sixtones = pg.sprite.Group()
    ypins = pg.sprite.Group()
    tpins = pg.sprite.Group()
    ytks = pg.sprite.Group()
    ykazesl = pg.sprite.Group()
    ykazesr = pg.sprite.Group()
    tkazes = pg.sprite.Group()

    clock = pg.time.Clock()

    # 基本ステージの描写(周りの壁)
    for x in range(7):
        ysts.add(Yoko_Stage((100 * x, 0)))
        ysts.add(Yoko_Stage((100 * x -50, 25)))
        ysts.add(Yoko_Stage((100 * x, 875)))
        ysts.add(Yoko_Stage((100 * x -50, 850)))
    for y in range(10):
        tsts.add(Tate_Stage((0, 100 * y)))
        tsts.add(Tate_Stage((25, 100 * y -50)))
        tsts.add(Tate_Stage((575, 100 * y)))
        tsts.add(Tate_Stage((550, 100 * y -50)))

    #ここはステージ毎に数値を変更することができる
    kokaton = Kokaton(150, 150)
    # 追加ステージの座標をfor文で指定する
    asis.add(Asiba((300, 300)))
    asis.add(Asiba((50, 500)))

    #ステージによって変えれる
    for x in range(6):
        #mgms.add(Obj(0, (325 + 20 * x, 250)))
        wtrs.add(Obj(2, (75 + 20 * x, 400)))
        trs.add(Obj(1, (75 + 20 * x, 800)))
    for i in range(2):
        mgms.add(Obj(0, (325 + 20 * x, 250)))

    # 使いたい棒の座標タプルが入ったリストを指定する
    ypins.add(Yoko_Pin((50, 200)))

    # 竹
    ytks.add(Yoko_Take((50, 330)))
    ytks.add(Yoko_Take((300, 530)))

    # 扇風機
    cm_l = Senpuki(90, (25, 200),True)
    cm_r = Senpuki(-90, (575, 100), True)
    nm_d = Senpuki(180, (250, 875), False)

    # 動かない風
    for y in range(2):
        tkazes.add(Tate_Kaze(nm_d.rect.centerx, nm_d.rect.centery - 125 * y))        

    while True:
        start.update(screen)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
            # 一ステージとばすチート
            if event.type == pg.KEYDOWN and event.key == pg.K_g:
                return "clear"
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            if (start.rect.topleft[0] <= mouse_x <= start.rect.bottomright[0]) and (start.rect.topleft[1] <= mouse_y <= start.rect.bottomright[1]):
                break

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "retire"
            if event.type == pg.KEYDOWN and event.key == pg.K_r:
                return "continue"
            if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[2]:
                mouse_x, mouse_y = pg.mouse.get_pos()
                if (cm_l.rect.topleft[0] <= mouse_x <= cm_l.rect.bottomright[0]) and (cm_l.rect.topleft[1] <= mouse_y <= cm_l.rect.bottomright[1]):
                    ykazesl.add(Yoko_Kaze(cm_l.rect.centerx + 125 * countl, cm_l.rect.centery))
                    countl += 1
                    ykazesl.update(countl, cm_l)
                    
                elif (cm_r.rect.topleft[0] <= mouse_x <= cm_r.rect.bottomright[0]) and (cm_r.rect.topleft[1] <= mouse_y <= cm_r.rect.bottomright[1]):
                    ykazesr.add(Yoko_Kaze(cm_r.rect.centerx - 125 * countr, cm_r.rect.centery))
                    countr += 1
                    ykazesr.update(countr, cm_r)
        
        screen.blit(bg_img, [0, 0])

        kokaton.vx = 0
        kokaton.vy = +1
        # 何にも衝突がなければobj.vyは+2になる
        for mgm in mgms:
            mgm.vx = 0
            mgm.vy = +2
        for wtr in wtrs:
            wtr.vx = 0
            wtr.vy = +2
        for tre in trs:
            tre.vx = 0
            tre.vy = +2
        for stone in sixtones:
            stone.vy = +2
            stone.vx = 0
        
        if pg.mouse.get_pressed()[0]: # マウスの処理
            mouse_x, mouse_y = pg.mouse.get_pos()
            # マウスがこうかとんに重なっていたら
            if (kokaton.rect.topleft[0] <= mouse_x <= kokaton.rect.bottomright[0]) and (kokaton.rect.topleft[1] <= mouse_y <= kokaton.rect.bottomright[1]):
                kokaton.vx, emp = calc_orientation(kokaton.rect, tre.rect)
            if (cm_l.rect.topleft[0] <= mouse_x <= cm_l.rect.bottomright[0]) and (cm_l.rect.topleft[1] <= mouse_y <= cm_l.rect.bottomright[1]):
                cm_l.rect.centery = mouse_y
            if (cm_r.rect.topleft[0] <= mouse_x <= cm_r.rect.bottomright[0]) and (cm_r.rect.topleft[1] <= mouse_y <= cm_r.rect.bottomright[1]):
                cm_r.rect.centery = mouse_y
        
        # こうかとんとステージの当たり判定
        if len(pg.sprite.spritecollide(kokaton, ysts, False)) != 0:
            kokaton.vy = 0
        for tst in pg.sprite.spritecollide(kokaton, tsts, False):
            if tst.rect.left <= kokaton.rect.right <= tst.rect.right:
                kokaton.vx = 0
                kokaton.rect.right -= 10
            elif tst.rect.left <= kokaton.rect.left <= tst.rect.right:
                kokaton.vx = 0
                kokaton.rect.centerx += 10
        
        # こうかとんと足場の当たり判定
        for asi in pg.sprite.spritecollide(kokaton, asis, False):
            kokaton.vy = 0
            if asi.rect.top +5 < kokaton.rect.bottom and asi.rect.bottom > kokaton.rect.top:
                if asi.rect.left <= kokaton.rect.right <= asi.rect.right:
                    kokaton.vx = 0
                    kokaton.rect.right -= 10
                elif asi.rect.left <= kokaton.rect.left <= asi.rect.right:
                    kokaton.vx = 0
                    kokaton.rect.centerx += 10
        
        # こうかとんとピンの当たり判定
        if len(pg.sprite.spritecollide(kokaton, tpins, False)) != 0:
            kokaton.vx = 0
        if len(pg.sprite.spritecollide(kokaton, ypins, False)) != 0:
            kokaton.vy = 0
        
        # こうかとんとマグマと水で出来た石の当たり判定
        for stone in pg.sprite.spritecollide(kokaton, sixtones, False):
            kokaton.vy = 0
            if kokaton.rect.bottom > stone.rect.top +5:
                if kokaton.rect.centerx <= stone.rect.centerx:
                    stone.vx = +2
                elif kokaton.rect.centerx >= stone.rect.centerx:
                    stone.vx = -2
                else:
                    stone.vx = +2
        
        # 風とこうかとんの当たり判定
        if len(pg.sprite.spritecollide(kokaton, ykazesl, False)) != 0:
            kokaton.vx = +1
        if len(pg.sprite.spritecollide(kokaton, ykazesr, False)) != 0:
            kokaton.vx = -1
        if len(pg.sprite.spritecollide(kokaton, tkazes, False)) != 0:
            kokaton.vy = -1

        # ピンとobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ypins, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ypins, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ypins, False, False).keys():
            tre.vy = 0
        
        # 竹とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ytks, False, True).keys():
            pass
        for wtr in pg.sprite.groupcollide(wtrs, ytks, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ytks, False, False).keys():
            tre.vy = 0
        
        # 床とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ysts, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, ysts, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, ysts, False, False).keys():
            tre.vy = 0
        
        # 足場とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, asis, False, False).keys():
            mgm.vy = 0
        for wtr in pg.sprite.groupcollide(wtrs, asis, False, False).keys():
            wtr.vy = 0
        for tre in pg.sprite.groupcollide(trs, asis, False, False).keys():
            tre.vy = 0
        
        # 左風とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ykazesl, False, False).keys():
            mgm.vx = +2
        for wtr in pg.sprite.groupcollide(wtrs, ykazesl, False, False).keys():
            wtr.vx = +2
        for tre in pg.sprite.groupcollide(trs, ykazesl, False, False).keys():
            tre.vx = +2
        
        # 右風とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, ykazesr, False, False).keys():
            mgm.vx = -2
        for wtr in pg.sprite.groupcollide(wtrs, ykazesr, False, False).keys():
            wtr.vx = -2
        for tre in pg.sprite.groupcollide(trs, ykazesr, False, False).keys():
            tre.vx = -2
        
        # 上風とobjの当たり判定
        for mgm in pg.sprite.groupcollide(mgms, tkazes, False, False).keys():
            mgm.vy = -2
        for wtr in pg.sprite.groupcollide(wtrs, tkazes, False, False).keys():
            wtr.vy = -2
        for tre in pg.sprite.groupcollide(trs, tkazes, False, False).keys():
            tre.vy = -2
        
        # 水とマグマの当たり判定 ... ステージごとに下においてある方を基準とする
        for mgm in pg.sprite.groupcollide(mgms, wtrs, True, True).keys():
            sixtones.add(Stone(mgm))
        
        # 宝とマグマと水で出来た石の当たり判定
        for tre in pg.sprite.groupcollide(trs, sixtones, False, False).keys():
            tre.vy = 0
        
        # ピンと石の当たり判定
        for stone in pg.sprite.groupcollide(sixtones, ypins, False, False).keys():
            stone.vy = 0
        
        # 石と足場の当たり判定
        for stone in pg.sprite.groupcollide(sixtones, asis, False, False).keys():
            stone.vy = 0

        # 石と竹の当たり判定
        if len(pg.sprite.groupcollide(sixtones, ytks, False, True)) != 0:
            pass

        # 石と床の当たり判定
        for stone in pg.sprite.groupcollide(sixtones, ysts, False, False).keys():
            stone.vy = 0
        
        # 縦のピンと横のピンの当たり判定 -> 縦ピンのy座標移動量を0にする
        for tpin in pg.sprite.groupcollide(tpins, ypins, False, False).keys():
            tpin.vy = 0
        
        # 横のピンと縦のピンの当たり判定 -> 横ピンのx座標移動量を0にする
        for ypin in pg.sprite.groupcollide(ypins, tpins, False, False).keys():
            ypin.vx = 0
        
        for stone in pg.sprite.groupcollide(sixtones, tkazes, False, True).keys():
            pass
        
        # マグマと宝物の当たり判定
        if len(pg.sprite.groupcollide(mgms, trs, False, True).values()) != 0:
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
        
        # こうかとんとマグマの当たり判定，ゲームオーバー
        if len(pg.sprite.spritecollide(kokaton, mgms, False)) != 0:
            game_stats = "gameover"
            kokaton.update(screen)
            kao.update(kokaton, screen)
            ysts.draw(screen)
            tsts.draw(screen)
            pg.display.update()
            time.sleep(2)
        
        # こうかとんと宝の当たり判定，クリアー！！
        if len(pg.sprite.spritecollide(kokaton, trs, True)) != 0:
            if len(trs) == 0:
                game_stats = "clear"
                kokaton.update(screen)
                kao.update(kokaton, screen)
                ysts.draw(screen)
                tsts.draw(screen)
                pg.display.update()
                time.sleep(2)

        if game_stats != None:
            break

        kokaton.update(screen)
        ypins.update()
        ypins.draw(screen)
        tpins.update()
        tpins.draw(screen)
        mgms.update()
        mgms.draw(screen)
        wtrs.update()
        wtrs.draw(screen)
        trs.update()
        trs.draw(screen)
        sixtones.update()
        sixtones.draw(screen)
        asis.draw(screen)
        ysts.draw(screen)
        tsts.draw(screen)
        ytks.draw(screen)
        cm_l.update(screen)
        cm_r.update(screen)
        nm_d.update(screen)
        ykazesl.update(countl, cm_l)
        ykazesr.update(countr, cm_r)
        ykazesl.draw(screen)
        ykazesr.draw(screen)
        tkazes.draw(screen)
        pg.display.update()
        clock.tick(60)

        if countl > 3:
            countl = 0
        if countr > 3:
            countr = 0
    
    while True:
        if game_stats == "gameover":
            go.update(screen)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "retire"
            if pg.mouse.get_pressed()[0]: # マウスの処理
                mouse_x, mouse_y = pg.mouse.get_pos()
                if (go.con_rect.topleft[0] <= mouse_x <= go.con_rect.bottomright[0]) and (go.con_rect.topleft[1] <= mouse_y <= go.con_rect.bottomright[1]):
                    return "continue"
                elif (go.ret_rect.topleft[0] <= mouse_x <= go.ret_rect.bottomright[0]) and (go.ret_rect.topleft[1] <= mouse_y <= go.ret_rect.bottomright[1]):
                    return "retire"
        
        elif game_stats == "clear":
            cl.update(screen)
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "retire"
            if pg.mouse.get_pressed()[0]: # マウスの処理
                mouse_x, mouse_y = pg.mouse.get_pos()
                if (cl.next_rect.topleft[0] <= mouse_x <= cl.next_rect.bottomright[0]) and (cl.next_rect.topleft[1] <= mouse_y <= cl.next_rect.bottomright[1]):
                    return "clear"
                elif (cl.con_rect.topleft[0] <= mouse_x <= cl.con_rect.bottomright[0]) and (cl.con_rect.topleft[1] <= mouse_y <= cl.con_rect.bottomright[1]):
                    return "continue"



if __name__=="__main__":
    pg.init()
    # ステージの変化とゲームオーバーなどの処理
    while True:
        GAME_STATS = None
        GAME_STATS = main(STAGE_NUM) # main関数内でreturnしてくる文字列を変数に格納する
        if GAME_STATS == "clear":
            STAGE_NUM += 1
            break
        elif GAME_STATS == "continue":
            continue
        elif GAME_STATS == "retire":
            pg.quit()
            sys.exit()
    
    while True:
        GAME_STATS = None
        GAME_STATS = main2(STAGE_NUM)
        if GAME_STATS == "clear":
            STAGE_NUM += 1
            break
        elif GAME_STATS == "continue":
            continue
        elif GAME_STATS == "retire":
            pg.quit()
            sys.exit()
    
    while True:
        GAME_STATS = None
        GAME_STATS = main3(STAGE_NUM)
        if GAME_STATS == "clear":
            STAGE_NUM += 1
            break
        elif GAME_STATS == "continue":
            continue
        elif GAME_STATS == "retire":
            pg.quit()
            sys.exit()
    
    while True:
        GAME_STATS = None
        GAME_STATS = main4(STAGE_NUM)
        if GAME_STATS == "clear":
            STAGE_NUM += 1
            break
        elif GAME_STATS == "continue":
            continue
        elif GAME_STATS == "retire":
            pg.quit()
            sys.exit()
    
    while True:
        GAME_STATS = None
        GAME_STATS = main5(STAGE_NUM) # main関数内でreturnしてくる文字列を変数に格納する
        if GAME_STATS == "clear":
            STAGE_NUM += 1
            break
        elif GAME_STATS == "continue":
            continue
        elif GAME_STATS == "retire":
            pg.quit()
            sys.exit()
    
    pg.quit()
    sys.exit()

