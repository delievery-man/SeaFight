import random
import time

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
from design import start_window_design, design, win_window_design, field_design


class Field:
    def __init__(self):
        self.ships = dict()
        self.cells_state = dict()
        self.set_cells_state()

    def set_cells_state(self):
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        for i in range(10):
            for j in range(1, 11):
                self.cells_state[(letters[i], j)] = True

    def generate_ships(self):
        s = 0
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        while s < 10:
            x = letters[random.randint(0, 9)]
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
                self.put_ship(ship)
                s += 1

    @staticmethod
    def make_four_deck_ship(x, y, turn):
        if turn == 0:
            if x == 'A':
                return [('A', y), ('B', y), ('C', y), ('D', y)]
            if x == 'J' or x == 'I':
                return [('G', y), ('H', y), ('I', y), ('J', y)]
            else:
                return [(chr(ord(x) - 1), y), (x, y),
                        (chr(ord(x) + 1), y),
                        (chr(ord(x) + 2), y)]
        else:
            if y == 1:
                return [(x, 1), (x, 2), (x, 3), (x, 4)]
            elif y == 10 or y == 9:
                return [(x, 10), (x, 9), (x, 8), (x, 7)]
            else:
                return [(x, y - 1), (x, y), (x, y + 1), (x, y + 2)]

    @staticmethod
    def make_three_deck_ship(x, y, turn):
        if turn == 0:
            if x == 'A':
                return [('A', y), ('B', y), ('C', y)]
            elif x == 'J':
                return [('H', y), ('I', y), ('J', y)]
            else:
                return [(chr(ord(x) - 1), y), (x, y), (chr(ord(x) + 1), y)]
        else:
            if y == 1:
                return [(x, 1), (x, 2), (x, 3)]
            elif y == 10:
                return [(x, 10), (x, 9), (x, 8)]
            else:
                return [(x, y + 1), (x, y), (x, y - 1)]

    @staticmethod
    def make_two_deck_ship(x, y, turn):
        if turn == 0:
            if x == 'J':
                return [(chr(ord(x) - 1), y), (x, y)]
            else:
                return [(x, y), (chr(ord(x) + 1), y)]
        else:
            if y == 10:
                return [(x, 10), (x, 9)]
            else:
                return [(x, y), (x, y + 1)]

    def is_ship_can_be_put(self, ship):
        for cell in ship:
            if self.cells_state[cell] is False:
                return False
        return True

    def put_ship(self, ship):
        for cell in ship:
            x = cell[0]
            y = cell[1]
            neighbours = []
            for n in ship:
                if n == cell:
                    continue
                neighbours.append(n)
            self.ships[cell] = (False, neighbours)
            self.disable_cells(x, y, self.cells_around(x, y))

    @staticmethod
    def cells_around(x, y):
        if y == 1:
            if x == 'A':
                return ['down', 'down-right', 'right']
            elif x == 'J':
                return ['left', 'down-left', 'down']
            else:
                return ['left', 'down-left', 'down', 'down-right', 'right']
        elif y == 10:
            if x == 'A':
                return ['up', 'up-right', 'right']
            elif x == 'J':
                return ['left', 'up-left', 'up']
            else:
                return ['left', 'up-left', 'up', 'up-right', 'right']
        else:
            if x == 'A':
                return ['up', 'up-right', 'right', 'down-right', 'down']
            elif x == 'J':
                return ['down', 'down-left', 'left', 'up-left', 'up']
            else:
                return ['left', 'up-left', 'up', 'up-right', 'right',
                        'down-right', 'down', 'down-left']

    def disable_cells(self, x, y, directions):
        self.cells_state[(x, y)] = False
        for d in directions:
            if d == 'up':
                self.cells_state[(x, y - 1)] = False
            elif d == 'down':
                self.cells_state[(x, y + 1)] = False
            elif d == 'left':
                key = (chr(ord(x) - 1), y)
                self.cells_state[key] = False
            elif d == 'right':
                key = (chr(ord(x) + 1), y)
                self.cells_state[key] = False
            elif d == 'up-left':
                key = (chr(ord(x) - 1), y - 1)
                self.cells_state[key] = False
            elif d == 'up-right':
                key = (chr(ord(x) + 1), y - 1)
                self.cells_state[key] = False
            elif d == 'down-left':
                key = (chr(ord(x) - 1), y + 1)
                self.cells_state[key] = False
            elif d == 'down-right':
                key = (chr(ord(x) + 1), y + 1)
                self.cells_state[key] = False


