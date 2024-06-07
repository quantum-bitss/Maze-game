import pygame as pg


class Medicine(pg.sprite.Sprite):
    def __init__(self, incre_medi):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(r"../image/medicine.png")
        self.image = pg.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()  # rect对象
        self.increment = incre_medi


class SpeedUp(pg.sprite.Sprite):
    def __init__(self, incre_speed):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(r"../image/speedup.png")
        self.image = pg.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()  # rect对象
        self.increment = incre_speed


class SpeedDown(pg.sprite.Sprite):
    def __init__(self, dec_speed):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(r"../image/speeddown.jpg")
        self.image = pg.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()  # rect对象
        self.increment = dec_speed


class Gun(pg.sprite.Sprite):
    image = pg.transform.scale(pg.image.load(r"../image/gun.png"), (32, 32))  # 类属性

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = Gun.image
        self.rect = self.image.get_rect()  # rect对象
