import pygame
import random
import ui
from ui import UIManager, DrawManager


GAME_WITH_BOT = False
middle_offset = (ui.screen_width - 15 * ui.cell_size) / 2 / ui.cell_size
# отступ для рисования поля и кораблей посередине
offset_for_field = 0


class Field:
    def __init__(self, field_params):
        self.field_size = field_params.field_size
        self.nums_of_ships = field_params.nums_of_ships
        # индекс + 1 - длина корабля, значение - количество таких кораблей
        self.cells_state = dict()
        self.set_cells_state()
        self.ships_to_draw = []
        self.ships = dict()

    # делает все клетки поля пустыми, доступными
    def set_cells_state(self):
        for x in range(1, self.field_size + 1):
            for y in range(1, self.field_size + 1):
                self.cells_state[(x, y)] = True

    # метод генерации кораблей.
    def generate_ships(self, drawer, uiManager):
        self.field_size = uiManager.field_params.field_size
        self.nums_of_ships = uiManager.field_params.nums_of_ships
        self.ships = {}
        self.set_cells_state()
        self.ships_to_draw = []
        drawer.show_window(uiManager.create_window)

        while len(self.ships_to_draw) < \
                uiManager.field_params.total_amount_of_ships:
            for i in range(len(self.nums_of_ships) - 1, -1, -1):
                self.generate_ships_by_length(self.nums_of_ships[i], i + 1)
        for ship in self.ships_to_draw:
            drawer.draw_ship(ship[0], ship[1])

    # генерирует корабли заданной длины. вызывается из предыдущего методы
    def generate_ships_by_length(self, number_of_ships, length):
        s = 0
        tries = 0
        while s < number_of_ships:
            x = random.randint(1, self.field_size)
            y = random.randint(1, self.field_size)
            turn = random.randint(0, 1)
            ship = self.make_ship(x, y, turn, length)
            if self.is_ship_can_be_put(ship):
                tries = 0
                self.add_ship(ship)
                self.ships_to_draw.append((ship, turn))
                s += 1
            else:
                tries += 1
            if tries == 10:
                self.ships = {}
                self.set_cells_state()
                self.ships_to_draw = []
                break

    # создает сам корабль - список таплов с координатами на поле
    def make_ship(self, x, y, turn, length):
        if turn == 0:
            if x == self.field_size or x == self.field_size - 1:
                return [(self.field_size - i, y) for i in
                        range(length - 1, -1, -1)]
            else:
                return [(i, y) for i in range(1, length + 1)]
        else:
            if y == self.field_size or y == self.field_size - 1:
                return [(x, self.field_size - i) for i in
                        range(length - 1, -1, -1)]
            else:
                return [(x, i) for i in range(1, length + 1)]

    # возвращает True, если корабль возможно поставить на поле
    def is_ship_can_be_put(self, ship):
        for cell in ship:
            if self.cells_state[cell] is False:
                return False
        return True

    # добавляет корабль в словарь кораблей
    def add_ship(self, ship):
        for cell in ship:
            x = cell[0]
            y = cell[1]
            neighbours = []
            for n in ship:
                if n == cell:
                    continue
                neighbours.append(n)
            self.disable_cells(x, y)
            self.ships[(x, y)] = (False, neighbours)

    # удаляет корабль
    def remove_ship(self, ship):
        for cell in ship:
            x = cell[0]
            y = cell[1]
            del self.ships[(x, y)]
            cells_around = [(x + i, y + j) for i in range(-1, 2) for j in
                            range(-1, 2)]
            for c in cells_around:
                if c[0] < 1 or c[0] > self.field_size or c[1] < 1 or \
                        c[1] > self.field_size:
                    continue
                self.cells_state[c] = True

    # делает клетки вокруг клетки (x, y) недоступными
    def disable_cells(self, x, y):
        cells_around = [(x + i, y + j) for i in range(-1, 2) for j in
                        range(-1, 2)]
        for cell in cells_around:
            if cell[0] < 1 or cell[0] > self.field_size or cell[1] < 1 or\
                    cell[1] > self.field_size:
                continue
            self.cells_state[cell] = False


