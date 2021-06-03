import pygame
import random
import ui
from ui import DrawManager

offset_for_field = 0
field_size = 0
GAME_WITH_BOT = False


class FieldParams:
    def __init__(self, size=10, *numbers):
        self.field_size = size
        ui.field_size = size
        self.nums_of_ships = [i for i in numbers]
        if len(numbers) == 0:
            self.nums_of_ships = [4, 3, 2, 1, 0, 0, 0, 0, 0, 0]
        self.offset = (10 - size) / 2
        self.max_score = 0
        self.total = 0
        for i in range(len(self.nums_of_ships)):
            self.total += self.nums_of_ships[i]
            self.max_score += self.nums_of_ships[i] * (i + 1)


class Field:
    def __init__(self, field_params):
        self.field_size = field_params.field_size
        self.nums_of_ships = field_params.nums_of_ships
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
        drawer.draw_field_window(label)
        for i in range(len(self.nums_of_ships)):
            self.generate_ships_by_length(self.nums_of_ships[i], i + 1, drawer)

    def generate_ships_by_length(self, number_of_ships, length, drawer):
        s = 0
        while s < number_of_ships:
            x = random.randint(1, self.field_size)
            y = random.randint(1, self.field_size)
            turn = random.randint(0, 1)
            ship = self.make_ship(x, y, turn, length)
            if self.is_ship_can_be_put(ship):
                self.add_ship(ship)
                drawer.draw_ship(ship, turn, 4)
                s += 1

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

    def do_shot(self, enemy):
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

        return target[0], target[1]


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


