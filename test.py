import pygame
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 153, 153)

OFFSETS = {1: 0,
           2: 15}
offset_for_field = 0
field_size = 10

cell_size = 30
left_margin = 60
top_margin = 90

screen_width, screen_height = left_margin * 2 + cell_size * 25, top_margin * 2 + 40 + cell_size * 10

btn_width, btn_height = 175, 45

pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Морской бой')

font_size = int(cell_size / 1.5)
font = pygame.font.SysFont('notosans', font_size)


class FieldParams:
    def __init__(self, field_size=10, num_4=1, num_3=2, num_2=3, num_1=4):
        self.field_size = field_size
        self.num_4 = num_4
        self.num_3 = num_3
        self.num_2 = num_2
        self.num_1 = num_1
        self.offset = (10 - field_size) / 2


class Field:
    def __init__(self, player, field_params):
        self.field_size = field_params.field_size
        self.num_4 = field_params.num_4
        self.num_3 = field_params.num_3
        self.num_2 = field_params.num_2
        self.num_1 = field_params.num_1
        self.cells_state = dict()
        self.set_cells_state()
        self.player = player
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

        numbers_of_ships = [self.num_1, self.num_2, self.num_3, self.num_4]
        for i in range(len(numbers_of_ships)):
            self.generate_ships_by_length(numbers_of_ships[i], i + 1, drawer)

    def generate_ships_by_length(self, number_of_ships, length, drawer):
        s = 0
        while s < number_of_ships:
            x = random.randint(1, self.field_size)
            y = random.randint(1, self.field_size)
            turn = random.randint(0, 1)
            ship = self.make_ship(x, y, turn, length)
            if self.is_ship_can_be_put(ship):
                self.add_ship(ship)
                drawer.draw_ship(ship, turn, 7.5)
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

    def disable_cells(self, x, y):
        cells_around = [(x + i, y + j) for i in range(-1, 2) for j in
                        range(-1, 2)]
        for cell in cells_around:
            if cell[0] < 1 or cell[0] > self.field_size or cell[1] < 1 or cell[1] > self.field_size:
                continue
            self.cells_state[cell] = False