class Player:
    def __init__(self, uiManager):
        self.uiManager = uiManager
        self.field = Field(self.uiManager.field_params)
        self.score = 0

    def do_shot(self, event, offset):
        x, y = event.pos
        if (offset + offset_for_field) * \
                ui.cell_size <= x <= \
                (self.uiManager.field_params.field_size + offset +
                 offset_for_field) * \
                ui.cell_size and ui.top_margin + \
                offset_for_field * \
                ui.cell_size <= y <= \
                ui.top_margin + (self.uiManager.field_params.field_size +
                                 offset_for_field) * \
                ui.cell_size:
            fired_cell = (
                int(x / ui.cell_size
                    + 1 - offset - offset_for_field),
                int((y - ui.top_margin) / ui.cell_size
                    + 1 - offset_for_field))
            return fired_cell
        else:
            return 0, 0


class Bot:
    def __init__(self, difficulty, field_params):
        self.level = difficulty
        self.last_shot_good = False
        self.last_shot = (0, 0)
        self.last_good_shot = (0, 0)
        self.recommendation = []
        self.killed = False
        self.field = Field(field_params)
        self.score = 0

    def do_shot(self, enemy, level):
        if level == 2:
            target = self.do_shot_level_2(enemy)
        elif level == 1:
            target = self.do_shot_level_1(enemy)
        else:
            target = self.do_shot_level_3(enemy)
        return target[0], target[1]

    def do_shot_level_2(self, enemy):
        available = []
        for key in enemy.field.cells_state.keys():
            if enemy.field.cells_state[key]:
                available.append(key)
        self.last_shot_good = self.last_shot in enemy.field.ships
        if self.last_good_shot != (0, 0) and not self.killed:
            crd = self.last_good_shot
            crd_rec = [[crd[0] - 1, crd[1]], [crd[0] + 1, crd[1]],
                       [crd[0], crd[1] - 1], [crd[0], crd[1] + 1]]
            crd_rec = filter(lambda x: 1 <= x[0] <=
                                       enemy.field.field_size and
                                       1 <= x[1] <= enemy.field.field_size,
                             crd_rec)
            crd_rec = filter(lambda x: (x[0], x[1]) in available, crd_rec)
            self.recommendation.extend(crd_rec)
            if len(self.recommendation) == 0:
                target = random.choice(available)
            else:
                target = self.recommendation.pop()
        else:
            target = random.choice(available)
        if self.killed:
            self.recommendation = []
            self.last_good_shot = (0, 0)

        return target

    def do_shot_level_1(self, enemy):
        available = []
        for key in enemy.field.cells_state.keys():
            if enemy.field.cells_state[key]:
                available.append(key)
        return random.choice(available)

    def do_shot_level_3(self, enemy):
        available = []
        if(len(available)==0):
            for key in enemy.field.ships.keys():
                if enemy.field.cells_state[key]:
                    available.append(key)
        return random.choice(available)if random.randint(0, 1) == 0 else random.choice(list(enemy.field.cells_state.keys()))


class ShootingManager:
    def __init__(self, player_num, player, drawer):
        self.player = player
        self.__offset = ui.OFFSETS[player_num]
        self.drawer = drawer

    def missed(self, x, y):
        self.drawer.put_dots([(x, y)], self.__offset)
        self.player.field.cells_state[(x, y)] = False

    def wounded(self, x, y):
        global offset_for_field
        self.drawer.put_cross(ui.cell_size * (x - 1 + self.__offset +
                                              offset_for_field),
                              ui.cell_size * (y - 1 + offset_for_field) +
                              ui.top_margin)
        self.drawer.put_dots([(x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1),
                              (x - 1, y + 1)], self.__offset)
        self.player.field.ships[(x, y)] = (True,
                                           self.player.field.ships[(x, y)][1])
        self.player.field.cells_state[(x, y)] = False
        for i in [(x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1),
                  (x - 1, y + 1)]:
            self.player.field.cells_state[i] = False

    def is_killed(self, x, y):
        killed_ship = [(x, y)]
        for neighbour in self.player.field.ships[(x, y)][1]:
            n_x = neighbour[0]
            n_y = neighbour[1]
            if self.player.field.ships[(n_x, n_y)][0]:
                killed_ship.append((n_x, n_y))
        if len(killed_ship) == len(self.player.field.ships[(x, y)][1]) + 1:
            return True
        return False

    def killed(self, x, y):
        global offset_for_field
        self.drawer.put_cross(ui.cell_size * (x - 1 + self.__offset +
                                              offset_for_field), ui.cell_size *
                              (y - 1 + offset_for_field) +
                              ui.top_margin, ui.RED)
        self.player.field.cells_state[(x, y)] = False
        neighbours = self.player.field.ships[(x, y)][1]
        for neighbour in neighbours:
            self.drawer.put_cross(ui.cell_size * (neighbour[0] - 1
                                                  + self.__offset +
                                                  offset_for_field), ui.cell_size *
                                  (neighbour[1] - 1 + offset_for_field) +
                                  ui.top_margin, ui.RED)
            self.player.field.cells_state[neighbour] = False
        dots = []
        ship = [n for n in neighbours]
        ship.append((x, y))
        if len(ship) > 1:
            if ship[0][0] == ship[1][0]:
                ship.sort(key=lambda i: i[1])
                dots = [(ship[0][0], ship[0][1] - 1),
                        (ship[0][0], ship[-1][1] + 1)]
            elif ship[0][1] == ship[1][1]:
                ship.sort(key=lambda i: i[0])
                dots = [(ship[0][0] - 1, ship[0][1]),
                        (ship[-1][0] + 1, ship[0][1])]
        else:
            dots = [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]
        for dot in dots:
            self.player.field.cells_state[dot] = False
        self.drawer.put_dots(dots, self.__offset)


