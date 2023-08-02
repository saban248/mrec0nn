from PyQt5.QtGui import *
from PyQt5.Qt import *

from Api.analyzeAddr import domainExist
from AppUI.Massage import ShowMessage
from AppUI.style import *


class WWelcome(QScrollArea):

    def __init__(self, parent_setting, parent=None):
        super(WWelcome, self).__init__(parent)
        # /* var setting */
        self.UI = {}
        self.SETTING_UI = {}
        self.parent_setting = parent_setting
        # self.psu = psu
        # self.target = surl
        self.Style = Style()
        self.animate: AnimateText = None
        self.address = None
        # /* win setting */

        # /* UI */
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(0)
        self.MParent = QWidget()
        self.MParent.setStyleSheet(Style().style("Frame"))
        self.MainGrid = QGridLayout()
        self.MParent.setLayout(self.MainGrid)
        self.setWidget(self.MParent)
        self.UI['leurl'] = QLineEdit()
        self.UI['leurl'].setPlaceholderText("target http(s)://*  . . .")
        self.UI['leurl'].setFont(QFont("consolas", 10, QFont.Light))
        self.UI['leurl'].setStyleSheet(self.Style.style('url'))
        self.UI['leurl'].textChanged.connect(self.isValidUrl)
        self.UI['leurl'].installEventFilter(self)
        self.UI['leurl'].setMinimumSize(250, 40)

        self.MainGrid.addWidget(self.UI['leurl'], 1, 0, Qt.AlignCenter | Qt.AlignTop)
        self.Title()

    def Title(self):

        self.UI['title'] = QLabel()
        self.UI['title'].setStyleSheet("*{color:#D56549;}")
        self.UI['title'].setFont(QFont("consolas", 15, QFont.ExtraLight))
        self.MainGrid.addWidget(self.UI['title'], 0, 0, Qt.AlignCenter | Qt.AlignTop)
        self.animate = AnimateText("Welcome to Rec0n v1.0 \xa9 Avi #2022 ", 0.09, parent=self)
        self.animate.emitLetter.connect(self.UI['title'].setText)
        self.animate.emitFinish.connect(self.animateFinished)
        self.animate.start()

    def animateFinished(self, signal):
        pass  # signal

    def isValidUrl(self) -> None:
        if not self.UI['leurl'].text():
            self.UI['leurl'].setStyleSheet(self.Style.style('url')+"*{border:1px solid rgb(98,98,98)}")

    def setTarget(self):
        if self.parent_setting['fuzz_on']:
            ShowMessage("fuzzer running!, cancel this to change url", self)
            return
        url = self.UI['leurl'].text()
        result = domainExist(url)
        if not isinstance(result, bool) and result[0]:
            _ , port, ip, dns_name, protocol, indexes = result
            self.UI['leurl'].setStyleSheet(self.Style.style('url') + "*{border:2px solid green;}")
            # /* set on setting */
            if port == 80:
                self.parent_setting['url'] = f"{protocol}{dns_name}{indexes}"
            else:
                self.parent_setting['url'] = f'{protocol}{dns_name}:{port}{indexes}'
            self.parent_setting['ip'] = ip
            self.parent_setting['domain'] = dns_name
            self.parent_setting['port'] = port
            self.parent_setting['indexes'] = indexes

        else:
            self.UI['leurl'].setStyleSheet(self.Style.style('url')+"*{border:2px solid red;}")

    def closeAnimate(self):
        if self.animate:
            self.animate.stop()
            while not self.animate.isFinished():
                sleep(0.1)

    def eventFilter(self, Type: 'QObject', event: 'QEvent') -> bool:
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter - 1:
                if Type is self.UI['leurl']:
                    self.setTarget()

        return super(WWelcome, self).eventFilter(Type, event)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.closeAnimate()
        a0.accept()
        self.MParent.deleteLater()
