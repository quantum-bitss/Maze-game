import pygame
import math
import Bullet


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.boss_list_l = []
        self.boss_list_r = []
        self.boss_list_l.append(pygame.image.load(r"../image/knight/1.png"))
        self.boss_list_l.append(pygame.image.load(r"../image/knight/2.png"))
        self.boss_list_l.append(pygame.image.load(r"../image/knight/3.png"))
        self.boss_list_l.append(pygame.image.load(r"../image/knight/4.png"))
        self.boss_list_l.append(pygame.image.load(r"../image/knight/5.png"))
        self.boss_list_l.append(pygame.image.load(r"../image/knight/6.png"))
        self.boss_list_l.append(pygame.image.load(r"../image/knight/7.png"))
        self.boss_list_l.append(pygame.image.load(r"../image/knight/8.png"))
        self.boss_list_l.append(pygame.image.load(r"../image/knight/9.png"))
        self.boss_list_l.append(pygame.image.load(r"../image/knight/10.png"))
        self.boss_list_l.append(pygame.image.load(r"../image/knight/11.png"))
        self.boss_list_l.append(pygame.image.load(r"../image/knight/12.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/1r.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/2r.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/3r.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/4r.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/5r.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/6r.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/7r.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/8r.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/9r.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/10r.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/11r.png"))
        self.boss_list_r.append(pygame.image.load(r"../image/knight/12r.png"))
        self.boss_cur = self.boss_list_l[0]
        self.rect = self.boss_cur.get_rect()
        self.health = 1000
        self.speed = 2
        self.direction = -1
        self.birth_pos = (5, 5)

        # self.boss_bullet = Bullet.Bullet()
        # self.boss_bullet.image = pygame.image.load(r"../image/fire.png")
        # self.boss_bullet.harm = 20
        self.bullet_group = pygame.sprite.Group()
        directions = []
        num_directions = 16
        angle_increment = 360 / num_directions

        for i in range(num_directions):
            angle = math.radians(angle_increment * i)
            x = math.cos(angle)
            y = math.sin(angle)
            directions.append([x, y])

        for i in range(16):
            boss_bullet = Bullet.Bullet()
            boss_bullet.image = pygame.image.load(r"../image/fire.png")
            boss_bullet.harm = 20
            boss_bullet.direction = directions[i]
            self.bullet_group.add(boss_bullet)  # 装填子弹

    def born(self):
        self.rect.top = self.birth_pos[0] * 64
        self.rect.left = self.birth_pos[1] * 64

    def shoot(self, bullet_group):
        # directions = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
        # i = 0
        for bullet in self.bullet_group:
            bullet.life = True
            bullet_group.add(bullet)
            # direction_vector = np.array(directions[i])
            # i += 1
            bullet.rect.left = self.rect.centerx - 32
            bullet.rect.top = self.rect.centery
            # bullet.move_bullet_all_direc(direction_vector, wall_group)

    def track_player(self, player, wall_group):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:  # 防止除以零
            unit_vector = (dx / distance, dy / distance)
            movement_vector = (unit_vector[0] * self.speed, unit_vector[1] * self.speed)
            original_rect = self.rect

            self.rect = self.rect.move(movement_vector[0], 0)
            if pygame.sprite.spritecollide(self, wall_group, False, None):
                self.rect = original_rect
                self.rect = self.rect.move(0, movement_vector[1])
                if pygame.sprite.spritecollide(self, wall_group, False, None):
                    self.rect = original_rect

            self.rect = self.rect.move(0, movement_vector[1])
            if pygame.sprite.spritecollide(self, wall_group, False, None):
                self.rect = original_rect
                self.rect = self.rect.move(movement_vector[0], 0)
                if pygame.sprite.spritecollide(self, wall_group, False, None):
                    self.rect = original_rect

    def charge_player(self, player, wall_group, charge_speed=10, knockback_distance=64):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:  # 防止除以零
            unit_vector = (dx / distance, dy / distance)
            movement_vector = (unit_vector[0] * charge_speed, unit_vector[1] * charge_speed)
            original_rect = self.rect

            self.rect = self.rect.move(movement_vector[0], movement_vector[1])
            if pygame.sprite.spritecollide(self, wall_group, False, None):
                self.rect = original_rect
                self.rect = self.rect.move(-movement_vector[0], -movement_vector[1])

            # 玩家击退
            knockback_vector = (unit_vector[0] * knockback_distance, unit_vector[1] * knockback_distance)
            original_player_rect = player.rect
            player.rect = player.rect.move(knockback_vector[0], knockback_vector[1])

            if pygame.sprite.spritecollide(player, wall_group, False, None):
                player.rect = original_player_rect

            # 可以在这里添加更多的冲撞效果，如造成伤害等
            player.health -= 20


class Treasure(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(r'../image/treasure2.png')
        self.life = False
        self.rect = self.image.get_rect()
