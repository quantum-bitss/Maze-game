import pygame
import Bullet
import numpy as np
import math


class MinHeap:
    def __init__(self):
        self.minHeap = []
        self.size = len(self.minHeap)

    def __swap(self, index1, index2):
        self.minHeap[index1], self.minHeap[index2] = self.minHeap[index2], self.minHeap[index1]  # 交换两个node

    def __is_leaf(self, index):
        if 2 * index + 1 < self.size:  # 没有children
            return False
        return True

    def __sift_down(self, index):
        while not self.__is_leaf(index):  # 为leaf node时停止
            if 2 * index + 2 < self.size:  # 存在右child
                if self.minHeap[2 * index + 1].f < self.minHeap[2 * index + 2].f:  # 根据f值来排序
                    min_child_index = 2 * index + 1
                else:
                    min_child_index = 2 * index + 2
                if self.minHeap[index].f > self.minHeap[min_child_index].f:
                    self.__swap(index, min_child_index)
                    index = min_child_index  # 更新下标
                else:
                    break
            else:  # 不存在右child
                if self.minHeap[index].f > self.minHeap[2 * index + 1].f:
                    self.__swap(index, 2 * index + 1)
                    index = 2 * index + 1  # 更新下标
                else:
                    break

    def __sift_up(self, index):
        while index != 0:  # 不是root时总有parent
            parent_index = math.floor((index - 1)/2)
            if self.minHeap[index].f < self.minHeap[parent_index].f:  # 比parent小
                self.__swap(index, parent_index)
                index = parent_index
            else:
                break

    def add(self, node):
        self.minHeap.append(node)
        self.__sift_up(self.size)  # elem的坐标
        self.size += 1

    def remove_min(self):
        self.size -= 1  # 元素减少一个
        self.__swap(0, self.size)  # 与最后一项交换
        self.__sift_down(0)  # 重新组织成min_heap
        return self.minHeap.pop(self.size)  # 将min移出并返回

    def visited(self, index):
        return self.minHeap[index]


class Node:  # A*寻路所需数据结构
    def __init__(self, x, y, g, f, parent=None):
        self.x = x
        self.y = y
        self.g = g  # 到达该点的路径代价
        self.f = f
        self.parent = parent

    def set(self, f, parent):
        self.parent = parent
        self.f = f


def manhattan(x1, x2, y1, y2):  # 采用曼哈顿距离作为启发式
    return abs(x1 - x2) + abs(y1 - y2)


def calculate_distance(monster, player):
    return math.sqrt((monster.rect.centerx - player.rect.centerx) ** 2 +
                     (monster.rect.centery - player.rect.centery) ** 2)


