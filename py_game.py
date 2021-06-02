import pygame
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

cell_size = 30
left_margin = 60
top_margin = 90
screen_width, screen_height = left_margin * 2 + cell_size * 25, \
                              top_margin * 2 + 40 + cell_size * 10
OFFSETS = {1: 0,
           2: 15}

btn_width, btn_height = 175, 45

pygame.init()

pygame.mixer.music.load('morskoj-priboj.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play()

sound_missed = pygame.mixer.Sound('splash.mp3')
sound_missed.set_volume(0.8)
sound_wounded = pygame.mixer.Sound('shot.mp3')
sound_wounded.set_volume(2)
sound_killed = pygame.mixer.Sound('killed-shot.mp3')
sound_killed.set_volume(1.3)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Морской бой')

font_size = int(cell_size / 1.5)
font = pygame.font.SysFont('notosans', font_size)


offset_for_field = 0
field_size = 0
GAME_WITH_BOT = False


class FieldParams:
    def __init__(self, size=10, *numbers):
        global field_size
        self.field_size = size
        field_size = size
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
            for cell in cells_around:
                if cell[0] < 1 or cell[0] > self.field_size or cell[1] < 1 or \
                        cell[1] > self.field_size:
                    continue
                self.cells_state[cell] = True


    def disable_cells(self, x, y):
        cells_around = [(x + i, y + j) for i in range(-1, 2) for j in
                        range(-1, 2)]
        for cell in cells_around:
            if cell[0] < 1 or cell[0] > self.field_size or cell[1] < 1 or cell[1] > self.field_size:
                continue
            self.cells_state[cell] = False



class Player:
    def __init__(self, field_params):
        self.field = Field(field_params)
        self.score = 0

    def do_shot(self, event, offset):
        x, y = event.pos
        if left_margin + (
                offset + offset_for_field) * cell_size <= x <= left_margin + \
                (
                        field_size + offset + offset_for_field) * cell_size \
                and top_margin + offset_for_field * cell_size <= y <= \
                top_margin + (field_size + offset_for_field) * cell_size:
            fired_cell = int((x - left_margin) / cell_size + 1 - offset -
                             offset_for_field), int((y - top_margin) /
                                                    cell_size + 1 -
                                                    offset_for_field)


class Bot:
    def __init__(self, difficulty, field_params):
        self.level = difficulty
        self.last_shot_good = False
        self.last_shot = (0, 0)
        self.last_good_shot = (0,0)
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
            crd_rec = [[crd[0] - 1, crd[1]], [crd[0] + 1, crd[1]], [crd[0], crd[1] - 1], [crd[0], crd[1] + 1]]
            crd_rec = filter(lambda x: 1 <= x[0] <= enemy.field.field_size and 1 <= x[1] <= enemy.field.field_size, crd_rec)
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


class Button:
    def __init__(self, button_title, drawer):
        self.title = button_title
        self.title_width, self.title_height = font.size(self.title)
        self.rect = pygame.Rect((0, 0, 0, 0))
        self.drawer = drawer

    def change_color_on_hover(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.drawer.draw_button(self, BLACK)


class DrawManager:

    def __init__(self):
        self.start_with_friend_btn = Button('Играть с другом',
                                            self)
        self.start_with_computer_btn = Button('Играть с компьютером', self)
        self.random_btn = Button('Расставить рандомно', self)
        self.manual_btn = Button('Нарисовать', self)
        self.next_btn = Button('Дальше', self)
        self.clear_btn = Button('Стереть всё', self)
        self.cancel_btn = Button('Отмена', self)

        self.minus_size_btn = Button('-', self)
        self.plus_size_btn = Button('+', self)
        self.minus_10_btn = Button('-', self)
        self.minus_9_btn = Button('-', self)
        self.minus_8_btn = Button('-', self)
        self.minus_7_btn = Button('-', self)
        self.minus_6_btn = Button('-', self)
        self.minus_5_btn = Button('-', self)
        self.plus_10_btn = Button('+', self)
        self.plus_9_btn = Button('+', self)
        self.plus_8_btn = Button('+', self)
        self.plus_7_btn = Button('+', self)
        self.plus_6_btn = Button('+', self)
        self.plus_5_btn = Button('+', self)
        self.minus_4_btn = Button('-', self)
        self.plus_4_btn = Button('+', self)
        self.minus_3_btn = Button('-', self)
        self.plus_3_btn = Button('+', self)
        self.minus_2_btn = Button('-', self)
        self.plus_2_btn = Button('+', self)
        self.minus_1_btn = Button('-', self)
        self.plus_1_btn = Button('+', self)

        self.field_settings_buttons = [(self.minus_1_btn, self.plus_1_btn),
                                       (self.minus_2_btn, self.plus_2_btn),
                                       (self.minus_3_btn, self.plus_3_btn),
                                       (self.minus_4_btn, self.plus_4_btn),
                                       (self.minus_5_btn, self.plus_5_btn),
                                       (self.minus_6_btn, self.plus_6_btn),
                                       (self.minus_7_btn, self.plus_7_btn),
                                       (self.minus_8_btn, self.plus_8_btn),
                                       (self.minus_9_btn, self.plus_9_btn),
                                       (self.minus_10_btn, self.plus_10_btn)]

    @staticmethod
    def draw_button(button, x_start, y_start, width=btn_width, height=btn_height, color=BLACK):
        title_params = (x_start + width / 2 - button.title_width / 2,
                        y_start + height / 2 - button.title_height / 2)
        pygame.draw.rect(screen, color, (x_start, y_start, width, height))
        screen.blit(font.render(button.title, True, WHITE), title_params)
        button.rect = pygame.Rect((x_start, y_start, width, height))

    @staticmethod
    def draw_field(offset):
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        for i in range(field_size + 1):
            pygame.draw.line(screen, BLACK,
                             (left_margin + (offset + offset_for_field) * cell_size,
                              top_margin + (i + offset_for_field) *
                              cell_size), (left_margin + (offset + field_size + offset_for_field) * cell_size,
                                           top_margin + (i + offset_for_field) * cell_size))
            pygame.draw.line(screen, BLACK,
                             (left_margin + (i + offset + offset_for_field) * cell_size,
                              top_margin + offset_for_field * cell_size),
                             (left_margin + (i + offset + offset_for_field) * cell_size,
                              top_margin + (field_size + offset_for_field) * cell_size))

            if i < field_size:
                num = font.render(str(i + 1), True, BLACK)
                let = font.render(letters[i], True, BLACK)

                num_width = num.get_width()
                num_height = num.get_height()
                let_width = let.get_width()

                screen.blit(num, (left_margin - (cell_size // 2 + num_width // 2) +
                                  (offset + offset_for_field) * cell_size,
                                  top_margin + (i + offset_for_field) * cell_size +
                                  (cell_size // 2 - num_height // 2)))

                screen.blit(let, (left_margin + (i + offset_for_field) * cell_size +
                                  (cell_size // 2 - let_width // 2) + offset *
                                  cell_size, top_margin - num_height * 1.5 + offset_for_field * cell_size))

    @staticmethod
    def make_label(text, x_offset, y_offset=-cell_size, color=BLACK):
        label = font.render(text, True, color)
        label_width = label.get_width()
        label_height = label.get_height()
        pygame.draw.rect(screen, WHITE, (left_margin + x_offset * cell_size +
                                         (10 * cell_size - label_width) / 2 - label_width * 0.5,
                                         top_margin - label_height + y_offset, label_width * 2, label_height))
        screen.blit(label, (left_margin + x_offset * cell_size +
                            (10 * cell_size - label_width) / 2,
                            top_margin - label_height + y_offset))

    def draw_start_window(self):
        self.draw_button(self.start_with_friend_btn, (screen_width - btn_width * 2) / 3,
                         (screen_height - btn_height) / 2)
        self.draw_button(self.start_with_computer_btn, (screen_width - btn_width * 2) *
                         (2 / 3) + btn_width,
                         (screen_height - btn_height) / 2)

    def draw_ship_examples(self, first_ship_size, last_ship_size, x_start,
                           y_start):
        for i in range(first_ship_size, last_ship_size, -1):
            for j in range(i + 1):
                pygame.draw.line(screen, BLACK,
                                 (x_start + j * cell_size, y_start),
                                 (
                                     x_start + j * cell_size,
                                     y_start + cell_size))

            pygame.draw.line(screen, BLACK, (x_start, y_start),
                             (x_start + j * cell_size, y_start))
            pygame.draw.line(screen, BLACK, (x_start, y_start + cell_size),
                             (x_start + j * cell_size, y_start + cell_size))

            y_start += 1.5 * cell_size
            x_start += 0.5 * cell_size

    def draw_plus_minus_buttons(self, first_btn, last_btn, x_start, y_start):
        for i in range(first_btn - 1, last_btn):
            minus_btn, plus_btn = self.field_settings_buttons[i][0], \
                                  self.field_settings_buttons[i][1]
            self.draw_button(minus_btn, x_start, y_start, cell_size, cell_size)
            self.draw_button(plus_btn, x_start + 2 * cell_size + 20, y_start,
                             cell_size, cell_size)
            y_start -= 1.5 * cell_size

    def draw_params_labels(self, field_params):
        x_start = left_margin + 21.5 * cell_size + 10
        y_start = 1.5 * top_margin + 7.5 * cell_size
        for i in range(len(field_params.nums_of_ships) // 2):
            self.update_param(field_params.nums_of_ships[i], 0, x_start, y_start)
            y_start -= 1.5 * cell_size

        x_start = left_margin + 11.5 * cell_size + 10
        y_start = 1.5 * top_margin + 7.5 * cell_size
        for i in range(len(field_params.nums_of_ships) // 2, len(field_params.nums_of_ships)):
            self.update_param(field_params.nums_of_ships[i], 0, x_start, y_start)
            y_start -= 1.5 * cell_size

    def draw_field_settings_window(self, field_params):
        screen.fill(WHITE)

        self.make_label('Настройте параметры поля', 7.5, 0)
        self.make_label('Размер поля', 5, 2.2 * cell_size)

        y_start = top_margin * 1.5 + 1.5 * cell_size
        self.draw_ship_examples(field_params.field_size, field_params.field_size // 2, left_margin, y_start)
        self.draw_ship_examples(field_params.field_size // 2, 0, left_margin + 15 * cell_size, y_start)

        self.draw_button(self.minus_size_btn, left_margin + 12 * cell_size, top_margin + 1.5 * cell_size, cell_size, cell_size)
        self.draw_button(self.plus_size_btn, left_margin + 14 * cell_size + 20, top_margin + 1.5 * cell_size, cell_size, cell_size)

        self.draw_plus_minus_buttons(1, 5, left_margin + 20.5 * cell_size, 1.5 * top_margin + 7.5 * cell_size)
        self.draw_plus_minus_buttons(6, 10, left_margin + 10.5 * cell_size, 1.5 * top_margin + 7.5 * cell_size)

        self.update_param(field_params.field_size, 0, left_margin + 10 + 13 * cell_size, top_margin * 1.5)
        self.draw_params_labels(field_params)

        self.draw_button(self.next_btn,
                         (screen_width - btn_width * 2 - 5) / 2 +
                         btn_width + 10, top_margin + 10 * cell_size +
                         btn_height)

    def update_param(self, param, delta, x_start, y_start):
        rect_params = (x_start, y_start, cell_size, cell_size)
        pygame.draw.rect(screen, WHITE, rect_params)
        pygame.draw.rect(screen, BLACK, rect_params, width=2)
        num = font.render(str(param + delta), True, BLACK)
        screen.blit(num,
                    (x_start + 0.3 * cell_size, y_start + 0.25 * cell_size))

    def draw_field_window(self, label):
        screen.fill(WHITE)
        self.draw_field(4)
        self.make_label(label, 7.5)
        self.draw_button(self.next_btn, (screen_width - btn_width * 2 - 5) / 2 +
                         2 * btn_width + 20, top_margin + 10 * cell_size +
                         btn_height)
        self.draw_button(self.manual_btn, left_margin + cell_size *
                         (field_size + 5), top_margin)
        self.draw_button(self.random_btn, left_margin + cell_size *
                         (field_size + 5), top_margin + 1.5 * btn_height)
        self.draw_button(self.cancel_btn, left_margin + cell_size *
                         (field_size + 5), top_margin + 3 * btn_height)
        self.draw_button(self.clear_btn, left_margin + cell_size *
                         (field_size + 5), top_margin + 4.5 * btn_height)

    @staticmethod
    def draw_ship(ship, turn, offset):
        ship.sort(key=lambda i: i[1])
        x = cell_size * (ship[0][0] - 1) + left_margin + (offset + offset_for_field) * cell_size
        y = cell_size * (ship[0][
                             1] - 1) + top_margin + offset_for_field * cell_size
        if turn == 1:
            width = cell_size
            height = cell_size * len(ship)
        else:
            width = cell_size * len(ship)
            height = cell_size
        pygame.draw.rect(screen, BLACK, ((x, y), (width, height)),
                         width=cell_size // 10)

    def draw_game_window(self, player1, player2):
        global OFFSETS
        screen.fill(WHITE)
        for offset in OFFSETS.values():
            self.draw_field(offset)

        self.make_label(player1, 0)
        self.make_label(player2, 15)
        self.update_score(0, 0)
        self.update_score(0, 15)

    @staticmethod
    def update_score(score, offset):
        score_label = font.render('Очки: {0}'.format(score), True, BLACK)
        score_label_width = score_label.get_width()
        score_label_height = score_label.get_height()
        x_start = left_margin + (
                offset + 5) * cell_size - score_label_width // 2
        y_start = top_margin + 10.5 * cell_size
        background_rect = pygame.Rect(
            x_start, y_start, score_label_width, score_label_height)
        screen.fill(WHITE, background_rect)
        screen.blit(score_label, (x_start, y_start))

    @staticmethod
    def put_dots(dots, offset):
        for (x, y) in dots:
            if x < 1 or y < 1 or x > field_size or y > field_size:
                continue
            x_d = x - 0.5 + offset + offset_for_field
            y_d = y + offset_for_field
            pygame.draw.circle(screen, BLACK, (cell_size * x_d + left_margin,
                                               cell_size * (y_d - 0.5) +
                                               top_margin), cell_size // 6)

    @staticmethod
    def put_cross(x_start, y_start, color=BLACK):
        pygame.draw.line(screen, color, (x_start, y_start),
                         (x_start + cell_size, y_start + cell_size), cell_size // 10)
        pygame.draw.line(screen, color, (x_start, y_start + cell_size),
                         (x_start + cell_size, y_start), cell_size // 10)


class ShootingManager:
    def __init__(self, player_num, player, drawer):
        self.player = player
        self.__offset = OFFSETS[player_num]
        self.drawer = drawer

    def missed(self, x, y):
        self.drawer.put_dots([(x, y)], self.__offset)
        self.player.field.cells_state[(x, y)] = False

    def wounded(self, x, y):
        self.drawer.put_cross(cell_size * (x - 1 + self.__offset + offset_for_field) + left_margin,
                              cell_size * (y - 1 + offset_for_field) + top_margin)
        self.drawer.put_dots([(x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1),
                              (x - 1, y + 1)], self.__offset)
        self.player.field.ships[(x, y)] = (True, self.player.field.ships[(x, y)][1])
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
        self.drawer.put_cross(cell_size * (x - 1 + self.__offset + offset_for_field) +
                              left_margin, cell_size * (y - 1 + offset_for_field) +
                              top_margin, RED)
        self.player.field.cells_state[(x, y)] = False
        neighbours = self.player.field.ships[(x, y)][1]
        for neighbour in neighbours:
            self.drawer.put_cross(cell_size * (neighbour[0] - 1 + self.__offset + offset_for_field) +
                                  left_margin, cell_size * (neighbour[1] - 1 + offset_for_field) +
                                  top_margin, RED)
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
    global offset_for_field, field_size, OFFSETS, GAME_WITH_BOT

    field_params = FieldParams()

    drawer = DrawManager()

    game_over = False
    game_start = False
    field_set_up = False
    first_field_made = False
    second_field_made = False
    drawing = False
    can_draw = False
    ships_created_2 = False
    ships_created_1 = False

    screen.fill(WHITE)
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
                    drawer.start_with_friend_btn.rect.collidepoint(mouse):
                game_start = True
                drawer.draw_field_settings_window(field_params)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    drawer.start_with_computer_btn.rect.collidepoint(mouse):
                GAME_WITH_BOT = True
                game_start = True
                drawer.draw_field_settings_window(field_params)
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

    y_start = top_margin * 1.5
    x_start_right = left_margin + 21.5 * cell_size + 10
    x_start_left = left_margin + 11.5 * cell_size + 10
    while not field_set_up:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                field_set_up = True
                first_field_made = True
                second_field_made = True
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if drawer.next_btn.rect.collidepoint(mouse):
                    if are_params_correct():
                        field_set_up = True
                        offset_for_field = field_params.offset
                        field_size = field_params.field_size
                        if GAME_WITH_BOT:
                            drawer.draw_field_window('Ваше поле')
                        else:
                            drawer.draw_field_window('Игрок 1')
                    else:
                        if field_params.field_size == 0:
                            drawer.make_label(
                                'Размер поля должен быть больше 0',
                                7.5, 11 * cell_size, RED)
                        elif zero_ships():
                            drawer.make_label(
                                'Слишком мало кораблей',
                                7.5, 11 * cell_size, RED)
                        elif too_many_ships():
                            drawer.make_label(
                                'Уменьшите количество кораблей',
                                7.5, 11 * cell_size, RED)

                elif drawer.plus_size_btn.rect.collidepoint(mouse):
                    if field_params.field_size == 10:
                        continue
                    drawer.update_param(field_params.field_size, 1,
                                        left_margin + 10 + 13 * cell_size,
                                        y_start)
                    field_params.field_size += 1

                elif drawer.minus_size_btn.rect.collidepoint(mouse):
                    if field_params.field_size == 2:
                        continue
                    drawer.update_param(field_params.field_size, -1,
                                        left_margin + 10 + 13 * cell_size,
                                        y_start)
                    field_params.field_size -= 1

                elif drawer.plus_4_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 4:
                        drawer.make_label(
                            '4-палубный корабль не влезет на поле',
                            7.5, 11 * cell_size, RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[3], 1,
                                        x_start_right, y_start + 3 * cell_size)
                    field_params.nums_of_ships[3] += 1
                elif drawer.minus_4_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[3] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[3], -1,
                                        x_start_right, y_start + 3 * cell_size)
                    field_params.nums_of_ships[3] -= 1

                elif drawer.plus_3_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 3:
                        drawer.make_label(
                            '3-палубный корабль не влезет на поле',
                            7.5, 11 * cell_size, RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[2], 1,
                                        x_start_right, y_start + 4.5 *
                                        cell_size)
                    field_params.nums_of_ships[2] += 1
                elif drawer.minus_3_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[2] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[2], -1,
                                        x_start_right, y_start + 4.5 *
                                        cell_size)
                    field_params.nums_of_ships[2] -= 1

                elif drawer.plus_2_btn.rect.collidepoint(mouse):
                    drawer.update_param(field_params.nums_of_ships[1], 1,
                                        x_start_right, y_start + 6 * cell_size)
                    field_params.nums_of_ships[1] += 1
                elif drawer.minus_2_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[1] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[1], -1,
                                        x_start_right, y_start + 6 * cell_size)
                    field_params.nums_of_ships[1] -= 1

                elif drawer.plus_1_btn.rect.collidepoint(mouse):
                    drawer.update_param(field_params.nums_of_ships[0], 1,
                                        x_start_right,
                                        y_start + 7.5 * cell_size)
                    field_params.nums_of_ships[0] += 1
                elif drawer.minus_1_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[0] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[0], -1,
                                        x_start_right, y_start + 7.5 *
                                        cell_size)
                    field_params.nums_of_ships[0] -= 1

                elif drawer.plus_5_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 5:
                        drawer.make_label(
                            '5-палубный корабль не влезет на поле',
                            7.5, 11 * cell_size, RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[4], 1,
                                        x_start_right,
                                        y_start + 1.5 * cell_size)
                    field_params.nums_of_ships[4] += 1
                elif drawer.minus_5_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[4] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[4], -1,
                                        x_start_right, y_start + 1.5 *
                                        cell_size)
                    field_params.nums_of_ships[4] -= 1

                elif drawer.plus_10_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 10:
                        drawer.make_label(
                            '10-палубный корабль не влезет на поле',
                            7.5, 11 * cell_size, RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[9], 1,
                                        x_start_left,
                                        y_start + 1.5 * cell_size)
                    field_params.nums_of_ships[9] += 1
                elif drawer.minus_10_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[9] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[9], -1,
                                        x_start_left, y_start + 1.5 *
                                        cell_size)
                    field_params.nums_of_ships[9] -= 1

                elif drawer.plus_9_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 9:
                        drawer.make_label(
                            '9-палубный корабль не влезет на поле',
                            7.5, 11 * cell_size, RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[8], 1,
                                        x_start_left,
                                        y_start + 3 * cell_size)
                    field_params.nums_of_ships[8] += 1
                elif drawer.minus_9_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[8] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[8], -1,
                                        x_start_left, y_start + 3 *
                                        cell_size)
                    field_params.nums_of_ships[8] -= 1

                elif drawer.plus_8_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 8:
                        drawer.make_label(
                            '8-палубный корабль не влезет на поле',
                            7.5, 11 * cell_size, RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[7], 1,
                                        x_start_left,
                                        y_start + 4.5 * cell_size)
                    field_params.nums_of_ships[7] += 1
                elif drawer.minus_8_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[7] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[7], -1,
                                        x_start_left, y_start + 4.5 *
                                        cell_size)
                    field_params.nums_of_ships[7] -= 1

                elif drawer.plus_7_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 7:
                        drawer.make_label(
                            '7-палубный корабль не влезет на поле',
                            7.5, 11 * cell_size, RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[6], 1,
                                        x_start_left,
                                        y_start + 6 * cell_size)
                    field_params.nums_of_ships[6] += 1
                elif drawer.minus_7_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[6] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[6], -1,
                                        x_start_left, y_start + 6 *
                                        cell_size)
                    field_params.nums_of_ships[6] -= 1

                elif drawer.plus_6_btn.rect.collidepoint(mouse):
                    if field_params.field_size < 6:
                        drawer.make_label(
                            '6-палубный корабль не влезет на поле',
                            7.5, 11 * cell_size, RED)
                        continue
                    drawer.update_param(field_params.nums_of_ships[5], 1,
                                        x_start_left,
                                        y_start + 7.5 * cell_size)
                    field_params.nums_of_ships[5] += 1
                elif drawer.minus_6_btn.rect.collidepoint(mouse):
                    if field_params.nums_of_ships[5] == 0:
                        continue
                    drawer.update_param(field_params.nums_of_ships[5], -1,
                                        x_start_left, y_start + 7.5 *
                                        cell_size)
                    field_params.nums_of_ships[5] -= 1
        pygame.display.update()

    if GAME_WITH_BOT:
        players = {1: Player(field_params),
                   2: Bot(1, field_params)}
        labels = {1: 'Ваше поле',
                  2: 'Поле компьютера'}
    else:
        players = {1: Player(field_params),
                   2: Player(field_params)}
        labels = {1: 'Игрок 1',
                  2: 'Игрок 2'}

    shootings = {1: ShootingManager(1, players[1], drawer),
                 2: ShootingManager(2, players[2], drawer)}
    enemy_num = 2
    player_num = 1

    x_start, y_start = 0, 0
    start = (0, 0)
    ship_size = 0, 0
    drawn_ships = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # сколько кораблей какой длины нарисовано
    ships_to_draw = []

    def redraw_field(player_label, num):
        nonlocal drawn_ships, ships_to_draw, first_field_made, ships_created_1, second_field_made, ships_created_2
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
                    drawer.next_btn.rect.collidepoint(mouse) and ships_created_1:
                first_field_made = True
                if GAME_WITH_BOT:
                    players[2].field.generate_ships(drawer, 'Поле компьютера')
                    second_field_made = True
                    ships_created_2 = True
                    drawer.draw_game_window('Ваше поле', 'Поле компьютера')
                else:
                    drawer.draw_field_window('Игрок 2')
            elif event.type == pygame.MOUSEBUTTONDOWN \
                    and drawer.random_btn.rect.collidepoint(mouse):
                if can_draw:
                    can_draw = False
                    redraw_field(labels[1], 1)
                players[1].field.generate_ships(drawer, labels[1])
                ships_created_1 = True
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    drawer.clear_btn.rect.collidepoint(mouse):
                redraw_field(labels[1], 1)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    drawer.cancel_btn.rect.collidepoint(mouse) and can_draw:
                if ships_to_draw:
                    last_ship = ships_to_draw.pop()
                    drawn_ships[len(last_ship) - 1] -= 1
                    players[1].field.remove_ship(last_ship)

            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    drawer.manual_btn.rect.collidepoint(mouse):
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
                start_cell = (int((x_start - left_margin) / cell_size + 1 -
                                  offset_for_field - 4),
                              int((y_start - top_margin) / cell_size + 1 -
                                  offset_for_field))
                end_cell = (int((x_end - left_margin) / cell_size + 1 -
                                offset_for_field - 4),
                            int((y_end - top_margin) / cell_size + 1 -
                                offset_for_field))
                print(start_cell, end_cell)
                if start_cell > end_cell:
                    start_cell, end_cell = end_cell, start_cell
                temp_ship = []
                if 1 <= start_cell[0] <= field_size \
                        and 1 <= start_cell[1] <= field_size \
                        and 1 <= end_cell[0] <= field_size \
                        and 1 <= end_cell[1] <= field_size:
                    no_ships = [] # кораблей какой длины не должно быть
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
            pygame.draw.rect(screen, BLACK, (start, ship_size), 3)
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
            elif event.type == pygame.MOUSEBUTTONDOWN and drawer.next_btn.rect.collidepoint(mouse) and ships_created_2:
                second_field_made = True
                drawer.draw_game_window(labels[1], labels[2])
            elif event.type == pygame.MOUSEBUTTONDOWN \
                    and drawer.random_btn.rect.collidepoint(mouse):
                if can_draw:
                    can_draw = False
                    redraw_field(labels[2], 2)
                players[2].field.generate_ships(drawer, labels[2])
                ships_created_2 = True
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                 drawer.clear_btn.rect.collidepoint(mouse):
                redraw_field(labels[2], 2)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    drawer.cancel_btn.rect.collidepoint(mouse) and can_draw:
                if ships_to_draw:
                    last_ship = ships_to_draw.pop()
                    drawn_ships[len(last_ship) - 1] -= 1
                    players[2].field.remove_ship(last_ship)

            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    drawer.manual_btn.rect.collidepoint(mouse):
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
                start_cell = (int((x_start - left_margin) / cell_size + 1 -
                                  offset_for_field - 4),
                              int((y_start - top_margin) / cell_size + 1 -
                                  offset_for_field))
                end_cell = (int((x_end - left_margin) / cell_size + 1 -
                                offset_for_field - 4),
                            int((y_end - top_margin) / cell_size + 1 -
                                offset_for_field))
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
            pygame.draw.rect(screen, BLACK, (start, ship_size), 3)
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

                offset = OFFSETS[enemy_num]
                enemy = players[enemy_num]
                fired_cell = (0, 0)
                if bot_turn:
                    fired_cell = players[2].do_shot(enemy)
                else:
                    x, y = event.pos
                    if left_margin + (offset + offset_for_field) * cell_size <= x <= left_margin + \
                            (
                                    field_size + offset + offset_for_field) * cell_size and top_margin + offset_for_field * cell_size <= y <= \
                            top_margin + (field_size + offset_for_field) * cell_size:
                        fired_cell = (int((x - left_margin) / cell_size + 1 - offset - offset_for_field),
                                      int((y - top_margin) / cell_size + 1 - offset_for_field))
                if fired_cell != (0, 0):
                    if fired_cell in enemy.field.ships and \
                            enemy.field.ships[fired_cell][0] is False:
                        if bot_turn:
                            players[2].last_good_shot = fired_cell
                        enemy.field.cells_state[fired_cell] = False
                        players[player_num].score += 1
                        shootings[enemy_num].wounded(fired_cell[0], fired_cell[1])
                        if bot_turn:
                            players[2].killed = False
                        drawer.update_score(players[player_num].score, OFFSETS[player_num])

                        if shootings[enemy_num].is_killed(fired_cell[0], fired_cell[1]):
                            if bot_turn:
                                players[2].killed = True
                                players[2].last_good_shot = (0, 0)
                            shootings[enemy_num].killed(fired_cell[0], fired_cell[1])
                            sound_killed.play()
                            drawer.make_label('Убил', 7.5, 12 * cell_size)
                        else:
                            sound_wounded.play()
                            drawer.make_label('Ранил', 7.5, 12 * cell_size)
                        if is_winner(player_num):
                            if GAME_WITH_BOT:
                                if player_num == 2:
                                    drawer.make_label(
                                        'Компьютер победил', 7.5,
                                        12 * cell_size, RED)
                                else:
                                    drawer.make_label('Вы победили',
                                        7.5,
                                        12 * cell_size, RED)
                            else:
                                drawer.make_label(
                                    'Игрок {0} победил'.format(player_num),
                                    7.5,
                                    12 * cell_size, RED)
                            game_over = True
                    elif fired_cell not in enemy.field.ships:
                        if enemy.field.cells_state[fired_cell] is True:
                            change_turn()
                            shootings[player_num].missed(fired_cell[0], fired_cell[1])
                            sound_missed.play()
                            drawer.make_label('Промазал', 7.5, 12 * cell_size)

        pygame.display.update()


if __name__ == '__main__':
    main()
    pygame.quit()
