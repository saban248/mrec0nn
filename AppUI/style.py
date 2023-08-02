from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QLabel, QPushButton

SColor = {
    "defa": f"rgb(206,216,224)",
    "sea": f"rgb(92,133,170)",
    "night": f"rgb(49,49,49)",
    "hack": "rgb(12,18,65)",
    "light": f"rgb(191,195,192)",
    "pof": "rgb(68,68,68)",
    "pof-h": "rgb(48,48,48)"
}

Templates = {"MainWindow": f"*{{background:qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0,"
                           f"stop:0 rgb(20,20,10),"
                           f"stop:1 {SColor['night']});"
                           f"color:{SColor['light']};"
                           f"font-family:consolas;}}",
             "Frame": f"*{{background:{SColor['pof-h']};"
                      f"border-radius:8px;"
                      f"font-family:consolas;"
                      f"font-size:14px;"
                      f"color:rgb(142,184,222);}}"
                      f"*:hover{{background:{SColor['pof']};}}",
             "button": "*{font-size:13px;"
                       f"color:rgb(171,201,227);}}"
                       f"*:hover{{background:{SColor['defa']};color:rgb(28,66,100);}}",
             "title": "*{background:rgb(10,10,10);"
                      "color:#D56549;border:1px solid rgb(38,38,38);}",
             "url": "*{color:white;}"
                    "*:hover{background:rgb(20,20,20);}",
             "info-lbl": "*{font-size:14px;"
                         "font-family:consolas;"
                         f"color:{SColor['light']};}}"
                         f"*:hover{{background:{SColor['pof-h']};"
                         f"}}",
             "look-lbl": "*{font-size:14px;"
                         "font-family:consolas;"
                         "color:rgb(205,205,83);}*:hover"
                         "{background:rgb(205,205,83);color:rgb(0,0,0);}"}


class Style:

    # def __init__(self, setting=None):
    #     self._setSetting(setting)

    def style(self, key):
        return Templates[key]

    def _setSetting(self, setting):
        self.setting = setting


class AnimateText(QThread):
    emitLetter = pyqtSignal(str)
    emitFinish = pyqtSignal(int)

    def __init__(self, text: str, w: float, parent=None):
        super(AnimateText, self).__init__(parent)

        self._wait = w
        self.text = text
        self.stopit = 0

    # noinspection PyUnresolvedReferences
    def run(self) -> None:
        for ltr in range(self.text.__len__() + 1):
            if self.stopit:
                break
            self.emitLetter.emit(self.text[0:ltr])
            sleep(self._wait)

        self.emitFinish.emit(1)

    def stop(self):
        self.stopit = 1


def QLabel_(text: str, style: str, tb=0) -> QLabel:
    label = QLabel(text)
    label.setMinimumHeight(25)

    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet(style)
    label.setWordWrap(True)
    if tb:
        label.setTextInteractionFlags(Qt.TextBrowserInteraction)
    return label


def QButton(text: str, style: str):
    button = QPushButton(text)
    button.setCursor(Qt.PointingHandCursor)
    button.setMinimumHeight(25)
    button.setStyleSheet(style)

    return button

#
# def generator(nums: list):
#     yield "start now!"
#     yield "processs"
#     return "finished"
#
#
# d = generator([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
#
# for i in range(0, 10):
#     try:
#         print(d.__next__())
#     except StopIteration as e:
#         print("finito")
#         break
