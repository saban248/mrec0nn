from PyQt5.QtGui import *
from PyQt5.Qt import *
from json import dumps, loads

from AppUI.style import Templates as Css, QLabel_, QButton

SETTING_FUZZ = {"allow_redirects": False,
                "show_403": False,
                "show_302": True,
                'content_and_length': False,
                "threads": 30,
                "User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; "
                              "Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)",
                "cookies": {"cookies":"SET_ABOUT_COOKIES"},
                "headers": {"x-powered-by": "Hack_r"},
                "protocol": "http"}


class WSetting(QWidget):

    def __init__(self, setting=None, parent=None):
        super(WSetting, self).__init__(parent)

        # /* var class */
        self.MAIN_UI = {}
        self.CHSET_UI = {}
        self.setting = setting or SETTING_FUZZ
        # /* window setting */
        self.setWindowFlag(Qt.Tool)
        self.setStyleSheet(Css['Frame']+"*{background:rgb(26,45,61);}")

        # /* ui */
        self.MainGrid = QGridLayout()

        self.setLayout(self.MainGrid)
        self.show()
        self.setUISetting()

    def setUISetting(self):
        self.modeUi(main=0, no_del=False)
        self.modeUi(main=1, no_del=False)
        for i, sett in enumerate(self.setting.items()):
            k, v = sett
            if isinstance(v, dict):
                v = ", ".join([i.__str__() for i in v.values()])
            self.MAIN_UI[f'{k}{i}'] = QLabel_(k.__str__(), Css['info-lbl'])
            if isinstance(v, bool):
                color = "*{color:rgb(182,215,168);}" if v else "*{color:rgb(195,128,124);}"
                self.MAIN_UI[f'{i}{k}'] = QButton(v.__str__(), Css['button'] + color)
            else:
                self.MAIN_UI[f'{i}{k}'] = QButton("change", Css['button'])
            self.MAIN_UI[f'{i}{k}'].setFont(QFont("consolas", 10, QFont.ExtraBold))
            self.MAIN_UI[f'{i}{k}'].clicked.connect(self.updateSetting)
            self.MAIN_UI[f'{i}{k}'].setWhatsThis(dumps(sett))
            self.MainGrid.addWidget(self.MAIN_UI[f'{k}{i}'], i, 0)
            self.MainGrid.addWidget(self.MAIN_UI[f'{i}{k}'], i, 1)

    def updateSetting(self):
        source_clicked = self.sender()
        k, v = loads(source_clicked.whatsThis())
        if isinstance(v, bool):
            self.setting[k] = not v
            # /* update */
            self.setUISetting()
            return

        self.changeSetting(k, v)

    def changeSetting(self, k, v):
        to_int = 1 if k in ["threads", "length", "length_redirect"] else 0
        to_dict = 1 if k in ['headers', "cookies"] else 0
        self.modeUi(main=1)
        self.CHSET_UI['title'] = QLabel_(f"set value for {k}", Css['info-lbl'])
        self.CHSET_UI['title'].setFont(QFont("consolas", 12, QFont.Bold))
        self.CHSET_UI['lechange'] = QLineEdit()
        self.CHSET_UI['lechange'].setMinimumHeight(40)
        self.CHSET_UI['lechange'].setAlignment(Qt.AlignCenter)
        self.CHSET_UI['lechange'].setStyleSheet(Css['info-lbl'])
        self.CHSET_UI['lechange'].setPlaceholderText("enter new value:")
        self.CHSET_UI['lechange'].setText(v.__str__())
        self.CHSET_UI['lechange'].installEventFilter(self)
        self.CHSET_UI['breturn'] = QButton("back", Css['button'])
        self.CHSET_UI['breturn'].clicked.connect(lambda: self.back(k, to_int, to_dict))
        self.MainGrid.addWidget(self.CHSET_UI['title'], 0, 0, Qt.AlignTop)
        self.MainGrid.addWidget(self.CHSET_UI['lechange'], 1, 0, Qt.AlignTop)
        self.MainGrid.addWidget(self.CHSET_UI['breturn'], 2, 0, Qt.AlignBottom)

    def back(self, key, to_int, to_dict):
        self.saveChange(key, to_int, to_dict)

    def saveChange(self, key, to_int, to_dict):
        if to_int:
            value = int(self.CHSET_UI['lechange'].text())
        elif to_dict:
            value = loads(self.CHSET_UI['lechange'].text().replace("'", "\""))
        else:
            value = self.CHSET_UI['lechange'].text()

        self.setting[key] = value
        self.setUISetting()

    def modeUi(self, main=1, no_del=True, hide=True):
        items = self.MAIN_UI if main else self.CHSET_UI
        if no_del:
            [item.setHidden(hide) for item in items.values()]
        else:
            try:
                [item.deleteLater() for item in items.values()]
            except RuntimeError:
                # /* object deleted */
                return
            items.clear()

    def closeEvent(self, a0: QCloseEvent) -> None:
        a0.accept()


import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = WSetting()
    ex.show()

    sys.exit(app.exec_())
