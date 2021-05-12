import pygame
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

cell_size = 30
left_margin = 70
top_margin = 90

size = (left_margin * 2 + cell_size * 20 + cell_size * 6,
        top_margin * 2 + cell_size * 10)

pygame.init()

screen = pygame.display.set_mode(size)
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
        print(self.ships)


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
        if self.player == 2:
            x += 15 * cell_size
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


def missed(x, y, player):
    if player == 2:
        x1 = x - 0.5 + 15
    else:
        x1 = x - 0.5
    pygame.draw.circle(screen, BLACK, (cell_size * x1 + left_margin, cell_size * (y - 0.5) + top_margin), cell_size // 6)


def wounded(x, y, player, ships):
    if player == 2:
        x1 = cell_size * (x - 1 + 15) + left_margin
    else:
        x1 = cell_size * (x - 1) + left_margin
    y1 = cell_size * (y - 1) + top_margin
    pygame.draw.line(screen, BLACK, (x1, y1),
                     (x1 + cell_size, y1 + cell_size), cell_size // 10)
    pygame.draw.line(screen, BLACK, (x1, y1 + cell_size),
                     (x1 + cell_size, y1), cell_size // 10)
    ships[(x, y)] = (True, ships[(x, y)][1])


def is_killed(x, y, ships):
    killed_ship = [(x, y)]
    for neighbour in ships[(x, y)][1]:
        n_x = neighbour[0]
        n_y = neighbour[1]
        if ships[(n_x, n_y)][0]:
            killed_ship.append((n_x, n_y))
    if len(killed_ship) == len(ships[(x, y)][1]) + 1:
        return True
    return False


def killed(x, y, player, ships):
    if player == 2:
        x1 = cell_size * (x - 1 + 15) + left_margin
    else:
        x1 = cell_size * (x - 1) + left_margin
    y1 = cell_size * (y - 1) + top_margin
    pygame.draw.line(screen, RED, (x1, y1),
                     (x1 + cell_size, y1 + cell_size), cell_size // 10)
    pygame.draw.line(screen, RED, (x1, y1 + cell_size),
                     (x1 + cell_size, y1), cell_size // 10)
    print(ships[(x, y)][1])
    for neighbour in ships[(x, y)][1]:
        print(neighbour)
        if player == 2:
            x1 = cell_size * (neighbour[0] - 1 + 15) + left_margin
        else:
            x1 = cell_size * (neighbour[0] - 1) + left_margin
        print(x1)
        y1 = cell_size * (neighbour[1] - 1) + top_margin
        pygame.draw.line(screen, RED, (x1, y1),
                         (x1 + cell_size, y1 + cell_size), cell_size // 10)
        pygame.draw.line(screen, RED, (x1, y1 + cell_size),
                         (x1 + cell_size, y1), cell_size // 10)


def draw_field():
    player1_label = font.render('Игрок 1', True, BLACK)
    player2_label = font.render('Игрок 2', True, BLACK)
    width_1 = player1_label.get_width()
    width_2 = player2_label.get_width()
    screen.blit(player1_label, (left_margin + 5 * cell_size - width_1 // 2, 
                                top_margin - cell_size // 2 - font_size - 10))
    screen.blit(player2_label, (left_margin + 20 * cell_size - width_2 // 2,
                                top_margin - cell_size // 2 - font_size - 10))

    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    for i in range(11):
        # field 1 horizontal and vertical
        pygame.draw.line(screen, BLACK,
                         (left_margin, top_margin + i * cell_size),
                         (left_margin + 10 * cell_size,
                          top_margin + i * cell_size))
        pygame.draw.line(screen, BLACK,
                         (left_margin + i * cell_size, top_margin),
                         (left_margin + i * cell_size,
                          top_margin + 10 * cell_size))

        # field 2 horizontal and vertical
        pygame.draw.line(screen, BLACK,
                         (left_margin + 15 * cell_size, top_margin +
                          i * cell_size), (left_margin + 25 * cell_size,
                                           top_margin + i * cell_size))
        pygame.draw.line(screen, BLACK,
                         (left_margin + (i + 15) * cell_size, top_margin),
                         (left_margin + (i + 15) * cell_size,
                          top_margin + 10 * cell_size))

        if i < 10:
            num = font.render(str(i + 1), True, BLACK)
            let = font.render(letters[i], True, BLACK)

            num_width = num.get_width()
            num_height = num.get_height()
            let_width = let.get_width()

            screen.blit(num,
                        (left_margin - (cell_size // 2 + num_width // 2),
                         top_margin + i * cell_size + (
                                 cell_size // 2 - num_height // 2)))

            screen.blit(let,
                        (left_margin + i * cell_size + (cell_size //
                                                        2 - let_width // 2),
                         top_margin - num_height * 1.5))

            screen.blit(num,
                        (left_margin - (cell_size // 2 + num_width // 2) + 15 *
                         cell_size, top_margin + i * cell_size +
                         (cell_size // 2 - num_height // 2)))

            screen.blit(let,
                        (left_margin + i * cell_size + (cell_size // 2 -
                                                        let_width // 2) + 15 * cell_size,
                         top_margin - num_height * 1.5))
            # Ver num grid2


def check_for_winner(score1, score2):
    if score1 == 20:
        print('1 поюедил')
    if score2 == 20:
        print('2 победил')

def main():
    game_over = False
    player1_turn = True
    player2_turn = False
    screen.fill(WHITE)

    draw_field()

    player1 = Field(1)
    player2 = Field(2)

    player1.generate_ships()
    player2.generate_ships()

    score1 = 0
    score2 = 0

    pygame.display.update()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if player1_turn:
                    if left_margin + 15 * cell_size <= x <= left_margin + 25 \
                            * cell_size and top_margin <= y <= top_margin + \
                            10 * cell_size:
                        fired_cell = ((x - left_margin) // cell_size + 1 - 15,
                                      (y - top_margin) // cell_size + 1)
                        if fired_cell in player2.ships and player2.ships[fired_cell][0] is False:
                            score1 += 1
                            wounded(fired_cell[0], fired_cell[1], 2, player2.ships)
                            if is_killed(fired_cell[0], fired_cell[1], player2.ships):
                                killed(fired_cell[0], fired_cell[1], 2, player2.ships)
                        elif fired_cell not in player2.ships:
                            missed(fired_cell[0], fired_cell[1], 2)
                            player1_turn = False
                            player2_turn = True
                if player2_turn:
                    if left_margin <= x <= left_margin + 10 * cell_size and \
                            top_margin <= y <= top_margin + 10 * cell_size:
                        fired_cell = ((x - left_margin) // cell_size + 1,
                                      (y - top_margin) // cell_size + 1)
                        print(fired_cell)
                        if fired_cell in player1.ships and player1.ships[fired_cell][0] is False:
                            score2 += 1
                            wounded(fired_cell[0], fired_cell[1], 1, player1.ships)
                            if is_killed(fired_cell[0], fired_cell[1], player1.ships):
                                killed(fired_cell[0], fired_cell[1], 1, player1.ships)
                        elif fired_cell not in player1.ships:
                            missed(fired_cell[0], fired_cell[1], 1)
                            player2_turn = False
                            player1_turn = True
                check_for_winner(score1, score2)

        pygame.display.update()


if __name__ == '__main__':
    main()
    pygame.quit()
