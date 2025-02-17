from PyQt5.Qt import *
from PyQt5.QtWidgets import *

from AppUI.Massage import ShowMessage
from AppUI.style import Templates as Css, QButton, QLabel_
from Api.mapper import ThreadMapper



class _Widget:
    m_grid:QGridLayout      = None
    start:QPushButton       = None
    url:QLabel              = None
    tree:QTreeWidget        = None
    

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
        _Widget.m_grid = QGridLayout()
        self.MParent.setLayout(_Widget.m_grid)
        self.setWidget(self.MParent)
        self.paths:dict[str, list] = dict()
        self.setTitles()
        self.setTree()

    def setTitles(self):
        _Widget.start = QButton("Mapp", Css['button'] + "*{color:rgb(205,205,103);}")
        _Widget.start.setMinimumWidth(100)
        _Widget.start.clicked.connect(self.OpenMapper)
        _Widget.start.setFont(QFont("consolas", 11, QFont.Bold))
        _Widget.m_grid.addWidget(_Widget.start, 0, 0, Qt.AlignTop | Qt.AlignLeft)
        _Widget.url = QLabel_(self.parent_setting['url'], Css['look-lbl'], tb=1)
        _Widget.url.installEventFilter(self)

        _Widget.m_grid.addWidget(_Widget.url, 0, 1, Qt.AlignTop)

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
            _Widget.start.setText("Create Tree...")
            _Widget.start.setStyleSheet(Css['button']+"*{color:rgb(163,65,65);}")
            
        else:
            _Widget.start.setText("Mapp")
            _Widget.start.setStyleSheet(Css['button'])

    def setTree(self) -> None:
        _Widget.tree = QTreeWidget()
        # /* set column */
        _Widget.tree.setColumnCount(1)
        _Widget.tree.setHeaderLabel(f"All Indexes on {self.parent_setting['url']}")
        _Widget.tree.setStyleSheet(Css['Frame'])
        _Widget.m_grid.addWidget(_Widget.tree, 1, 0, 1, 2)

    # /* None
    def SetItemsTree(self, indexes: list[str]):
        _Widget.tree.clear()
        items:dict[str, QTreeWidgetItem] = dict()
        self.test(indexes, None, 0, items)

    def test(self, indexes:list[str], root:QTreeWidgetItem = None, index:int = 0, it:dict[str, QTreeWidgetItem]= None):

        if index>indexes.__len__()-1:return
        p = indexes[index]
        if p.startswith("/"):
            p = p[1::]
        parent = self.get_parent(p)
        children = self.get_children(p)
        root = it.get(parent)

        for _i, path in enumerate(p.split("/")):
            if path == "" or path == " " or path == "'" or not path:
                continue

            if not root:
                root = QTreeWidgetItem([path])
                _Widget.tree.addTopLevelItem(root)
                it[parent] = root
                continue

            child = QTreeWidgetItem([path])
            it[children] = child

            root.addChild(child)
            root = child


        self.test(indexes, None, index+1, it)

    def get_parent(self, path:str):
        return path.split("/")[0]

    def get_children(self, path:str):
        return "".join(path.split("/")[1::])

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

            return _Widget.tree.findItems(name, Qt.MatchFlag.MatchContains)[0]
        except IndexError:
            return False

    # /* TODO: */
    def changeUrl(self, mode):
        url = _Widget.url.text()
        _Widget.url.deleteLater()
        if mode:
            _Widget.url = QLineEdit()
            _Widget.url.setText(url)
            _Widget.url.setStyleSheet(Css['button'])
            _Widget.url.setAlignment(Qt.AlignCenter)
            _Widget.url.setMaximumWidth(self.width() // 2)
            _Widget.url.setMinimumHeight(25)
        else:
            _Widget.url = QLabel_(url, Css['look-lbl'])

        _Widget.url.installEventFilter(self)
        _Widget.m_grid.addWidget(_Widget.url, 0, 1, Qt.AlignTop)

    def eventFilter(self, Type: QObject, Event: QEvent) -> bool:
        if Event.type() == QEvent.MouseButtonDblClick:
            if Type == _Widget.url:
                if type(Type) == QLabel:
                    self.changeUrl(1)
                elif type(Type) == QLineEdit:
                    self.changeUrl(0)

        elif Event.type() == QEvent.KeyPress:
            if Event.key() == Qt.Key_Enter - 1:
                if Type is _Widget.url and type(Type) == QLineEdit:
                    # /* TODO: . . . */
                    self.parent_setting['url'] = _Widget.url.text()
                    ShowMessage("url update!", self)
                    self.changeUrl(0)

        return super(WMapper, self).eventFilter(Type, Event)

    def showEvent(self, a0: QShowEvent):
        _Widget.url.setText(self.parent_setting['url'])

    def closeEvent(self, a0: QCloseEvent):
        self.deleteLater()
        a0.accept()
