import pygame
import random
import ui
from ui import DrawManager

offset_for_field = 0
field_size = 0
middle_offset = ui.middle_offset
GAME_WITH_BOT = False


class FieldParams:
    def __init__(self, size=10, *numbers):
        self.field_size = size
        ui.field_size = size
        self.nums_of_ships = [i for i in numbers]
        if len(numbers) == 0:
            self.nums_of_ships = [4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.offset = 0
        self.max_score = 0
        self.total = 0
        self.update_params()

    def update_params(self):
        self.offset = (15 - self.field_size) / 2
        self.total = 0
        self.max_score = 0
        for i in range(len(self.nums_of_ships)):
            self.total += self.nums_of_ships[i]
            self.max_score += self.nums_of_ships[i] * (i + 1)


class Field:
    def __init__(self, field_params):
        self.field_size = field_params.field_size
        self.nums_of_ships = field_params.nums_of_ships
        self.total = field_params.total
        self.cells_state = dict()
        self.set_cells_state()
        self.ships_to_draw = []
        self.ships = dict()

    def set_cells_state(self):
        for x in range(1, self.field_size + 1):
            for y in range(1, self.field_size + 1):
                self.cells_state[(x, y)] = True

    def generate_ships(self, drawer, label):
        self.ships = {}
        self.set_cells_state()
        self.ships_to_draw = []
        drawer.draw_field_window(label)
        while len(self.ships_to_draw) < self.total:
            for i in range(len(self.nums_of_ships)):
                self.generate_ships_by_length(self.nums_of_ships[i], i + 1)
        for ship in self.ships_to_draw:
            drawer.draw_ship(ship[0], ship[1], middle_offset)

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
                break

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

    def is_ship_can_be_put(self, ship):
        for cell in ship:
            if self.cells_state[cell] is False:
                return False
        return True

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

    def disable_cells(self, x, y):
        cells_around = [(x + i, y + j) for i in range(-1, 2) for j in
                        range(-1, 2)]
        for cell in cells_around:
            if cell[0] < 1 or cell[0] > self.field_size or cell[1] < 1 or\
                    cell[1] > self.field_size:
                continue
            self.cells_state[cell] = False


class Player:
    def __init__(self, field_params):
        self.field = Field(field_params)
        self.score = 0

    # def do_shot(self, event, offset):
    #     x, y = event.pos
    #     if left_margin + (
    #             offset + offset_for_field) * cell_size <= x <= \
    #             left_margin + (field_size + offset + offset_for_field) * \
    #             cell_size \
    #             and top_margin + offset_for_field * cell_size <= y <= \
    #             top_margin + (field_size + offset_for_field) * cell_size:
    #         fired_cell = int((x - left_margin) / cell_size + 1 - offset -
    #                          offset_for_field), int((y - top_margin) /
    #                                                 cell_size + 1 -
    #                                                 offset_for_field)


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
        for key in enemy.field.ships.keys():
            if enemy.field.ships[key][0] is False:
                return key


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
                                              offset_for_field) +
                              ui.left_margin,
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
                                              offset_for_field) +
                              ui.left_margin, ui.cell_size *
                              (y - 1 + offset_for_field) +
                              ui.top_margin, ui.RED)
        self.player.field.cells_state[(x, y)] = False
        neighbours = self.player.field.ships[(x, y)][1]
        for neighbour in neighbours:
            self.drawer.put_cross(ui.cell_size * (neighbour[0] - 1
                                                  + self.__offset +
                                                  offset_for_field) +
                                  ui.left_margin, ui.cell_size *
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
        self.game_start = False
        self.level_chosen = False
        self.field_set_up = False
        self.field_made = False
        self.ships_created = False
        self.bot_turn = False
        self.game_over = False
        self.game_finished = False

        self.field_params = FieldParams()
        self.drawer = DrawManager(self.field_params)
        self.labels = {}
        self.players = {}
        self.shootings = {}
        self.level = 0
        self.enemy_num = 2
        self.player_num = 1
        self.ships_to_draw = []
        self.drawn_ships = [0 for i in range(15)]

    def new_game(self):
        self.game_start = False
        self.level_chosen = False
        self.field_set_up = False
        self.field_made = False
        self.ships_created = False
        self.bot_turn = False
        self.game_over = False
        self.game_finished = False
        self.field_params = FieldParams()
        self.drawer = DrawManager(self.field_params)
        self.choose_mode()
        self.choose_level()
        self.setLabels()
        self.setup_field()
        self.setPlayers()
        self.setShootings()
        self.enemy_num = 2
        self.player_num = 1
        self.ships_to_draw = []
        self.drawn_ships = [0 for i in range(15)]
        self.create_field(1)
        for p in self.players.values():
            p.field.set_cells_state()
        self.play()
        self.finish()

    def setLabels(self):
        if GAME_WITH_BOT:
            self.labels = {1: 'Ваше поле',
                           2: 'Поле компьютера'}
        else:
            self.labels = {1: 'Игрок 1',
                           2: 'Игрок 2'}

    def setPlayers(self):
        if GAME_WITH_BOT:
            self.players = {1: Player(self.field_params),
                            2: Bot(1, self.field_params)}
        else:
            self.players = {1: Player(self.field_params),
                            2: Player(self.field_params)}

    def setShootings(self):
        self.shootings = {1: ShootingManager(1, self.players[1], self.drawer),
                          2: ShootingManager(2, self.players[2], self.drawer)}

    def choose_mode(self):
        global GAME_WITH_BOT
        self.drawer.draw_start_window()
        while not self.game_start:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_start = True
                    self.field_set_up = True
                    self.field_made = True
                    self.game_over = True
                    self.game_finished = True
                    self.level_chosen = True
                elif event.type == pygame.MOUSEBUTTONDOWN and \
                        ui.start_with_friend_btn.rect.collidepoint(mouse):
                    self.game_start = True
                    self.level_chosen = True
                    self.drawer.draw_field_settings_window()
                elif event.type == pygame.MOUSEBUTTONDOWN and \
                        ui.start_with_computer_btn.rect.collidepoint(mouse):
                    GAME_WITH_BOT = True
                    self.game_start = True
                    self.drawer.draw_levels_window()
            pygame.display.update()

    def choose_level(self):
        while not self.level_chosen:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.level_chosen = True
                    self.field_set_up = True
                    self.field_made = True
                    self.ships_created = True
                    self.game_over = True
                    self.game_finished = True
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and ui.level_1_btn.rect.collidepoint(mouse):
                    self.level = 1
                    self.level_chosen = True
                    self.drawer.draw_field_settings_window()
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and ui.level_2_btn.rect.collidepoint(mouse):
                    self.level = 2
                    self.level_chosen = True
                    self.drawer.draw_field_settings_window()
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and ui.level_3_btn.rect.collidepoint(mouse):
                    self.level = 3
                    self.level_chosen = True
                    self.drawer.draw_field_settings_window()
            pygame.display.update()

    def are_params_correct(self):
        return not self.zero_ships() and self.field_params.field_size > 0 and \
               not self.too_many_ships()

    def zero_ships(self):
        for num in self.field_params.nums_of_ships:
            if num != 0:
                return False
        return True

    def too_many_ships(self):
        total = 0
        for i in range(len(self.field_params.nums_of_ships)):
            total += self.field_params.nums_of_ships[i] * i + 1
        return total >= (self.field_params.field_size *
                         self.field_params.field_size) / 3

    def check_buttons(self, mouse):
        y_start = 2 * ui.top_margin
        x_start_right = ui.left_margin + 33.5 * ui.cell_size + 10
        x_start_left = ui.left_margin + 21.5 * ui.cell_size + 10
        koef = {14: 0, 13: 1.5, 12: 3, 11: 4.5, 10: 6, 9: 7.5, 8: 9, 7: 10.5, 6: 0, 5: 1.5, 4: 3, 3: 4.5, 2: 6, 1: 7.5, 0:9}
        for i in range(len(ui.minus_plus_buttons)):
            minus_btn = ui.minus_plus_buttons[i][0]
            plus_btn = ui.minus_plus_buttons[i][1]
            if 7 <= i <= 14:
                x_start = x_start_left
            else:
                x_start = x_start_right
            if plus_btn.rect.collidepoint(mouse):
                if self.field_params.field_size < i + 1:
                    self.drawer.make_label(
                        '{0}-палубный корабль не влезет на поле'.format(i + 1),
                        middle_offset, 17 * ui.cell_size, ui.RED)
                    continue
                self.drawer.update_param(self.field_params.nums_of_ships[i],
                                         1, x_start, y_start + koef[i] *
                                         ui.cell_size)
                self.field_params.nums_of_ships[i] += 1
            elif minus_btn.rect.collidepoint(mouse):
                if self.field_params.nums_of_ships[i] == 0:
                    continue
                self.drawer.update_param(self.field_params.nums_of_ships[i],
                                         -1, x_start, y_start + koef[i] *
                                         ui.cell_size)
                self.field_params.nums_of_ships[i] -= 1

    def setup_field(self):
        global offset_for_field, field_size
        while not self.field_set_up:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.field_set_up = True
                    self.field_made = True
                    self.game_over = True
                    self.game_finished = True
                    self.level_chosen = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if ui.next_btn.rect.collidepoint(mouse):
                        if self.are_params_correct():
                            self.field_params.update_params()
                            self.field_set_up = True
                            offset_for_field = self.field_params.offset
                            field_size = self.field_params.field_size
                            self.drawer = DrawManager(self.field_params)
                            self.drawer.draw_field_window(self.labels[1])
                        else:
                            if self.field_params.field_size == 0:
                                self.drawer.make_label(
                                    'Размер поля должен быть больше 0',
                                    middle_offset, 17 * ui.cell_size, ui.RED)
                            elif self.zero_ships():
                                self.drawer.make_label(
                                    'Слишком мало кораблей',
                                    middle_offset, 17 * ui.cell_size, ui.RED)
                            elif self.too_many_ships():
                                self.drawer.make_label(
                                    'Уменьшите количество кораблей',
                                    middle_offset, 17 * ui.cell_size, ui.RED)

                    elif ui.plus_size_btn.rect.collidepoint(mouse):
                        if self.field_params.field_size == 15:
                            continue
                        self.drawer.update_param(self.field_params.field_size,
                                                 1, ui.left_margin + 21 * ui.cell_size + 10, 1.4 * ui.top_margin)
                        self.field_params.field_size += 1

                    elif ui.minus_size_btn.rect.collidepoint(mouse):
                        if self.field_params.field_size == 2:
                            continue
                        self.drawer.update_param(self.field_params.field_size,
                                                 -1, ui.left_margin + 21 * ui.cell_size + 10, 1.4 * ui.top_margin)
                        self.field_params.field_size -= 1

                    else:
                        self.check_buttons(mouse)

            pygame.display.update()

    def redraw_field(self, player_label, num):
        self.drawer.draw_field_window(player_label)
        self.players[num].field.set_cells_state()
        self.players[num].field.ships = dict()
        self.ships_to_draw = []
        self.drawn_ships = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.field_made = False
        self.ships_created = False

    def create_field(self, player):
        can_draw = False
        drawing = False
        self.field_made = False
        self.ships_created = False
        x_start, y_start = 0, 0
        ship_size = 0, 0

        while not self.field_made:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.field_made = True
                    self.game_over = True
                    self.game_finished = True
                    self.level_chosen = True
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and ui.next_btn.rect.collidepoint(mouse) \
                        and self.ships_created:
                    self.field_made = True
                    if player == 1:
                        if GAME_WITH_BOT:
                            self.players[2].field.generate_ships(self.drawer,
                                                                 self.labels[2])
                            self.drawer.draw_game_window(self.labels[1],
                                                         self.labels[2])
                        else:
                            self.drawer.draw_field_window(self.labels[2])
                            self.create_field(2)
                    else:
                        self.drawer.draw_game_window(self.labels[1],
                                                     self.labels[2])
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and ui.random_btn.rect.collidepoint(mouse):
                    if can_draw:
                        can_draw = False
                        self.redraw_field(self.labels[player], player)
                    self.players[player].field.generate_ships(
                        self.drawer, self.labels[player])
                    self.ships_created = True
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and ui.clear_btn.rect.collidepoint(mouse):
                    self.redraw_field(self.labels[player], player)
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and ui.cancel_btn.rect.collidepoint(mouse) \
                        and can_draw:
                    if self.ships_to_draw:
                        last_ship = self.ships_to_draw.pop()
                        self.drawn_ships[len(last_ship) - 1] -= 1
                        self.players[player].field.remove_ship(last_ship)

                elif event.type == pygame.MOUSEBUTTONDOWN and \
                        ui.manual_btn.rect.collidepoint(mouse):
                    can_draw = True
                    self.redraw_field(self.labels[player], player)
                elif event.type == pygame.MOUSEBUTTONDOWN and can_draw:
                    drawing = True
                    x_start, y_start = event.pos
                    ship_size = 0, 0
                elif event.type == pygame.MOUSEMOTION and drawing:
                    x_end, y_end = event.pos
                    ship_size = x_end - x_start, y_end - y_start
                elif event.type == pygame.MOUSEBUTTONUP and drawing:
                    x_end, y_end = event.pos
                    ship_size = 0, 0
                    drawing = False
                    start_cell = (int((x_start - ui.left_margin) / ui.cell_size
                                      + 1 - offset_for_field - middle_offset),
                                  int((y_start - ui.top_margin) / ui.cell_size
                                      + 1 - offset_for_field))
                    end_cell = (int((x_end - ui.left_margin) / ui.cell_size
                                    + 1 - offset_for_field - middle_offset),
                                int((y_end - ui.top_margin) / ui.cell_size
                                    + 1 - offset_for_field))
                    if start_cell > end_cell:
                        start_cell, end_cell = end_cell, start_cell
                    temp_ship = []

                    if 1 <= start_cell[0] <= field_size \
                            and 1 <= start_cell[1] <= field_size \
                            and 1 <= end_cell[0] <= field_size \
                            and 1 <= end_cell[1] <= field_size:

                        ships_stop_list = []
                        for n in range(len(self.field_params.nums_of_ships)):
                            if self.field_params.nums_of_ships[n] == 0:
                                ships_stop_list.append(n + 1)
                        if end_cell[1] - start_cell[1] + 1 in ships_stop_list \
                                or end_cell[0] - start_cell[0] + 1 in \
                                ships_stop_list:
                            continue
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
                            self.field_params.nums_of_ships[
                                len(temp_ship) - 1]:
                        self.players[player].field.add_ship(temp_ship)
                        self.drawn_ships[len(temp_ship) - 1] += 1
                        self.ships_to_draw.append(temp_ship)
                if len(self.ships_to_draw) == self.field_params.total:
                    self.ships_created = True
            if not self.field_made and can_draw:
                self.drawer.draw_field_window(self.labels[player])
                pygame.draw.rect(ui.screen, ui.BLACK,
                                 ((x_start, y_start), ship_size), 3)
                for ship in self.ships_to_draw:
                    if len(ship) > 1 and ship[0][1] == ship[1][1]:
                        self.drawer.draw_ship(ship, 0, middle_offset)
                    else:
                        self.drawer.draw_ship(ship, 1, middle_offset)
            pygame.display.update()

    def change_turn(self):
        self.player_num, self.enemy_num = self.enemy_num, self.player_num
        if GAME_WITH_BOT:
            self.bot_turn = not self.bot_turn

    def is_winner(self):
        return self.players[self.player_num].score == self.field_params.max_score

    def play(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    self.game_finished = True
                    self.level_chosen = True
                elif event.type == pygame.MOUSEBUTTONDOWN or self.bot_turn:
                    offset = ui.OFFSETS[self.enemy_num]
                    enemy = self.players[self.enemy_num]
                    fired_cell = (0, 0)
                    if self.bot_turn:
                        fired_cell = self.players[2].do_shot(enemy, self.level)
                    else:
                        x, y = event.pos
                        if ui.left_margin + (offset + offset_for_field) * \
                                ui.cell_size <= x <= ui.left_margin + \
                                (field_size + offset + offset_for_field) * \
                                ui.cell_size and ui.top_margin + \
                                offset_for_field * \
                                ui.cell_size <= y <= \
                                ui.top_margin + (field_size +
                                                 offset_for_field) * \
                                ui.cell_size:
                            fired_cell = (
                            int((x - ui.left_margin) / ui.cell_size
                                + 1 - offset - offset_for_field),
                            int((y - ui.top_margin) / ui.cell_size
                                + 1 - offset_for_field))
                    if fired_cell != (0, 0):
                        if fired_cell in enemy.field.ships and \
                                enemy.field.ships[fired_cell][0] is False:
                            if self.bot_turn:
                                self.players[2].last_good_shot = fired_cell
                            enemy.field.cells_state[fired_cell] = False
                            self.players[self.player_num].score += 1
                            self.shootings[self.enemy_num].wounded(fired_cell[0],
                                                         fired_cell[1])
                            if self.bot_turn:
                                self.players[2].killed = False
                            self.drawer.update_score(self.players[self.player_num].score,
                                                ui.OFFSETS[self.player_num])

                            if self.shootings[self.enemy_num].is_killed(fired_cell[0],
                                                              fired_cell[1]):
                                if self.bot_turn:
                                    self.players[2].killed = True
                                    self.players[2].last_good_shot = (0, 0)
                                self.shootings[self.enemy_num].killed(fired_cell[0],
                                                            fired_cell[1])
                                ui.sound_killed.play()
                                self.drawer.make_label('Убил', middle_offset,
                                                  17 * ui.cell_size)
                            else:
                                ui.sound_wounded.play()
                                self.drawer.make_label('Ранил', middle_offset,
                                                  17 * ui.cell_size)
                            if self.is_winner():
                                self.game_over = True
                                if GAME_WITH_BOT:
                                    if self.player_num == 2:
                                        self.drawer.draw_win_window(
                                            'Компьютер победил')
                                    else:
                                        self.drawer.draw_win_window(
                                            'Вы победили')
                                else:
                                    self.drawer.draw_win_window(
                                        'Игрок {0} победил'.format(
                                            self.player_num))

                        elif fired_cell not in enemy.field.ships:
                            print(self.enemy_num)
                            if enemy.field.cells_state[fired_cell] is True:
                                self.change_turn()
                                self.shootings[self.player_num].missed(fired_cell[0],
                                                             fired_cell[1])
                                ui.sound_missed.play()
                                self.drawer.make_label('Промазал', middle_offset, 17 *
                                                  ui.cell_size)

            pygame.display.update()

    def finish(self):
        while not self.game_finished:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_finished = True
                    self.level_chosen = True
                elif event.type == pygame.MOUSEBUTTONDOWN and \
                        ui.restart_btn.rect.collidepoint(mouse):
                    self.new_game()
            pygame.display.update()


def main():
    game = Game()
    game.new_game()


if __name__ == '__main__':
    main()
    pygame.quit()
