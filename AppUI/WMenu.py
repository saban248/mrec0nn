from PyQt5.QtGui import *
from PyQt5.Qt import *

from AppUI.style import Style, QButton


class WMenu(QScrollArea):

    def __init__(self, controller,  parent=None):
        super(WMenu, self).__init__(parent)

        # /* var */
        self.UI = {}
        self.MenuControl = controller
        # /* ui setting */
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(0)
        self.MParent = QWidget()
        self.MParent.setStyleSheet(Style().style("Frame"))
        self.MainGrid = QGridLayout()
        self.MParent.setLayout(self.MainGrid)
        self.setWidget(self.MParent)

        self.setButtonMenuTools()

    def setButtonMenuTools(self):

        action = ['welcome', 'info', 'fuzzer', 'mapper',  'exit']
        for act in action:
            key = f'b{act}'
            self.UI[key] = QButton(act, Style().style("button"))
            self.UI[key].setMinimumHeight(20)
            self.MainGrid.addWidget(self.UI[key], action.index(act), 0)

        self.UI['bwelcome'].clicked.connect(lambda: self.MenuControl("wel"))
        self.UI['binfo'].clicked.connect(lambda: self.MenuControl("info"))
        self.UI['bfuzzer'].clicked.connect(lambda: self.MenuControl("fuzz"))
        self.UI['bmapper'].clicked.connect(lambda: self.MenuControl("mapp"))
        self.UI['bexit'].clicked.connect(lambda: self.MenuControl("exit"))

