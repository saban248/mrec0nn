from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from time import sleep

from Api.analyzeAddr import get_IpInfo, get_Shodan
from AppUI.Massage import ShowMessage
from AppUI.style import Style, QLabel_


class QThreadIO(QThread):

    # /* emit */
    emitOutput = pyqtSignal(dict, dict)
    emitStatus = pyqtSignal(int)

    def __init__(self, ip,  parent):
        super(QThreadIO, self).__init__(parent)
        # /* address of target */
        self.ip = ip

    # noinspection PyUnresolvedReferences
    def run(self) -> None:
        self.emitStatus.emit(1)
        shodan = get_Shodan(self.ip)
        ipinfo = get_IpInfo(self.ip)
        # /* verify data */
        if shodan and ipinfo:
            self.emitOutput.emit(shodan, ipinfo)

        # /* finito */
        self.emitStatus.emit(0)


class WInfo(QScrollArea):

    def __init__(self, parent_setting, parent=None):
        super(WInfo, self).__init__(parent)
        # /* var setting */
        self.UI = {}
        self.parent_setting = parent_setting
        self.json_ipinfo = {}
        self.json_shodan = {}
        self.address = parent_setting['ip']
        self.getStatus: ShowMessage = None
        self.request: QThreadIO = None
        # /* win setting */
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(0)
        self.MParent = QWidget()
        self.MParent.setStyleSheet(Style().style("Frame"))
        self.MainGrid = QGridLayout()
        self.MParent.setLayout(self.MainGrid)
        self.setWidget(self.MParent)
        # /* UI */

        # /* event : show api data */

    def getFinish(self, signal):
        if signal:
            self.getStatus = ShowMessage("processing..", dis_close=True, parent=self)
        else:
            self.getStatus.closeEvent(QCloseEvent())

    # noinspection PyUnresolvedReferences
    def RequestApi(self):

        if self.address != self.parent_setting['ip'] or not self.json_shodan:
            [item.deleteLater() for item in self.UI.values()]
            self.UI.clear()
            self.address = self.parent_setting['ip']
            self.request = QThreadIO(self.parent_setting['ip'], self)
            self.request.emitOutput.connect(self.setInfoApi)
            self.request.emitStatus.connect(self.getFinish)
            self.request.start()

    def setInfoApi(self, shodan: dict, ipinfo: dict):
        """
        *used-for:
            with api from webservers, show all data about ip
            set ui by loop, set labels and categories.
            if ip changed, data set on ui again,

        :return: None
        """
        # /* set ui */

        # /* data */
        self.json_ipinfo = ipinfo
        self.json_shodan = shodan
        print("DATA: OK")

        # /* ipinfo.io */
        self.UI['tit_ip'] = QLabel("info address channel")
        self.UI['tit_ip'].setStyleSheet(Style().style("title"))
        self.UI['tit_ip'].setFont(QFont("consolas", 12, QFont.Light))
        self.UI['tit_ip'].setAlignment(Qt.AlignCenter)
        self.UI['tit_ip'].setMinimumHeight(30)
        self.MainGrid.addWidget(self.UI['tit_ip'], 0, 0, 1, 5)
        for i, js in enumerate(self.json_ipinfo.items(), start=1):
            k, v = js
            # /* k */
            self.UI[k] = QLabel_(k.__str__(), Style().style("info-lbl"))
            # /* V */
            self.UI[f'{k}{i}'] = QLabel_(v.__str__(), Style().style("info-lbl") + "*{color:rgb(132,171,44);}", tb=1)
            self.MainGrid.addWidget(self.UI[k], i, 0)
            self.MainGrid.addWidget(self.UI[f'{k}{i}'], i, 1, 1, 4)

        # /* about webserver */
        self.UI['tit_web'] = QLabel("info web server")
        self.UI['tit_web'].setStyleSheet(Style().style("title"))
        self.UI['tit_web'].setFont(QFont("consolas", 12, QFont.Light))
        self.UI['tit_web'].setAlignment(Qt.AlignCenter)
        self.UI['tit_web'].setMinimumHeight(30)
        self.MainGrid.addWidget(self.UI['tit_web'], self.MainGrid.count(), 0, 1, 5)
        for i, js in enumerate(self.json_shodan.items(), start=self.MainGrid.count()):
            k, v = js
            if isinstance(v, list):
                v = ", ".join([i.__str__() for i in v])

            # /* K */
            if k == "vulns":
                style_critical = "*{color:rgb(192,55,45);}"
            else:
                style_critical = ""
            self.UI[f'{k}{i}'] = QLabel_(k.__str__(), Style().style("info-lbl")+style_critical)
            # /* V */
            self.UI[f'{k}{len(k)}'] = QLabel_(v.__str__(), Style().style('info-lbl') + "*{color:rgb(132,171,44);}", tb=1)
            self.MainGrid.addWidget(self.UI[f'{k}{i}'], i, 0)
            self.MainGrid.addWidget(self.UI[f'{k}{len(k)}'], i, 1, 1, 4)

    def showEvent(self, *args, **kwargs):
        self.RequestApi()

    def closeEvent(self, a0: QCloseEvent) -> None:
        while self.request.isRunning():
            sleep(0.1)
        a0.accept()
        self.deleteLater()
