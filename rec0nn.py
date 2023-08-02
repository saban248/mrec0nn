import os

from PyQt5.QtGui import *
from PyQt5.Qt import *
import sys

from AppUI.Massage import ShowMessage
from AppUI.WInfo import WInfo
from AppUI.WMapper import WMapper
from AppUI.WMenu import WMenu
from AppUI.WFuzzer import WFuzzer
from AppUI.Wwelcome import WWelcome
from AppUI.style import *

# /*- configuration Qt5 Window -*/
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"


WINS = {'wel': 0,
        'info': 0,
        'fuzz': 0,
        'mapp': 0,
        'exit': 0}


class MainWindow(QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        # /* var setting */
        self.UI = {}
        self.SETTING = {'ip': None,
                        'url': None,
                        'fuzz_on': 0}
        self.WIND0W: QWidget = None
        self.WINDOWS: dict[str, QWidget] = WINS
        self.Style = Style()
        self.address = None
        # /* window setting */
        self.setWindowTitle("Rec0nn V1.0")
        self.setGeometry(140, 60, 600, 400)
        self.installEventFilter(self)

        # /* UI */
        self.MainGrid = QGridLayout()
        # /* win tool */

        self.win_menu = WMenu(self.OpenWindow, self)
        # /* By default */
        self.OpenWindow('wel')

        # /* add wins to grid */
        self.MainGrid.addWidget(self.win_menu, 0, 0, Qt.AlignLeft)
        self.setLayout(self.MainGrid)

    def OpenWindow(self, win):
        if self.isWindowNow(win):
            return

        # /* hide */
        self.HideWindow()
        if self.WINDOWS[win]:
            self.WINDOWS[win].setHidden(False)
            self.WIND0W = self.WINDOWS[win]
            return

        if win == "wel":
            self.WIND0W = WWelcome(self.SETTING, self)
        elif win == "exit":
            self.closeEvent(QCloseEvent())
            return
        else:
            if self.SETTING['ip']:
                if win == "info":
                    self.WIND0W = WInfo(self.SETTING, self)
                elif win == "fuzz":
                    self.WIND0W = WFuzzer(self.SETTING, self)
                elif win == "mapp":
                    self.WIND0W = WMapper(self.SETTING, self)
            else:
                ShowMessage("please set ip of target before", self)
                return
        # /* set window */
        self.WINDOWS[win] = self.WIND0W
        # /* set window on grid */
        self.MainGrid.addWidget(self.WIND0W, 0, 1)

    def isWindowNow(self, win):
        if self.WINDOWS[win] == self.WIND0W:
            return 1

        return 0

    def HideWindow(self):
        if self.WIND0W:
            self.WIND0W.hide()

            self.WIND0W = None

    def CloseWindow(self, key):
        if self.WINDOWS[key]:
            self.WINDOWS[key].closeEvent(QCloseEvent())

            self.WINDOWS[key] = None

    def eventFilter(self, Type: 'QObject', event: 'QEvent') -> bool:
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter - 1:
                pass

        return super(MainWindow, self).eventFilter(Type, event)

    def closeEvent(self, a0: QCloseEvent) -> None:
        for win in self.WINDOWS.keys():
            self.CloseWindow(win)
        a0.accept()
        self.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()

    sys.exit(app.exec_())







