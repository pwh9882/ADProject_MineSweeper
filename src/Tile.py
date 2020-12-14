from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QFont


class Tile(QToolButton):
    "지뢰찾기의 한 타일이 될 QToolButton을 상속한 타일 클래스"

    def __init__(self, callback) -> None:
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.clicked.connect(callback)
        font = QFont("Segoe UI Emoji")
        font.setBold(True)
        font.setPointSize(18)
        self.setFont(font)

    def sizeHint(self) -> None:
        size = super(Tile, self).sizeHint()
        size.setHeight(40)
        size.setWidth(40)
        return size

    def mousePressEvent(self, ev) -> None:
        self.clicked.emit()

    def setPos(self, x: int, y: int) -> None:
        self.posX = x
        self.posY = y

    def getPos(self) -> tuple:
        return self.posX, self.posY

    def setTileList(tileList: list):
        "tileList 정적으로 사용되므로 클래스 정적변수로 설정"
        Tile.tileList = tileList

    def getTileList() -> list:
        return Tile.tileList

    def setState(self) -> None:
        "주변 타일을 읽어와 지뢰 갯수만큼 해당 타일의 상태값 지정"
        x, y = self.getPos()
        tileNum = 0
        self.loadSurroundTiles()
        if self.getState() != "-1":
            for tile in self.surroundTiles:
                if tile.state == "-1":
                    tileNum += 1
            self.state = str(tileNum)

    def getState(self) -> str:
        return self.state

    def setDisplayState(self, displayState: bool) -> None:
        "해당 타일의 밝혀짐 여부를 설정"
        self.displayState = displayState

    def getDisplayState(self) -> bool:
        return self.displayState

    def loadSurroundTiles(self) -> None:
        # 입력 타일의 주변 타일들을 포함시킨 리스트를 저장
        x, y = self.getPos()
        self.surroundTiles = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not ((i == 0 and j == 0) or (x+i < 0 or y+j < 0) or (x+i >= len(Tile.tileList) or (y+j) >= len(Tile.tileList[0]))):
                    btn = Tile.tileList[x+i][y+j]
                    self.surroundTiles.append(btn)

    def getSurroundTiles(self) -> list:
        return self.surroundTiles
