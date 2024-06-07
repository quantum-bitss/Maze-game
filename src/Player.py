import pygame
import Bullet


def calculate_distance(monster, player):
    return ((monster.rect.centerx - player.rect.centerx) ** 2 + (monster.rect.centery - player.rect.centery) ** 2)**0.5


class Player(pygame.sprite.Sprite):
    sword_left_image_list = []
    sword_right_image_list = []
    for i in range(0, 22):
        sword_left_image_list.append(pygame.transform.scale(
            pygame.image.load(r"../image/sword/left sword " + str(i) + r".png"), (60, 60)))
        sword_right_image_list.append(pygame.transform.scale(
            pygame.image.load(r"../image/sword/right sword " + str(i) + r".png"), (60, 60)))

    def __init__(self, x, y, health=100, speed=2, weapon=0, own_gun=False):
        pygame.sprite.Sprite.__init__(self)
        self.hero = pygame.image.load(r"../image/hero.png")  # 人物素材
        # self.sword_left_image = pygame.transform.scale(pygame.image.load(r"../image/sword/left sword.png"), (48, 24))
        self.sword_right_image = pygame.transform.scale(pygame.image.load(r"../image/sword/right sword.png"), (48, 24))
        # 运动中的几个子形态
        hero_l0 = self.hero.subsurface((0, 48), (32, 48))
        hero_l1 = self.hero.subsurface((32, 48), (32, 48))
        hero_l2 = self.hero.subsurface((64, 48), (32, 48))
        hero_l3 = self.hero.subsurface((96, 48), (32, 48))
        self.hero_l = [hero_l0, hero_l1, hero_l2, hero_l3]

        hero_r0 = self.hero.subsurface((0, 96), (32, 48))
        hero_r1 = self.hero.subsurface((32, 96), (32, 48))
        hero_r2 = self.hero.subsurface((64, 96), (32, 48))
        hero_r3 = self.hero.subsurface((96, 96), (32, 48))
        self.hero_r = [hero_r0, hero_r1, hero_r2, hero_r3]

        self.image = self.hero_r[0]
        self.rect = self.image.get_rect()
        self.rect.top = x * 64  # 64是cell_size
        self.rect.left = y * 64
        self.rect.width = 32
        self.rect.height = 48
        self.bullet_number = 3  # 弹夹为3颗子弹
        self.health = health
        self.speed = speed
        self.life = True  # 是否存活
        self.bullet_list = [Bullet.Bullet() for x in range(self.bullet_number)]  # 最多同时存在3个子弹
        self.bullet_cooling = False

        # self.attack_image_list = Player.sword_right_image_list
        # self.attack_list = []
        self.attack_list_index = -1
        self.attack_cooling = False  # 近战冷却
        self.weapon = weapon  # 0为近战，1为远程
        self.own_gun = own_gun  # 默认没有枪，用于判断是否可以切换武器

    def initialization(self, x, y):
        self.rect.top = x * 64  # 64是cell_size
        self.rect.left = y * 64

    def move(self, dir_x, dir_y, stride):
        self.rect = self.rect.move(self.speed * dir_x * stride, self.speed * dir_y * stride)

    def is_left(self):
        return self.image in self.hero_l

    def is_right(self):
        return self.image in self.hero_r

    def collide(self, dir_x, dir_y, wall_group, char_group):  # 返回true表示发生碰撞
        # 不管是否碰撞都应该可以转向
        if dir_x > 0:
            self.image = self.hero_r[0]
        elif dir_x < 0:
            self.image = self.hero_l[0]
        self.rect = self.rect.move(self.speed * dir_x, self.speed * dir_y)
        collide = False
        if dir_x == 0 and dir_y == -1:  # 向上走，检测上边界
            if self.rect.top - self.speed < 0:
                collide = True
        if dir_x == 1 and dir_y == 0:  # 向右走，检测右边界
            if self.rect.right + self.speed > 768:
                collide = True
        if dir_x == 0 and dir_y == 1:  # 向下走，检测下边界
            if self.rect.bottom + self.speed > 768:
                collide = True
        if dir_x == -1 and dir_y == 0:  # 向左走，检测左边界
            if self.rect.left - self.speed < 0:
                collide = True
        if pygame.sprite.spritecollide(self, wall_group, False, None):
            collide = True
        if pygame.sprite.spritecollide(self, char_group, False, None):
            collide = True
        self.rect = self.rect.move(self.speed * -dir_x, self.speed * -dir_y)  # 碰撞检测函数不应该有移动作用
        if collide:
            return True
        return False

    def shoot(self):
        for bullet in self.bullet_list:
            if not bullet.life:  # 有空闲的子弹则可以射击
                self.bullet_number -= 1
                bullet.life = True
                # 设置当前子弹的初始位置
                if self.is_left():
                    bullet.direction = -1
                    bullet.image = bullet.bullet_left
                    bullet.rect.left = self.rect.left - self.rect.width / 3
                if self.is_right():
                    bullet.direction = 1
                    bullet.image = bullet.bullet_right
                    bullet.rect.left = self.rect.left + self.rect.width / 3
                bullet.rect.top = self.rect.top + self.rect.height / 3
                break

    def self_attack(self, enemy_group, bullet_group, speed_down_group):
        # self.attack_list.clear()
        for each in enemy_group:  # 对每个敌人进行判断
            if calculate_distance(each, self) <= 100:  # 判断方式要改
                if self.is_left() and each.rect.centerx-self.rect.centerx < 0 or\
                        self.is_right() and each.rect.centerx-self.rect.centerx > 0:
                    each.health -= 15  # 近战伤害为15
        for each in bullet_group:
            if calculate_distance(each, self) <= 100:
                if self.is_left() and each.rect.centerx - self.rect.centerx < 0 or \
                        self.is_right() and each.rect.centerx - self.rect.centerx > 0:
                    each.life = False  # 砍弹幕
        for each in speed_down_group:
            if calculate_distance(each, self) <= 100:
                if self.is_left() and each.rect.centerx - self.rect.centerx < 0 or \
                        self.is_right() and each.rect.centerx - self.rect.centerx > 0:
                    speed_down_group.remove(each)  # 砍掉蛛网
        self.attack_list_index = 0
