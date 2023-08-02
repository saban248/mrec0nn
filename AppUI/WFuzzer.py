from PyQt5.QtGui import *
from PyQt5.Qt import *
from pyperclip import copy

from Api.analyzeAddr import HTTP_ERROR, MECHANISM_ERROR
from Api.fuzzer import FuzzerUI
from Api.functions_api import *
from AppUI.Massage import ShowMessage
from AppUI.WSetting import SETTING_FUZZ, WSetting
from AppUI.style import *
from AppUI.style import Templates as Css


class WFuzzer(QScrollArea):

    def __init__(self, parent_setting, parent=None):
        super(WFuzzer, self).__init__(parent)

        # /* var and setting */
        self.parent_setting = parent_setting
        self.UI = {}
        self.fileFuzz: str = "choose file.."  # Default
        self.Fuzzer: FuzzerUI = None
        self.SETTING_FUZZ = SETTING_FUZZ
        self.SETTING_FUZZ_BACK = SETTING_FUZZ
        self.founds = 0
        self.indexes = {}
        self.settingUI: WSetting = None
        # /* window setting */
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(0)
        self.MParent = QWidget()
        self.MParent.setStyleSheet(Style().style("Frame"))
        self.MainGrid = QGridLayout()
        self.MParent.setLayout(self.MainGrid)
        self.setWidget(self.MParent)

        self.show()
        self.setUIFuzz()

    def setTitles(self):

        # /* url */
        if not self.Fuzzer:
            self.UI['lip'] = QLineEdit(f'{self.parent_setting["url"]}')
            self.UI['lip'].setStyleSheet(Css['info-lbl'] + "*{color:rgb(217,234,211);}")
            self.UI['lip'].installEventFilter(self)
            self.UI['lip'].setAlignment(Qt.AlignCenter)
            self.UI['lip'].setFont(QFont("consolas", 10, QFont.Bold))
            self.MainGrid.addWidget(self.UI['lip'], 1, 0, 1, 4)
            # /* file */
            self.UI['bfile'] = QButton(fixWidthPath(os.path.basename(self.fileFuzz)), Css['button'])
            self.UI['bfile'].clicked.connect(self.OpenFileFuzz)
            self.MainGrid.addWidget(self.UI['bfile'], 0, 2, Qt.AlignTop)
            # /* start */
            self.UI['bstart'] = QButton("Start fuzzz", Css['button'])
            self.UI['bstart'].setFont(QFont("consolas", 11, QFont.Bold))
            self.UI['bstart'].clicked.connect(self.OpenFuzzer)
            self.MainGrid.addWidget(self.UI['bstart'], 0, 0, Qt.AlignTop)
            # /* setting */
            self.UI['bsetting'] = QButton("setting", Css['button'] + "*{color:rgb(161,208,53);}")
            self.UI['bsetting'].setIcon(self.style().standardIcon(QStyle.SP_CustomBase))
            self.UI['bsetting'].clicked.connect(self.OpenSetting)
            self.MainGrid.addWidget(self.UI['bsetting'], 0, 3, Qt.AlignTop)

    def OpenSetting(self):
        self.settingUI = WSetting(self.SETTING_FUZZ, self)

    def OpenFileFuzz(self):
        path = QFileDialog.getOpenFileName(self, filter="just txt files (*.txt)")
        if path[0]:
            self.fileFuzz = path[0]
            self.sender().setText(fixWidthPath(os.path.basename(self.fileFuzz)))
            self.sender().setStyleSheet(Css['button'] + "*{color:rgb(148,165,141);}")

    def OpenFuzzer(self):
        file, errors = OpenBruteFile(self.fileFuzz)
        if isinstance(file, list):
            # /* set on setting */
            self.SETTING_FUZZ_BACK = self.SETTING_FUZZ
            self.parent_setting['fuzz_on'] = 1
            self.setUIModeFuzz(1)

            self.Fuzzer = FuzzerUI(self.parent_setting, self.SETTING_FUZZ, file, self)
            self.Fuzzer.emitStatus.connect(self.getStatus)
            self.Fuzzer.emitFinish.connect(self.getFinish)
            self.Fuzzer.emitSetting.connect(self.settingOnFuzz)
            self.Fuzzer.emitErrors.connect(self.getErrors)
            self.Fuzzer.start()
            return
        ShowMessage(errors, self)

    def setUIFuzz(self):
        self.delUIFuzz()
        self.UI['bstat'] = QLabel_("complete: A/N indexes scanned: A/N", Css['info-lbl'])
        self.UI['bstat'].setFont(QFont("consolas", 11, QFont.Bold))
        self.MainGrid.addWidget(self.UI['bstat'], 2, 0, 1, 4)
        self.UI['lresult'] = QTreeWidget()
        self.UI['lresult'].setMinimumHeight(300)
        self.UI['lresult'].setAnimated(True)
        self.UI['lresult'].setColumnCount(4)
        self.UI['lresult'].setContextMenuPolicy(Qt.CustomContextMenu)
        self.UI['lresult'].customContextMenuRequested.connect(self.OpenMenu)
        self.UI['lresult'].setColumnWidth(300, 300)
        self.UI['lresult'].setHeaderLabels(['index', 'status code', 'type', 'size'])
        self.UI['lresult'].header().setFont(QFont("Rockwell", 8, QFont.Bold))
        self.MainGrid.addWidget(self.UI['lresult'], 3, 0, 1, 4)
        self.UI['bsavefuzz'] = QButton("Save Fuzz", Css['button'])
        self.UI['bsavefuzz'].clicked.connect(self.SaveFuzz)
        self.MainGrid.addWidget(self.UI['bsavefuzz'], 4, 3)

    def OpenMenu(self, Event: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet(Css['Frame'])
        self.setMenuOptions(menu, Event)
        menu.exec_(self.UI['lresult'].mapToGlobal(Event))

    def setMenuOptions(self, menu: QMenu, Event: QPoint):
        try:
            item = self.UI['lresult'].itemAt(Event)
        except RuntimeError:
            return

        if not item:
            return
        url = self.parent_setting['url'] + item.text(0)
        menu.addSeparator()
        # /* copy full path* /
        ACopy = menu.addMenu("Copy")
        ACFull = ACopy.addAction("&Copy url")
        ACName = ACopy.addAction("&Copy index")
        ACFull.triggered.connect(lambda: copy(f"{url}"))
        ACName.triggered.connect(lambda: copy(f"{item.text(0)}"))
        menu.addSeparator()
        # /* open url */
        AUrl = menu.addAction("Open On explorer")
        AUrl.triggered.connect(lambda: OpenUrl(url))

    def delUIFuzz(self):
        try:
            self.UI['bstat']
        except KeyError:
            return

        self.UI['bstat'].deleteLater()
        self.UI['lresult'].clear()

    def setUIModeFuzz(self, mode):

        if mode:
            self.UI['bstart'].setText("Initializing...")
            self.UI['bstart'].setStyleSheet(Css['button'] + "*{color:rgb(194,40,40);}")
            self.UI['bstart'].disconnect()
            self.UI['bstart'].clicked.connect(self.CancelFuzzer)
            self.UI['bfile'].setDisabled(True)
            self.UI['lresult'].clear()
        else:
            self.UI['bstart'].setText("Start fuzzz")
            self.UI['bstart'].disconnect()
            self.UI['bstart'].setStyleSheet(Css['button'])
            self.UI['bstart'].clicked.connect(self.OpenFuzzer)

        self.UI['bfile'].setDisabled(bool(mode))

    def getStatus(self, total: int, size: int, n_found: int, indexes: list[dict]):
        res = (100 * total) / (size or 100)
        self.UI['bstat'].setText(f"complete: {res:.2f}% scanned: {total:,} indexes found: {n_found:,} pages")
        if self.founds != indexes.__len__():
            self.setIndexesResult(indexes)
            self.founds = indexes.__len__()

    def getFinish(self, signal, about, pages_found):
        self.SETTING_FUZZ = self.SETTING_FUZZ_BACK
        if about != "ok":
            ShowMessage(about, self)
        self.setUIModeFuzz(0)
        self.Fuzzer = None
        self.parent_setting['fuzz_on'] = 0
        self.indexes = pages_found

    def setIndexesResult(self, l_urls):
        self.UI['lresult'].clear()
        # /* set item */
        for index in l_urls:
            # /* url */
            url = QTreeWidgetItem([f'/{index["ind"]}', index['stat'].__str__(), index['typ'], index['size'].__str__()])
            url.setForeground(0, QColor("#BCBCBC"))
            url.setForeground(1, QColor(("#BB5151" if index['stat'] == 200 else "#89A744")))
            url.setForeground(3, QColor(index['size'] // 2 % 255, index['size'] % 255, 0))
            self.UI['lresult'].addTopLevelItem(url)

    def getErrors(self, err: dict, _key):
        if err['moved']:
            ShowMessage(HTTP_ERROR[0x1], self)
        elif err['waf']:
            ShowMessage(HTTP_ERROR[0x2], self)
        elif err['error']:
            ShowMessage(HTTP_ERROR[0x3], self)
        elif err['net_rest']:
            ShowMessage(HTTP_ERROR[0x4], self)
        elif err['captcha']:
            ShowMessage(HTTP_ERROR[0x5], self)

        MECHANISM_ERROR[_key] = 0

    def settingOnFuzz(self, sett: dict):
        # /* fuzzing started: update setting */
        self.UI['bstart'].setText("Cancel")
        # /* update setting */
        self.SETTING_FUZZ = self.SETTING_FUZZ | sett
        self.UI['lip'].setText(self.parent_setting['url'])

    def SaveFuzz(self):
        save_as = QFileDialog.getSaveFileName(self, "", self.parent_setting['domain'] + "-fuzz.txt")
        if save_as[0]:
            if self.indexes:
                SaveFileFuzz(save_as[0], self.indexes, 200)
            else:
                ShowMessage("fuzzing list is empty", self)

    def CancelFuzzer(self):
        self.sender().setText("kill brute-fource...")
        self.Fuzzer.Cancel()

    def showEvent(self, a0: QShowEvent) -> None:
        self.setTitles()

    def eventFilter(self, Type: QObject, Event: QEvent) -> bool:
        if Event.type() == QEvent.KeyPress:
            if Event.key() == Qt.Key_Enter - 1:
                if Type is self.UI['lip']:
                    self.parent_setting['url'] = self.UI['lip'].text()
                    ShowMessage("url Update!", self)

        return super(WFuzzer, self).eventFilter(Type, Event)

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.Fuzzer:
            self.Fuzzer.Cancel()
            while self.Fuzzer.isRunning():
                sleep(0.1)
        if self.settingUI:
            self.settingUI.closeEvent(QCloseEvent())

        a0.accept()
        self.deleteLater()


import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WFuzzer()
    ex.show()

    sys.exit(app.exec_())