class Button:
    def __init__(self, button_title, drawer):
        self.title = button_title
        self.title_width, self.title_height = font.size(self.title)
        self.rect = pygame.Rect((0, 0, 0, 0))
        self.drawer = drawer

    def change_color_on_hover(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.drawer.draw_button(self, GREEN)


class ShootingManager:
    def __init__(self, player, drawer):
        self.player = player
        self.__offset = OFFSETS[player.player]
        self.drawer = drawer

    def missed(self, x, y):
        self.drawer.put_dots([(x, y)], self.__offset)
        self.player.cells_state[(x, y)] = False

    def wounded(self, x, y):
        self.drawer.put_cross(cell_size * (x - 1 + self.__offset + offset_for_field) + left_margin,
                         cell_size * (y - 1 + offset_for_field) + top_margin)
        self.drawer.put_dots([(x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1),
                         (x - 1, y + 1)], self.__offset)
        self.player.ships[(x, y)] = (True, self.player.ships[(x, y)][1])

    def is_killed(self, x, y):
        killed_ship = [(x, y)]
        for neighbour in self.player.ships[(x, y)][1]:
            n_x = neighbour[0]
            n_y = neighbour[1]
            if self.player.ships[(n_x, n_y)][0]:
                killed_ship.append((n_x, n_y))
        if len(killed_ship) == len(self.player.ships[(x, y)][1]) + 1:
            return True
        return False

    def killed(self, x, y):
        self.drawer.put_cross(cell_size * (x - 1 + self.__offset + offset_for_field) +
                         left_margin, cell_size * (y - 1 + offset_for_field) +
                         top_margin, RED)
        neighbours = self.player.ships[(x, y)][1]
        for neighbour in neighbours:
            self.drawer.put_cross(cell_size * (neighbour[0] - 1 + self.__offset + offset_for_field) +
                             left_margin, cell_size * (neighbour[1] - 1 + offset_for_field) +
                             top_margin, RED)
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
        self.drawer.put_dots(dots, self.__offset)


class DrawManager:

    def __init__(self):
        self.start_with_friend_btn = Button('Играть с другом',
                                            self)
        self.start_with_computer_btn = Button('Играть с компьютером', self)
        self.random_btn = Button('Расставить рандомно', self)
        self.next_btn = Button('Дальше', self)

        self.minus_size_btn = Button('-', self)
        self.plus_size_btn = Button('+', self)
        self.minus_4_btn = Button('-', self)
        self.plus_4_btn = Button('+', self)
        self.minus_3_btn = Button('-', self)
        self.plus_3_btn = Button('+', self)
        self.minus_2_btn = Button('-', self)
        self.plus_2_btn = Button('+', self)
        self.minus_1_btn = Button('-', self)
        self.plus_1_btn = Button('+', self)

        self.field_settings_buttons = [(self.minus_size_btn,
                                        self.plus_size_btn),
                                       (self.minus_4_btn, self.plus_4_btn),
                                       (self.minus_3_btn, self.plus_3_btn),
                                       (self.minus_2_btn, self.plus_2_btn),
                                       (self.minus_1_btn, self.plus_1_btn)]


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
                             (left_margin + (offset + offset_for_field) * cell_size, top_margin + (i + offset_for_field) *
                              cell_size), (left_margin + (offset + field_size + offset_for_field) * cell_size,
                                           top_margin + (i + offset_for_field) * cell_size))
            pygame.draw.line(screen, BLACK,
                             (left_margin + (i + offset + offset_for_field) * cell_size, top_margin + offset_for_field * cell_size),
                             (left_margin + (i + offset + offset_for_field) * cell_size,
                              top_margin + (field_size + offset_for_field) * cell_size))

            if i < field_size:
                num = font.render(str(i + 1), True, BLACK)
                let = font.render(letters[i], True, BLACK)

                num_width = num.get_width()
                num_height = num.get_height()
                let_width = let.get_width()

                screen.blit(num, (left_margin - (cell_size // 2 + num_width // 2) +
                                  (offset + offset_for_field) * cell_size, top_margin + (i + offset_for_field) * cell_size +
                                  (cell_size // 2 - num_height // 2)))

                screen.blit(let, (left_margin + (i + offset_for_field) * cell_size +
                                  (cell_size // 2 - let_width // 2) + offset *
                                  cell_size, top_margin - num_height * 1.5 + offset_for_field * cell_size))

    @staticmethod
    def make_label(text, x_offset, y_offset=-cell_size, color=BLACK):
        label = font.render(text, True, color)
        label_width = label.get_width()
        print(label_width)
        label_height = label.get_height()
        pygame.draw.rect(screen, WHITE, (left_margin + x_offset * cell_size +
                            (10 * cell_size - label_width) / 2 - label_width * 0.5, top_margin - label_height + y_offset, label_width * 2, label_height))
        screen.blit(label, (left_margin + x_offset * cell_size +
                            (10 * cell_size - label_width) / 2,
                            top_margin - label_height + y_offset))

    def draw_start_window(self):
        self.draw_button(self.start_with_friend_btn, (screen_width - btn_width * 2) / 3,
                                            (screen_height - btn_height) / 2)
        self.draw_button(self.start_with_computer_btn, (screen_width - btn_width * 2) *
                                              (2 / 3) + btn_width,
                                              (screen_height - btn_height) / 2)

    def draw_field_settings_window(self, field_params):
        screen.fill(WHITE)

        self.make_label('Настройте параметры поля', 7.5, 0)
        self.make_label('Размер поля', 5, 2.2 * cell_size)

        x_start = left_margin + 8 * cell_size
        y_start = top_margin * 1.5 + 1.5 * cell_size

        for i in range(4, 0, -1):
            for j in range(i + 1):
                pygame.draw.line(screen, BLACK, (x_start + j * cell_size, y_start), (x_start + j * cell_size, y_start + cell_size))

            pygame.draw.line(screen, BLACK, (x_start, y_start), (x_start + j * cell_size, y_start))
            pygame.draw.line(screen, BLACK, (x_start, y_start + cell_size), (x_start + j * cell_size, y_start + cell_size))

            y_start += 1.5 * cell_size
            x_start += 0.5 * cell_size

        x_start = left_margin + 13 * cell_size
        y_start = top_margin * 1.5
        for minus_btn, plus_btn in self.field_settings_buttons:
            self.draw_button(minus_btn, x_start, y_start, cell_size, cell_size)
            self.draw_button(plus_btn, x_start + 2.5 * cell_size + 20, y_start, cell_size, cell_size)
            y_start += 1.5 * cell_size

        params = [field_params.field_size, field_params.num_4,
                  field_params.num_3, field_params.num_2, field_params.num_1]
        y_start = top_margin * 1.5
        for p in params:
            self.update_param(p, 0, y_start)
            y_start += 1.5 * cell_size
        self.draw_button(self.next_btn, (screen_width - btn_width * 2 - 5) / 2 +
                               btn_width + 10, top_margin + 10 * cell_size +
                               btn_height)

    def update_param(self, param, delta, y_start):
        x_start = left_margin + 10 + 14 * cell_size
        rect_params = (x_start, y_start, cell_size * 1.5, cell_size)
        pygame.draw.rect(screen, WHITE, rect_params)
        pygame.draw.rect(screen, BLACK, rect_params, width=2)
        num = font.render(str(param + delta), True, BLACK)
        screen.blit(num, (x_start + 0.5 * cell_size, y_start + 0.25 * cell_size))

    def draw_field_window(self, label):
        screen.fill(WHITE)
        self.draw_field(7.5)
        self.make_label(label, 7.5)
        self.draw_button(self.next_btn, (screen_width - btn_width * 2 - 5) / 2 +
                               btn_width + 10, top_margin + 10 * cell_size +
                               btn_height)
        self.draw_button(self.random_btn, (screen_width - btn_width * 2 - 5) / 2,
                                 top_margin + 10 * cell_size + btn_height)

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


def main():
    global offset_for_field, field_size, OFFSETS

    field_params = FieldParams()

    drawer = DrawManager()

    game_over = False
    game_start = False
    field_set_up = False
    first_field_made = False
    second_field_made = False
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
        pygame.display.update()

    def are_params_correct():
        return not zero_ships() and field_params.field_size > 0 and \
               not too_many_ships()

    def zero_ships():
        return field_params.num_1 == 0 and field_params.num_2 == 0 \
               and field_params.num_3 == 0 and field_params.num_4 == 0

    def too_many_ships():
        return field_params.num_4 * 4 + field_params.num_3 * 3 + \
               field_params.num_2 * 2 + field_params.num_1 >= \
               (field_params.field_size * field_params.field_size) / 2

    y_start = top_margin * 1.5
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
                        field_params = FieldParams(field_params.field_size, field_params.num_4, field_params.num_3, field_params.num_2, field_params.num_1)
                        offset_for_field = field_params.offset
                        field_size = field_params.field_size
                        drawer.draw_field_window('Игрок 1')
                    else:
                        if field_params.field_size == 0:
                            drawer.make_label(
                                'Размер поля должен быть больше 0',
                                7.5, 10 * cell_size, RED)
                        elif zero_ships():
                            drawer.make_label(
                                'Слишком мало кораблей',
                                7.5, 10 * cell_size, RED)
                        elif too_many_ships():
                            drawer.make_label(
                                'Уменьшите количество кораблей',
                                7.5, 10 * cell_size, RED)

                elif drawer.plus_size_btn.rect.collidepoint(mouse):
                    if field_params.field_size == 10:
                        continue
                    drawer.update_param(field_params.field_size, 1, y_start)
                    field_params.field_size += 1
                elif drawer.minus_size_btn.rect.collidepoint(mouse):
                    if field_params.field_size == 0:
                        continue
                    drawer.update_param(field_params.field_size, -1, y_start)
                    field_params.field_size -= 1

                elif drawer.plus_4_btn.rect.collidepoint(mouse):
                    drawer.update_param(field_params.num_4, 1, y_start + 1.5 * cell_size)
                    field_params.num_4 += 1
                elif drawer.minus_4_btn.rect.collidepoint(mouse):
                    if field_params.num_4 == 0:
                        continue
                    drawer.update_param(field_params.num_4, -1, y_start + 1.5 * cell_size)
                    field_params.num_4 -= 1

                elif drawer.plus_3_btn.rect.collidepoint(mouse):
                    drawer.update_param(field_params.num_3, 1,
                                        y_start + 3 * cell_size)
                    field_params.num_3 += 1
                elif drawer.minus_3_btn.rect.collidepoint(mouse):
                    if field_params.num_3 == 0:
                        continue
                    drawer.update_param(field_params.num_3, -1,
                                        y_start + 3 * cell_size)
                    field_params.num_3 -= 1

                elif drawer.plus_2_btn.rect.collidepoint(mouse):
                    drawer.update_param(field_params.num_2, 1,
                                        y_start + 4.5 * cell_size)
                    field_params.num_2 += 1
                elif drawer.minus_2_btn.rect.collidepoint(mouse):
                    if field_params.num_2 == 0:
                        continue
                    drawer.update_param(field_params.num_2, -1,
                                        y_start + 4.5 * cell_size)
                    field_params.num_2 -= 1

                elif drawer.plus_1_btn.rect.collidepoint(mouse):
                    drawer.update_param(field_params.num_1, 1,
                                        y_start + 6 * cell_size)
                    field_params.num_1 += 1
                elif drawer.minus_1_btn.rect.collidepoint(mouse):
                    if field_params.num_1 == 0:
                        continue
                    drawer.update_param(field_params.num_1, -1,
                                        y_start + 6 * cell_size)
                    field_params.num_1 -= 1

        pygame.display.update()

    players = {1: Field(1, field_params),
               2: Field(2, field_params)}
    scores = {2: 0,
              1: 0}
    shootings = {1: ShootingManager(players[1], drawer),
                 2: ShootingManager(players[2], drawer)}
    enemy_num = 2
    player_num = 1

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
                drawer.draw_field_window('Игрок 2')
            elif event.type == pygame.MOUSEBUTTONDOWN \
                    and drawer.random_btn.rect.collidepoint(mouse):
                players[1].generate_ships(drawer, 'Игрок 1')

                ships_created_1 = True
        pygame.display.update()

    while not second_field_made:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                second_field_made = True
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN and drawer.next_btn.rect.collidepoint(mouse) and ships_created_2:
                second_field_made = True
                drawer.draw_game_window('Игрок 1', 'Игрок 2')
            elif event.type == pygame.MOUSEBUTTONDOWN \
                    and drawer.random_btn.rect.collidepoint(mouse):
                players[2].generate_ships(drawer, 'Игрок 2')

                ships_created_2 = True
        pygame.display.update()

    for p in players.values():
        p.set_cells_state()

    def change_turn():
        nonlocal player_num, enemy_num
        player_num, enemy_num = enemy_num, player_num

    def is_winner(player):
        return scores[player] == field_params.num_4 * 4 + \
               field_params.num_3 * 3 + field_params.num_2 * 2 \
               + field_params.num_1

    pygame.mixer.music.load('morskoj-priboj.mp3')
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()

    sound_missed = pygame.mixer.Sound('splash.mp3')
    sound_missed.set_volume(0.8)
    sound_wounded = pygame.mixer.Sound('shot.mp3')
    sound_wounded.set_volume(2)
    sound_killed = pygame.mixer.Sound('killed-shot.mp3')
    sound_wounded.set_volume(1.3)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                offset = OFFSETS[enemy_num]
                enemy = players[enemy_num]
                if left_margin + (offset + offset_for_field) * cell_size <= x <= left_margin + \
                        (field_size + offset + offset_for_field) * cell_size and top_margin + offset_for_field * cell_size <= y <= \
                        top_margin + (field_size + offset_for_field) * cell_size:
                    fired_cell = (int((x - left_margin) / cell_size + 1 - offset - offset_for_field),
                                  int((y - top_margin) / cell_size + 1 - offset_for_field))
                    print(fired_cell)
                    if fired_cell in enemy.ships and \
                            enemy.ships[fired_cell][0] is False:
                        scores[player_num] += 1
                        shootings[enemy_num].wounded(fired_cell[0], fired_cell[1])
                        drawer.update_score(scores[player_num], OFFSETS[player_num])
                        if shootings[enemy_num].is_killed(fired_cell[0], fired_cell[1]):
                            shootings[enemy_num].killed(fired_cell[0], fired_cell[1])
                            sound_killed.play()
                            drawer.make_label('Убил', 7.5, 12 * cell_size)
                        else:
                            sound_wounded.play()
                            drawer.make_label('Ранил', 7.5, 12 * cell_size)
                        if is_winner(player_num):
                            drawer.make_label(
                                'Игрок {0} победил'.format(player_num), 7.5,
                                12 * cell_size, RED)
                    elif fired_cell not in enemy.ships:
                        if enemy.cells_state[fired_cell] is True:
                            change_turn()
                        shootings[player_num].missed(fired_cell[0], fired_cell[1])
                        sound_missed.play()
                        drawer.make_label('Промазал', 7.5, 12 * cell_size)

        pygame.display.update()


if __name__ == '__main__':
    main()
    pygame.quit()