def main():
    global GAME_WITH_BOT, offset_for_field, field_size

    field_params = FieldParams()

    drawer = DrawManager(field_params)

    game_over = False
    game_start = False
    field_set_up = False
    first_field_made = False
    second_field_made = False
    drawing = False
    can_draw = False
    ships_created_2 = False
    ships_created_1 = False

    ui.screen.fill(ui.WHITE)
    drawer.draw_start_window()

    while not game_start:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_start = True
                field_set_up = True
                first_field_made = True
                second_field_made = True
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    ui.start_with_friend_btn.rect.collidepoint(mouse):
                game_start = True
                drawer.draw_field_settings_window()
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    ui.start_with_computer_btn.rect.collidepoint(mouse):
                GAME_WITH_BOT = True
                game_start = True
                drawer.draw_field_settings_window()
        pygame.display.update()

    def are_params_correct():
        return not zero_ships() and field_params.field_size > 0 and \
               not too_many_ships()

    def zero_ships():
        for num in field_params.nums_of_ships:
            if num != 0:
                return False
        return True

    def too_many_ships():
        total = 0
        for i in range(len(field_params.nums_of_ships)):
            total += field_params.nums_of_ships[i] * i + 1
        return total >= (field_params.field_size * field_params.field_size) / 3

    if GAME_WITH_BOT:
        labels = {1: 'Ваше поле',
                  2: 'Поле компьютера'}
    else:
        labels = {1: 'Игрок 1',
                  2: 'Игрок 2'}

    y_start = ui.top_margin * 1.5
    x_start_right = ui.left_margin + 21.5 * ui.cell_size + 10
    x_start_left = ui.left_margin + 11.5 * ui.cell_size + 10
    while not field_set_up:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                field_set_up = True
                first_field_made = True
                second_field_made = True
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ui.next_btn.rect.collidepoint(mouse):
                    if are_params_correct():
                        field_set_up = True
                        offset_for_field = field_params.offset
                        field_size = field_params.field_size
                        drawer = DrawManager(field_params)
                        drawer.draw_field_window(labels[1])
                    else:
                        if field_params.field_size == 0:
                            drawer.make_label(
                                'Размер поля должен быть больше 0',
                                7.5, 11 * ui.cell_size, ui.RED)
                        elif zero_ships():
                            drawer.make_label(
                                'Слишком мало кораблей',
                                7.5, 11 * ui.cell_size, ui.RED)
                        elif too_many_ships():
                            drawer.make_label(
                                'Уменьшите количество кораблей',
                                7.5, 11 * ui.cell_size, ui.RED)

                elif ui.plus_size_btn.rect.collidepoint(mouse):
                    if field_params.field_size == 10:
                        continue
                    drawer.update_param(field_params.field_size, 1,
                                        ui.left_margin + 10 + 13 *
                                        ui.cell_size,
                                        y_start)
                    field_params.field_size += 1

                elif ui.minus_size_btn.rect.collidepoint(mouse):
                    if field_params.field_size == 2:
                        continue
                    drawer.update_param(field_params.field_size, -1,
                                        ui.left_margin + 10 + 13 *
                                        ui.cell_size,
                                        y_start)
                    field_params.field_size -= 1

                elif ui.plus_4_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 4:
                        drawer.make_label(
                            '4-палубный корабль не влезет на поле',
                            7.5, 11 * ui.cell_size, ui.RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[3], 1,
                                        x_start_right, y_start + 3 *
                                        ui.cell_size)
                    field_params.nums_of_ships[3] += 1
                elif ui.minus_4_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[3] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[3], -1,
                                        x_start_right, y_start + 3 *
                                        ui.cell_size)
                    field_params.nums_of_ships[3] -= 1

                elif ui.plus_3_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 3:
                        drawer.make_label(
                            '3-палубный корабль не влезет на поле',
                            7.5, 11 * ui.cell_size, ui.RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[2], 1,
                                        x_start_right, y_start + 4.5 *
                                        ui.cell_size)
                    field_params.nums_of_ships[2] += 1
                elif ui.minus_3_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[2] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[2], -1,
                                        x_start_right, y_start + 4.5 *
                                        ui.cell_size)
                    field_params.nums_of_ships[2] -= 1

                elif ui.plus_2_btn.rect.collidepoint(mouse):
                    drawer.update_param(field_params.nums_of_ships[1], 1,
                                        x_start_right, y_start + 6 *
                                        ui.cell_size)
                    field_params.nums_of_ships[1] += 1
                elif ui.minus_2_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[1] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[1], -1,
                                        x_start_right, y_start + 6 *
                                        ui.cell_size)
                    field_params.nums_of_ships[1] -= 1

                elif ui.plus_1_btn.rect.collidepoint(mouse):
                    drawer.update_param(field_params.nums_of_ships[0], 1,
                                        x_start_right,
                                        y_start + 7.5 * ui.cell_size)
                    field_params.nums_of_ships[0] += 1
                elif ui.minus_1_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[0] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[0], -1,
                                        x_start_right, y_start + 7.5 *
                                        ui.cell_size)
                    field_params.nums_of_ships[0] -= 1

                elif ui.plus_5_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 5:
                        drawer.make_label(
                            '5-палубный корабль не влезет на поле',
                            7.5, 11 * ui.cell_size, ui.RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[4], 1,
                                        x_start_right,
                                        y_start + 1.5 * ui.cell_size)
                    field_params.nums_of_ships[4] += 1
                elif ui.minus_5_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[4] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[4], -1,
                                        x_start_right, y_start + 1.5 *
                                        ui.cell_size)
                    field_params.nums_of_ships[4] -= 1

                elif ui.plus_10_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 10:
                        drawer.make_label(
                            '10-палубный корабль не влезет на поле',
                            7.5, 11 * ui.cell_size, ui.RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[9], 1,
                                        x_start_left,
                                        y_start + 1.5 * ui.cell_size)
                    field_params.nums_of_ships[9] += 1
                elif ui.minus_10_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[9] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[9], -1,
                                        x_start_left, y_start + 1.5 *
                                        ui.cell_size)
                    field_params.nums_of_ships[9] -= 1

                elif ui.plus_9_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 9:
                        drawer.make_label(
                            '9-палубный корабль не влезет на поле',
                            7.5, 11 * ui.cell_size, ui.RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[8], 1,
                                        x_start_left,
                                        y_start + 3 * ui.cell_size)
                    field_params.nums_of_ships[8] += 1
                elif ui.minus_9_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[8] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[8], -1,
                                        x_start_left, y_start + 3 *
                                        ui.cell_size)
                    field_params.nums_of_ships[8] -= 1

                elif ui.plus_8_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 8:
                        drawer.make_label(
                            '8-палубный корабль не влезет на поле',
                            7.5, 11 * ui.cell_size, ui.RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[7], 1,
                                        x_start_left,
                                        y_start + 4.5 * ui.cell_size)
                    field_params.nums_of_ships[7] += 1
                elif ui.minus_8_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[7] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[7], -1,
                                        x_start_left, y_start + 4.5 *
                                        ui.cell_size)
                    field_params.nums_of_ships[7] -= 1

                elif ui.plus_7_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 7:
                        drawer.make_label(
                            '7-палубный корабль не влезет на поле',
                            7.5, 11 * ui.cell_size, ui.RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[6], 1,
                                        x_start_left,
                                        y_start + 6 * ui.cell_size)
                    field_params.nums_of_ships[6] += 1
                elif ui.minus_7_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[6] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[6], -1,
                                        x_start_left, y_start + 6 *
                                        ui.cell_size)
                    field_params.nums_of_ships[6] -= 1

                elif ui.plus_6_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 6:
                        drawer.make_label(
                            '6-палубный корабль не влезет на поле',
                            7.5, 11 * ui.cell_size, ui.RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[5], 1,
                                        x_start_left,
                                        y_start + 7.5 * ui.cell_size)
                    field_params.nums_of_ships[5] += 1
                elif ui.minus_6_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[5] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[5], -1,
                                        x_start_left, y_start + 7.5 *
                                        ui.cell_size)
                    field_params.nums_of_ships[5] -= 1
        pygame.display.update()

    if GAME_WITH_BOT:
        players = {1: Player(field_params),
                   2: Bot(1, field_params)}
    else:
        players = {1: Player(field_params),
                   2: Player(field_params)}

    shootings = {1: ShootingManager(1, players[1], drawer),
                 2: ShootingManager(2, players[2], drawer)}
    enemy_num = 2
    player_num = 1

    x_start, y_start = 0, 0
    start = (0, 0)
    ship_size = 0, 0
    drawn_ships = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # сколько кораблей
    # какой длины нарисовано
    ships_to_draw = []

    def redraw_field(player_label, num):
        nonlocal drawn_ships, ships_to_draw, first_field_made, \
            ships_created_1, second_field_made, ships_created_2
        drawer.draw_field_window(player_label)
        players[num].field.set_cells_state()
        players[num].field.ships = dict()
        ships_to_draw = []
        drawn_ships = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if num == 1:
            first_field_made = False
            ships_created_1 = False
        else:
            second_field_made = False
            ships_created_2 = False

    while not first_field_made:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                first_field_made = True
                second_field_made = True
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    ui.next_btn.rect.collidepoint(mouse) and ships_created_1:
                first_field_made = True
                if GAME_WITH_BOT:
                    players[2].field.generate_ships(drawer, 'Поле компьютера')
                    second_field_made = True
                    ships_created_2 = True
                    drawer.draw_game_window('Ваше поле', 'Поле компьютера')
                else:
                    drawer.draw_field_window('Игрок 2')
            elif event.type == pygame.MOUSEBUTTONDOWN \
                    and ui.random_btn.rect.collidepoint(mouse):
                if can_draw:
                    can_draw = False
                    redraw_field(labels[1], 1)
                players[1].field.generate_ships(drawer, labels[1])
                ships_created_1 = True
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    ui.clear_btn.rect.collidepoint(mouse):
                redraw_field(labels[1], 1)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    ui.cancel_btn.rect.collidepoint(mouse) and can_draw:
                if ships_to_draw:
                    last_ship = ships_to_draw.pop()
                    drawn_ships[len(last_ship) - 1] -= 1
                    players[1].field.remove_ship(last_ship)

            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    ui.manual_btn.rect.collidepoint(mouse):
                can_draw = True
                redraw_field(labels[1], 1)
            elif event.type == pygame.MOUSEBUTTONDOWN and can_draw:
                drawing = True
                x_start, y_start = event.pos
                start = x_start, y_start
                ship_size = 0, 0
            elif event.type == pygame.MOUSEMOTION and drawing:
                x_end, y_end = event.pos
                end = x_end, y_end
                ship_size = x_end - x_start, y_end - y_start
            elif event.type == pygame.MOUSEBUTTONUP and drawing:
                x_end, y_end = event.pos
                ship_size = 0, 0
                drawing = False
                start_cell = (int((x_start - ui.left_margin) / ui.cell_size
                                  + 1 - offset_for_field - 4),
                              int((y_start - ui.top_margin) / ui.cell_size
                                  + 1 - offset_for_field))
                end_cell = (int((x_end - ui.left_margin) / ui.cell_size
                                + 1 - offset_for_field - 4),
                            int((y_end - ui.top_margin) / ui.cell_size
                                + 1 - offset_for_field))
                print(start_cell, end_cell)
                if start_cell > end_cell:
                    start_cell, end_cell = end_cell, start_cell
                temp_ship = []
                if 1 <= start_cell[0] <= field_size \
                        and 1 <= start_cell[1] <= field_size \
                        and 1 <= end_cell[0] <= field_size \
                        and 1 <= end_cell[1] <= field_size:
                    no_ships = []  # кораблей какой длины не должно быть
                    for n in range(len(field_params.nums_of_ships)):
                        if field_params.nums_of_ships[n] == 0:
                            no_ships.append(n + 1)
                    if end_cell[1] - start_cell[1] in no_ships or \
                            end_cell[0] - start_cell[0] in no_ships:
                        continue
                    else:
                        if start_cell[0] == end_cell[0]:
                            for cell in range(start_cell[1], end_cell[1] + 1):
                                temp_ship.append((start_cell[0], cell))
                        elif start_cell[1] == end_cell[1]:
                            for cell in range(start_cell[0], end_cell[0] + 1):
                                temp_ship.append((cell, start_cell[1]))
                if temp_ship:
                    if players[1].field.is_ship_can_be_put(temp_ship) and \
                            drawn_ships[len(temp_ship) - 1] < \
                            field_params.nums_of_ships[len(temp_ship) - 1]:
                        players[1].field.add_ship(temp_ship)
                        drawn_ships[len(temp_ship) - 1] += 1
                        ships_to_draw.append(temp_ship)
            if len(ships_to_draw) == field_params.total:
                ships_created_1 = True
        if not first_field_made and can_draw:
            drawer.draw_field_window(labels[1])
            pygame.draw.rect(ui.screen, ui.BLACK, (start, ship_size), 3)
            for ship in ships_to_draw:
                if len(ship) > 1 and ship[0][1] == ship[1][1]:
                    drawer.draw_ship(ship, 0, 4)
                else:
                    drawer.draw_ship(ship, 1, 4)
        pygame.display.update()

    can_draw = False

    while not second_field_made:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                second_field_made = True
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    ui.next_btn.rect.collidepoint(mouse) and ships_created_2:
                second_field_made = True
                drawer.draw_game_window(labels[1], labels[2])
            elif event.type == pygame.MOUSEBUTTONDOWN \
                    and ui.random_btn.rect.collidepoint(mouse):
                if can_draw:
                    can_draw = False
                    redraw_field(labels[2], 2)
                players[2].field.generate_ships(drawer, labels[2])
                ships_created_2 = True
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    ui.clear_btn.rect.collidepoint(mouse):
                redraw_field(labels[2], 2)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    ui.cancel_btn.rect.collidepoint(mouse) and can_draw:
                if ships_to_draw:
                    last_ship = ships_to_draw.pop()
                    drawn_ships[len(last_ship) - 1] -= 1
                    players[2].field.remove_ship(last_ship)

            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    ui.manual_btn.rect.collidepoint(mouse):
                can_draw = True
                redraw_field(labels[2], 2)
            elif event.type == pygame.MOUSEBUTTONDOWN and can_draw:
                drawing = True
                x_start, y_start = event.pos
                start = x_start, y_start
                ship_size = 0, 0
            elif event.type == pygame.MOUSEMOTION and drawing:
                x_end, y_end = event.pos
                end = x_end, y_end
                ship_size = x_end - x_start, y_end - y_start
            elif event.type == pygame.MOUSEBUTTONUP and drawing:
                x_end, y_end = event.pos
                ship_size = 0, 0
                drawing = False
                start_cell = (int((x_start - ui.left_margin) / ui.cell_size
                                  + 1 - offset_for_field - 4),
                              int((y_start - ui.top_margin) / ui.cell_size
                                  + 1 - offset_for_field))
                end_cell = (int((x_end - ui.left_margin) / ui.cell_size
                                + 1 - offset_for_field - 4),
                            int((y_end - ui.top_margin) / ui.cell_size
                                + 1 - offset_for_field))
                print(start_cell, end_cell)
                if start_cell > end_cell:
                    start_cell, end_cell = end_cell, start_cell
                temp_ship = []
                if 1 <= start_cell[0] <= field_size \
                        and 1 <= start_cell[1] <= field_size \
                        and 1 <= end_cell[0] <= field_size \
                        and 1 <= end_cell[1] <= field_size:
                    no_ships = []  # кораблей какой длины не должно быть
                    for n in range(len(field_params.nums_of_ships)):
                        if field_params.nums_of_ships[n] == 0:
                            no_ships.append(n + 1)
                    if end_cell[1] - start_cell[1] in no_ships or \
                            end_cell[0] - start_cell[0] in no_ships:
                        continue
                    else:
                        if start_cell[0] == end_cell[0]:
                            for cell in range(start_cell[1], end_cell[1] + 1):
                                temp_ship.append((start_cell[0], cell))
                        elif start_cell[1] == end_cell[1]:
                            for cell in range(start_cell[0], end_cell[0] + 1):
                                temp_ship.append((cell, start_cell[1]))
                if temp_ship:
                    if players[2].field.is_ship_can_be_put(temp_ship) and \
                            drawn_ships[len(temp_ship) - 1] < \
                            field_params.nums_of_ships[len(temp_ship) - 1]:
                        players[2].field.add_ship(temp_ship)
                        drawn_ships[len(temp_ship) - 1] += 1
                        ships_to_draw.append(temp_ship)
            if len(ships_to_draw) == field_params.total:
                ships_created_2 = True
        if not second_field_made and can_draw:
            drawer.draw_field_window(labels[2])
            pygame.draw.rect(ui.screen, ui.BLACK, (start, ship_size), 3)
            for ship in ships_to_draw:
                if len(ship) > 1 and ship[0][1] == ship[1][1]:
                    drawer.draw_ship(ship, 0, 4)
                else:
                    drawer.draw_ship(ship, 1, 4)
        pygame.display.update()

    for p in players.values():
        p.field.set_cells_state()

    def change_turn():
        nonlocal player_num, enemy_num, bot_turn
        player_num, enemy_num = enemy_num, player_num
        if GAME_WITH_BOT:
            bot_turn = not bot_turn

    def is_winner(player):
        return players[player].score == field_params.max_score

    bot_turn = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN or bot_turn:

                offset = ui.OFFSETS[enemy_num]
                enemy = players[enemy_num]
                fired_cell = (0, 0)
                if bot_turn:
                    fired_cell = players[2].do_shot(enemy)
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
                        fired_cell = (int((x - ui.left_margin) / ui.cell_size
                                          + 1 - offset - offset_for_field),
                                      int((y - ui.top_margin) / ui.cell_size
                                          + 1 - offset_for_field))
                if fired_cell != (0, 0):
                    if fired_cell in enemy.field.ships and \
                            enemy.field.ships[fired_cell][0] is False:
                        if bot_turn:
                            players[2].last_good_shot = fired_cell
                        enemy.field.cells_state[fired_cell] = False
                        players[player_num].score += 1
                        shootings[enemy_num].wounded(fired_cell[0],
                                                     fired_cell[1])
                        if bot_turn:
                            players[2].killed = False
                        drawer.update_score(players[player_num].score,
                                            ui.OFFSETS[player_num])

                        if shootings[enemy_num].is_killed(fired_cell[0],
                                                          fired_cell[1]):
                            if bot_turn:
                                players[2].killed = True
                                players[2].last_good_shot = (0, 0)
                            shootings[enemy_num].killed(fired_cell[0],
                                                        fired_cell[1])
                            ui.sound_killed.play()
                            drawer.make_label('Убил', 7.5, 12 * ui.cell_size)
                        else:
                            ui.sound_wounded.play()
                            drawer.make_label('Ранил', 7.5, 12 * ui.cell_size)
                        if is_winner(player_num):
                            if GAME_WITH_BOT:
                                if player_num == 2:
                                    drawer.make_label(
                                        'Компьютер победил', 7.5,
                                        12 * ui.cell_size, ui.RED)
                                else:
                                    drawer.make_label('Вы победили', 7.5,
                                                      12 * ui.cell_size,
                                                      ui.RED)
                            else:
                                drawer.make_label(
                                    'Игрок {0} победил'.format(player_num),
                                    7.5,
                                    12 * ui.cell_size, ui.RED)
                            game_over = True
                    elif fired_cell not in enemy.field.ships:
                        if enemy.field.cells_state[fired_cell] is True:
                            change_turn()
                            shootings[player_num].missed(fired_cell[0],
                                                         fired_cell[1])
                            ui.sound_missed.play()
                            drawer.make_label('Промазал', 7.5, 12 *
                                              ui.cell_size)

        pygame.display.update()


if __name__ == '__main__':
    main()
    pygame.quit()
