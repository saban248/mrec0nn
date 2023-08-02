from PyQt5.QtWidgets import *
from PyQt5.Qt import *

from AppUI.style import Templates as Css


class ShowMessage(QWidget):

    def __init__(self, msg, parent=None, dis_close=False):
        super(ShowMessage, self).__init__(parent)

        self.msg = msg
        self.msgShowed = 0
        self.Close = dis_close
        self.setWindowFlags(Qt.SplashScreen)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setStyleSheet(Css['Frame']+"*{background:rgb(94,128,159);}")
        self.setMinimumSize(200, 130)
        self.setMaximumWidth(350)
        # /* mainGrid */
        self.MainGrid = QGridLayout(self)
        self.msg = QLabel(msg, self)
        self.msg.setStyleSheet("color:rgb(234,185,44);font-size:14px;")
        self.msg.setFont(QFont("rockwell", 10, QFont.ExtraLight))
        self.msg.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.msg.setWordWrap(True)

        self.bClose = QPushButton("CLOSE", self)
        self.bClose.setFont(QFont("consolas", 11, QFont.ExtraBold))
        self.bClose.setStyleSheet(Css['info-lbl'])
        self.bClose.setMinimumHeight(25)
        self.bClose.setCursor(Qt.PointingHandCursor)
        self.bClose.setDisabled(self.Close)
        self.bClose.clicked.connect(lambda: self.closeEvent(QCloseEvent()))
        self.MainGrid.addWidget(self.msg, 0, 0)
        self.MainGrid.addWidget(self.bClose, 1, 0)
        self.setLayout(self.MainGrid)

        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.msgShowed = 1
        self.deleteLater()
        a0.accept()
