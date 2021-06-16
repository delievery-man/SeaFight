import pygame
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (65, 105, 225)
BLUE = (0, 0, 139)
cell_size = 30
left_margin = 60
top_margin = 90
screen_width, screen_height = left_margin * 2 + cell_size * 40, \
                              top_margin * 2 + 40 + cell_size * 16
btn_width, btn_height = 175, 45

OFFSETS = {1: 0,
           2: (left_margin + 23 * cell_size) / cell_size}

middle_offset = OFFSETS[2] / 2
print(screen_width / cell_size, OFFSETS[2], middle_offset)

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


class Button:
    def __init__(self, button_title):
        self.title = button_title
        self.title_width, self.title_height = font.size(self.title)
        self.rect = pygame.Rect((0, 0, 0, 0))

class DrawManager:
    def __init__(self, field_params):
        self.screen = screen
        self.font = font
        self.field_size = field_params.field_size
        self.offset_for_field = field_params.offset
        self.nums_of_ships = field_params.nums_of_ships
        self.letters = [chr(i) for i in range(65, 65 + self.field_size)]

    def draw_grid(self):
        for i in range(screen_width // cell_size):
            pygame.draw.line(self.screen, LIGHT_BLUE,
                             (cell_size * i, 0),
                             (cell_size * i, screen_height))
            pygame.draw.line(self.screen, LIGHT_BLUE, (0, cell_size * i),
                             (screen_width, cell_size * i))

    def draw_button(self, button, x_start, y_start, width=btn_width,
                    height=btn_height, color=BLACK):
        title_params = (x_start + width / 2 - button.title_width / 2,
                        y_start + height / 2 - button.title_height / 2)
        pygame.draw.rect(self.screen, color, (x_start, y_start, width, height))
        self.screen.blit(self.font.render(button.title, True, WHITE),
                         title_params)
        button.rect = pygame.Rect((x_start, y_start, width, height))

    def draw_field(self, offset):
        for i in range(self.field_size + 1):
            pygame.draw.line(self.screen, BLUE,
                             (left_margin + (offset + self.offset_for_field)
                              * cell_size,
                              top_margin + (i + self.offset_for_field) *
                              cell_size), (left_margin +
                                           (offset + self.field_size +
                                            self.offset_for_field) * cell_size,
                                           top_margin +
                                           (i + self.offset_for_field) *
                                           cell_size), 2)
            pygame.draw.line(self.screen, BLUE,
                             (left_margin +
                              (i + offset + self.offset_for_field) * cell_size,
                              top_margin + self.offset_for_field * cell_size),
                             (left_margin +
                              (i + offset + self.offset_for_field) * cell_size,
                              top_margin +
                              (self.field_size + self.offset_for_field) *
                              cell_size), 2)

            if i < self.field_size:
                num = self.font.render(str(i + 1), True, BLACK)
                let = self.font.render(self.letters[i], True, BLACK)

                num_width = num.get_width()
                num_height = num.get_height()
                let_width = let.get_width()

                self.screen.blit(num, (left_margin -
                                       (cell_size // 2 + num_width // 2) +
                                       (offset + self.offset_for_field) *
                                       cell_size, top_margin +
                                       (i + self.offset_for_field) *
                                       cell_size +
                                       (cell_size // 2 - num_height // 2)))

                self.screen.blit(let, (left_margin +
                                       (i + self.offset_for_field) *
                                       cell_size + (cell_size // 2
                                                    - let_width // 2) +
                                       offset * cell_size,
                                       top_margin - num_height * 1.5 +
                                       self.offset_for_field * cell_size))

    def make_label(self, text, x_start, y_start, color=BLACK):
        label = self.font.render(text, True, color)
        label_width = label.get_width()
        self.screen.blit(label, (x_start - label_width / 2, y_start + 0.25 *
                                 cell_size))

    def draw_start_window(self):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.draw_button(start_with_friend_btn,
                         (screen_width - btn_width * 2) / 3,
                         (screen_height - btn_height) / 2)
        self.draw_button(start_with_computer_btn,
                         (screen_width - btn_width * 2) * (2 / 3) + btn_width,
                         (screen_height - btn_height) / 2)

    def draw_ship_examples(self, size):
        y_start = 5 * cell_size
        x_start = left_margin
        for i in range(size, size // 2, -1):
            for j in range(i + 1):
                pygame.draw.line(self.screen, BLUE,
                                 (x_start + j * cell_size, y_start),
                                 (x_start + j * cell_size,
                                  y_start + cell_size), 2)
            pygame.draw.line(self.screen, BLUE, (x_start, y_start),
                             (x_start + j * cell_size, y_start), 2)
            pygame.draw.line(self.screen, BLUE, (x_start, y_start +
                                                 cell_size),
                             (x_start + j * cell_size, y_start + cell_size), 2)
            y_start += 2 * cell_size

        y_start = 5 * cell_size
        x_start += 22 * cell_size
        for i in range(size // 2, 0, -1):
            for j in range(i + 1):
                pygame.draw.line(self.screen, BLUE,
                                 (x_start + j * cell_size, y_start),
                                 (x_start + j * cell_size,
                                  y_start + cell_size), 2)

            pygame.draw.line(self.screen, BLUE, (x_start, y_start),
                             (x_start + j * cell_size, y_start), 2)
            pygame.draw.line(self.screen, BLUE, (x_start, y_start +
                                                  cell_size),
                             (x_start + j * cell_size, y_start + cell_size), 2)

            y_start += 2 * cell_size

    def draw_plus_minus_buttons(self, size):
        x_start = left_margin + (size + 1) * cell_size
        y_start = 5 * cell_size
        buttons_to_draw = [minus_plus_buttons[i] for i in range(size)]
        buttons_to_draw.reverse()
        if size % 2 == 0:
            middle = size // 2
        else:
            middle = size // 2 + 1
        for i in range(middle):
            minus_btn, plus_btn = buttons_to_draw[i][0], \
                                  buttons_to_draw[i][1]
            self.draw_button(minus_btn, x_start, y_start, cell_size, cell_size)
            self.draw_button(plus_btn, x_start + 3 * cell_size, y_start,
                             cell_size, cell_size)
            y_start += 2 * cell_size

        x_start = (25 + size // 2) * cell_size
        y_start = 5 * cell_size
        for i in range(middle, size):
            minus_btn, plus_btn = buttons_to_draw[i][0], \
                                  buttons_to_draw[i][1]
            self.draw_button(minus_btn, x_start, y_start, cell_size, cell_size)
            self.draw_button(plus_btn, x_start + 3 * cell_size, y_start,
                             cell_size, cell_size)
            y_start += 2 * cell_size

    def draw_params_labels(self, size):
        y_start = 5 * cell_size
        x_start = left_margin + (size + 2) * cell_size
        for i in range(size, size // 2, -1):
            self.update_param(self.nums_of_ships[i-1], 0, x_start, y_start)
            y_start += 2 * cell_size

        x_start = (size // 2 + 26) * cell_size
        y_start = 5 * cell_size
        for i in range(size//2, 0, -1):
            self.update_param(self.nums_of_ships[i-1], 0, x_start, y_start)
            y_start += 2 * cell_size

    def redraw_field_settings_window(self, field_params):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.make_label('Настройте параметры поля', screen_width / 2, cell_size)
        self.make_label('Размер поля', 20 * cell_size, 3 * cell_size)

        self.draw_button(minus_size_btn, left_margin + 20 * cell_size,
                         3 * cell_size, cell_size, cell_size)
        self.draw_button(plus_size_btn, left_margin + 23 * cell_size,
                         3 * cell_size, cell_size, cell_size)
        self.update_param(field_params.field_size, 0, left_margin + 21 * cell_size,
                        3 * cell_size)
        self.draw_ship_examples(field_params.field_size)
        self.draw_params_labels(field_params.field_size)
        self.draw_plus_minus_buttons(field_params.field_size)
        self.draw_button(next_btn,
                         screen_width - left_margin - btn_width,
                         top_margin + 15 * cell_size + btn_height)

    def draw_field_settings_window(self):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.make_label('Настройте параметры поля', screen_width / 2, cell_size)
        self.make_label('Размер поля', 20 * cell_size, 3 * cell_size)

        self.draw_button(minus_size_btn, left_margin + 20 * cell_size,
                         3 * cell_size, cell_size, cell_size)
        self.draw_button(plus_size_btn, left_margin + 23 * cell_size,
                         3 * cell_size, cell_size, cell_size)
        self.update_param(self.field_size, 0, left_margin + 21 * cell_size,
                        3 * cell_size)

        self.draw_ship_examples(self.field_size)
        self.draw_plus_minus_buttons(self.field_size)
        self.draw_params_labels(self.field_size)

        self.draw_button(next_btn,
                         screen_width - left_margin - btn_width,
                         top_margin + 15 * cell_size + btn_height)

    def update_param(self, param, delta, x_start, y_start):
        rect_params = (x_start, y_start, 2 * cell_size, cell_size)
        pygame.draw.rect(self.screen, WHITE, rect_params)
        pygame.draw.rect(self.screen, LIGHT_BLUE, rect_params, width=1)
        pygame.draw.line(self.screen, LIGHT_BLUE,
                         (x_start + cell_size, y_start),
                         (x_start + cell_size, y_start + cell_size))
        num = self.font.render(str(param + delta), True, BLACK)
        self.screen.blit(num,
                         (x_start + 2 * cell_size / 2, y_start + 0.25 *
                          cell_size))

    def draw_ships_in_game(self):
        x_start = left_margin
        y_start = top_margin
        for i in range(len(self.nums_of_ships)):
            if self.nums_of_ships[i] != 0:
                for j in range(i + 2):
                    pygame.draw.line(self.screen, BLACK,
                                     (x_start, y_start + j * cell_size),
                                     (x_start + cell_size,
                                      y_start + j * cell_size))

                pygame.draw.line(self.screen, BLACK, (x_start, y_start),
                                 (x_start, y_start + j * cell_size))
                pygame.draw.line(self.screen, BLACK, (x_start + cell_size, y_start),
                                 (x_start + cell_size, y_start + j * cell_size))
                x_start += 1.5 * cell_size

    def draw_field_window(self, label):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.draw_field(middle_offset)
        self.make_label(label, 22 * cell_size, cell_size)
        self.draw_ships_in_game()
        self.draw_button(next_btn, screen_width - left_margin - btn_width,
                         top_margin + 15 * cell_size +
                         btn_height)
        self.draw_button(manual_btn, screen_width - left_margin - btn_width,
                         top_margin)
        self.draw_button(random_btn, screen_width - left_margin - btn_width,
                         top_margin + 1.5 * btn_height)
        self.draw_button(cancel_btn, screen_width - left_margin - btn_width,
                         top_margin + 3 * btn_height)
        self.draw_button(clear_btn, screen_width - left_margin - btn_width,
                         top_margin + 4.5 * btn_height)

    def draw_ship(self, ship, turn, offset):
        ship.sort(key=lambda i: i[1])
        x = cell_size * (ship[0][0] - 1) + left_margin + \
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
        pygame.draw.rect(self.screen, BLACK, ((x, y), (width, height)),
                         width=cell_size // 10)

    def draw_game_window(self, player1, player2):
        global OFFSETS
        self.screen.fill(WHITE)
        self.draw_grid()
        for offset in OFFSETS.values():
            self.draw_field(offset)
            self.update_score(0, offset)

        self.make_label(player1, left_margin + OFFSETS[1] * cell_size, top_margin)
        self.make_label(player2, left_margin + OFFSETS[2] * cell_size, top_margin)

    def update_score(self, score, offset):
        score_label = self.font.render('Очки: {0}'.format(score), True, BLACK)
        score_label_width = score_label.get_width()
        score_label_height = score_label.get_height()
        x_start = left_margin + offset * cell_size + (15 * cell_size - score_label_width) / 2
        y_start = top_margin + 17 * cell_size
        background_rect = pygame.Rect(
            x_start, y_start, score_label_width, score_label_height)
        self.screen.fill(WHITE, background_rect)
        self.screen.blit(score_label, (x_start, y_start))

    def put_dots(self, dots, offset):
        for (x, y) in dots:
            if x < 1 or y < 1 or x > self.field_size or y > self.field_size:
                continue
            x_d = x - 0.5 + offset + self.offset_for_field
            y_d = y + self.offset_for_field
            pygame.draw.circle(self.screen, BLACK,
                               (cell_size * x_d + left_margin,
                                cell_size * (y_d - 0.5) + top_margin),
                               cell_size // 6)

    def put_cross(self, x_start, y_start, color=BLACK):
        pygame.draw.line(self.screen, color, (x_start, y_start),
                         (x_start + cell_size, y_start + cell_size),
                         cell_size // 10)
        pygame.draw.line(self.screen, color, (x_start, y_start + cell_size),
                         (x_start + cell_size, y_start), cell_size // 10)

    def draw_win_window(self, label):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.make_label(label, middle_offset, top_margin, color=RED)
        self.draw_button(restart_btn, (screen_width - btn_width) / 2,
                         (screen_height - btn_height) / 2)

    def draw_levels_window(self):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.make_label('Выберите уровень сложности', middle_offset, top_margin)
        y_start = (screen_height - 3 * btn_height - 2 * cell_size) / 2
        self.draw_button(level_1_btn, (screen_width - btn_width) / 2,
                         y_start)
        self.draw_button(level_2_btn, (screen_width - btn_width) / 2,
                         y_start + btn_height + cell_size)
        self.draw_button(level_3_btn, (screen_width - btn_width) / 2,
                         y_start + 2 * btn_height + 2 * cell_size)


start_with_friend_btn = Button('Играть с другом')
start_with_computer_btn = Button('Играть с компьютером')
random_btn = Button('Расставить рандомно')
manual_btn = Button('Нарисовать')
next_btn = Button('Дальше')
clear_btn = Button('Стереть всё')
cancel_btn = Button('Отмена')
restart_btn = Button('Начать заново')
level_1_btn = Button('Лёгкий уровень')
level_2_btn = Button('Средний уровень')
level_3_btn = Button('Сложный уровень')

minus_size_btn = Button('-')
plus_size_btn = Button('+')
minus_11_btn = Button('-')
minus_12_btn = Button('-')
minus_13_btn = Button('-')
minus_14_btn = Button('-')
minus_15_btn = Button('-')
minus_10_btn = Button('-')
minus_9_btn = Button('-')
minus_8_btn = Button('-')
minus_7_btn = Button('-')
minus_6_btn = Button('-')
minus_5_btn = Button('-')
plus_11_btn = Button('+')
plus_12_btn = Button('+')
plus_13_btn = Button('+')
plus_14_btn = Button('+')
plus_15_btn = Button('+')
plus_10_btn = Button('+')
plus_9_btn = Button('+')
plus_8_btn = Button('+')
plus_7_btn = Button('+')
plus_6_btn = Button('+')
plus_5_btn = Button('+')
minus_4_btn = Button('-')
plus_4_btn = Button('+')
minus_3_btn = Button('-')
plus_3_btn = Button('+')
minus_2_btn = Button('-')
plus_2_btn = Button('+')
minus_1_btn = Button('-')
plus_1_btn = Button('+')

minus_plus_buttons = [(minus_1_btn, plus_1_btn),
                      (minus_2_btn, plus_2_btn),
                      (minus_3_btn, plus_3_btn),
                      (minus_4_btn, plus_4_btn),
                      (minus_5_btn, plus_5_btn),
                      (minus_6_btn, plus_6_btn),
                      (minus_7_btn, plus_7_btn),
                      (minus_8_btn, plus_8_btn),
                      (minus_9_btn, plus_9_btn),
                      (minus_10_btn, plus_10_btn),
                      (minus_11_btn, plus_11_btn),
                      (minus_12_btn, plus_12_btn),
                      (minus_13_btn, plus_13_btn),
                      (minus_14_btn, plus_14_btn),
                      (minus_15_btn, plus_15_btn)]