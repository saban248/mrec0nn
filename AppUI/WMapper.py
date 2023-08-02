from PyQt5.Qt import *
from PyQt5.QtWidgets import *

from AppUI.Massage import ShowMessage
from AppUI.style import Templates as Css, QButton, QLabel_
from Api.mapper import ThreadMapper


class WMapper(QScrollArea):

    def __init__(self, parent_setting, parent=None):
        super(WMapper, self).__init__(parent)

        self.parent_setting = parent_setting
        self.ui_t = {}
        self.ui_i = {}
        self.mapper_api: ThreadMapper = None
        self.ParentIndexes = []
        # /* UI */
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(0)
        self.MParent = QWidget()
        self.MParent.setStyleSheet(Css["Frame"])
        self.MainGrid = QGridLayout()
        self.MParent.setLayout(self.MainGrid)
        self.setWidget(self.MParent)

        self.setTitles()
        self.setTree()

    def setTitles(self):
        self.ui_t['bstart'] = QButton("Mapp", Css['button'] + "*{color:rgb(205,205,103);}")
        self.ui_t['bstart'].setMinimumWidth(100)
        self.ui_t['bstart'].clicked.connect(self.OpenMapper)
        self.ui_t['bstart'].setFont(QFont("consolas", 11, QFont.Bold))
        self.MainGrid.addWidget(self.ui_t['bstart'], 0, 0, Qt.AlignTop | Qt.AlignLeft)
        self.ui_t['lurl'] = QLabel_(self.parent_setting['url'], Css['look-lbl'], tb=1)
        self.ui_t['lurl'].installEventFilter(self)

        self.MainGrid.addWidget(self.ui_t['lurl'], 0, 1, Qt.AlignTop)

    def OpenMapper(self):
        self.setUiMode(1)
        if not self.mapper_api:
            self.mapper_api = ThreadMapper(self.parent_setting, parent=self)
            self.mapper_api.emitError.connect(self.getError)
            self.mapper_api.emitFinish.connect(self.getFinish)
            self.mapper_api.emitOutput.connect(self.SetItemsTree)
            self.mapper_api.start()

    def getFinish(self, finish):
        self.setUiMode(0)
        self.mapper_api = None

    def getError(self, error):

        ShowMessage(error.__str__(), self)

    def setUiMode(self, mode):
        if mode:
            self.ui_t['bstart'].setText("Create Tree...")
            self.ui_t['bstart'].setStyleSheet(Css['button']+"*{color:rgb(163,65,65);}")
        else:
            self.ui_t['bstart'].setText("Mapp")
            self.ui_t['bstart'].setStyleSheet(Css['button'])

    def setTree(self) -> None:
        self.ui_i['tree'] = QTreeWidget()
        # /* set column */
        self.ui_i['tree'].setColumnCount(1)
        self.ui_i['tree'].setHeaderLabel(f"All Indexes on {self.parent_setting['url']}")
        self.ui_i['tree'].setStyleSheet(Css['Frame'])
        self.MainGrid.addWidget(self.ui_i['tree'], 1, 0, 1, 2)

    # /* None
    def SetItemsTree(self, indexes: list[str]):
        self.ui_i['tree'].clear()
        for ind in indexes:
            li, parent_name = self.setParentTreeName(ind)
            # /* set parent per Tree */
            if li:
                li.pop(0)
            if self.getItemParent(parent_name):
                root = self.getItemParent(parent_name)
            else:
                root = QTreeWidgetItem([parent_name])
                self.ui_i['tree'].addTopLevelItem(root)

            self.TreeParent(li, root)

    def TreeParent(self, indexes: list, parent: QTreeWidgetItem = None):

        for ind in indexes:
            child = QTreeWidgetItem([ind.__str__()])
            parent.addChild(child)
            indexes.pop(0)
            self.TreeParent(indexes, child)

    def setParentTreeName(self, path: str) -> tuple[list, str]:
        indexes = path.split("/")
        for i in indexes:
            if i != "." and i:
                indexes.pop(0)
                return indexes, i
        return [], "<empty>"

    def getItemParent(self, name):
        try:

            return self.ui_i['tree'].findItems(name, Qt.MatchFlag.MatchContains)[0]
        except IndexError:
            return False

    # /* TODO: */
    def changeUrl(self, mode):
        url = self.ui_t['lurl'].text()
        self.ui_t['lurl'].deleteLater()
        if mode:
            self.ui_t['lurl'] = QLineEdit()
            self.ui_t['lurl'].setText(url)
            self.ui_t['lurl'].setStyleSheet(Css['button'])
            self.ui_t['lurl'].setAlignment(Qt.AlignCenter)
            self.ui_t['lurl'].setMaximumWidth(self.width() // 2)
            self.ui_t['lurl'].setMinimumHeight(25)
        else:
            self.ui_t['lurl'] = QLabel_(url, Css['look-lbl'])

        self.ui_t['lurl'].installEventFilter(self)
        self.MainGrid.addWidget(self.ui_t['lurl'], 0, 1, Qt.AlignTop)

    def eventFilter(self, Type: QObject, Event: QEvent) -> bool:
        if Event.type() == QEvent.MouseButtonDblClick:
            if Type == self.ui_t['lurl']:
                if type(Type) == QLabel:
                    self.changeUrl(1)
                elif type(Type) == QLineEdit:
                    self.changeUrl(0)

        elif Event.type() == QEvent.KeyPress:
            if Event.key() == Qt.Key_Enter - 1:
                if Type is self.ui_t['lurl'] and type(Type) == QLineEdit:
                    # /* TODO: . . . */
                    self.parent_setting['url'] = self.ui_t['lurl'].text()
                    ShowMessage("url update!", self)
                    self.changeUrl(0)

        return super(WMapper, self).eventFilter(Type, Event)

    def showEvent(self, a0: QShowEvent):
        self.ui_t['lurl'].setText(self.parent_setting['url'])

    def closeEvent(self, a0: QCloseEvent):
        self.deleteLater()
        a0.accept()
