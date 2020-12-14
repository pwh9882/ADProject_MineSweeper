from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QApplication, QLCDNumber, QMenuBar, QWidget, QMainWindow
from PyQt5.QtWidgets import QToolButton, QDialog, QDialogButtonBox, QFormLayout
from PyQt5.QtWidgets import QGridLayout, qApp, QDesktopWidget, QMessageBox, QSpinBox
from PyQt5.QtGui import QIcon,  QFont
from PyQt5.QtCore import QTimer

from MineDeployer import MineDeployer
from Tile import Tile


class MineSweeper(QWidget):
    "지뢰찾기 게임의 로직이 구현되어 있는 클래스"

    def __init__(self) -> None:
        super().__init__()
        self.StartFlag = False
        Tile.StartFlag = self.StartFlag
        self.initUI()

    def initUI(self) -> None:
        self.setDifficulty((9, 9, 10))
        MainLayout = QGridLayout()
        # 내용물
        InfoLayout = QGridLayout()
        # 정보: 남은 지뢰수, 리셋버튼, 찾은 지뢰수

        self.leftMineInfo = QLCDNumber()
        self.leftMineInfo.setDecMode()
        self.leftMineInfo.setDigitCount(3)
        self.leftMineInfo.setStyleSheet("""QLCDNumber {
                                            padding: 20px;
                                            min-height:0px;
                                            min-width: 0px;
                                            }""")
        self.leftMineInfo.setSegmentStyle(QLCDNumber.Flat)

        self.displayTime = QLCDNumber()
        self.displayTime.setDecMode()
        self.displayTime.setDigitCount(3)
        self.displayTime.setSegmentStyle(QLCDNumber.Flat)
        self.timePassed = 0
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.showTime)
        self.timer.start()

        self.newGameBtn = QToolButton()
        font = QFont("Segoe UI Emoji")
        font.setBold(True)
        font.setPointSize(18)
        self.newGameBtn.setFont(font)
        self.newGameBtn.setText("🙂")
        self.newGameBtn.clicked.connect(self.newGame)
        self.newGameBtn.setStyleSheet("min-height: 50%;")

        # 디버그용ShowAll, HindAll 버튼
        # self.debugBtn = QToolButton()
        # self.debugBtn.setText("showAll")
        # self.debugBtn.clicked.connect(self.showAllTiles)

        # self.hideAllBtn = QToolButton()
        # self.hideAllBtn.setText("hideAll")
        # self.hideAllBtn.clicked.connect(self.hideAllTiles)

        InfoLayout.addWidget(self.leftMineInfo, 0, 1)
        InfoLayout.addWidget(self.displayTime, 0, 6)
        InfoLayout.addWidget(self.newGameBtn, 0, 2)

        # InfoLayout.addWidget(self.debugBtn, 0, 4)
        # InfoLayout.addWidget(self.hideAllBtn, 0, 5)

        # 실제 지뢰찾기 게임 화면
        self.GameLayout = QGridLayout()
        self.GameLayout.setSpacing(0)
        self.tileList = []
        MineDeployer.tileInit(
            self.GameLayout, self.tileList, self.difficulty, self.tileClicked)
        self.newGame()

        MainLayout.addLayout(InfoLayout, 0, 1)
        MainLayout.addLayout(self.GameLayout, 1, 1)

        self.setLayout(MainLayout)

    def tileClicked(self) -> None:
        """Tile 버튼이 마우스로 클릭됬을 경우 마우스 버튼 종류에 따라 동작을 수행한다.
        \n마우스 왼쪽: 해당 타일을 밝힌다. 깃발 또는 물음표일 경우 밝히지 않는다.(클릭미스 방지용)
        \n  -게임이 진행 중이고 해당 타일이 폭탄 타일이었다면 게임오버
        \n마우스 오른쪽: 해당타일의 표시상태를 깃발 또는 물음표로 변경한다.
        \n마우스 왼쪽, 오른쪽 동시 클릭 또는 가운데 클릭: 주변 타일을 한번에 밝힌다.
        \n
        \n만약 체크한 타일이 마지막 폭탄을 찾은 것이라면 게임 승리"""
        btn = self.sender()
        if app.mouseButtons() == Qt.RightButton | Qt.LeftButton or app.mouseButtons() == Qt.MiddleButton:
            self.handleMiddleClick(btn)
            return
        elif app.mouseButtons() == Qt.LeftButton and (btn.text() != "🚩" and btn.text() != "❓"):
            self.revealTile(btn)
            if btn.state == "-1" and self.StartFlag == True:
                self.gameOver()
        elif app.mouseButtons() == Qt.RightButton:
            self.handleRightClick(btn)

        if self.leftMines_real == self.leftMines == 0:
            self.gameWon()

    def handleRightClick(self, tile: Tile) -> None:
        """입력된 타일의 표시 상태를 읽어와 규칙에 맞게 깃발, 물음표로 바꾼다.
        \n 밝혀지지 않은 타일에만 깃발 또는 물음표 표시를 할 수 있다."""
        show_text = str(tile.text())
        if show_text == "" and not tile.getDisplayState():
            show_text = "🚩"
            if tile.getState() == "-1":
                self.leftMines_real -= 1
            self.leftMines -= 1
            displayText = '{0:03d}'.format(self.leftMines)
            self.leftMineInfo.display(displayText)
        elif show_text == "🚩":
            show_text = "❓"
            if tile.getState() == "-1":
                self.leftMines_real += 1
            self.leftMines += 1
            displayText = '{0:03d}'.format(self.leftMines)
            self.leftMineInfo.display(displayText)
        elif show_text == "❓":
            show_text = ""
        tile.setText(show_text)

    def handleMiddleClick(self, tile: Tile) -> None:
        "입력된 타일의 주변 타일을 밝힌다."
        self.revealSurroundTiles(tile)

    def revealTile(self, tile: Tile) -> None:
        """게임을 시작하는 첫 클릭이면 시작로직으로 보낸다. 
        \n 게임이 시작됐다면 정상적으로 타일을 밝히고, 지뢰면 폭탄으로 표시로 밝혀준다.
        \n 만약 주변에 타일이 없는 0-타일이면 주변을 자동으로 밝혀준다."""
        if self.StartFlag == False:
            self.gameStart(tile)
        elif self.StartFlag == True:
            curr_tile_state = tile.getState()
            tile.setDisplayState(True)
            tile.setStyleSheet("background-color: white")
            if curr_tile_state == "-1":
                tile.setText("💣")
            elif curr_tile_state == "0":
                self.revealZeroTiles(tile)
            else:
                tile.setText(curr_tile_state)

    def revealZeroTiles(self, tile: Tile) -> None:
        """해당 타일이 0이면 주변의 밝혀지지 않고 깃발 또는 물음표 표시가 되지 않은 타일을 모두 밝힌다.
        주변에 0인 타일이 있으면 마찬가지로 그 타일의 주변을 모두 밝힌다.(revealTile에 의한 재귀)"""
        for surroundTile in tile.getSurroundTiles():
            if surroundTile.getDisplayState() == False and (surroundTile.text() != "🚩" and surroundTile.text() != "❓"):
                if surroundTile.state == "-1":
                    self.gameOver()
                else:
                    self.revealTile(surroundTile)

    def revealSurroundTiles(self, tile: Tile) -> None:
        """가운데 또는 양쪽 마우스 동시 클릭에 대응
        해당 타일의 state 만큼의 깃발이 주변에 있으면 주변의 모든 타일을 밝힌다.
        revealTile을 통해 밝힘 -> zerorevel도 자동 수행"""
        surroundPlags = 0
        for surroundTile in tile.getSurroundTiles():
            if surroundTile.text() == "🚩":
                surroundPlags += 1
        if surroundPlags == int(tile.state):
            self.revealZeroTiles(tile)

    def gameStart(self, tile: Tile) -> None:
        """처음으로 0인 타일을 열게 되면 start 변수 값이 False에서 Ture로 바뀐다.
        \n 만약 지뢰의 개수가 일정 이상이면 0인 타일에서 시작하는 것이 불가능 하므로 지뢰만 아니면 시작한다.
        \n 지뢰의 개수가 일정 이하여서 연 타일이 무조건 0일 때를 구해낼 수 있다면 시작타일이 0일때만 게임을 시작한다. 아니면 계속 newGame을 시도한다."""
        row, column, mine = self.difficulty
        state = tile.getState()
        if (state == "0") or ((row * column < 3*mine) and (state != "-1")):
            self.StartFlag = True
        else:
            self.newGame(tile)

        self.revealTile(tile)

    def newGame(self, tile=None) -> None:
        """모든 게임의 요소들을 초기화하고 게임을 새로 시작한다. 
        """
        self.StartFlag = False
        self.newGameBtn.setText("🙂")
        self.timerReset()
        self.newTiles = MineDeployer.tileCreateOptimal(self.difficulty, tile.getPos()) \
            if tile else MineDeployer.tileCreateOptimal(self.difficulty)
        MineDeployer.tileDeploy(self.tileList, self.newTiles)
        self.hideAllTiles()
        self.leftMines = self.difficulty[-1]
        self.leftMines_real = self.leftMines
        displayText = '{0:03d}'.format(self.leftMines)
        self.leftMineInfo.display(displayText)

    def gameOver(self) -> None:
        "모든 지뢰를 밝히고 끝낸다."
        self.newGameBtn.setText("😭")
        for row in self.tileList:
            for tile in row:
                tile.setEnabled(False)
                if tile.state == "-1":
                    self.revealTile(tile)
        self.StartFlag = False

    def gameWon(self) -> None:
        "모든 지뢰를 하트로 바꾸고 끝낸다."
        self.newGameBtn.setText("😎")
        for row in self.tileList:
            for tile in row:
                tile.setEnabled(False)
                if tile.state == "-1":
                    tile.setText("❤")
        self.StartFlag = False

    def setDifficulty(self, difficulty) -> None:
        "외부-윈도우 메뉴창에서 난이도 변경을 할 때 사용할 캡슐화 지향 seter 함수"
        self.difficulty = difficulty

    def clearLayout(self, layout) -> None:
        "새로운 난이도-다른 tile창 크기로 설정하기전에 이전 타일들을 제거한다."
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def showTime(self) -> None:
        "현재까지 지나간 시간을 출력한다. Qt.timer의 timeout에 콜백한다."
        if self.StartFlag == True:
            self.timePassed += 1
        displayText = "{0:03d}".format(self.timePassed)
        self.displayTime.display(displayText)

    def timerReset(self) -> None:
        "시간을 0초로 초기화한다."
        self.timePassed = 0
        displayText = "{0:03d}".format(self.timePassed)
        self.displayTime.display(displayText)

    def hideAllTiles(self) -> None:
        "새 게임을 시작하는 등의 상황에 모든 타일을 감춘다."
        for i in self.tileList:
            for j in i:
                j.setDisplayState(False)
                j.setText("")
                j.setStyleSheet("background-color: #222526")
        # 디버깅용 hideAll 버튼 상황에 필요한 코드
        # self.StartFlag = False
        # self.leftMines = self.difficulty[-1]
        # self.leftMines_real = self.difficulty[-1]
        # displayText = '{0:03d}'.format(self.leftMines)
        # self.leftMineInfo.display(displayText)
        # self.timerReset()

    # for debuging==========================

    # def showAllTiles(self):
    #     self.StartFlag = True
    #     for i in self.tileList:
    #         for j in i:
    #             j.setDisplayState(True)
    #             self.revealTile(j)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.modes[0].trigger()  # 난이도는 easy모드로 초기화

    def initUI(self) -> None:
        "윈도우 창을 만들고 game인 mineSweeper를 가운데 설정"
        self.setWindowTitle("MineSweeper by 20203070")
        self.mineSweeper = MineSweeper()
        self.setCentralWidget(self.mineSweeper)
        self.initMenuBar()
        self.resize(self.minimumSizeHint())
        self.center()
        self.show()

    def initMenuBar(self) -> None:
        "게임, 난이도, 도움말 메뉴 항목을 생성"
        menuBar = QMenuBar()

        gameMenu = menuBar.addMenu("Game")

        newGame = QAction("New Game", self)
        newGame.setShortcut('Ctrl+N')
        newGame.triggered.connect(self.mineSweeper.newGame)

        exit_action = QAction(QIcon('exit.png'), "&Exit", self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(qApp.quit)

        gameMenu.addAction(newGame)
        gameMenu.addAction(exit_action)

        difficultyMenu = menuBar.addMenu("Difficulty")
        # (9, 9, 10)  # (16, 16, 40) # (30, 16, 99)
        easyMode = QAction("Easy   (9x9, 10)", self)
        mediumMode = QAction("Medium (16x16, 40)", self)
        hardMode = QAction("Hard   (16x30, 99)", self)
        customMode = QAction("Custom", self)
        self.modes = [easyMode, mediumMode, hardMode, customMode]
        for mode in self.modes:
            mode.setCheckable(True)
            mode.triggered.connect(self.handleDifficultyButton)
        difficultyMenu.addActions(self.modes)

        helpMenu = menuBar.addMenu("Help")
        info = QAction("Info", self)
        info.triggered.connect(self.handleInfo)
        helpMenu.addAction(info)

        self.setMenuBar(menuBar)

    def handleDifficultyButton(self) -> None:
        "현재 난이도에 맞게 항목에 체크표시, 해당 난이도의 타일초기화"
        btn = self.sender()
        btn.setChecked(True)
        for other in self.modes:
            if other != btn:
                other.setChecked(False)

        if btn.text() == "Easy   (9x9, 10)":
            self.mineSweeper.setDifficulty((9, 9, 10))
        elif btn.text() == "Medium (16x16, 40)":
            self.mineSweeper.setDifficulty((16, 16, 40))
        elif btn.text() == "Hard   (16x30, 99)":
            self.mineSweeper.setDifficulty((16, 30, 99))
        elif btn.text() == self.modes[-1].text():
            self.handleCustomGame()

        self.mineSweeper.clearLayout(self.mineSweeper.GameLayout)
        self.mineSweeper.tileList = []
        MineDeployer.tileInit(
            self.mineSweeper.GameLayout, self.mineSweeper.tileList, self.mineSweeper.difficulty, self.mineSweeper.tileClicked)

        self.mineSweeper.newGame()
        # 창의 크기를 정확히 조절하기 위해 일정 이벤트 처리 시간을 지나게 하고 조절한다.
        for i in range(0, 10):
            QApplication.processEvents()
        self.resize(self.minimumSizeHint())
        self.setFixedSize(self.size())
        self.center()

    def handleInfo(self) -> None:
        "help메뉴의 info 창을 띄운다."
        dlg = QMessageBox(self)
        dlg.setWindowTitle("INFO")
        dlg.setText(
            "Made by Park-Woohyeok\nVer1.1\nhttps://github.com/kmu-cs-swp2-2018/class-02-pwh9882/tree/master/AD_project/MineSweeper")
        dlg.exec_()

    def center(self) -> None:
        # 창을 가운데로 움직이는 코드
        # https://gist.github.com/saleph/163d73e0933044d0e2c4
        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

    def handleCustomGame(self) -> None:
        # 유효한 난이도가 들어오면 난이도 설정을 한다.
        dlg = InputDialog(self)
        dlg.exec_()
        setting = dlg.getInputs()
        if setting[0]*setting[1] > setting[2]:
            self.mineSweeper.setDifficulty(setting)


class InputDialog(QDialog):
    "커스텀 난이도의 입력을 받기 위한 InputDialog"

    def __init__(self, window, parent=None) -> None:
        super().__init__(parent)

        self.customRowSize = QSpinBox(self)
        self.customColumnSize = QSpinBox(self)
        self.customMineNum = QSpinBox(self)
        self.customSetting = [self.customRowSize,
                              self.customColumnSize, self.customMineNum]
        for setting in self.customSetting:
            setting.setSingleStep(1)
            setting.setRange(9, 30)
        self.customMineNum.setRange(
            10, 999)
        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow("Size of Row(Max:30):", self.customRowSize)
        layout.addRow("Size of Column(Max:30):", self.customColumnSize)
        layout.addRow("Number of Mine(Max:999): ", self.customMineNum)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self) -> list:
        return [x.value() for x in self.customSetting]


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    calc = MainWindow()
    calc.show()
    app.exec_()
