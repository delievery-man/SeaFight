import pygame
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 153, 153)

cell_size = 30
left_margin = 70
top_margin = 90

screen_size = (left_margin * 2 + cell_size * 20 + cell_size * 5,
               top_margin * 2 + cell_size * 10)

pygame.init()

screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Морской бой')

font_size = int(cell_size / 1.5)
font = pygame.font.SysFont('notosans', font_size)


class Field:
    def __init__(self, player):
        self.cells_state = dict()
        self.set_cells_state()
        self.player = player
        self.ships = dict()

    def set_cells_state(self):
        for x in range(1, 11):
            for y in range(1, 11):
                self.cells_state[(x, y)] = True

    def generate_ships(self):
        s = 0
        while s < 10:
            x = random.randint(1, 10)
            y = random.randint(1, 10)
            turn = random.randint(0, 1)
            if s == 0:
                ship = self.make_four_deck_ship(x, y, turn)
            elif 1 <= s <= 2:
                ship = self.make_three_deck_ship(x, y, turn)
            elif 3 <= s <= 5:
                ship = self.make_two_deck_ship(x, y, turn)
            else:
                ship = [(x, y)]
            if self.is_ship_can_be_put(ship):
                self.add_ship(ship)
                self.draw_ship(ship, turn)
                s += 1

    def make_four_deck_ship(self, x, y, turn):
        if turn == 0:
            if x == 1:
                return [(1, y), (2, y), (3, y), (4, y)]
            if x == 10 or x == 9:
                return [(7, y), (8, y), (9, y), (10, y)]
            else:
                return [(x - 1, y), (x, y), (x + 1, y), (x + 2, y)]
        else:
            if y == 1:
                return [(x, 1), (x, 2), (x, 3), (x, 4)]
            elif y == 10 or y == 9:
                return [(x, 10), (x, 9), (x, 8), (x, 7)]
            else:
                return [(x, y - 1), (x, y), (x, y + 1), (x, y + 2)]

    def make_three_deck_ship(self, x, y, turn):
        if turn == 0:
            if x == 1:
                return [(1, y), (2, y), (3, y)]
            elif x == 10:
                return [(8, y), (9, y), (10, y)]
            else:
                return [(x - 1, y), (x, y), (x + 1, y)]
        else:
            if y == 1:
                return [(x, 1), (x, 2), (x, 3)]
            elif y == 10:
                return [(x, 10), (x, 9), (x, 8)]
            else:
                return [(x, y + 1), (x, y), (x, y - 1)]

    def make_two_deck_ship(self, x, y, turn):
        if turn == 0:
            if x == 10:
                return [(x - 1, y), (x, y)]
            else:
                return [(x, y), (x + 1, y)]
        else:
            if y == 10:
                return [(x, y), (x, y - 1)]
            else:
                return [(x, y), (x, y + 1)]

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
            self.disable_cells(x, y, self.cells_around(x, y))
            self.ships[(x, y)] = (False, neighbours)

    def draw_ship(self, ship, turn):
        ship.sort(key=lambda i: i[1])
        x = cell_size * (ship[0][0] - 1) + left_margin
        y = cell_size * (ship[0][1] - 1) + top_margin
        if turn == 1:
            width = cell_size
            height = cell_size * len(ship)

        else:
            width = cell_size * len(ship)
            height = cell_size
        pygame.draw.rect(screen, BLACK, ((x, y), (width, height)),
                         width=cell_size // 10)

    def disable_cells(self, x, y, directions):
        self.cells_state[(x, y)] = False
        for d in directions:
            if d == 'up':
                self.cells_state[(x, y - 1)] = False
            elif d == 'down':
                self.cells_state[(x, y + 1)] = False
            elif d == 'left':
                key = (x - 1, y)
                self.cells_state[key] = False
            elif d == 'right':
                key = (x + 1, y)
                self.cells_state[key] = False
            elif d == 'up-left':
                key = (x - 1, y - 1)
                self.cells_state[key] = False
            elif d == 'up-right':
                key = (x + 1, y - 1)
                self.cells_state[key] = False
            elif d == 'down-left':
                key = (x - 1, y + 1)
                self.cells_state[key] = False
            elif d == 'down-right':
                key = (x + 1, y + 1)
                self.cells_state[key] = False

    def cells_around(self, x, y):
        if y == 1:
            if x == 1:
                return ['down', 'down-right', 'right']
            elif x == 10:
                return ['left', 'down-left', 'down']
            else:
                return ['left', 'down-left', 'down', 'down-right', 'right']
        elif y == 10:
            if x == 1:
                return ['up', 'up-right', 'right']
            elif x == 10:
                return ['left', 'up-left', 'up']
            else:
                return ['left', 'up-left', 'up', 'up-right', 'right']
        else:
            if x == 1:
                return ['up', 'up-right', 'right', 'down-right', 'down']
            elif x == 10:
                return ['down', 'down-left', 'left', 'up-left', 'up']
            else:
                return ['left', 'up-left', 'up', 'up-right', 'right',
                        'down-right', 'down', 'down-left']


class Button:
    def __init__(self, x_offset, button_title):
        self.title = button_title
        title_width, title_height = font.size(self.title)
        self.button_width = title_width + cell_size
        button_height = title_height + cell_size
        x_start = x_offset
        y_start = top_margin + 10 * cell_size + button_height
        self.btn_params = x_start, y_start, self.button_width, button_height
        self.rect = pygame.Rect(self.btn_params)
        self.title_params = x_start + self.button_width / 2 - title_width / 2,\
                            y_start + button_height / 2 - title_height / 2

    def draw_button(self, color=BLACK):
        pygame.draw.rect(screen, color, self.btn_params)
        screen.blit(font.render(self.title, True, WHITE), self.title_params)

    def change_color_on_hover(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.draw_button(GREEN)


def draw_field(offset):
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    for i in range(11):
        pygame.draw.line(screen, BLACK,
                         (left_margin + offset * cell_size, top_margin + i *
                          cell_size), (left_margin + (offset + 10) * cell_size,
                                       top_margin + i * cell_size))
        pygame.draw.line(screen, BLACK,
                         (left_margin + (i + offset) * cell_size, top_margin),
                         (left_margin + (i + offset) * cell_size,
                          top_margin + 10 * cell_size))

        if i < 10:
            num = font.render(str(i + 1), True, BLACK)
            let = font.render(letters[i], True, BLACK)

            num_width = num.get_width()
            num_height = num.get_height()
            let_width = let.get_width()

            screen.blit(num, (left_margin - (cell_size // 2 + num_width // 2) +
                              offset * cell_size, top_margin + i * cell_size +
                              (cell_size // 2 - num_height // 2)))

            screen.blit(let, (left_margin + i * cell_size +
                              (cell_size // 2 - let_width // 2) + offset *
                              cell_size, top_margin - num_height * 1.5))


def make_label(label, offset):
    player_label = font.render(label, True, BLACK)
    width = player_label.get_width()
    screen.blit(player_label, (left_margin + (offset + 5) * cell_size -
                               width // 2, top_margin - cell_size // 2 -
                               font_size - 10))


def main():
    players = {1: Field(1),
               2: Field(2)}
    scores = {2: 0,
              1: 0}
    offsets = {1: 0,
               2: 15}

    enemy_num = 2
    player_num = 1

    game_over = False
    game_start = False
    first_field_made = False
    second_field_made = False

    screen.fill(WHITE)

    start_with_friend_btn = Button(left_margin, 'Играть с другом')
    start_with_friend_btn.draw_button()

    start_with_computer_btn = Button(left_margin + 200, 'Играть с компьютером')
    start_with_computer_btn.draw_button()

    random_btn = Button(left_margin + 11 * cell_size, 'Расставить рандомно')
    next_btn = Button(left_margin + 11 * cell_size + random_btn.button_width + cell_size, 'Дальше')

    pygame.display.update()

    def draw_field_window(label):
        screen.fill(WHITE)
        draw_field(0)
        make_label(label, 0)
        random_btn.draw_button()
        next_btn.draw_button()

    def draw_game_window(player1, player2):
        screen.fill(WHITE)
        for offset in offsets.values():
            draw_field(offset)
        make_label(player1, 0)
        make_label(player2, 15)

    while not game_start:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_start = True
                first_field_made = True
                second_field_made = True
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    start_with_friend_btn.rect.collidepoint(mouse):
                game_start = True
                draw_field_window('Игрок 1')
        pygame.display.update()

    while not first_field_made:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                first_field_made = True
                second_field_made = True
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    next_btn.rect.collidepoint(mouse):
                first_field_made = True
                draw_field_window('Игрок 2')
            elif event.type == pygame.MOUSEBUTTONDOWN \
                    and random_btn.rect.collidepoint(mouse):
                players[1].generate_ships()
        pygame.display.update()

    while not second_field_made:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                second_field_made = True
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN and next_btn.rect.collidepoint(mouse):
                second_field_made = True
                draw_game_window('Игрок 1', 'Игрок 2')
            elif event.type == pygame.MOUSEBUTTONDOWN \
                    and random_btn.rect.collidepoint(mouse):
                players[2].generate_ships()
        pygame.display.update()

    def change_turn():
        nonlocal player_num, enemy_num
        player_num, enemy_num = enemy_num, player_num

    def missed():
        nonlocal offset, fired_cell
        x_d = fired_cell[0] - 0.5 + offset
        y_d = fired_cell[1]
        pygame.draw.circle(screen, BLACK, (cell_size * x_d + left_margin,
                                           cell_size * (
                                                   y_d - 0.5) + top_margin),
                           cell_size // 6)

    def wounded(ships):
        nonlocal offset, fired_cell
        x_c = fired_cell[0]
        y_c = fired_cell[1]
        x_d = cell_size * (x_c - 1 + offset) + left_margin
        y_d = cell_size * (y_c - 1) + top_margin
        pygame.draw.line(screen, BLACK, (x_d, y_d),
                         (x_d + cell_size, y_d + cell_size), cell_size // 10)
        pygame.draw.line(screen, BLACK, (x_d, y_d + cell_size),
                         (x_d + cell_size, y_d), cell_size // 10)
        ships[(x_c, y_c)] = (True, ships[(x_c, y_c)][1])

    def is_killed(ships):
        nonlocal fired_cell
        x_c = fired_cell[0]
        y_c = fired_cell[1]
        killed_ship = [(x_c, y_c)]
        for neighbour in ships[(x_c, y_c)][1]:
            n_x = neighbour[0]
            n_y = neighbour[1]
            if ships[(n_x, n_y)][0]:
                killed_ship.append((n_x, n_y))
        if len(killed_ship) == len(ships[(x_c, y_c)][1]) + 1:
            return True
        return False

    def killed(ships):
        nonlocal offset, fired_cell
        x_d = cell_size * (fired_cell[0] - 1 + offset) + left_margin
        y_d = cell_size * (fired_cell[1] - 1) + top_margin
        pygame.draw.line(screen, RED, (x_d, y_d),
                         (x_d + cell_size, y_d + cell_size), cell_size // 10)
        pygame.draw.line(screen, RED, (x_d, y_d + cell_size),
                         (x_d + cell_size, y_d), cell_size // 10)

        for neighbour in ships[(fired_cell[0], fired_cell[1])][1]:
            x_d = cell_size * (neighbour[0] - 1 + offset) + left_margin
            y_d = cell_size * (neighbour[1] - 1) + top_margin
            pygame.draw.line(screen, RED, (x_d, y_d),
                             (x_d + cell_size, y_d + cell_size),
                             cell_size // 10)
            pygame.draw.line(screen, RED, (x_d, y_d + cell_size),
                             (x_d + cell_size, y_d), cell_size // 10)

    def check_for_winner():
        if scores[1] == 20:
            print('1 победил')
        if scores[2] == 20:
            print('2 победил')

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                offset = offsets[enemy_num]
                enemy = players[enemy_num]
                if left_margin + offset * cell_size <= x <= left_margin + \
                        (10 + offset) * cell_size and top_margin <= y <= \
                        top_margin + 10 * cell_size:
                    fired_cell = ((x - left_margin) // cell_size + 1 - offset,
                                  (y - top_margin) // cell_size + 1)
                    if fired_cell in enemy.ships and \
                            enemy.ships[fired_cell][0] is False:
                        scores[player_num] += 1
                        wounded(enemy.ships)
                        if is_killed(enemy.ships):
                            killed(enemy.ships)
                    elif fired_cell not in enemy.ships:
                        missed()
                        # players[player_num].cells_state[(x_c, y_c)] = False
                        change_turn()

                check_for_winner()

        pygame.display.update()


if __name__ == '__main__':
    main()
    pygame.quit()