class Game:
    def __init__(self):
        # объявляем все необходимые для игры переменные
        self.game_start = False
        self.level_chosen = False
        self.field_set_up = False
        self.field_made = False
        self.ships_created = False
        self.bot_turn = False
        self.game_over = False
        self.game_finished = False

        self.uiManager = UIManager()
        self.labels = {}
        self.players = {}
        self.shootings = {}
        self.level = 0
        self.enemy_num = 2
        self.player_num = 1
        self.ships_to_draw = []
        self.drawn_ships = [0 for i in range(15)]
        self.scene_number = 0

    # сам процесс игры. по очереди все методы - этапы игры.
    def play_game(self):
        self.choose_mode()
        self.choose_level()
        self.set_labels()
        self.set_players()
        self.set_shootings()
        self.setup_field()
        self.create_field(1)
        if not GAME_WITH_BOT and self.ships_created:
            self.field_made = False
            self.ships_created = False
            self.create_field(2)
        for p in self.players.values():
            p.field.set_cells_state()
        self.play()
        self.finish()

    # вызывается когда мы нажимаем на выходи из игры (чтобы в каждом цикле
    # эти переменные не перечислять)
    def quit_game(self):
        self.game_start = True
        self.level_chosen = True
        self.field_set_up = True
        self.field_made = True
        self.bot_turn = True
        self.game_over = True
        self.game_finished = True

    def set_labels(self):
        # выбираются подписи к полям в зависимости от режима игры
        if GAME_WITH_BOT:
            self.labels = {1: 'Ваше поле',
                           2: 'Поле компьютера'}
        else:
            self.labels = {1: 'Игрок 1',
                           2: 'Игрок 2'}
        # и отправляются в окна, где они будут отображаться
        self.uiManager.create_window.add_labels(
            ui.Label(self.labels[1], (22 * ui.cell_size, ui.cell_size)))

    # создается словарь с игроками в зависимости от режима игры
    def set_players(self):
        if GAME_WITH_BOT:
            self.players = {1: Player(self.uiManager),
                            2: Bot(1, self.uiManager.field_params)}
        else:
            self.players = {1: Player(self.uiManager),
                            2: Player(self.uiManager)}

    # создается словарь с шутинг менеджерами
    def set_shootings(self):
        self.shootings = {1: ShootingManager(1, self.players[1],
                                             self.uiManager.drawer),
                          2: ShootingManager(2, self.players[2],
                                             self.uiManager.drawer)}

    # метод для окна с выбором режима игры
    def choose_mode(self):
        global GAME_WITH_BOT
        self.uiManager.next_window()
        while not self.game_start:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.uiManager.start_with_friend_button.rect.\
                            collidepoint(mouse):
                        self.game_start = True
                        self.level_chosen = True
                        self.uiManager.next_window(2)
                    elif self.uiManager.start_with_computer_button.rect.\
                            collidepoint(mouse):
                        GAME_WITH_BOT = True
                        self.game_start = True
                        self.uiManager.next_window()
            pygame.display.update()

    # метод для окна с выбором уровня бота. открывается,
    # если мы выбрали играть с ботом
    def choose_level(self):
        while not self.level_chosen:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and self.uiManager.level_1_button.rect.\
                        collidepoint(mouse):
                    self.level = 1
                    self.level_chosen = True
                    self.uiManager.game_window.add_labels(ui.Label(
                        'Лёгкий уровень', (22 * ui.cell_size, ui.cell_size)))
                    self.uiManager.next_window()
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and self.uiManager.level_2_button.rect.\
                        collidepoint(mouse):
                    self.level = 2
                    self.level_chosen = True
                    self.uiManager.game_window.add_labels(ui.Label(
                        'Средний уровень', (22 * ui.cell_size, ui.cell_size)))
                    self.uiManager.next_window()
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and self.uiManager.level_3_button.rect.\
                        collidepoint(mouse):
                    self.level = 3
                    self.level_chosen = True
                    self.uiManager.game_window.add_labels(ui.Label(
                        'Сложный уровень', (22 * ui.cell_size, ui.cell_size)))
                    self.uiManager.next_window()
            pygame.display.update()

    # проверяет не нажата ли кнопка + или - в окне с настройками
    # (кроме + и - для раземра поля)
    def check_buttons(self, mouse):
        for i in range(0, len(self.uiManager.plus_minus_buttons) - 1, 2):
            minus_btn, plus_btn = self.uiManager.plus_minus_buttons[i], \
                                  self.uiManager.plus_minus_buttons[i + 1]
            # если кнопка - нажата, уменьшаем количество соответствующих
            # кораблей, обновляем везде параметры
            if minus_btn.rect.collidepoint(mouse):
                if self.uiManager.field_params.nums_of_ships[i // 2] == 0:
                    continue
                self.uiManager.field_params.nums_of_ships[i // 2] -= 1
                self.uiManager.field_params.update_params()
                self.uiManager.drawer = DrawManager(self.uiManager.field_params)
                self.uiManager.drawer.put_params_labels()
            # если кнопка + нажата, увеличиваем количество соответствующих
            # кораблей, обновляем везде параметры
            elif plus_btn.rect.collidepoint(mouse):
                self.uiManager.field_params.nums_of_ships[i // 2] += 1
                self.uiManager.field_params.update_params()
                self.uiManager.drawer = DrawManager(self.uiManager.field_params)
                self.uiManager.drawer.put_params_labels()

    # обновляет окно с настройками, после того, как меняется рзамер поля
    def update_settings_window(self):
        self.uiManager.set_plus_minus_btns_params()
        self.uiManager.settings_window.clear_buttons()
        self.uiManager.settings_window.add_buttons(
            self.uiManager.plus_size_button,
            self.uiManager.minus_size_btn, self.uiManager.next_button)
        for button in self.uiManager.plus_minus_buttons:
            self.uiManager.settings_window.add_buttons(button)
        self.uiManager.next_window(0)
        self.uiManager.drawer.draw_ship_examples()
        self.uiManager.drawer.put_params_labels()

    # проверяет верны ли введеные в настйроках параметры
    def are_params_correct(self):
        return not self.zero_ships() and \
               self.uiManager.field_params.field_size > 0 and \
               not self.too_many_ships()

    # возвращает True, если не выбрано ни одного корабля. Иначе - False
    def zero_ships(self):
        for num in self.uiManager.field_params.nums_of_ships:
            if num != 0:
                return False
        return True

    # возвращает True, если корабли не влезают на поле. Иначе - False
    def too_many_ships(self):
        total = 0
        for i in range(len(self.uiManager.field_params.nums_of_ships)):
            total += self.uiManager.field_params.nums_of_ships[i] * (i + 1)
        return total > (self.uiManager.field_params.field_size *
                self.uiManager.field_params.field_size) / 2

    # если мы уменьшили размер поля, но не уменьшили количество кораблей,
    # длина которых больше длины поля, вызывается этот метод, и слишком длинные
    # корабли удаляются
    def delete_extra_ships(self):
        for i in range(self.uiManager.field_params.field_size,
                       len(self.uiManager.field_params.nums_of_ships)):
            if self.uiManager.field_params.nums_of_ships[i] != 0:
                self.uiManager.field_params.nums_of_ships[i] = 0

    # метод для окна с настройками
    def setup_field(self):
        global offset_for_field
        if not self.field_set_up:
            self.update_settings_window()
        while not self.field_set_up:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # увеличиваем размер поля
                    if self.uiManager.plus_size_button.rect.\
                            collidepoint(mouse) and \
                            self.uiManager.field_params.field_size < 15:
                        self.uiManager.field_params.field_size += 1
                        self.update_settings_window()
                        self.delete_extra_ships()
                    # уменьшаем размер поля
                    elif self.uiManager.minus_size_btn.rect.\
                            collidepoint(mouse) and \
                            self.uiManager.field_params.field_size > 2:
                        self.uiManager.field_params.field_size -= 1
                        self.update_settings_window()
                        self.delete_extra_ships()
                    elif self.uiManager.next_button.rect.collidepoint(mouse):
                        # перед тем как перейти к созданию поля, проверяем
                        # верны ли параметры
                        if self.are_params_correct():
                            self.field_set_up = True
                            self.uiManager.field_params.update_params()
                            self.uiManager.drawer = DrawManager(self.uiManager.field_params)
                            self.uiManager.next_window()
                            offset_for_field = self.uiManager.field_params.offset
                        # если не верны, то выводим сообщение о
                        # соответствующей ошибке
                        else:
                            if self.too_many_ships():
                                self.uiManager.drawer.put_dynamic_label(ui.Label(
                                    'Слишком много кораблей',
                                    (22 * ui.cell_size, ui.screen_height - 2
                                     * ui.cell_size), ui.RED))
                            elif self.zero_ships():
                                self.uiManager.drawer.put_dynamic_label(ui.Label(
                                    'Слишком мало кораблей',
                                    (22 * ui.cell_size, ui.screen_height - 2
                                     * ui.cell_size), ui.RED))
                    else:
                        # проверяем кнопки + и -
                        self.check_buttons(mouse)
            pygame.display.update()

    # перерисовывает поле, удаляет с него все корабли
    def redraw_field(self, num):
        self.uiManager.drawer.show_window(self.uiManager.create_window)
        self.players[num].field.set_cells_state()
        self.players[num].field.ships = dict()
        self.ships_to_draw = []
        self.drawn_ships = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.field_made = False
        self.ships_created = False

    def set_start_end_cells(self, x_end, x_start, y_start, y_end):
        start_cell = (int((x_start) / ui.cell_size
                          + 1 - offset_for_field - middle_offset),
                      int((y_start - ui.top_margin) / ui.cell_size
                          + 1 - offset_for_field))
        end_cell = (int((x_end) / ui.cell_size
                        + 1 - offset_for_field - middle_offset),
                    int((y_end - ui.top_margin) / ui.cell_size
                        + 1 - offset_for_field))
        if start_cell > end_cell:
            start_cell, end_cell = end_cell, start_cell
        return (start_cell, end_cell)

    def check_borders(self, start_cell, end_cell, ships_stop_list, temp_ship, player):
        # проверяем, что не зашли за границы поля
        if 1 <= start_cell[0] <= self.uiManager.field_params.field_size \
                and 1 <= start_cell[1] <= self.uiManager.field_params.field_size \
                and 1 <= end_cell[0] <= self.uiManager.field_params.field_size \
                and 1 <= end_cell[1] <= self.uiManager.field_params.field_size:

            if end_cell[0] - start_cell[0] + 1 in ships_stop_list \
                    and end_cell[1] - start_cell[1] + 1 in \
                    ships_stop_list:
                return
            else:
                if start_cell[0] == end_cell[0]:
                    for cell in range(start_cell[1],
                                      end_cell[1] + 1):
                        temp_ship.append((start_cell[0], cell))
                elif start_cell[1] == end_cell[1]:
                    for cell in range(start_cell[0],
                                      end_cell[0] + 1):
                        temp_ship.append((cell, start_cell[1]))
        if temp_ship and \
                self.players[player].field.is_ship_can_be_put(
                    temp_ship) and \
                self.drawn_ships[len(temp_ship) - 1] < \
                self.uiManager.field_params.nums_of_ships[
                    len(temp_ship) - 1]:
            self.players[player].field.add_ship(temp_ship)
            self.drawn_ships[len(temp_ship) - 1] += 1
            self.ships_to_draw.append(temp_ship)

    # метод для окна с созданием поля
    def create_field(self, player):
        can_draw = False
        drawing = False
        x_start, y_start = 0, 0
        ship_size = 0, 0
        start_cell, end_cell = (), ()

        # создаем и заполняем список с номерами кораблей, которых нет в игре
        ships_stop_list = []
        for n in range(len(
                self.uiManager.field_params.nums_of_ships)):
            if self.uiManager.field_params.nums_of_ships[n] == 0:
                ships_stop_list.append(n + 1)

        while not self.field_made:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                # если нажата кнопка 'дальше'
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and self.uiManager.next_button.rect.collidepoint(mouse) \
                        and self.ships_created:
                    self.field_made = True
                    # если сейчас мы на первом окне создания кораблей
                    if player == 1:
                        # если играм с ботом, то сразу переходим в игру
                        if GAME_WITH_BOT:
                            self.players[2].field.generate_ships(self.uiManager.drawer,
                                                                 self.uiManager)
                            self.uiManager.next_window(2)
                        # если с другом, то на следующее окно создания
                        else:
                            self.uiManager.create_window.clear_labels()
                            self.uiManager.create_window.add_labels(
                                ui.Label(self.labels[2],
                                         (22 * ui.cell_size, ui.cell_size)))
                            self.uiManager.next_window()
                    # если мы уже на втором окне, то переходим к игре
                    else:
                        self.uiManager.next_window()

                # если нажата кнопка 'сгенерировать рандомно'
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and self.uiManager.random_button.rect.collidepoint(mouse):
                    # если мы уже порисовали, то поле отчищается
                    if can_draw:
                        can_draw = False
                        self.redraw_field(player)
                    # и генерируется новое
                    self.players[player].field.generate_ships(
                        self.uiManager.drawer, self.uiManager)
                    self.ships_created = True
                # если нажата кнопка 'стереть всё', поле отчищается
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and self.uiManager.clear_button.rect.collidepoint(mouse):
                    self.redraw_field(player)
                # если нажата кнопка 'отмена', стирается последний
                # нарисованный корабль
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and self.uiManager.cancel_button.rect.collidepoint(mouse) \
                        and can_draw:
                    if self.ships_to_draw:
                        last_ship = self.ships_to_draw.pop()
                        self.drawn_ships[len(last_ship) - 1] -= 1
                        self.players[player].field.remove_ship(last_ship)
                # если нажата кнопка 'нарисовать', можем начать рисовать
                elif event.type == pygame.MOUSEBUTTONDOWN and \
                        self.uiManager.manual_button.rect.collidepoint(mouse):
                    can_draw = True
                    self.redraw_field(player)
                # далее процесс рисования
                # отмечаем куда мы нажали мышкой, то есть начало корабля
                elif event.type == pygame.MOUSEBUTTONDOWN and can_draw:
                    drawing = True
                    x_start, y_start = event.pos
                    ship_size = 0, 0
                # ведём мышкой
                elif event.type == pygame.MOUSEMOTION and drawing:
                    x_end, y_end = event.pos
                    ship_size = x_end - x_start, y_end - y_start
                # заканичваем корабль
                elif event.type == pygame.MOUSEBUTTONUP and drawing:
                    x_end, y_end = event.pos
                    ship_size = 0, 0
                    drawing = False
                    start_cell, end_cell = self.set_start_end_cells(x_end, x_start, y_start, y_end)
                    temp_ship = []
                    # проверяем, что не зашли за границы поля
                    self.check_borders(start_cell, end_cell, ships_stop_list, temp_ship, player)

                # проверяем что нарисовали уже все корабли
                if len(self.ships_to_draw) == self.uiManager.field_params.total_amount_of_ships:
                    self.ships_created = True
            # если поле еще не создано и мы в процессе рисования, отрисовываем
            # нарисованные корабли
            if not self.field_made and can_draw:
                self.uiManager.drawer.show_window(self.uiManager.create_window)
                pygame.draw.rect(ui.screen, ui.BLACK,
                                 ((x_start, y_start), ship_size), 3)
                for ship in self.ships_to_draw:
                    if len(ship) > 1 and ship[0][1] == ship[1][1]:
                        self.uiManager.drawer.draw_ship(ship, 0)
                    else:
                        self.uiManager.drawer.draw_ship(ship, 1)
            pygame.display.update()

    # передается ход
    def change_turn(self):
        self.uiManager.drawer.update_turn(self.labels[self.player_num],
                                          self.labels[self.enemy_num])
        self.player_num, self.enemy_num = self.enemy_num, self.player_num
        if GAME_WITH_BOT:
            self.bot_turn = not self.bot_turn

    # возвращает True, если текущий игрок стал победителем
    def is_winner(self):
        return self.players[self.player_num].score == \
               self.uiManager.field_params.max_score

    def kill(self, fired_cell):
        if self.bot_turn:
            self.players[2].killed = True
        self.shootings[self.enemy_num].killed(fired_cell[0],
                                              fired_cell[1])
        ui.sound_killed.play()

        self.uiManager.drawer.last_move(fired_cell, 'убил', self.player_num)
        # self.uiManager.drawer.put_dynamic_label(ui.Label(
        #     'Убил', (22 * ui.cell_size,
        #              17 * ui.cell_size), ui.WHITE))

    def wound(self, fired_cell):
        # у бота отмечаем что мы еще не убили корабль полностью
        if self.bot_turn:
            self.players[2].killed = False
        # "раним" клетку
        self.shootings[self.enemy_num].wounded(fired_cell[0],
                                               fired_cell[1])
        ui.sound_wounded.play()
        self.uiManager.drawer.last_move(fired_cell, 'ранил', self.player_num)

    def win(self):
        self.game_over = True
        if GAME_WITH_BOT:
            if self.player_num == 2:
                self.uiManager.win_window.add_labels(
                    ui.Label('Компьютер победил', (
                        ui.screen_width / 2, 2 * ui.cell_size)))
            else:
                self.uiManager.win_window.add_labels(
                    ui.Label('Вы победили',
                             (ui.screen_width / 2,
                              2 * ui.cell_size)))
        else:
            self.uiManager.win_window.add_labels(
                ui.Label('Игрок {0} победил'.format(
                    self.player_num),
                    (ui.screen_width / 2,
                     2 * ui.cell_size)))
        self.uiManager.next_window()

    def miss(self, fired_cell):
        self.change_turn()
        self.shootings[self.player_num].missed(fired_cell[0],
                                               fired_cell[1])
        ui.sound_missed.play()
        self.uiManager.drawer.last_move(fired_cell, 'мимо', self.player_num)

    def check_fired_cell(self, fired_cell, enemy):
        if fired_cell != (0, 0):
            # если попали в корабль врага и он еще не подбитый
            if fired_cell in enemy.field.ships and \
                    enemy.field.ships[fired_cell][0] is False:
                # если стрелял бот, то отмечаем, что это был удачный выстрел
                if self.bot_turn:
                    self.players[2].last_good_shot = fired_cell
                # делаем клетку недоступной. в нее больше нельзя стрелять
                enemy.field.cells_state[fired_cell] = False
                # увеличиваем очки
                self.players[self.player_num].score += 1
                # обновляем лейбл с очками
                self.uiManager.drawer.update_score(
                    self.players[self.player_num].score,
                    self.player_num)

                # если убили корабль
                if self.shootings[self.enemy_num].is_killed(fired_cell[0],
                                                            fired_cell[1]):
                    self.kill(fired_cell)
                else:
                    self.wound(fired_cell)

                if self.is_winner():
                    self.win()

            elif fired_cell not in enemy.field.ships and \
                    enemy.field.cells_state[fired_cell] is True:
                self.miss(fired_cell)

    # метод для окна игры
    def play(self):
        self.uiManager.drawer.update_score(0, 1)
        self.uiManager.drawer.update_score(0, 2)
        self.uiManager.drawer.update_turn(self.labels[self.enemy_num],
                                          self.labels[self.player_num], False)

        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN or self.bot_turn:
                    enemy = self.players[self.enemy_num]
                    if self.bot_turn:
                        fired_cell = self.players[2].do_shot(enemy, self.level)
                    else:
                        fired_cell = self.players[self.player_num].do_shot(
                            event, ui.OFFSETS[self.enemy_num])
                    self.check_fired_cell(fired_cell, enemy)

            pygame.display.update()

    # метод для окна победы
    def finish(self):
        while not self.game_finished:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                # начинаем заново
                elif event.type == pygame.MOUSEBUTTONDOWN and self.uiManager.restart_button.rect.collidepoint(mouse):
                    self.game_finished = True
                    game = Game()
                    game.play_game()
            pygame.display.update()


def main():
    game = Game()
    game.play_game()


if __name__ == '__main__':
    main()
    pygame.quit()
