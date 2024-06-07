import pygame
import numpy as np
import math


class Bullet(pygame.sprite.Sprite):  # 子弹类
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # 子弹射向不同方向的图像
        self.bullet_left = pygame.image.load(r"../image/bullet_left.png")
        self.bullet_right = pygame.image.load(r"../image/bullet_right.png")

        self.life = False  # 是否显示子弹
        self.speed = 2
        self.harm = 30
        self.direction = 1  # 1 为向右运动，-1为向左运动
        self.bullet = self.bullet_right
        self.rect = self.bullet.get_rect()
        self.direction = [0, 0]

    def update_image(self, direction):
        self.direction = direction
        if direction == 1:
            self.bullet = self.bullet_right
        if direction == -1:
            self.bullet = self.bullet_left

    def move_bullet(self, wall_group, bullet_group):
        self.rect = self.rect.move(self.speed * self.direction, 0)
        if self.rect.top < self.speed:
            self.life = False
        if self.rect.bottom > 768 - self.speed:
            self.life = False
        if self.rect.left < self.speed:
            self.life = False
        if self.rect.top > 768 - self.speed:
            self.life = False
        if pygame.sprite.spritecollide(self, wall_group, False, None):
            self.life = False
        if not self.life:
            bullet_group.remove(self)  # 删除子弹
        # if pygame.sprite.spritecollide(self, all_enemy_group, False, None):
        #     self.life = False

    def move_bullet_all_direc(self, wall_group, bullet_group):
        self.direction = np.array(self.direction)  # 转换为ndarray结构
        unit_vector = self.direction / np.linalg.norm(self.direction)
        movement_vector = unit_vector * self.speed
        self.rect = self.rect.move(movement_vector[0], movement_vector[1])
        if self.rect.top < 0 or self.rect.bottom > 768 or self.rect.left < 0 or self.rect.right > 1024:
            self.life = False
        if pygame.sprite.spritecollide(self, wall_group, False, None):
            self.life = False
        if not self.life:
            bullet_group.remove(self)  # 删除子弹

    def search_player(self, hero, wall_group, bullet_group):  # 弹幕追踪玩家
        direction = [hero.rect.centerx - self.rect.centerx, hero.rect.centery - self.rect.centery]
        length = (direction[0]**2+direction[1]**2)**0.5  # 求向量长度
        for i in range(0, 2):
            if direction[i] < 0:
                direction[i] = math.floor(direction[i] / length)
            else:
                direction[i] = math.ceil(direction[i] / length)
        self.rect = self.rect.move(direction[0], direction[1])  # 追踪玩家
        if self.rect.top < 0 or self.rect.bottom > 768 or self.rect.left < 0 or self.rect.right > 1024:
            self.life = False
        if pygame.sprite.spritecollide(self, wall_group, False, None):
            self.life = False
        if not self.life:
            bullet_group.remove(self)  # 删除子弹
