import pygame
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 153, 153)

OFFSETS = {1: 0,
           2: 15}

cell_size = 30
left_margin = 70
top_margin = 90

screen_width, screen_height = left_margin * 2 + cell_size * 25, top_margin * 2 + 40 + cell_size * 10
btn_width, btn_height = 175, 45

pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Морской бой')

font_size = int(cell_size / 1.5)
font = pygame.font.SysFont('notosans', font_size)


class Field:
    def __init__(self, player):
        self.cells_state = dict()
        self.set_cells_state()
        self.player = player
        self.ships_to_draw = []
        self.ships = dict()

    def set_cells_state(self):
        for x in range(1, 11):
            for y in range(1, 11):
                self.cells_state[(x, y)] = True

    def generate_ships(self, drawer, label):
        s = 0
        self.ships = {}
        self.set_cells_state()
        drawer.draw_field_window(label)

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
                self.draw_ship(ship, turn, 7.5 * cell_size)
                s += 1

    @staticmethod
    def draw_ship(ship, turn, offset):
        ship.sort(key=lambda i: i[1])
        x = cell_size * (ship[0][0] - 1) + left_margin + offset
        y = cell_size * (ship[0][1] - 1) + top_margin
        if turn == 1:
            width = cell_size
            height = cell_size * len(ship)

        else:
            width = cell_size * len(ship)
            height = cell_size
        pygame.draw.rect(screen, BLACK, ((x, y), (width, height)),
                         width=cell_size // 10)

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
                return [(x, 7), (x, 8), (x, 9), (x, 10)]
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
                return [(x, 8), (x, 9), (x, 10)]
            else:
                return [(x, y - 1), (x, y), (x, y + 1)]

    def make_two_deck_ship(self, x, y, turn):
        if turn == 0:
            if x == 10:
                return [(x - 1, y), (x, y)]
            else:
                return [(x, y), (x + 1, y)]
        else:
            if y == 10:
                return [(x, y - 1), (x, y)]
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
    def __init__(self, x_start, y_start, button_title, drawer):
        self.title = button_title
        title_width, title_height = font.size(self.title)
        self.button_width = 175
        self.button_height = 45
        self.btn_params = x_start, y_start, self.button_width, self.button_height
        self.rect = pygame.Rect(self.btn_params)
        self.title_params = x_start + self.button_width / 2 - title_width / 2, \
                            y_start + self.button_height / 2 - title_height / 2
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
        self.drawer.put_cross(cell_size * (x - 1 + self.__offset) + left_margin,
                         cell_size * (y - 1) + top_margin)
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
        self.drawer.put_cross(cell_size * (x - 1 + self.__offset) +
                         left_margin, cell_size * (y - 1) +
                         top_margin, RED)
        neighbours = self.player.ships[(x, y)][1]
        for neighbour in neighbours:
            self.drawer.put_cross(cell_size * (neighbour[0] - 1 + self.__offset) +
                             left_margin, cell_size * (neighbour[1] - 1) +
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
        self.start_with_friend_btn = Button((screen_width - btn_width * 2) / 3,
                                            (screen_height - btn_height) / 2,
                                            'Играть с другом',
                                            self)
        self.start_with_computer_btn = Button((screen_width - btn_width * 2) *
                                              (2 / 3) + btn_width,
                                              (screen_height - btn_height) / 2,
                                              'Играть с компьютером', self)
        self.random_btn = Button((screen_width - btn_width * 2 - 5) / 2,
                                 top_margin + 10 * cell_size + btn_height,
                                 'Расставить рандомно', self)
        self.next_btn = Button((screen_width - btn_width * 2 - 5) / 2 +
                               btn_width + 10, top_margin + 10 * cell_size +
                               btn_height, 'Дальше', self)

    @staticmethod
    def draw_button(button, color=BLACK):
        pygame.draw.rect(screen, color, button.btn_params)
        screen.blit(font.render(button.title, True, WHITE), button.title_params)

    @staticmethod
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

    @staticmethod
    def make_label(text, x_offset, y_offset=-cell_size, color=BLACK):
        label = font.render(text, True, color)
        label_width = label.get_width()
        label_height = label.get_height()
        screen.blit(label, (left_margin + x_offset * cell_size +
                            (10 * cell_size - label_width) / 2, top_margin - label_height + y_offset))

    def draw_field_window(self, label):
        screen.fill(WHITE)
        self.draw_field(7.5)
        self.make_label(label, 7.5)
        self.draw_button(self.next_btn)
        self.draw_button(self.random_btn)

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
    def draw_ships(ships, offset=0.0):
        for ship in ships:
            if len(ship) > 1:
                if ship[0][1] == ship[1][1]:
                    turn = 0
                else:
                    turn = 1
            else:
                turn = 1
            if turn == 1:
                width = cell_size
                height = cell_size * len(ship)
            else:
                width = cell_size * len(ship)
                height = cell_size
            x = cell_size * (ship[0][0] - 1) + left_margin + offset
            y = cell_size * (ship[0][1] - 1) + top_margin
            pygame.draw.rect(screen, BLACK, ((x, y), (width, height)),
                             width=cell_size // 10)

    @staticmethod
    def put_dots(dots, offset):
        for (x, y) in dots:
            if x < 1 or y < 1 or x > 10 or y > 10:
                continue
            x_d = x - 0.5 + offset
            y_d = y
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
    ships_created_2 = False
    ships_created_1 = False
    screen.fill(WHITE)
    drawer = DrawManager()
    drawer.draw_button(drawer.start_with_friend_btn)
    drawer.draw_button(drawer.start_with_computer_btn)
    shootings = {1: ShootingManager(players[1], drawer),
                 2: ShootingManager(players[2], drawer)}

    while not game_start:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_start = True
                first_field_made = True
                second_field_made = True
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    drawer.start_with_friend_btn.rect.collidepoint(mouse):
                game_start = True
                drawer.draw_field_window('Игрок 1')
        pygame.display.update()

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
        return scores[player] == 20

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
                        shootings[enemy_num].wounded(fired_cell[0], fired_cell[1])
                        drawer.update_score(scores[player_num], offsets[player_num])
                        if shootings[enemy_num].is_killed(fired_cell[0], fired_cell[1]):
                            shootings[enemy_num].killed(fired_cell[0], fired_cell[1])
                        if is_winner(player_num):
                            drawer.make_label(
                                'Игрок {0} победил'.format(player_num), 7.5,
                                12 * cell_size, RED)
                    elif fired_cell not in enemy.ships:
                        if enemy.cells_state[fired_cell] is True:
                            change_turn()
                        shootings[player_num].missed(fired_cell[0], fired_cell[1])

        pygame.display.update()


if __name__ == '__main__':
    main()
    pygame.quit()
