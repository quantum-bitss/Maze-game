import pygame
import random
import Prop


class MapEntryType:
    MAP_EMPTY = 0,
    MAP_BLOCK = 1,


class WallDirection:
    WALL_LEFT = 0,
    WALL_UP = 1,
    WALL_RIGHT = 2,
    WALL_DOWN = 3,


wall_image = r"../image/brick.jpg"  # 素材相对地址
flag_image = r"../image/flag.png"
flame_image = r"../image/flame.png"
portal_image = r"../image/portal.png"


class Wall(pygame.sprite.Sprite):  # 墙
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(wall_image)
        self.rect = self.image.get_rect()


class Start(pygame.sprite.Sprite):  # 旗帜
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(flag_image)
        self.rect = self.image.get_rect()


class Flame(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(flame_image)
        self.flame_list = []
        for i in range(0, 10):
            image_flame = self.image.subsurface((i * 64, 64 * 2), (64, 64))
            self.flame_list.append(image_flame)
        self.rect = self.image.get_rect()


class Portal(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(portal_image)
        self.rect = self.image.get_rect()
        self.life = False


class Map:  # 定义WIDTH 10,HEIGHT 10
    def __init__(self, width, height, screen_width, screen_height, map_width, map_height, left_distance, top_distance):
        self.width = width  # 矩阵列数 12
        self.height = height  # 矩阵行数 12
        self.screen_width = screen_width  # screen宽度， screen为主屏幕
        self.screen_height = screen_height  # screen高度
        self.map_width = map_width  # screen中地图宽度
        self.map_height = map_height  # screen中地图高度
        self.left_distance = left_distance  # 该地图在screen中的纵坐标
        self.top_distance = top_distance  # 该地图在screen中的横坐标

        self.room_pos = (0, 0)  # 房间的位置
        self.start_pos = (0, 0)  # 玩家初始位置
        self.monster_birth = {}  # 存放怪物出生地点的字典

        self.map = [[0 for x in range(self.width)] for y in range(self.height)]  # 地图矩阵 初始化为0
        self.wallGroup = pygame.sprite.Group()  # 墙的集合
        self.flagGroup = pygame.sprite.Group()  # 旗帜集合
        self.flameGroup = pygame.sprite.Group()  # 火焰集合
        self.medicine_group = pygame.sprite.Group()  # 医药包集合
        self.speed_up_group = pygame.sprite.Group()  # 加速包集合
        self.speed_down_group = pygame.sprite.Group()  # 蜘蛛网集合
        self.gun_group = pygame.sprite.Group()  # 枪集合
        self.empty_space = []
        self.medicine_list = []
        self.speed_up_list = []
        self.speed_down_list = []
        self.gun_list = []
        self.portal = Portal()

    def reset_map(self, value):  # 重设矩阵的值为value
        for y in range(self.height):
            for x in range(self.width):
                self.set_map(x, y, value)

    def set_map(self, x, y, value):
        if value == MapEntryType.MAP_EMPTY:
            self.map[x][y] = 0  # 该点为空
        elif value == MapEntryType.MAP_BLOCK:
            self.map[x][y] = 1  # 该点为墙

    def is_visited(self, x, y):
        return self.map[x][y] != 1  # 值为1为未访问，为墙

    def create_bounds(self):
        for i in range(0, self.width):
            # 第一行和最后一行都设为墙
            self.map[0][i] = 1
            self.map[self.height - 1][i] = 1
        for i in range(1, self.height - 1):
            # 两侧也都设为墙
            self.map[i][0] = 1
            self.map[i][self.width - 1] = 1

    def create_room(self):  # 随机生成一个空白房间
        room_size = int(self.height / 5)
        while True:
            start_row = random.randint(1, self.height - 2 - room_size)
            start_col = random.randint(1, self.width - 2 - room_size)  # 在靠近上方的地方生成房间
            # 找对角为墙的地方
            if self.map[start_row][start_col] == 1 and self.map[start_row + room_size][start_col + room_size] == 1:
                break
        self.room_pos = (start_row, start_col)  # 房间的位置
        for i in range(start_row, start_row + room_size + 1):
            for j in range(start_col, start_col + room_size + 1):
                self.map[i][j] = 0
                # 随机制造空白空间

    def create_entrance_help(self):
        empty_row = []
        for i in range(0, self.height):
            for j in range(0, self.width):
                if self.map[i][j] == 0:
                    empty_row.append(i)
                    break
        return empty_row

    def create_entrance(self):  # 生成玩家出生点
        empty_row = self.create_entrance_help()
        entrance_row = random.choice(empty_row)  # 行空白越多，被选中的概率越大
        y = 0
        x = entrance_row
        self.map[x][y] = 8  # 玩家出生点
        self.start_pos = (x, y)
        y += 1
        # 打通至迷宫路径中
        while self.map[x][y]:
            self.map[x][y] = 0
            y += 1
            if y > self.width - 1:
                break

    def create_monster_birth(self, n):
        self.monster_birth = {}
        selected = []
        while len(selected) < n * 2:  # 选择出生点的数量
            i, j = random.randint(0, self.height - 1), random.randint(1, self.width - 2)
            if self.map[i][j] == 0 and self.map[i][j - 1] == 0 and self.map[i][j + 1] == 0:
                if (i, j) not in selected:
                    selected.append((i, j))
        list_1 = random.sample(selected, k=n)
        selected = [x for x in selected if x not in list_1]
        self.monster_birth.update({"Ghost": list_1, "Spider": selected})

    def check_empty_space(self):
        self.empty_space.clear()
        for x in range(0, self.height):
            for y in range(0, self.width):
                if self.map[x][y] == 0:
                    self.empty_space.append((x, y))

    def create_medicine(self, num):  # num:医药包数量
        self.check_empty_space()
        self.medicine_list = random.choices(self.empty_space, k=num)
        for obj in self.medicine_list:
            self.map[obj[0]][obj[1]] = 11  # 医药包专属数字

    def create_speed_up(self, num):  # num:加速包数量
        self.check_empty_space()
        self.speed_up_list = random.choices(self.empty_space, k=num)
        for obj in self.speed_up_list:
            self.map[obj[0]][obj[1]] = 12  # 加速包专属数字

    def create_speed_down(self, num):  # num:减速包数量
        self.check_empty_space()
        self.speed_down_list = random.choices(self.empty_space, k=num)
        for obj in self.speed_down_list:
            self.map[obj[0]][obj[1]] = 13  # 减速包专属数字

    def create_gun(self):
        self.check_empty_space()
        self.gun_list = random.choices(self.empty_space, k=1)
        for obj in self.gun_list:
            self.map[obj[0]][obj[1]] = 14  # 枪专属数字

    def create_portal(self):
        zero_positions = []
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if self.map[i][j] != 1:
                    zero_positions.append((i, j))
        pos = random.choice(zero_positions)
        self.portal.rect.left = 64 * pos[1]
        self.portal.rect.top = 64 * pos[0]

    def draw_map(self):
        cell_width = self.map_width / self.width  # 格子宽度
        cell_height = self.map_height / self.height  # 格子高度
        for x in range(0, self.height):
            for y in range(0, self.width):
                if self.map[x][y] == 8:  # 玩家出生点
                    start = Start()  # 创建旗帜/玩家对象
                    start.rect.left = self.left_distance + y * cell_width  # screen中玩家的位置
                    start.rect.top = self.top_distance + x * cell_height  # screen中玩家的位置
                    start.rect.width = cell_width  # screen中玩家对象的宽度
                    start.rect.height = cell_height  # screen中玩家对象的高度
                    self.flagGroup.add(start)  # 添加到移动对象集合中

                if self.map[x][y] == 1:  # 墙
                    wall = Wall()
                    wall.rect.left = self.left_distance + y * cell_width  # screen中墙的位置
                    wall.rect.top = self.top_distance + x * cell_height  # screen中墙的位置
                    wall.rect.width = cell_width  # screen中墙的宽度
                    wall.rect.height = cell_height  # screen中墙的高度
                    self.wallGroup.add(wall)  # 添加到墙壁集合中
                    if x != 0:  # 第一行用作任务状态显示
                        random_list = [1, 2, 3, 4, 5]
                        random_num = random.choice(random_list)
                        if random_num == 1:
                            flame = Flame()
                            flame.rect.left = self.left_distance + y * cell_width
                            flame.rect.top = self.top_distance + x * cell_height
                            flame.rect.width = cell_width
                            flame.rect.height = cell_height
                            self.flameGroup.add(flame)

                if self.map[x][y] == 11:  # 医药包
                    medi = Prop.Medicine(20)
                    medi.rect.left = self.left_distance + y * cell_width
                    medi.rect.top = self.top_distance + x * cell_height
                    medi.rect.width = cell_width
                    medi.rect.height = cell_height
                    self.medicine_group.add(medi)

                if self.map[x][y] == 12:  # 加速包
                    sped_up = Prop.SpeedUp(20)
                    sped_up.rect.left = self.left_distance + y * cell_width
                    sped_up.rect.top = self.top_distance + x * cell_height
                    sped_up.rect.width = cell_width
                    sped_up.rect.height = cell_height
                    self.speed_up_group.add(sped_up)

                if self.map[x][y] == 13:  # 减速包
                    sped_down = Prop.SpeedDown(20)
                    sped_down.rect.left = self.left_distance + y * cell_width
                    sped_down.rect.top = self.top_distance + x * cell_height
                    sped_down.rect.width = cell_width
                    sped_down.rect.height = cell_height
                    self.speed_down_group.add(sped_down)

                if self.map[x][y] == 14:  # 枪
                    gun = Prop.Gun()
                    gun.rect.left = self.left_distance + y * cell_width + 16
                    gun.rect.top = self.top_distance + x * cell_height + 16
                    gun.rect.width = cell_width
                    gun.rect.height = cell_height
                    self.gun_group.add(gun)


def recursive_back_tracker(map, width, height):
    start_x, start_y = (random.randint(0, width - 1), random.randint(0, height - 1))  # 随机初始位置
    print("start(%d, %d)" % (start_x, start_y))
    map.set_map(2 * start_x + 1, 2 * start_y + 1, MapEntryType.MAP_EMPTY)
    # map.set_map(start_x, start_y, MapEntryType.MAP_EMPTY)
    checklist = [(start_x, start_y)]
    while len(checklist):
        # use checklist as a stack, get entry from the top of stack
        entry = checklist[-1]
        if not check_adjacent_pos(map, entry[0], entry[1], width, height, checklist):  # DFS算法生成迷宫，无近点则返回False，则移除top元素
            # the entry has no unvisited adjacent entry, so remove it from checklist
            checklist.remove(entry)


def do_recursive_back_tracker(map):
    map.reset_map(MapEntryType.MAP_BLOCK)  # 将地图格子都设为墙
    # recursive_back_tracker(map, (map.width - 1) // 2, (map.height - 1) // 2)
    recursive_back_tracker(map, map.width // 2, map.height // 2)
    # recursive_back_tracker(map, map.width, map.height)


def check_adjacent_pos(map, x, y, width, height, checklist):
    directions = []
    # 检查并收集合法方向
    if x > 0:
        # if not map.is_visited(x - 1, y):
        if not map.is_visited(2 * (x - 1) + 1, 2 * y + 1):  # 是墙，才能拓展
            directions.append(WallDirection.WALL_LEFT)

    if y > 0:
        # if not map.is_visited(x, y - 1):
        if not map.is_visited(2 * x + 1, 2 * (y - 1) + 1):
            directions.append(WallDirection.WALL_UP)

    if x < width - 1:
        # if not map.is_visited(x + 1, y):
        if not map.is_visited(2 * (x + 1) + 1, 2 * y + 1):
            directions.append(WallDirection.WALL_RIGHT)

    if y < height - 1:
        # if not map.is_visited(x, y + 1):
        if not map.is_visited(2 * x + 1, 2 * (y + 1) + 1):
            directions.append(WallDirection.WALL_DOWN)

    if len(directions):
        direction = random.choice(directions)  # 随机选择一个方向来生成路径
        # 步长为2进行路径拓展
        if direction == WallDirection.WALL_LEFT:
            map.set_map(2 * (x - 1) + 1, 2 * y + 1, MapEntryType.MAP_EMPTY)
            map.set_map(2 * x, 2 * y + 1, MapEntryType.MAP_EMPTY)  # 这里设哪里为空
            # map.set_map(x - 1, y, MapEntryType.MAP_EMPTY)
            checklist.append((x - 1, y))  # DFS算法
        elif direction == WallDirection.WALL_UP:
            map.set_map(2 * x + 1, 2 * (y - 1) + 1, MapEntryType.MAP_EMPTY)
            map.set_map(2 * x + 1, 2 * y, MapEntryType.MAP_EMPTY)
            # map.set_map(x, y - 1, MapEntryType.MAP_EMPTY)
            checklist.append((x, y - 1))
        elif direction == WallDirection.WALL_RIGHT:
            map.set_map(2 * (x + 1) + 1, 2 * y + 1, MapEntryType.MAP_EMPTY)
            map.set_map(2 * x + 2, 2 * y + 1, MapEntryType.MAP_EMPTY)
            # map.set_map(x + 1, y, MapEntryType.MAP_EMPTY)
            checklist.append((x + 1, y))
        elif direction == WallDirection.WALL_DOWN:
            map.set_map(2 * x + 1, 2 * (y + 1) + 1, MapEntryType.MAP_EMPTY)
            map.set_map(2 * x + 1, 2 * y + 2, MapEntryType.MAP_EMPTY)
            # map.set_map(x, y + 1, MapEntryType.MAP_EMPTY)
            checklist.append((x, y + 1))
        return True
    else:
        # if not find any unvisited adjacent entry
        return False


def generate_maze(map):
    do_recursive_back_tracker(map)  # 生成迷宫
    # map.create_bounds()
    map.create_entrance()
    # map.create_monster_birth()  # 生成怪物出生点
    map.create_room()  # 随机生成空白房间


def self_checking_generate_maze(map, n):
    # while abs(map.start_pos[0]-map.room_pos[0] < map.height/2) and
    #       abs(map.start_pos[1]-map.room_pos[1] < map.width/2)    当玩家和房间的距离过近时，重新生成迷宫
    while not (abs(map.start_pos[0] - map.room_pos[0] >= map.height / 2) or
               abs(map.start_pos[1] - map.room_pos[1] >= map.width / 2)):
        generate_maze(map)
    map.create_monster_birth(n)
    print(map.monster_birth)
    for val in map.monster_birth.values():
        for item in val:
            print(map.map[item[0]][item[1]])
    map.check_empty_space()
    map.create_medicine(2)  # 2个血包
    map.create_speed_up(2)  # 2个加速包
    map.create_speed_down(2)  # 2个蛛网
    map.create_gun()
    map.draw_map()  # 确定迷宫各个元素在screen中的位置