class StartWindow(QMainWindow, start_window_design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Морской бой')

        self.start_friend.clicked.connect(self.open_field_window)
        self.start_computer.clicked.connect(self.open_field_window_bot)
        self.exit.clicked.connect(self.hide)

    def open_main_window(self):
        self.hide()
        GameWindow()

    def open_field_window(self):
        self.hide()
        self.field_window = FieldWindow(1)
        self.field_window.show()

    def open_field_window_bot(self):
        self.hide()
        self.field_window = FieldWindow(0)
        self.field_window.show()


class FieldWindow(QMainWindow, field_design.Ui_MainWindow):
    def __init__(self, player):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Морской бой')
        if player == 0:
            self.player_label.setText('Игрок')
        else:
            self.player_label.setText('Игрок {0}'.format(player))

        self.random.clicked.connect(self.generate_ships_randomly)
        if player == 1:
            self.next.clicked.connect(self.open_field_window)
        if player == 2:
            self.next.clicked.connect(self.open_main_window)
        if player == 0:
            second_field.generate_ships()
            self.next.clicked.connect(self.open_main_window_bot)

        self.player = player

        self.show()

    def generate_ships_randomly(self):
        if self.player == 1 or self.player == 0:
            first_field.generate_ships()
        else:
            second_field.generate_ships()

    def open_field_window(self):
        self.hide()
        self.field_window = FieldWindow(2)
        self.field_window.show()

    def open_main_window(self):
        self.hide()
        GameWindow()

    def open_main_window_bot(self):
        self.hide()
        GameWithBotWindow()


class GameWindow(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.first_player_buttons = {
            ('A', 1): self.f_A1, ('A', 2): self.f_A2, ('A', 3): self.f_A3,
            ('A', 4): self.f_A4, ('A', 5): self.f_A5, ('A', 6): self.f_A6,
            ('A', 7): self.f_A7, ('A', 8): self.f_A8, ('A', 9): self.f_A9,
            ('A', 10): self.f_A10, ('B', 1): self.f_B1, ('B', 2): self.f_B2,
            ('B', 3): self.f_B3, ('B', 4): self.f_B4, ('B', 5): self.f_B5,
            ('B', 6): self.f_B6, ('B', 7): self.f_B7, ('B', 8): self.f_B8,
            ('B', 9): self.f_B9, ('B', 10): self.f_B10, ('C', 1): self.f_C1,
            ('C', 2): self.f_C2, ('C', 3): self.f_C3, ('C', 4): self.f_C4,
            ('C', 5): self.f_C5, ('C', 6): self.f_C6, ('C', 7): self.f_C7,
            ('C', 8): self.f_C8, ('C', 9): self.f_C9, ('C', 10): self.f_C10,
            ('D', 1): self.f_D1, ('D', 2): self.f_D2, ('D', 3): self.f_D3,
            ('D', 4): self.f_D4, ('D', 5): self.f_D5, ('D', 6): self.f_D6,
            ('D', 7): self.f_D7, ('D', 8): self.f_D8, ('D', 9): self.f_D9,
            ('D', 10): self.f_D10, ('E', 1): self.f_E1, ('E', 2): self.f_E2,
            ('E', 3): self.f_E3, ('E', 4): self.f_E4, ('E', 5): self.f_E5,
            ('E', 6): self.f_E6, ('E', 7): self.f_E7, ('E', 8): self.f_E8,
            ('E', 9): self.f_E9, ('E', 10): self.f_E10, ('F', 1): self.f_F1,
            ('F', 2): self.f_F2, ('F', 3): self.f_F3, ('F', 4): self.f_F4,
            ('F', 5): self.f_F5, ('F', 6): self.f_F6, ('F', 7): self.f_F7,
            ('F', 8): self.f_F8, ('F', 9): self.f_F9, ('F', 10): self.f_F10,
            ('G', 1): self.f_G1, ('G', 2): self.f_G2, ('G', 3): self.f_G3,
            ('G', 4): self.f_G4, ('G', 5): self.f_G5, ('G', 6): self.f_G6,
            ('G', 7): self.f_G7, ('G', 8): self.f_G8, ('G', 9): self.f_G9,
            ('G', 10): self.f_G10, ('H', 1): self.f_H1, ('H', 2): self.f_H2,
            ('H', 3): self.f_H3, ('H', 4): self.f_H4, ('H', 5): self.f_H5,
            ('H', 6): self.f_H6, ('H', 7): self.f_H7, ('H', 8): self.f_H8,
            ('H', 9): self.f_H9, ('H', 10): self.f_H10, ('I', 1): self.f_I1,
            ('I', 2): self.f_I2, ('I', 3): self.f_I3, ('I', 4): self.f_I4,
            ('I', 5): self.f_I5, ('I', 6): self.f_I6, ('I', 7): self.f_I7,
            ('I', 8): self.f_I8, ('I', 9): self.f_I9, ('I', 10): self.f_I10,
            ('J', 1): self.f_J1, ('J', 2): self.f_J2, ('J', 3): self.f_J3,
            ('J', 4): self.f_J4, ('J', 5): self.f_J5, ('J', 6): self.f_J6,
            ('J', 7): self.f_J7, ('J', 8): self.f_J8, ('J', 9): self.f_J9,
            ('J', 10): self.f_J10}
        self.second_player_buttons = {
            ('A', 1): self.s_A1, ('A', 2): self.s_A2, ('A', 3): self.s_A3,
            ('A', 4): self.s_A4, ('A', 5): self.s_A5, ('A', 6): self.s_A6,
            ('A', 7): self.s_A7, ('A', 8): self.s_A8, ('A', 9): self.s_A9,
            ('A', 10): self.s_A10, ('B', 1): self.s_B1, ('B', 2): self.s_B2,
            ('B', 3): self.s_B3, ('B', 4): self.s_B4, ('B', 5): self.s_B5,
            ('B', 6): self.s_B6, ('B', 7): self.s_B7, ('B', 8): self.s_B8,
            ('B', 9): self.s_B9, ('B', 10): self.s_B10, ('C', 1): self.s_C1,
            ('C', 2): self.s_C2, ('C', 3): self.s_C3, ('C', 4): self.s_C4,
            ('C', 5): self.s_C5, ('C', 6): self.s_C6, ('C', 7): self.s_C7,
            ('C', 8): self.s_C8, ('C', 9): self.s_C9, ('C', 10): self.s_C10,
            ('D', 1): self.s_D1, ('D', 2): self.s_D2, ('D', 3): self.s_D3,
            ('D', 4): self.s_D4, ('D', 5): self.s_D5, ('D', 6): self.s_D6,
            ('D', 7): self.s_D7, ('D', 8): self.s_D8, ('D', 9): self.s_D9,
            ('D', 10): self.s_D10, ('E', 1): self.s_E1, ('E', 2): self.s_E2,
            ('E', 3): self.s_E3, ('E', 4): self.s_E4, ('E', 5): self.s_E5,
            ('E', 6): self.s_E6, ('E', 7): self.s_E7, ('E', 8): self.s_E8,
            ('E', 9): self.s_E9, ('E', 10): self.s_E10, ('F', 1): self.s_F1,
            ('F', 2): self.s_F2, ('F', 3): self.s_F3, ('F', 4): self.s_F4,
            ('F', 5): self.s_F5, ('F', 6): self.s_F6, ('F', 7): self.s_F7,
            ('F', 8): self.s_F8, ('F', 9): self.s_F9, ('F', 10): self.s_F10,
            ('G', 1): self.s_G1, ('G', 2): self.s_G2, ('G', 3): self.s_G3,
            ('G', 4): self.s_G4, ('G', 5): self.s_G5, ('G', 6): self.s_G6,
            ('G', 7): self.s_G7, ('G', 8): self.s_G8, ('G', 9): self.s_G9,
            ('G', 10): self.s_G10, ('H', 1): self.s_H1, ('H', 2): self.s_H2,
            ('H', 3): self.s_H3, ('H', 4): self.s_H4, ('H', 5): self.s_H5,
            ('H', 6): self.s_H6, ('H', 7): self.s_H7, ('H', 8): self.s_H8,
            ('H', 9): self.s_H9, ('H', 10): self.s_H10, ('I', 1): self.s_I1,
            ('I', 2): self.s_I2, ('I', 3): self.s_I3, ('I', 4): self.s_I4,
            ('I', 5): self.s_I5, ('I', 6): self.s_I6, ('I', 7): self.s_I7,
            ('I', 8): self.s_I8, ('I', 9): self.s_I9, ('I', 10): self.s_I10,
            ('J', 1): self.s_J1, ('J', 2): self.s_J2, ('J', 3): self.s_J3,
            ('J', 4): self.s_J4, ('J', 5): self.s_J5, ('J', 6): self.s_J6,
            ('J', 7): self.s_J7, ('J', 8): self.s_J8, ('J', 9): self.s_J9,
            ('J', 10): self.s_J10}

        self.killed_ship = []
        self.unavailable_buttons = []
        self.first_player_score = 0
        self.second_player_score = 0

        self.player = 1
        self.ships = second_field.ships
        self.buttons = self.second_player_buttons
        for btn in self.first_player_buttons.values():
            btn.setEnabled(False)

        for cell, btn in self.first_player_buttons.items():
            btn.clicked.connect(lambda arg, x=cell, y=btn:
                                self.stroke(x, y))

        for cell, btn in self.second_player_buttons.items():
            btn.clicked.connect(lambda arg, x=cell, y=btn:
                                self.stroke(x, y))

        self.ships_shown_1 = False
        self.show_1.clicked.connect(self.show_hide_ships_1)
        self.ships_shown_2 = False
        self.show_2.clicked.connect(self.show_hide_ships_2)

    def initUI(self):
        self.setupUi(self)
        self.setWindowTitle('Морской бой')
        self.show()

    def show_hide_ships_1(self):
        if not self.ships_shown_1:
            for ship in first_field.ships:
                self.first_player_buttons[ship]. \
                    setStyleSheet('background-color: lightgreen')
            self.show_1.setText('Скрыть корабли')
            self.ships_shown_1 = True
        else:
            for ship in first_field.ships:
                self.first_player_buttons[ship]. \
                    setStyleSheet('default')
            self.show_1.setText('Показать корабли')
            self.ships_shown_1 = False

    def show_hide_ships_2(self):
        if not self.ships_shown_2:
            for ship in second_field.ships:
                self.second_player_buttons[ship]. \
                    setStyleSheet('background-color: lightgreen')
            self.show_2.setText('Скрыть корабли')
            self.ships_shown_2 = True
        else:
            for ship in second_field.ships:
                self.second_player_buttons[ship]. \
                    setStyleSheet('default')
            self.show_2.setText('Показать корабли')
            self.ships_shown_2 = False

    def switch_move(self):
        if self.player == 1:
            self.player = 2
            self.ships = first_field.ships
            self.buttons = self.first_player_buttons
            for btn in self.first_player_buttons.values():
                if btn not in self.unavailable_buttons:
                    btn.setEnabled(True)
            for btn in self.second_player_buttons.values():
                btn.setEnabled(False)

        elif self.player == 2:
            self.player = 1
            self.ships = second_field.ships
            self.buttons = self.second_player_buttons
            for btn in self.second_player_buttons.values():
                if btn not in self.unavailable_buttons:
                    btn.setEnabled(True)
            for btn in self.first_player_buttons.values():
                btn.setEnabled(False)

    def check_for_winner(self):
        if self.first_player_score == 20:
            self.win = WinWindow('Первый игрок', self)
            self.win.show()
        if self.second_player_score == 20:
            self.win = WinWindow('Второй игрок', self)
            self.win.show()

    def stroke(self, cell, btn):
        x = cell[0]
        y = cell[1]

        if (x, y) in self.ships:
            self.wounded(x, y, btn)
            self.updateScore()
            if self.is_killed(x, y):
                self.killed()
                self.check_for_winner()
        else:
            self.missed(btn)
            self.switch_move()

    def updateScore(self):
        if self.player == 1:
            self.first_player_score += 1
            self.score_first.setText(
                'Очки: {0}'.format(self.first_player_score))
        else:
            self.second_player_score += 1
            self.score_second.setText(
                'Очки: {0}'.format(self.second_player_score))

    def wounded(self, x, y, btn):
        btn.setStyleSheet('background-color: pink')
        btn.setEnabled(False)
        self.ships[(x, y)] = (True, self.ships[(x, y)][1])

    def missed(self, btn):
        btn.setEnabled(False)
        self.unavailable_buttons.append(btn)

    def is_killed(self, x, y):
        self.killed_ship = [(x, y)]
        for neighbour in self.ships[(x, y)][1]:
            n_x = neighbour[0]
            n_y = neighbour[1]
            if self.ships[(n_x, n_y)][0]:
                self.killed_ship.append((n_x, n_y))
        if len(self.killed_ship) == len(self.ships[(x, y)][1]) + 1:
            return True
        return False

    def killed(self):
        for cell in self.killed_ship:
            x = cell[0]
            y = cell[1]
            self.buttons[(x, y)].setStyleSheet('background-color: red')
            self.disable_buttons(x, y, self.cells_around(x, y))

    @staticmethod
    def cells_around(x, y):
        if y == 1:
            if x == 'A':
                return ['down', 'down-right', 'right']
            elif x == 'J':
                return ['left', 'down-left', 'down']
            else:
                return ['left', 'down-left', 'down', 'down-right', 'right']
        elif y == 10:
            if x == 'A':
                return ['up', 'up-right', 'right']
            elif x == 'J':
                return ['left', 'up-left', 'up']
            else:
                return ['left', 'up-left', 'up', 'up-right', 'right']
        else:
            if x == 'A':
                return ['up', 'up-right', 'right', 'down-right', 'down']
            elif x == 'J':
                return ['down', 'down-left', 'left', 'up-left', 'up']
            else:
                return ['left', 'up-left', 'up', 'up-right', 'right',
                        'down-right', 'down', 'down-left']

    def disable_buttons(self, x, y, directions):
        self.buttons[(x, y)].setEnabled(False)
        self.unavailable_buttons.append(self.buttons[(x, y)])
        for d in directions:
            if d == 'up':
                self.buttons[(x, y - 1)].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[(x, y - 1)])
            elif d == 'down':
                self.buttons[(x, y + 1)].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[(x, y + 1)])
            elif d == 'left':
                key = (chr(ord(x) - 1), y)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])
            elif d == 'right':
                key = (chr(ord(x) + 1), y)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])
            elif d == 'up-left':
                key = (chr(ord(x) - 1), y - 1)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])
            elif d == 'up-right':
                key = (chr(ord(x) + 1), y - 1)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])
            elif d == 'down-left':
                key = (chr(ord(x) - 1), y + 1)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])
            elif d == 'down-right':
                key = (chr(ord(x) + 1), y + 1)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])


