import pygame as pg
import sys
import random
import pygame.sprite
import pygame.mask
import math
import Maze
import Player
import Monster
import Boss
import Prop


def calculate_distance(monster, player):
    return math.sqrt((monster.rect.centerx - player.rect.centerx) ** 2 +
                     (monster.rect.centery - player.rect.centery) ** 2)


def attack_check(bullet, char):
    if pygame.sprite.collide_rect(bullet, char) and bullet.life:
        char.health -= bullet.harm
        bullet.life = False


class TombRaider:  # 定义一个游戏类，方便管理
    def __init__(self):
        # 游戏素材
        self.screen = pg.display.set_mode((768, 768))  # 设窗口大小
        pg.display.set_caption("Tomb Raider")  # 改窗口标题
        self.clock = pg.time.Clock()
        self.start_image = pg.image.load(r"../image/start.jpg")
        self.lose_image = pg.image.load(r"../image/lose.jpg")
        self.background_image = pg.image.load(r"../image/background.jpg")
        self.victory_image = pg.image.load(r"../image/victory.jpg")

        # 游戏状态
        self.start = True

        # 游戏实体
        self.hero = None
        self.game_map = None
        self.all_char_group = pg.sprite.Group()
        self.all_enemy_group = pg.sprite.Group()
        self.ghost_group = pg.sprite.Group()
        self.spider_group = pg.sprite.Group()
        self.all_enemy_bullet_group = pg.sprite.Group()

        # 游戏事件
        self.FLAMEUPDATE = pg.constants.USEREVENT
        self.MYBULLETCOOLINGEVENT = pg.constants.USEREVENT + 1
        self.ENEMYBULLETCOOLINGEVENT = pg.constants.USEREVENT + 2
        self.MAINLOOP = pg.constants.USEREVENT + 3
        self.BULLETMOVE = pg.constants.USEREVENT + 4
        self.GHOSTMOVE = pg.constants.USEREVENT + 5
        self.ATTACKCHECK = pg.constants.USEREVENT + 6
        self.BULLETUPDATE = pg.constants.USEREVENT + 7
        self.WALKALONGPATH = pg.constants.USEREVENT + 8
        self.LIFECHECK = pg.constants.USEREVENT + 9
        self.ATTACKCOOLINGEVENT = pg.constants.USEREVENT + 10  # 玩家近战冷却
        pg.time.set_timer(self.MYBULLETCOOLINGEVENT, 200)  # 每200毫秒发生一次my bullet cooling event
        pg.time.set_timer(self.ENEMYBULLETCOOLINGEVENT, 1000)  # 每1000毫秒发生一次敌人子弹冷却
        pg.time.set_timer(self.FLAMEUPDATE, 10)  # 每10毫秒更新一次
        pg.time.set_timer(self.MAINLOOP, 10)  # 每10毫秒更新一次
        pg.time.set_timer(self.BULLETMOVE, 4)
        pg.time.set_timer(self.GHOSTMOVE, 10)
        pg.time.set_timer(self.ATTACKCHECK, 10)
        pg.time.set_timer(self.BULLETUPDATE, 2000)  # 每2秒获得3颗子弹
        pg.time.set_timer(self.WALKALONGPATH, 8)  # 8毫秒走1步
        pg.time.set_timer(self.LIFECHECK, 20)  # 20毫秒检查一次人物是否存活
        pg.time.set_timer(self.ATTACKCOOLINGEVENT, 1000)  # 每秒1刀

        self.frame_index_hero = [0, 0]
        self.frame_counter_hero = [0, 0]
        self.frame_index_flame = 0
        self.frame_counter_flame = 0
        self.frame_index_ghost = [0, 0]
        self.frame_counter_ghost = [0, 0]
        self.frame_index_spider = [0, 0]
        self.frame_counter_spider = [0, 0]
        self.frame_index_boss = [0, 0]
        self.frame_counter_boss = [0, 0]
        self.frame_rate = 50

    def render(self):  # 画面渲染
        self.screen.blit(self.background_image, (0, 0))  # 背景图
        for each in self.game_map.flagGroup:  # 旗帜
            self.screen.blit(each.image, each.rect)
        for each in self.game_map.wallGroup:  # 墙
            self.screen.blit(each.image, each.rect)
        for each in self.game_map.medicine_group:  # 医药包
            self.screen.blit(each.image, each.rect)
        for each in self.game_map.speed_up_group:  # 加速
            self.screen.blit(each.image, each.rect)
        for each in self.game_map.speed_down_group:  # 减速
            self.screen.blit(each.image, each.rect)
        for each in self.game_map.gun_group:  # 枪
            self.screen.blit(each.image, each.rect)
        if self.hero.attack_list_index >= 0:  # 近战攻击图像
            if self.hero.is_right():
                self.screen.blit(Player.Player.sword_right_image_list[self.hero.attack_list_index],
                                 (self.hero.rect.centerx,
                                  self.hero.rect.centery - 45 + (21 - self.hero.attack_list_index) * 2))
            if self.hero.is_left():
                self.screen.blit(Player.Player.sword_left_image_list[self.hero.attack_list_index],
                                 (self.hero.rect.centerx - 60,
                                  self.hero.rect.centery - 45 + (21 - self.hero.attack_list_index) * 2))
            self.hero.attack_list_index += 1
            if self.hero.attack_list_index >= 22:  # 超出范围
                self.hero.attack_list_index = -1  # 结束渲染
        font = pg.font.SysFont('Times', 30)  # 设置字体
        font.bold = True  # 黑体字
        text = font.render('Health: ' + str(self.hero.health), True, (255, 221, 85))
        self.screen.blit(text, (50, 25))  # 展示文本
        if self.hero.weapon == 0:  # 近战
            self.screen.blit(self.hero.sword_right_image, (250, 25))
        else:
            self.screen.blit(Prop.Gun.image, (250, 25))

    def is_player_at_portal(self, portal):
        player_center = self.hero.rect.center
        portal_center = portal.rect.center
        distance = ((player_center[0] - portal_center[0]) ** 2 + (player_center[1] - portal_center[1]) ** 2) ** 0.5
        return distance <= 30

    def initialization(self, number_of_monsters, player_health=100, player_speed=2, player_weapon=0, player_own_gun=False):
        # 实例化地图对象, 用关键字传值方便查看
        self.game_map = Maze.Map(width=12, height=12, screen_width=768, screen_height=768,
                                 map_width=768, map_height=768, left_distance=0, top_distance=0)
        Maze.self_checking_generate_maze(self.game_map, number_of_monsters - 1)
        self.game_map.create_portal()  # 初始化传送门
        self.all_char_group = pg.sprite.Group()  # 所有对象精灵组
        self.all_enemy_group = pg.sprite.Group()  # 所有怪物精灵组
        self.ghost_group = pg.sprite.Group()  # 幽灵精灵组
        self.spider_group = pg.sprite.Group()  # 蜘蛛精灵组
        self.hero = Player.Player(self.game_map.start_pos[0], self.game_map.start_pos[1],
                                  player_health, player_speed, player_weapon, player_own_gun)  # 初始位置
        for i in range(1, number_of_monsters):
            ghost = Monster.Monster(kind=1)
            spider = Monster.Monster(kind=2)
            self.all_char_group.add(ghost)
            self.all_char_group.add(spider)
            self.all_enemy_group.add(ghost)
            self.all_enemy_group.add(spider)
            self.ghost_group.add(ghost)
            self.spider_group.add(spider)

        # 初始化怪物出生坐标
        birth_list = self.game_map.monster_birth["Ghost"]
        birth_list_spider = self.game_map.monster_birth["Spider"]
        i = 0
        for each in self.ghost_group:
            each.birth_pos(birth_list[i][0], birth_list[i][1])
            i += 1
        i = 0
        for each in self.spider_group:
            each.birth_pos(birth_list_spider[i][0], birth_list_spider[i][1])
            i += 1

    def pick_up_props_check(self):
        for prop in self.game_map.medicine_group:
            if self.is_player_at_portal(prop):
                self.game_map.medicine_group.remove(prop)
                self.hero.health += 30
                self.hero.health = min(100, self.hero.health)  # 100为英雄生命值上限
        for prop in self.game_map.speed_up_group:
            if self.is_player_at_portal(prop):
                self.game_map.speed_up_group.remove(prop)
                self.hero.speed += 1
        for prop in self.game_map.gun_group:
            if self.is_player_at_portal(prop):
                self.game_map.gun_group.remove(prop)
                self.hero.own_gun = True
                self.hero.weapon = 1  # 切为远程，可切换回近战

    def player_behavior(self, keys, movable, moving, loop):
        if keys[pg.K_w] == 1 or keys[pg.K_UP] == 1:  # 向上走
            if self.hero.collide(0, -1, self.game_map.wallGroup, self.all_char_group):  # True表示碰撞
                movable = False
            if movable:
                self.hero.move(0, -1, 1)
            movable = True
            moving = True

        if keys[pg.K_d] == 1 or keys[pg.K_RIGHT] == 1:  # 向右走
            if self.hero.collide(1, 0, self.game_map.wallGroup, self.all_char_group):  # True表示碰撞
                movable = False
            if movable:
                self.hero.move(1, 0, 1)
            movable = True
            moving = True

        if keys[pg.K_s] == 1 or keys[pg.K_DOWN] == 1:  # 向下走
            if self.hero.collide(0, 1, self.game_map.wallGroup, self.all_char_group):  # True表示碰撞
                movable = False
            if movable:
                self.hero.move(0, 1, 1)
            movable = True
            moving = True

        if keys[pg.K_a] == 1 or keys[pg.K_LEFT] == 1:  # 向左走
            if self.hero.collide(-1, 0, self.game_map.wallGroup, self.all_char_group):  # True表示碰撞
                movable = False
            if movable:
                self.hero.move(-1, 0, 1)
            movable = True
            moving = True

        if keys[pg.K_j]:
            self.pick_up_props_check()
            if self.game_map.portal.life and self.is_player_at_portal(self.game_map.portal):
                loop = False
            if self.hero.weapon == 1:  # 武器为枪时
                if self.hero.bullet_number > 0:  # 子弹打完暂时不能打
                    # 这里子弹冷却意味着最大攻速限制，具体攻速由自定义事件子弹冷却的频率来定义
                    if self.hero.life and not self.hero.bullet_cooling:  # 需要一个子弹对象池，不然只能射出一个子弹
                        self.hero.shoot()
                        self.hero.bullet_cooling = True
            else:  # 近战伤害判断
                if not self.hero.attack_cooling:  # 不在冷却中可以攻击
                    self.hero.self_attack(self.all_enemy_group,
                                          self.all_enemy_bullet_group,
                                          self.game_map.speed_down_group)
                    self.hero.attack_cooling = True

        for prop in self.game_map.speed_down_group:
            if self.is_player_at_portal(prop):
                self.game_map.speed_down_group.remove(prop)
                self.hero.speed -= 1
                if self.hero.speed <= 0:
                    self.hero.speed = 1  # 最低为1
        return movable, moving, loop

    def player_update(self, moving):
        # 人物运动图像更新
        if moving and self.hero.is_left():
            self.frame_counter_hero[0] += 5
            if self.frame_counter_hero[0] >= self.frame_rate:
                self.frame_counter_hero[0] = 0
                self.frame_index_hero[0] = (self.frame_index_hero[0] + 1) % len(self.hero.hero_l)
            self.hero.image = self.hero.hero_l[self.frame_index_hero[0]]

        if moving and self.hero.is_right():
            self.frame_counter_hero[1] += 5
            if self.frame_counter_hero[1] >= self.frame_rate:
                self.frame_counter_hero[1] = 0
                self.frame_index_hero[0] = (self.frame_index_hero[0] + 1) % len(self.hero.hero_r)
            self.hero.image = self.hero.hero_r[self.frame_index_hero[0]]
        # 人物存活判断
        if self.hero.health > 0:
            self.screen.blit(self.hero.image, self.hero.rect)
        else:
            self.hero.life = False  # 人物死亡，触发死亡事件

    def monster_behavior(self):
        # 怪物幽灵行为判定
        for each in self.ghost_group:
            distance = calculate_distance(each, self.hero)
            if distance >= 64 * 2.2:
                self.all_char_group.remove(each)
                each.wander_around_current_position(self.game_map.wallGroup, self.all_char_group)
                self.all_char_group.add(each)
            else:
                if each.rect.x - self.hero.rect.x > 0:
                    each.direction = -1
                else:
                    each.direction = 1

            if each.health <= 0:
                each.life = False  # 检查血量
                self.ghost_group.remove(each)
                self.all_enemy_group.remove(each)
                self.all_char_group.remove(each)

            if each.direction < 0 and each.life:
                self.frame_counter_ghost[0] += 5
                # print(frame_counter_ghost[0])
                if self.frame_counter_ghost[0] >= self.frame_rate * 7:
                    self.frame_counter_ghost[0] = 0
                    self.frame_index_ghost[0] = (self.frame_index_ghost[0] + 1) % len(each.monster_list_l)
                each.monster_cur = each.monster_list_l[self.frame_index_ghost[0]]
                self.screen.blit(each.monster_cur, each.rect)
            if each.direction > 0 and each.life:
                self.frame_counter_ghost[1] += 5
                if self.frame_counter_ghost[1] >= self.frame_rate * 7:
                    self.frame_counter_ghost[1] = 0
                    self.frame_index_ghost[0] = (self.frame_index_ghost[0] + 1) % len(each.monster_list_r)
                each.monster_cur = each.monster_list_r[self.frame_index_ghost[0]]
                self.screen.blit(each.monster_cur, each.rect)

        # 怪物蜘蛛行为判定
        for each in self.spider_group:
            if not each.attack_cooling:  # 不在攻击冷却时才能行动
                distance = calculate_distance(each, self.hero)
                if distance >= 64 * 2.2 and not each.walking:  # 没有在寻路的时候才能游荡
                    self.all_char_group.remove(each)
                    each.wander_around_current_position(self.game_map.wallGroup, self.all_char_group)
                    self.all_char_group.add(each)
                else:
                    # 改变怪物朝向
                    if each.rect.x - self.hero.rect.x > 0:
                        each.direction = -1
                    else:
                        each.direction = 1
                    if not each.walking:  # 不处于走路状态时寻路
                        self.all_char_group.remove(each)  # 先将自己从碰撞判定对象中移除
                        each.path_finding(self.hero, self.game_map.wallGroup, self.all_char_group)
                        self.all_char_group.add(each)

            if each.health <= 0:
                each.life = False  # 检查血量
                self.spider_group.remove(each)
                self.all_enemy_group.remove(each)
                self.all_char_group.remove(each)
            # 怪物运动图像更新
            if each.direction < 0 and each.life:
                self.frame_counter_spider[0] += 5
                if self.frame_counter_spider[0] >= self.frame_rate * 5:
                    self.frame_counter_spider[0] = 0
                    self.frame_index_spider[0] = (self.frame_index_spider[0] + 1) % len(each.monster_list_l)
                each.monster_cur = each.monster_list_l[self.frame_index_spider[0]]
                self.screen.blit(each.monster_cur, each.rect)
            if each.direction > 0 and each.life:
                self.frame_counter_spider[1] += 5
                if self.frame_counter_spider[1] >= self.frame_rate * 5:
                    self.frame_counter_spider[1] = 0
                    self.frame_index_spider[0] = (self.frame_index_spider[0] + 1) % len(each.monster_list_r)
                each.monster_cur = each.monster_list_r[self.frame_index_spider[0]]
                self.screen.blit(each.monster_cur, each.rect)

    def constant_event_check(self, event):
        if event.type == pg.QUIT:  # 右上角关闭游戏
            pg.quit()
            sys.exit()

        if event.type == self.FLAMEUPDATE:  # 火焰动态效果
            for each in self.game_map.flameGroup:
                self.frame_counter_flame += 1
                if self.frame_counter_flame >= self.frame_rate * 5:
                    self.frame_counter_flame = 0
                    self.frame_index_flame = (self.frame_index_flame + 1) % len(each.flame_list)
                self.screen.blit(each.flame_list[self.frame_index_flame], each.rect)

        if event.type == self.MYBULLETCOOLINGEVENT:  # 人物子弹冷却
            self.hero.bullet_cooling = False

        if event.type == self.ATTACKCOOLINGEVENT:  # 人物自身攻击冷却
            self.hero.attack_cooling = False
            for each in self.spider_group:  # 蜘蛛攻击冷却
                if each.attack_cooling:
                    each.attack_cooling = False

        if event.type == self.BULLETUPDATE:  # 人物弹夹填充
            self.hero.bullet_number = 3

        if event.type == self.LIFECHECK:  # 检测人物状态
            if self.hero.health <= 0:
                self.hero.life = False
                return False
        return True

    def monster_loop(self):
        moving, movable, loop = False, True, True
        while loop:
            for event in pg.event.get():
                loop = self.constant_event_check(event)  # 常规事件
                if len(self.ghost_group) == 0 and len(self.spider_group) == 0:
                    self.game_map.portal.life = True  # 设为存在
                    self.screen.blit(self.game_map.portal.image, self.game_map.portal.rect)
                    # if self.is_player_at_portal(self.game_map.portal):
                    #     loop = False
                if event.type == self.MAINLOOP:  # 游戏主循环
                    pressed_keys = pg.key.get_pressed()
                    movable, moving, loop = self.player_behavior(pressed_keys, movable, moving, loop)
                    if not loop:
                        break
                    self.render()  # 地图基本设施
                    self.player_update(moving)
                    self.monster_behavior()

                if event.type == pg.KEYDOWN:  # 切换武器的判定
                    if event.key == pg.K_q:
                        if self.hero.own_gun:  # 有枪才能切换武器
                            self.hero.weapon += 1
                            self.hero.weapon %= 2  # 在0和1之间切换

                if event.type == self.ENEMYBULLETCOOLINGEVENT:  # 怪物子弹冷却
                    for each in self.ghost_group:
                        distance = calculate_distance(each, self.hero)
                        if distance < 64 * 2.2:
                            if abs(each.rect.y - self.hero.rect.y) < 64 and (not each.monster_bullet.life):
                                each.shoot(self.all_enemy_bullet_group)

                if event.type == self.BULLETMOVE:  # 更新子弹位置
                    for bullet in self.hero.bullet_list:
                        if bullet.life and self.hero.health > 0:
                            bullet.move_bullet(self.game_map.wallGroup, self.all_enemy_bullet_group)
                            self.screen.blit(bullet.image, bullet.rect)
                    for each in self.all_enemy_group:  # 更新所有怪物的弹幕
                        if each.monster_bullet.life and each.health > 0:
                            each.monster_bullet.move_bullet(self.game_map.wallGroup, self.all_enemy_bullet_group)
                            self.screen.blit(each.monster_bullet.image, each.monster_bullet.rect)

                if event.type == self.ATTACKCHECK:  # 人物和怪物攻击判定(仅子弹，无近战)
                    for each in self.all_enemy_group:
                        for bullet in self.hero.bullet_list:
                            attack_check(bullet, each)
                    for each in self.all_enemy_group:
                        attack_check(each.monster_bullet, self.hero)

                if event.type == self.WALKALONGPATH:  # 蜘蛛自动寻路
                    for each in self.spider_group:
                        if each.life and each.walking and not each.attack_cooling:
                            self.all_char_group.add(self.hero)
                            self.all_char_group.remove(each)
                            each.walk_along_path(self.game_map.wallGroup, self.all_char_group, self.hero)
                            self.all_char_group.add(each)
                            self.all_char_group.remove(self.hero)
                moving = False
            pg.display.update()  # 刷新页面

    def boss_loop(self):
        # level2 结束，进入boss关卡
        pg.time.set_timer(self.ENEMYBULLETCOOLINGEVENT, 1200)  # 重设怪物子弹冷却时间
        self.all_char_group.empty()
        self.all_enemy_group.empty()
        self.ghost_group.empty()
        self.spider_group.empty()

        self.game_map.map = [[0 for _ in range(12)] for _a in range(12)]
        self.game_map.wallGroup.empty()
        self.game_map.flagGroup.empty()
        self.game_map.flameGroup.empty()
        self.game_map.medicine_group.empty()
        self.game_map.speed_up_group.empty()
        self.game_map.speed_down_group.empty()
        # 绘制boss关卡地图
        for i in range(12):  # 将四周围起来
            self.game_map.map[0][i] = 1
            self.game_map.map[11][i] = 1
            self.game_map.map[i][0] = 1
            self.game_map.map[i][11] = 1
        self.game_map.map[6][3] = 1
        self.game_map.map[6][9] = 1  # 随便设几个掩体
        self.game_map.map[1][2] = 1
        self.game_map.map[10][8] = 1
        self.game_map.map[5][3] = 1
        self.game_map.map[5][9] = 1
        self.game_map.map[7][8] = 1
        self.game_map.map[1][1] = 11
        self.game_map.map[10][1] = 11
        self.game_map.map[1][10] = 11
        self.game_map.map[10][10] = 11

        start_row = random.choice(range(1, 10))  # 随机选取最终出生点
        self.game_map.map[start_row][0] = 8
        self.game_map.draw_map()

        self.hero.initialization(start_row, 0)
        boss = Boss.Boss()
        self.all_enemy_group.add(boss)
        boss.born()
        treasure = Boss.Treasure()
        shooting = True

        moving, movable, loop = False, True, True
        while loop:
            for event in pg.event.get():
                loop = self.constant_event_check(event)  # 常规事件
                if treasure.life and self.is_player_at_portal(treasure):
                    loop = False
                if event.type == self.MAINLOOP:  # 游戏主循环
                    pressed_keys = pg.key.get_pressed()
                    movable, moving, loop = self.player_behavior(pressed_keys, movable, moving, loop)
                    self.render()  # 渲染地图基本部件
                    self.player_update(moving)

                    # Boss行为逻辑
                    if boss.health <= 0:
                        treasure.life = True
                        treasure.rect.left = boss.rect.centerx - 32
                        treasure.rect.top = boss.rect.centery
                    elif boss.health >= 500:
                        shooting = True
                    elif 500 > boss.health > 0:
                        shooting = False
                        distance_to_hero = calculate_distance(boss, self.hero)
                        if distance_to_hero > 70:
                            boss.track_player(self.hero, self.game_map.wallGroup)
                        else:
                            boss.charge_player(self.hero, self.game_map.wallGroup)
                    # self.player_update(moving)

                    # boss图像更新
                    if self.hero.rect.left <= boss.rect.left:
                        self.frame_counter_boss[0] += 5  # 1
                        if self.frame_counter_boss[0] >= self.frame_rate:
                            self.frame_counter_boss[0] = 0
                            self.frame_index_boss[0] = (self.frame_index_boss[0] + 1) % len(boss.boss_list_l)
                        boss.boss_cur = boss.boss_list_l[self.frame_index_boss[0]]
                    if self.hero.rect.left > boss.rect.left:
                        self.frame_counter_boss[1] += 5  # 1
                        if self.frame_counter_boss[1] >= self.frame_rate:
                            self.frame_counter_boss[1] = 0
                            self.frame_index_boss[0] = (self.frame_index_boss[0] + 1) % len(boss.boss_list_r)
                        boss.boss_cur = boss.boss_list_r[self.frame_index_boss[0]]

                    # boss血量判断
                    if boss.health > 0:
                        self.screen.blit(boss.boss_cur, boss.rect)
                    if treasure.life:
                        self.screen.blit(treasure.image, treasure.rect)

                if event.type == pg.KEYDOWN:  # 切换武器的判定
                    if event.key == pg.K_q:
                        if self.hero.own_gun:  # 有枪才能切换武器
                            self.hero.weapon += 1
                            self.hero.weapon %= 2  # 在0和1之间切换

                # 怪物子弹冷却
                if event.type == self.ENEMYBULLETCOOLINGEVENT:
                    if shooting:
                        distance = calculate_distance(boss, self.hero)
                        if distance < 320:
                            boss.shoot(self.all_enemy_bullet_group)

                # 更新所有存在的子弹的位置
                if event.type == self.BULLETMOVE:
                    for bullet in self.hero.bullet_list:
                        if bullet.life and self.hero.health > 0:
                            bullet.move_bullet(self.game_map.wallGroup, self.all_enemy_bullet_group)
                            self.screen.blit(bullet.image, bullet.rect)
                    for bullet in boss.bullet_group:
                        if bullet.life and boss.health > 0:
                            if calculate_distance(bullet, self.hero) <= 100:  # 距离100以内弹幕追踪玩家
                                bullet.search_player(self.hero, self.game_map.wallGroup, self.all_enemy_bullet_group)
                                self.screen.blit(bullet.image, bullet.rect)
                            else:
                                bullet.move_bullet_all_direc(self.game_map.wallGroup, self.all_enemy_bullet_group)
                                self.screen.blit(bullet.image, bullet.rect)

                # 攻击判定
                if event.type == self.ATTACKCHECK:
                    for bullet in self.hero.bullet_list:
                        attack_check(bullet, boss)
                    if shooting:
                        for bullet in boss.bullet_group:
                            attack_check(bullet, self.hero)
                moving = False
            pg.display.update()  # 刷新页面

    def lose_loop(self):
        self.game_map.flameGroup.empty()
        self.game_map.wallGroup.empty()
        self.game_map.flagGroup.empty()
        self.all_char_group.empty()
        self.all_enemy_group.empty()
        self.ghost_group.empty()
        self.spider_group.empty()
        self.screen.blit(self.lose_image, (0, 0))
        font = pg.font.SysFont('Times', 30)  # 设置字体
        font.bold = True  # 黑体字
        self.screen.blit(font.render('You Lose!', True, (166, 226, 46)), (100, 0))
        self.screen.blit(font.render('Click anywhere to restart.', True, (166, 226, 46)), (300, 0))
        pg.display.update()
        loop = True
        while loop:
            for event in pg.event.get():
                if event.type == pg.QUIT:  # 右上角关闭游戏
                    pg.quit()
                    sys.exit()

                if event.type == pg.MOUSEBUTTONDOWN:
                    self.start = True
                    loop = False
            self.clock.tick(30)

    def victory_loop(self):
        self.screen.blit(self.victory_image, (0, 0))
        font = pg.font.SysFont('Times', 50)  # 设置字体
        font.bold = True  # 黑体字
        text = font.render('You Won!', True, (146, 0, 0))  # 参数分别为 文本内容，是否抗锯齿，字体颜色
        self.screen.blit(text, (280, 280))  # 展示文本
        pg.display.update()
        loop = True
        while loop:
            for event in pg.event.get():
                if event.type == pg.QUIT:  # 右上角关闭游戏
                    pg.quit()
                    sys.exit()

                if event.type == pg.MOUSEBUTTONDOWN:
                    self.start = True
                    loop = False
            self.clock.tick(30)

    def game_start(self):
        pg.init()
        self.screen.blit(self.start_image, (0, 0))
        font = pg.font.SysFont('Times', 30)  # 设置字体
        font.bold = True  # 黑体字
        # render参数分别为 文本内容，是否抗锯齿，字体颜色
        self.screen.blit(font.render('Click anywhere to start', True, (255, 221, 85)), (350, 700))
        self.screen.blit(font.render('helps', True, (255, 221, 85)), pg.Rect((650, 0, 50, 50)))
        pg.display.update()  # 刷新页面

        start_loop, show_help = True, False
        while start_loop:
            for event in pg.event.get():
                if event.type == pg.QUIT:  # 右上角关闭游戏
                    pg.quit()
                    sys.exit()

                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_position = pg.mouse.get_pos()
                    if 650 < mouse_position[0] < 700 and 0 < mouse_position[1] < 50:
                        if not show_help:
                            show_help = True
                            self.screen.blit(self.start_image, (0, 0))
                            self.screen.blit(font.render('Press J to pick up props', True, (255, 221, 85)), (200, 500))
                            self.screen.blit(font.render('Press Q to switch weapon', True, (255, 221, 85)), (200, 550))
                            self.screen.blit(font.render('Click anywhere to start', True, (255, 221, 85)), (350, 700))
                            pg.display.update()  # 刷新页面
                    else:
                        start_loop = False
            self.clock.tick(30)
        while self.start:
            self.start = False  # 游戏默认只进行一次
            # Level 1
            self.initialization(number_of_monsters=4)
            self.monster_loop()
            if self.hero.life:
                # Level 2
                self.initialization(number_of_monsters=6, player_health=self.hero.health,
                                    player_speed=self.hero.speed, player_weapon=self.hero.weapon,
                                    player_own_gun=self.hero.own_gun)  # 玩家保留上一关的数据
                self.monster_loop()
            else:
                self.lose_loop()

            if not self.start:
                if self.hero.life:
                    # Boss
                    self.boss_loop()
                else:
                    self.lose_loop()

            if not self.start:
                if self.hero.life:
                    self.victory_loop()
                else:
                    self.lose_loop()
            # 直接进入boss关测试
            # self.boss_loop()
            # if not self.start:
            #     if self.hero.life:
            #         self.victory_loop()
            #     else:
            #         self.lose_loop()


def main():
    game = TombRaider()
    game.game_start()
    # input("please input any key to exit!")


if __name__ == "__main__":  # 工程入口，不能被其他模块调用
    main()