class Monster(pygame.sprite.Sprite):
    def __init__(self, kind=1):
        pygame.sprite.Sprite.__init__(self)
        self.kind = kind  # 靠kind属性区分怪物种类
        self.wandering = True
        if self.kind == 1:
            self.monster_list_l = []
            self.monster_list_r = []
            self.monster_list_l.append(
                pygame.image.load(r"..\image\ghost\1.png"))
            self.monster_list_l.append(
                pygame.image.load(r"..\image\ghost\2.png"))
            self.monster_list_l.append(
                pygame.image.load(r"..\image\ghost\3.png"))
            self.monster_list_l.append(
                pygame.image.load(r"..\image\ghost\4.png"))
            self.monster_list_l.append(
                pygame.image.load(r"..\image\ghost\5.png"))
            self.monster_list_l.append(
                pygame.image.load(r"..\image\ghost\6.png"))

            self.monster_list_r.append(
                pygame.image.load(r"..\image\ghost\1_rotated.png"))
            self.monster_list_r.append(
                pygame.image.load(r"..\image\ghost\2_rotated.png"))
            self.monster_list_r.append(
                pygame.image.load(r"..\image\ghost\3_rotated.png"))
            self.monster_list_r.append(
                pygame.image.load(r"..\image\ghost\4_rotated.png"))
            self.monster_list_r.append(
                pygame.image.load(r"..\image\ghost\5_rotated.png"))
            self.monster_list_r.append(
                pygame.image.load(r"..\image\ghost\6_rotated.png"))
            self.image = self.monster_list_l[0]
            self.health = 70
            self.speed = 1
            self.monster_bullet = Bullet.Bullet()
            self.monster_bullet.image = pygame.image.load(r"..\image\ghost\ball.png")
            self.monster_bullet.harm = 10

        if self.kind == 2:
            self.monster_list_l = []
            self.monster_list_r = []
            self.spider_walk = pygame.image.load(r"..\image\spider\walk_change_direction.png")
            spider_r0 = self.spider_walk.subsurface((0, 0), (55, 57.5))
            self.spider_attack_r = spider_r0
            spider_r1 = self.spider_walk.subsurface((55, 0), (55, 57.5))
            spider_r2 = self.spider_walk.subsurface((110, 0), (55, 57.5))
            spider_r3 = self.spider_walk.subsurface((165, 0), (55, 57.5))
            spider_r4 = self.spider_walk.subsurface((220, 0), (55, 57.5))

            spider_l0 = self.spider_walk.subsurface((0, 57.5), (55, 57.5))
            self.spider_attack_l = spider_l0
            spider_l1 = self.spider_walk.subsurface((55, 57.5), (55, 57.5))
            spider_l2 = self.spider_walk.subsurface((110, 57.5), (55, 57.5))
            spider_l3 = self.spider_walk.subsurface((165, 57.5), (55, 57.5))
            spider_l4 = self.spider_walk.subsurface((220, 57.5), (55, 57.5))

            self.monster_list_l.append(spider_l0)
            self.monster_list_l.append(spider_l1)
            self.monster_list_l.append(spider_l2)
            self.monster_list_l.append(spider_l3)
            self.monster_list_l.append(spider_l4)

            self.monster_list_r.append(spider_r0)
            self.monster_list_r.append(spider_r1)
            self.monster_list_r.append(spider_r2)
            self.monster_list_r.append(spider_r3)
            self.monster_list_r.append(spider_r4)
            self.image = self.monster_list_l[0]

            self.health = 100
            self.speed = 1
            self.monster_bullet = Bullet.Bullet()
            self.monster_bullet.image = pygame.image.load(r"..\image\spider\laser.png")
            self.monster_bullet.image = self.monster_bullet.image.subsurface((0, 0), (60, 7))
            self.monster_bullet.harm = 20

            # 自动寻路
            self.stride = 3
            self.walking = False  # 默认一开始没有处于寻路状态
            self.step1 = 0  # 寻路中的第几步
            self.step2 = 0  # 将步长为3的一步分为步长为1的三步，记录第几步
            self.path = []  # 记录路径
            self.next_node = None
            self.dir_x = 0
            self.dir_y = 0
            self.attack_cooling = False

        # if self.kind == 3:
        self.rect = self.image.get_rect()
        self.life = True
        self.birth_y = 0
        self.direction = 1
        self.attacking_state = False  # 定义寻路完成之后的状态
        self.wander_center = self.rect.centerx  # 确定游荡中心

    def birth_pos(self, x, y):
        self.rect.top = x * 64
        self.rect.left = y * 64
        self.birth_y = self.rect.left
        self.wander_center = self.rect.centerx

    def shoot(self, bullet_group):
        self.monster_bullet.life = True
        bullet_group.add(self.monster_bullet)
        if self.direction < 0:
            self.monster_bullet.direction = -1
            self.monster_bullet.rect.left = self.rect.left - self.rect.width / 3
        if self.direction > 0:
            self.monster_bullet.direction = 1
            self.monster_bullet.rect.left = self.rect.left + self.rect.width / 3

        self.monster_bullet.rect.top = self.rect.top + self.rect.height / 3

    def move(self, dir_x, dir_y):
        self.rect = self.rect.move(self.speed * dir_x, self.speed * dir_y)

    def collide(self, dir_x, dir_y, wall_group, char_group):  # 返回true表示发生碰撞
        self.rect = self.rect.move(self.speed * dir_x, self.speed * dir_y)
        collide = False
        if self.rect.top + self.speed * dir_y < 0:
            collide = True
        if self.rect.right + self.speed * dir_x > 768:
            collide = True
        if self.rect.bottom + self.speed * dir_y > 768:
            collide = True
        if self.rect.left + self.speed * dir_x < 0:
            collide = True
        # 要注意自己碰自己的bug
        if pygame.sprite.spritecollide(self, wall_group, False, None):
            collide = True
        if pygame.sprite.spritecollide(self, char_group, False, None):
            collide = True
        self.rect = self.rect.move(self.speed * -dir_x, self.speed * -dir_y)  # 碰撞检测函数不应有移动作用
        if collide:
            return True
        return False

    def wander_around_current_position(self, wall_group, char_group):
        left_boundary = self.wander_center - 64
        right_boundary = self.wander_center + 64
        if not self.collide(self.direction, 0, wall_group, char_group):  # 没有碰撞
            self.move(self.direction, 0)
        else:
            self.direction = -self.direction
        if self.rect.left <= left_boundary or self.rect.right >= right_boundary:  # 超过游荡范围
            self.direction = -self.direction  # 方向反转

    def path_finding(self, hero, wall_group, char_group):  # 寻路跟踪玩家，要满足玩家在检测范围内
        # 使用rect的centerx和centery来寻路
        start_x, start_y = self.rect.centerx, self.rect.centery  # 记录寻路的起点
        close_list = []  # 记录已走过的点
        f_priority_queue = MinHeap()  # 记录open_list的各个点的f值，并排序，输出最小f值的下标
        f_priority_queue.add(Node(self.rect.centerx, self.rect.centery,
                                  0, manhattan(self.rect.centerx, hero.rect.centerx,
                                               self.rect.centery, hero.rect.centery)))
        final_path = []  # 记录最终路径
        direction = [(0, -self.stride),             # 上
                     (self.stride, -self.stride),   # 右上
                     (self.stride, 0),              # 右
                     (self.stride, self.stride),    # 右下
                     (0, self.stride),              # 下
                     (-self.stride, self.stride),   # 左下
                     (-self.stride, 0),             # 左
                     (-self.stride, -self.stride)]  # 左上
        step = 0  # step取值可以根据检测半径来定
        finish = False
        while not finish:
            step += 1
            if step > 40:  # 四十步以内认为可寻路，防止游戏卡顿
                break
            if f_priority_queue.size != 0:  # 无可走的点
                close_list.append(f_priority_queue.remove_min())  # 将该点从f_priority_queue中取出，放入close_list中
                current = close_list[-1]  # 最新的就是当前点current
                for dire in direction:  # 检查周围点
                    x = current.x + dire[0]  # 邻近点的x坐标
                    y = current.y + dire[1]  # 邻近点的y坐标
                    if not self.collide(dire[0], dire[1], wall_group, char_group):  # 该方向没有碰撞，则该点可到达
                        # print(f"step: {step}  direction: {dire[0], dire[1]}")
                        if abs(x - hero.rect.centerx) < 20 and abs(y - hero.rect.centery) < 20:  # 到达英雄周围，即终点
                            while current.x != start_x or current.y != start_y:  # 一直回溯到起点，找最短路径
                                final_path.append(current)  # 储存最短路径上的点
                                # print(f"current.x: {current.x} current.y: {current.y}")
                                current = current.parent
                            final_path.append(current)  # 将起点也包括进去
                            # print(f"start.x: {current.x} start.y: {current.y}")
                            finish = True
                        else:  # 没到达终点
                            list2 = [(close_list[i].x, close_list[i].y) for i in range(len(close_list))]
                            if not (x, y) in list2:  # 不在close_list中
                                list3 = [(f_priority_queue.visited(i).x, f_priority_queue.visited(i).y)
                                         for i in range(f_priority_queue.size)]
                                if not (x, y) in list3:  # 不在open_list中
                                    # 路径代价为步数
                                    f_priority_queue.add(Node(x, y, current.g + 1,
                                                              current.g + 1 + manhattan(x, hero.rect.centerx, y,
                                                                                        hero.rect.centery), current))
                                else:  # 在open_list中
                                    # for xy in open_list:
                                    for i in range(f_priority_queue.size):
                                        xy = f_priority_queue.visited(i)
                                        if x == xy.x and y == xy.y:  # 找到该点
                                            if xy.f > current.g + 1 + manhattan(x, hero.rect.centerx, y,
                                                                                hero.rect.centery):
                                                xy.f = current.g + 1 + manhattan(x, hero.rect.centerx, y,
                                                                                 hero.rect.centery)  # 更新f值
                                                xy.parent = current  # 更新父节点
                                            break
            else:
                break
        if len(final_path) != 0:
            self.walking = True  # 将正在寻路设为真
            self.path = final_path  # 记录最短路径
            self.step1 = len(self.path) - 1  # 倒序走

    def walk_along_path(self, wall_group, char_group, hero):  # 沿着路走，path中最后一个点才是起点
        if self.walking:  # 正在寻路为真才能寻路
            if self.step1 == len(self.path) - 1:  # 第一步的时候校准怪物位置为起点
                self.rect.centerx = self.path[self.step1].x
                self.rect.centery = self.path[self.step1].y
                self.step1 -= 1
            if self.step2 == 0:  # step2为0的时候获取新的一步
                self.next_node = self.path[self.step1]  # 下一步坐标
                self.dir_x = int((self.next_node.x - self.rect.centerx) / self.stride)
                self.dir_y = int((self.next_node.y - self.rect.centery) / self.stride)
                self.step1 -= 1  # 下一步坐标
            self.step2 += 1
            if self.collide(self.dir_x, self.dir_y, wall_group, char_group):
                self.walking = False
                self.step1 = 0
                self.step2 = 0
                self.wander_center = self.rect.centerx
                if calculate_distance(self, hero) <= 75:  # 与英雄发生碰撞
                    hero.health -= 10
                    self.attack_cooling = True  # 对英雄造成伤害后暂停行动一段时间
            else:  # 没有发生碰撞，则怪物移动，默认移动一单位距离
                self.move(self.dir_x, self.dir_y)  # dir_x和dir_y本身已经包含了步长
            if self.step1 < 0:  # 已走完这段路
                self.walking = False  # 停止这段寻路
                self.step1 = 0  # 重置步数
                self.step2 = 0
                self.wander_center = self.rect.centerx
            if self.step2 == 3:
                self.step2 = 0