class BotMemory:
    def __init__(self):
        self.checked = []
        self.wounds = []
        self.possible_ships = []


class GameWithBotWindow(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.first_player_buttons = {
            ('A', 1): self.f_A1, ('A', 2): self.f_A2, ('A', 3): self.f_A3,
            ('A', 4): self.f_A4, ('A', 5): self.f_A5, ('A', 6): self.f_A6,
            ('A', 7): self.f_A7, ('A', 8): self.f_A8, ('A', 9): self.f_A9,
            ('A', 10): self.f_A10, ('B', 1): self.f_B1, ('B', 2): self.f_B2,
            ('B', 3): self.f_B3, ('B', 4): self.f_B4, ('B', 5): self.f_B5,
            ('B', 6): self.f_B6, ('B', 7): self.f_B7, ('B', 8): self.f_B8,
            ('B', 9): self.f_B9, ('B', 10): self.f_B10, ('C', 1): self.f_C1,
            ('C', 2): self.f_C2, ('C', 3): self.f_C3, ('C', 4): self.f_C4,
            ('C', 5): self.f_C5, ('C', 6): self.f_C6, ('C', 7): self.f_C7,
            ('C', 8): self.f_C8, ('C', 9): self.f_C9, ('C', 10): self.f_C10,
            ('D', 1): self.f_D1, ('D', 2): self.f_D2, ('D', 3): self.f_D3,
            ('D', 4): self.f_D4, ('D', 5): self.f_D5, ('D', 6): self.f_D6,
            ('D', 7): self.f_D7, ('D', 8): self.f_D8, ('D', 9): self.f_D9,
            ('D', 10): self.f_D10, ('E', 1): self.f_E1, ('E', 2): self.f_E2,
            ('E', 3): self.f_E3, ('E', 4): self.f_E4, ('E', 5): self.f_E5,
            ('E', 6): self.f_E6, ('E', 7): self.f_E7, ('E', 8): self.f_E8,
            ('E', 9): self.f_E9, ('E', 10): self.f_E10, ('F', 1): self.f_F1,
            ('F', 2): self.f_F2, ('F', 3): self.f_F3, ('F', 4): self.f_F4,
            ('F', 5): self.f_F5, ('F', 6): self.f_F6, ('F', 7): self.f_F7,
            ('F', 8): self.f_F8, ('F', 9): self.f_F9, ('F', 10): self.f_F10,
            ('G', 1): self.f_G1, ('G', 2): self.f_G2, ('G', 3): self.f_G3,
            ('G', 4): self.f_G4, ('G', 5): self.f_G5, ('G', 6): self.f_G6,
            ('G', 7): self.f_G7, ('G', 8): self.f_G8, ('G', 9): self.f_G9,
            ('G', 10): self.f_G10, ('H', 1): self.f_H1, ('H', 2): self.f_H2,
            ('H', 3): self.f_H3, ('H', 4): self.f_H4, ('H', 5): self.f_H5,
            ('H', 6): self.f_H6, ('H', 7): self.f_H7, ('H', 8): self.f_H8,
            ('H', 9): self.f_H9, ('H', 10): self.f_H10, ('I', 1): self.f_I1,
            ('I', 2): self.f_I2, ('I', 3): self.f_I3, ('I', 4): self.f_I4,
            ('I', 5): self.f_I5, ('I', 6): self.f_I6, ('I', 7): self.f_I7,
            ('I', 8): self.f_I8, ('I', 9): self.f_I9, ('I', 10): self.f_I10,
            ('J', 1): self.f_J1, ('J', 2): self.f_J2, ('J', 3): self.f_J3,
            ('J', 4): self.f_J4, ('J', 5): self.f_J5, ('J', 6): self.f_J6,
            ('J', 7): self.f_J7, ('J', 8): self.f_J8, ('J', 9): self.f_J9,
            ('J', 10): self.f_J10}
        self.second_player_buttons = {
            ('A', 1): self.s_A1, ('A', 2): self.s_A2, ('A', 3): self.s_A3,
            ('A', 4): self.s_A4, ('A', 5): self.s_A5, ('A', 6): self.s_A6,
            ('A', 7): self.s_A7, ('A', 8): self.s_A8, ('A', 9): self.s_A9,
            ('A', 10): self.s_A10, ('B', 1): self.s_B1, ('B', 2): self.s_B2,
            ('B', 3): self.s_B3, ('B', 4): self.s_B4, ('B', 5): self.s_B5,
            ('B', 6): self.s_B6, ('B', 7): self.s_B7, ('B', 8): self.s_B8,
            ('B', 9): self.s_B9, ('B', 10): self.s_B10, ('C', 1): self.s_C1,
            ('C', 2): self.s_C2, ('C', 3): self.s_C3, ('C', 4): self.s_C4,
            ('C', 5): self.s_C5, ('C', 6): self.s_C6, ('C', 7): self.s_C7,
            ('C', 8): self.s_C8, ('C', 9): self.s_C9, ('C', 10): self.s_C10,
            ('D', 1): self.s_D1, ('D', 2): self.s_D2, ('D', 3): self.s_D3,
            ('D', 4): self.s_D4, ('D', 5): self.s_D5, ('D', 6): self.s_D6,
            ('D', 7): self.s_D7, ('D', 8): self.s_D8, ('D', 9): self.s_D9,
            ('D', 10): self.s_D10, ('E', 1): self.s_E1, ('E', 2): self.s_E2,
            ('E', 3): self.s_E3, ('E', 4): self.s_E4, ('E', 5): self.s_E5,
            ('E', 6): self.s_E6, ('E', 7): self.s_E7, ('E', 8): self.s_E8,
            ('E', 9): self.s_E9, ('E', 10): self.s_E10, ('F', 1): self.s_F1,
            ('F', 2): self.s_F2, ('F', 3): self.s_F3, ('F', 4): self.s_F4,
            ('F', 5): self.s_F5, ('F', 6): self.s_F6, ('F', 7): self.s_F7,
            ('F', 8): self.s_F8, ('F', 9): self.s_F9, ('F', 10): self.s_F10,
            ('G', 1): self.s_G1, ('G', 2): self.s_G2, ('G', 3): self.s_G3,
            ('G', 4): self.s_G4, ('G', 5): self.s_G5, ('G', 6): self.s_G6,
            ('G', 7): self.s_G7, ('G', 8): self.s_G8, ('G', 9): self.s_G9,
            ('G', 10): self.s_G10, ('H', 1): self.s_H1, ('H', 2): self.s_H2,
            ('H', 3): self.s_H3, ('H', 4): self.s_H4, ('H', 5): self.s_H5,
            ('H', 6): self.s_H6, ('H', 7): self.s_H7, ('H', 8): self.s_H8,
            ('H', 9): self.s_H9, ('H', 10): self.s_H10, ('I', 1): self.s_I1,
            ('I', 2): self.s_I2, ('I', 3): self.s_I3, ('I', 4): self.s_I4,
            ('I', 5): self.s_I5, ('I', 6): self.s_I6, ('I', 7): self.s_I7,
            ('I', 8): self.s_I8, ('I', 9): self.s_I9, ('I', 10): self.s_I10,
            ('J', 1): self.s_J1, ('J', 2): self.s_J2, ('J', 3): self.s_J3,
            ('J', 4): self.s_J4, ('J', 5): self.s_J5, ('J', 6): self.s_J6,
            ('J', 7): self.s_J7, ('J', 8): self.s_J8, ('J', 9): self.s_J9,
            ('J', 10): self.s_J10}

        self.killed_ship = []
        self.unavailable_buttons = []
        self.first_player_score = 0
        self.second_player_score = 0
        self.bot_memory = BotMemory()

        self.player = 1
        self.ships = second_field.ships
        self.buttons = self.second_player_buttons
        self.player_1.setStyleSheet('background-color: lightgreen')
        # for btn in self.first_player_buttons.values():
        #     btn.setEnabled(False)


        for cell, btn in self.second_player_buttons.items():
            btn.clicked.connect(lambda arg, x=cell, y=btn:
                                self.stroke(x, y))

        self.ships_shown_1 = False
        self.show_1.clicked.connect(self.show_hide_ships_1)
        self.ships_shown_2 = False
        self.show_2.clicked.connect(self.show_hide_ships_2)

    def initUI(self):
        self.setupUi(self)
        self.setWindowTitle('Морской бой')
        self.show()

    def show_hide_ships_1(self):
        if not self.ships_shown_1:
            for ship in first_field.ships:
                if self.first_player_buttons[ship] not in \
                        self.unavailable_buttons:
                    self.first_player_buttons[ship]. \
                        setStyleSheet('background-color: lightgreen')
            self.show_1.setText('Скрыть корабли')
            self.ships_shown_1 = True
        else:
            for ship in first_field.ships:
                if self.first_player_buttons[ship] not in \
                        self.unavailable_buttons:
                    self.first_player_buttons[ship]. \
                        setStyleSheet('default')
            self.show_1.setText('Показать корабли')
            self.ships_shown_1 = False

    def show_hide_ships_2(self):
        if not self.ships_shown_2:
            for ship in second_field.ships:
                if self.second_player_buttons[ship] not in \
                        self.unavailable_buttons:
                    self.second_player_buttons[ship]. \
                        setStyleSheet('background-color: lightgreen')
            self.show_2.setText('Скрыть корабли')
            self.ships_shown_2 = True
        else:
            for ship in second_field.ships:
                if self.second_player_buttons[ship] not in \
                        self.unavailable_buttons:
                    self.second_player_buttons[ship]. \
                        setStyleSheet('default')
            self.show_2.setText('Показать корабли')
            self.ships_shown_2 = False

    def switch_move(self):
        if self.player == 1:
            self.player = 2
            self.ships = first_field.ships
            self.buttons = self.first_player_buttons
            self.player_2.setStyleSheet('background-color: lightgreen')
            self.player_1.setStyleSheet('default')

            # for btn in self.first_player_buttons.values():
            #     if btn not in self.unavailable_buttons:
            #         btn.setEnabled(True)
            # for btn in self.second_player_buttons.values():
            #     btn.setEnabled(False)

            self.bot_stroke()
        elif self.player == 2:
            self.player = 1
            self.ships = second_field.ships
            self.buttons = self.second_player_buttons
            self.player_1.setStyleSheet('background-color: lightgreen')
            self.player_2.setStyleSheet('default')
            # for btn in self.second_player_buttons.values():
            #     if btn not in self.unavailable_buttons:
            #         btn.setEnabled(True)
            # for btn in self.first_player_buttons.values():
            #     btn.setEnabled(False)

    def check_for_winner(self):
        if self.first_player_score == 20:
            self.win = WinWindow('Первый игрок', self)
            self.win.show()
        if self.second_player_score == 20:
            self.win = WinWindow('Второй игрок', self)
            self.win.show()

    def stroke(self, cell, btn):
        x = cell[0]
        y = cell[1]

        if (x, y) in self.ships:
            self.wounded(x, y, btn)
            self.updateScore()
            if self.is_killed(x, y):
                self.killed()
                self.check_for_winner()
        else:
            self.missed(btn)
            self.switch_move()

    def bot_stroke(self):
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        if len(self.bot_memory.possible_ships) != 0:
            x = self.bot_memory.possible_ships[0][0]
            y = self.bot_memory.possible_ships[0][1]
            while len(self.bot_memory.possible_ships) != 0 and \
                    (x, y) in self.bot_memory.checked:
                self.bot_memory.possible_ships.remove((x, y))
                x = self.bot_memory.possible_ships[0][0]
                y = self.bot_memory.possible_ships[0][1]
            self.bot_memory.possible_ships.remove((x, y))
        else:
            x = letters[random.randint(0, 9)]
            y = random.randint(1, 10)
            while (x, y) in self.bot_memory.checked:
                x = letters[random.randint(0, 9)]
                y = random.randint(1, 10)

        self.bot_memory.checked.append((x, y))

        if (x, y) in self.ships:
            self.wounded(x, y, self.buttons[(x, y)])
            if self.is_killed(x, y):
                self.killed()
                self.bot_memory.possible_ships = []
            else:
                self.make_possible_ships(x, y)
            self.updateScore()
            self.bot_stroke()
        else:
            self.missed(self.buttons[(x, y)])
            self.switch_move()

    def make_possible_ships(self, x, y):
        # if x == 'A' and y == 1:
        #     self.bot_memory.possible_ships.append(('B', 1))
        #     self.bot_memory.possible_ships.append(('C', 1))
        #     self.bot_memory.possible_ships.append(('D', 1))
        #     self.bot_memory.possible_ships.append(('A', 2))
        #     self.bot_memory.possible_ships.append(('A', 3))
        #     self.bot_memory.possible_ships.append(('A', 4))
        # elif x == 'A' and y == 10:
        #     self.bot_memory.possible_ships.append(('A', 9))
        #     self.bot_memory.possible_ships.append(('A', 8))
        #     self.bot_memory.possible_ships.append(('A', 7))
        #     self.bot_memory.possible_ships.append(('B', 10))
        #     self.bot_memory.possible_ships.append(('C', 10))
        #     self.bot_memory.possible_ships.append(('D', 10))
        # elif x == 'J' and y == 1:
        #     self.bot_memory.possible_ships.append(('I', 1))
        #     self.bot_memory.possible_ships.append(('H', 1))
        #     self.bot_memory.possible_ships.append(('G', 1))
        #     self.bot_memory.possible_ships.append(('J', 2))
        #     self.bot_memory.possible_ships.append(('J', 3))
        #     self.bot_memory.possible_ships.append(('J', 4))
        # elif x == 'J' and y == 10:
        #     self.bot_memory.possible_ships.append(('I', 10))
        #     self.bot_memory.possible_ships.append(('H', 10))
        #     self.bot_memory.possible_ships.append(('G', 10))
        #     self.bot_memory.possible_ships.append(('J', 9))
        #     self.bot_memory.possible_ships.append(('J', 8))
        #     self.bot_memory.possible_ships.append(('J', 7))
        if y == 1:
            if x == 'A':
                cells = ['down', 'right']
            elif x == 'J':
                cells = ['left', 'down']
            else:
                cells = ['left', 'down', 'right']
        elif y == 10:
            if x == 'A':
                cells = ['up', 'right']
            elif x == 'J':
                cells = ['left', 'up']
            else:
                cells = ['left', 'up', 'right']
        else:
            if x == 'A':
                cells = ['up', 'right', 'down']
            elif x == 'J':
                cells = ['down', 'left', 'up']
            else:
                cells = ['left', 'up', 'right', 'down']
        for cell in cells:
            if cell == 'down':
                self.bot_memory.possible_ships.append((x, y + 1))
            elif cell == 'up':
                self.bot_memory.possible_ships.append((x, y - 1))
            elif cell == 'left':
                self.bot_memory.possible_ships.append((chr(ord(x) - 1), y))
            elif cell == 'right':
                self.bot_memory.possible_ships.append((chr(ord(x) + 1), y))

    def updateScore(self):
        if self.player == 1:
            self.first_player_score += 1
            self.score_first.setText(
                'Очки: {0}'.format(self.first_player_score))
        else:
            self.second_player_score += 1
            self.score_second.setText(
                'Очки: {0}'.format(self.second_player_score))

    def wounded(self, x, y, btn):
        btn.setStyleSheet('background-color: pink')
        btn.setEnabled(False)
        self.ships[(x, y)] = (True, self.ships[(x, y)][1])

    def missed(self, btn):
        btn.setEnabled(False)
        self.unavailable_buttons.append(btn)

    def is_killed(self, x, y):
        self.killed_ship = [(x, y)]
        for neighbour in self.ships[(x, y)][1]:
            n_x = neighbour[0]
            n_y = neighbour[1]
            if self.ships[(n_x, n_y)][0]:
                self.killed_ship.append((n_x, n_y))
        if len(self.killed_ship) == len(self.ships[(x, y)][1]) + 1:
            return True
        return False

    def killed(self):
        for cell in self.killed_ship:
            x = cell[0]
            y = cell[1]
            self.buttons[(x, y)].setStyleSheet('background-color: red')
            self.disable_buttons(x, y, self.cells_around(x, y))

    @staticmethod
    def cells_around(x, y):
        if y == 1:
            if x == 'A':
                return ['down', 'down-right', 'right']
            elif x == 'J':
                return ['left', 'down-left', 'down']
            else:
                return ['left', 'down-left', 'down', 'down-right', 'right']
        elif y == 10:
            if x == 'A':
                return ['up', 'up-right', 'right']
            elif x == 'J':
                return ['left', 'up-left', 'up']
            else:
                return ['left', 'up-left', 'up', 'up-right', 'right']
        else:
            if x == 'A':
                return ['up', 'up-right', 'right', 'down-right', 'down']
            elif x == 'J':
                return ['down', 'down-left', 'left', 'up-left', 'up']
            else:
                return ['left', 'up-left', 'up', 'up-right', 'right',
                        'down-right', 'down', 'down-left']

    def disable_buttons(self, x, y, directions):
        self.buttons[(x, y)].setEnabled(False)
        self.unavailable_buttons.append(self.buttons[(x, y)])
        self.bot_memory.possible_ships.append((x, y))
        for d in directions:
            if d == 'up':
                self.buttons[(x, y - 1)].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[(x, y - 1)])
                self.bot_memory.possible_ships.append((x, y - 1))
            elif d == 'down':
                self.buttons[(x, y + 1)].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[(x, y + 1)])
                self.bot_memory.possible_ships.append((x, y + 1))
            elif d == 'left':
                key = (chr(ord(x) - 1), y)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])
                self.bot_memory.possible_ships.append(key)
            elif d == 'right':
                key = (chr(ord(x) + 1), y)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])
                self.bot_memory.possible_ships.append(key)
            elif d == 'up-left':
                key = (chr(ord(x) - 1), y - 1)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])
                self.bot_memory.possible_ships.append(key)
            elif d == 'up-right':
                key = (chr(ord(x) + 1), y - 1)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])
                self.bot_memory.possible_ships.append(key)
            elif d == 'down-left':
                key = (chr(ord(x) - 1), y + 1)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])
                self.bot_memory.possible_ships.append(key)
            elif d == 'down-right':
                key = (chr(ord(x) + 1), y + 1)
                self.buttons[key].setEnabled(False)
                self.unavailable_buttons.append(self.buttons[key])
                self.bot_memory.possible_ships.append(key)


class WinWindow(QMainWindow, win_window_design.Ui_MainWindow):
    def __init__(self, winner, gameWindow):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Морской бой')
        self.gameWindow = gameWindow

        self.label.setText('{0} победил'.format(winner))
        self.start.clicked.connect(self.open_main_window)
        self.exit.clicked.connect(self.hide)

        self.show()

    def open_main_window(self):
        self.hide()
        self.gameWindow.hide()
        GameWindow()


first_field = Field()
second_field = Field()


def main():
    app = QApplication([])
    window = StartWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()