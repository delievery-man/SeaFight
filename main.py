import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
import design


class App(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        buttons = [self.y_A1, self.y_A2, self.y_A3, self.y_A4, self.y_A5,
                   self.y_A6, self.y_A7, self.y_A8, self.y_A9, self.y_A10,
                   self.y_B1, self.y_B2, self.y_B3, self.y_B4, self.y_B5,
                   self.y_B6, self.y_B7, self.y_B8, self.y_B9, self.y_B10,
                   self.y_C1, self.y_C2, self.y_C3, self.y_C4, self.y_C5,
                   self.y_C6, self.y_C7, self.y_C8, self.y_C9, self.y_C10,
                   self.y_D1, self.y_D2, self.y_D3, self.y_D4, self.y_D5,
                   self.y_D6, self.y_D7, self.y_D8, self.y_D9, self.y_D10,
                   self.y_E1, self.y_E2, self.y_E3, self.y_E4, self.y_E5,
                   self.y_E6, self.y_E7, self.y_E8, self.y_E9, self.y_E10,
                   self.y_F1, self.y_F2, self.y_F3, self.y_F4, self.y_F5,
                   self.y_F6, self.y_F7, self.y_F8, self.y_F9, self.y_F10,
                   self.y_G1, self.y_G2, self.y_G3, self.y_G4, self.y_G5,
                   self.y_G6, self.y_G7, self.y_G8, self.y_G9, self.y_G10,
                   self.y_H1, self.y_H2, self.y_H3, self.y_H4, self.y_H5,
                   self.y_H6, self.y_H7, self.y_H8, self.y_H9, self.y_H10,
                   self.y_I1, self.y_I2, self.y_I3, self.y_I4, self.y_I5,
                   self.y_I6, self.y_I7, self.y_I8, self.y_I9, self.y_I10,
                   self.y_J1, self.y_J2, self.y_J3, self.y_J4, self.y_J5,
                   self.y_J6, self.y_J7, self.y_J8, self.y_J9, self.y_J10]

        for btn in buttons:
            btn.clicked.connect(lambda arg, x=btn: self.fill_button(x))

    @staticmethod
    def fill_button(btn):
        btn.setStyleSheet('background-color: black')


def main():
    app = QApplication([])

    window = App()
    window.setWindowTitle('Морской бой')
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()


