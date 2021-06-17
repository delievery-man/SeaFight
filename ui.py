import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (65, 105, 225)
BLUE = (0, 0, 139)
BUTTON_BLUE = (70,130,180)
cell_size = 30
left_margin = 60
top_margin = 90
screen_width, screen_height = left_margin * 2 + cell_size * 40, \
                              top_margin * 2 + cell_size * 16
btn_width, btn_height = 180, 60

OFFSETS = {1: 3,
           2: 26}

middle_offset = (screen_width - 15 * cell_size) / 2 / cell_size

pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Морской бой')

font_size = 24
font = pygame.font.SysFont('notosans', font_size)

pygame.mixer.music.load('morskoj-priboj.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play()

sound_missed = pygame.mixer.Sound('splash.mp3')
sound_missed.set_volume(0.8)
sound_wounded = pygame.mixer.Sound('shot.mp3')
sound_wounded.set_volume(2)
sound_killed = pygame.mixer.Sound('killed-shot.mp3')
sound_killed.set_volume(1.3)

class FieldParams:
    def __init__(self):
        self.field_size = 10
        self.nums_of_ships = [4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.total_amount_of_ships = 10
        self.max_score = 20
        self.offset = (15 - self.field_size) / 2

    def update_params(self):
        self.total_amount_of_ships = sum(self.nums_of_ships)
        self.max_score = sum(self.nums_of_ships[i] * (i + 1) for i in
                             range(len(self.nums_of_ships)))
        self.offset = (15 - self.field_size) / 2


class Button:
    def __init__(self, button_title, params, width=btn_width,
                 height=btn_height):
        self.title = button_title
        self.title_width, self.title_height = font.size(self.title)
        self.x_start, self.y_start = params[0], params[1]
        self.width, self.height = width, height
        self.rect = pygame.Rect((self.x_start, self.y_start,
                                 width, height))


class Label:
    def __init__(self, text, params, color=BUTTON_BLUE):
        self.text = font.render(text, True, color)
        self.width, self.height = font.size(text)
        self.x_start, self.y_start = params[0], params[1]


class Window:
    def __init__(self):
        self.fields = 0
        self.buttons = []
        self.labels = []

    def add_buttons(self, *buttons):
        for button in buttons:
            self.buttons.append(button)

    def add_labels(self, *labels):
        for label in labels:
            self.labels.append(label)


class UIManager:
    def __init__(self):
        self.field_params = FieldParams()
        self.create_buttons()
        self.create_windows()

    def set_plus_minus_btns_params(self):
        size = self.field_params.field_size
        x_start = left_margin + (size + 1) * cell_size
        y_start = 5 * cell_size
        if size % 2 == 0:
            middle = size // 2
        else:
            middle = size // 2 + 1
        self.plus_minus_buttons = []
        start, end = 0, middle
        for j in range(2):
            for i in range(start, end):
                minus_btn = Button('-', (x_start, y_start), cell_size,
                                   cell_size)
                plus_btn = Button('+', (x_start + 3 * cell_size, y_start),
                                  cell_size, cell_size)
                self.plus_minus_buttons.append(minus_btn)
                self.plus_minus_buttons.append(plus_btn)
                y_start += 2 * cell_size

            x_start += 21 * cell_size
            y_start = 5 * cell_size
            start, end = middle, size

    def create_buttons(self):
        self.start_with_friend_button = Button(
            'Играть с другом', ((screen_width - btn_width * 2) / 3,
                                (screen_height - btn_height) / 2))
        self.start_with_computer_button = Button(
            'Играть с компьютером', ((screen_width - btn_width * 2) * (2 / 3)
                                     + btn_width, (screen_height - btn_height)
                                     / 2))
        y_start = (screen_height - 3 * btn_height - 2 * cell_size) / 2
        self.level_1_button = Button(
            'Лёгкий уровень', ((screen_width - btn_width) / 2, y_start))
        self.level_2_button = Button(
            'Средний уровень', ((screen_width - btn_width) / 2,
                                y_start + btn_height + cell_size))
        self.level_3_button = Button(
            'Сложный уровень', ((screen_width - btn_width) / 2,
                                y_start + 2 * btn_height + 2 * cell_size))
        self.next_button = Button(
            'Дальше', (screen_width - left_margin - btn_width,
                       screen_height - 3 * cell_size))
        self.random_button = Button(
            'Расставить рандомно', (screen_width - left_margin - btn_width,
                                    top_margin + 1.5 * btn_height))
        self.manual_button = Button(
            'Нарисовать', (screen_width - left_margin - btn_width, top_margin))
        self.clear_button = Button(
            'Стереть всё', (screen_width - left_margin - btn_width,
                            top_margin + 4.5 * btn_height))
        self.cancel_button = Button(
            'Отмена', (screen_width - left_margin - btn_width,
                       top_margin + 3 * btn_height))
        self.restart_button = Button(
            'Начать заново', ((screen_width - btn_width) / 2, screen_height // 2))
        self.plus_size_button = Button(
            '+', (left_margin + 23 * cell_size, 3 * cell_size),
            cell_size, cell_size)
        self.minus_size_btn = Button(
            '-', (left_margin + 20 * cell_size, 3 * cell_size),
            cell_size, cell_size)
        self.set_plus_minus_btns_params()

    def create_windows(self):
        self.start_window = Window()
        self.start_window.add_buttons(self.start_with_friend_button,
                                      self.start_with_computer_button)

        self.levels_window = Window()
        self.levels_window.add_buttons(
            self.level_1_button, self.level_2_button, self.level_3_button)
        self.levels_window.add_labels(Label('Выберите уровень сложности',
                                            (screen_width / 2, top_margin)))

        self.settings_window = Window()
        self.settings_window.add_buttons(self.plus_size_button,
                                         self.minus_size_btn, self.next_button)
        self.settings_window.add_labels(Label('Настройте параметры поля',
                                              (screen_width / 2, cell_size)))
        for b in self.plus_minus_buttons:
            self.settings_window.add_buttons(b)

        self.create_window = Window()
        self.create_window.add_buttons(self.next_button, self.random_button,
                                       self.manual_button, self.cancel_button,
                                       self.clear_button)
        self.create_window.fields = 1

        self.game_window = Window()
        self.game_window.fields = 2

        self.win_window = Window()
        self.win_window.add_buttons(self.restart_button)


    def reset_settings_window(self):
        self.set_plus_minus_btns_params()
        self.settings_window.buttons = []
        self.settings_window.add_buttons(self.plus_size_button,
                                         self.minus_size_btn, self.next_button)
        for button in self.plus_minus_buttons:
            self.settings_window.add_buttons(button)


class DrawManager:
    def __init__(self, field_params):
        self.update(field_params)

    def update(self, field_params):
        self.field_size = field_params.field_size
        self.offset_for_field = field_params.offset
        self.nums_of_ships = field_params.nums_of_ships
        self.letters = [chr(i) for i in range(65, 65 + self.field_size)]

    def show_window(self, window):
        screen.fill(WHITE)
        self.draw_grid(LIGHT_BLUE)
        for button in window.buttons:
            self.draw_button(button)
        for label in window.labels:
            self.put_static_label(label)
        if window.fields == 1:
            self.draw_field((screen_width - 15 * cell_size) / 2 / cell_size)
            self.draw_ships_in_game()
        elif window.fields == 2:
            self.draw_field(OFFSETS[1])
            self.draw_field(OFFSETS[2])

    @staticmethod
    def draw_grid(color):
        for i in range(screen_width // cell_size):
            pygame.draw.line(screen, color,
                             (cell_size * i, 0),
                             (cell_size * i, screen_height))
            pygame.draw.line(screen, color, (0, cell_size * i),
                             (screen_width, cell_size * i))

    @staticmethod
    def draw_button(button, color=BUTTON_BLUE):
        x_start, y_start = button.x_start, button.y_start
        width, height = button.width, button.height
        title_params = (x_start + width / 2 - button.title_width / 2,
                        y_start + height / 2 - button.title_height / 2)
        pygame.draw.rect(screen, color, (x_start, y_start, width, height))
        screen.blit(font.render(button.title, True, WHITE),
                    title_params)
        button.rect = pygame.Rect((x_start, y_start, width, height))

    @staticmethod
    def put_static_label(label):
        screen.blit(label.text, (label.x_start - label.width / 2,
                                 label.y_start + 0.25 * cell_size))

    def put_params_labels(self):
        self.update_param(-1, left_margin + 21 * cell_size, 3 * cell_size)

        x_start = left_margin + (self.field_size + 2) * cell_size
        y_start = 5 * cell_size
        if self.field_size % 2 == 0:
            middle = self.field_size // 2
        else:
            middle = self.field_size // 2 + 1

        start, end = 0, middle
        for j in range(2):
            for i in range(start, end):
                self.update_param(i, x_start, y_start)
                y_start += 2 * cell_size
            x_start += 21 * cell_size
            y_start = 5 * cell_size
            start, end = middle, self.field_size

    def draw_ship_examples(self):
        y_start = 5 * cell_size
        x_start = left_margin

        if self.field_size % 2 == 0:
            middle = self.field_size // 2
        else:
            middle = self.field_size // 2 + 1

        start, end = 1, middle + 1
        for x in range(2):
            for i in range(start, end):
                for j in range(i + 1):
                    pygame.draw.line(screen, BLUE,
                                     (x_start + j * cell_size, y_start),
                                     (x_start + j * cell_size,
                                      y_start + cell_size), 2)
                pygame.draw.line(screen, BLUE, (x_start, y_start),
                                 (x_start + j * cell_size, y_start), 2)
                pygame.draw.line(screen, BLUE, (x_start, y_start +
                                                cell_size),
                                 (
                                 x_start + j * cell_size, y_start + cell_size),
                                 2)
                y_start += 2 * cell_size

            start, end = middle + 1, self.field_size + 1
            y_start = 5 * cell_size
            x_start += 21 * cell_size

    def update_param(self, ship_num, x_start, y_start):
        pygame.draw.rect(screen, WHITE, (x_start, y_start, 2 *
                                         cell_size, cell_size))
        pygame.draw.rect(screen, LIGHT_BLUE,
                         (x_start, y_start, 2 * cell_size, cell_size),
                         1)
        pygame.draw.line(screen, LIGHT_BLUE,
                         (x_start + cell_size, y_start),
                         (x_start + cell_size, y_start + cell_size))
        if ship_num == -1:
            self.put_static_label(Label(str(self.field_size),
                                        (x_start + cell_size, y_start), BLUE))
        else:
            self.put_static_label(Label(str(self.nums_of_ships[ship_num]),
                                        (x_start + cell_size, y_start),
                                        BLUE))

    def draw_field(self, offset):
        for i in range(self.field_size + 1):
            pygame.draw.line(screen, BLUE,
                             ((offset + self.offset_for_field) * cell_size,
                              top_margin + (i + self.offset_for_field) *
                              cell_size), ((offset + self.field_size +
                                            self.offset_for_field) * cell_size,
                                           top_margin +
                                           (i + self.offset_for_field) *
                                           cell_size), 2)

            pygame.draw.line(screen, BLUE,
                             ((i + offset + self.offset_for_field) * cell_size,
                              top_margin + self.offset_for_field * cell_size),
                             ((i + offset + self.offset_for_field) * cell_size,
                              top_margin + (self.field_size +
                                            self.offset_for_field) *
                              cell_size), 2)

            if i < self.field_size:
                num = font.render(str(i + 1), True, BLUE)
                let = font.render(self.letters[i], True, BLUE)

                num_width = num.get_width()
                num_height = num.get_height()
                let_width = let.get_width()

                screen.blit(num, ((offset + self.offset_for_field) * cell_size
                                  - (cell_size // 2 + num_width // 2),
                                  top_margin + (i + self.offset_for_field) *
                                  cell_size + (cell_size // 2 - num_height
                                               // 2)))

                screen.blit(let, ((i + self.offset_for_field) * cell_size +
                                  (cell_size // 2 - let_width // 2) +
                                  offset * cell_size, top_margin - num_height
                                  * 1.5 + self.offset_for_field * cell_size))

    def draw_ships_in_game(self):
        x_start = cell_size
        y_start = cell_size
        for i in range(len(self.nums_of_ships)):
            if self.nums_of_ships[i] != 0:
                for j in range(i + 2):
                    pygame.draw.line(screen, BLUE,
                                     (x_start, y_start + j * cell_size),
                                     (x_start + cell_size,
                                      y_start + j * cell_size), 2)

                pygame.draw.line(screen, BLUE, (x_start, y_start),
                                 (x_start, y_start + j * cell_size), 2)
                pygame.draw.line(screen, BLUE,
                                 (x_start + cell_size, y_start),
                                 (
                                 x_start + cell_size, y_start + j * cell_size),
                                 2)
                x_start += 2 * cell_size

    def draw_ship(self, ship, turn, offset):
        ship.sort(key=lambda i: i[1])
        x = cell_size * (ship[0][0] - 1) + \
            (offset + self.offset_for_field) * cell_size
        y = cell_size * (ship[0][
                             1] - 1) + top_margin + \
            self.offset_for_field * cell_size
        if turn == 1:
            width = cell_size
            height = cell_size * len(ship)
        else:
            width = cell_size * len(ship)
            height = cell_size
        pygame.draw.rect(screen, BLUE, ((x, y), (width, height)),
                         width=cell_size // 10)

    def update_score(self, score, player_num):
        self.put_dynamic_label(Label('Очки: {0}'.format(score), ((OFFSETS[player_num] + self.field_size / 2 + self.offset_for_field) * cell_size, screen_height - 2 * cell_size), WHITE))

    def put_dots(self, dots, offset):
        for (x, y) in dots:
            if x < 1 or y < 1 or x > self.field_size or y > self.field_size:
                continue
            x_d = x - 0.5 + offset + self.offset_for_field
            y_d = y + self.offset_for_field
            pygame.draw.circle(screen, BLUE,
                               (cell_size * x_d,
                                cell_size * (y_d - 0.5) + top_margin),
                               cell_size // 6)

    @staticmethod
    def put_cross(x_start, y_start, color=BLUE):
        pygame.draw.line(screen, color, (x_start, y_start),
                         (x_start + cell_size, y_start + cell_size),
                         cell_size // 10)
        pygame.draw.line(screen, color, (x_start, y_start + cell_size),
                         (x_start + cell_size, y_start), cell_size // 10)

    def put_dynamic_label(self, label):
        pygame.draw.rect(screen, BUTTON_BLUE, (label.x_start - label.width / 2 - cell_size, label.y_start, label.width + 2 * cell_size, cell_size))
        self.put_static_label(label)









