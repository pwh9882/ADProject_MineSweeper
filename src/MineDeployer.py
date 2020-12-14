import random
from Tile import Tile


class MineDeployer():
    "지뢰를 배치하는 함수들을 모아둔 클래스. 객체를 만들지 않음"

    def tileCreateOptimal(difficulty, tilePos=(0, 0)) -> list:
        """행렬의 크기와 폭탄의 개수를 입력받아 랜덤하게 지뢰를 배치한 위치 리스트를 리턴한다.
        \n+Optiaml 로직 추가: tilePos를 입력받아 해당 타일을 제외한 리스트만을 리턴하도록 함."""
        row_size, column_size, num_mine = difficulty
        size = row_size * column_size
        all_list = list(range(size))
        avoidPos = tilePos[0]*column_size + tilePos[1]
        while True:
            samples = random.sample(all_list, k=num_mine)
            if avoidPos not in samples:
                break
        samplesPosition = [(x//column_size, x % column_size) for x in samples]
        newTiles = []
        for i in range(row_size):
            row = [0 for i in range(column_size)]
            newTiles.append(row)

        for x, y in samplesPosition:
            newTiles[x][y] = -1

        return newTiles

    def tileInit(tileLayout, tileList: list, difficulty, callback) -> None:
        """tile widget들을 생성해 tileList에 저장"""
        row, column = difficulty[0], difficulty[1]
        MineDeployer.tileList = tileList  # []
        Tile.tileList = tileList
        for i in range(row):
            curr_column = []
            for j in range(column):
                btn = Tile(callback)
                btn.setPos(i, j)
                curr_column.append(btn)
                tileLayout.addWidget(btn, i, j)
                btn.setText("")
            tileList.append(curr_column)

    def tileDeploy(tileList: list, newTiles) -> None:
        "지뢰 위치가 들어있는 newTiles를 입력받아 tileList에 배치하고, 각각의 타일의 state를 설정한다."
        MineDeployer.tileList = tileList

        for i in range(len(tileList)):
            for j in range(len(tileList[0])):
                MineDeployer.tileList[i][j].state = str(newTiles[i][j])

        # 지뢰를 모두 배치한 후에야 비로소 타일의 숫자를 정할 수 있음!
        for row in MineDeployer.tileList:
            for tile in row:
                tile.setEnabled(True)
                tile.setState()


if __name__ == "__main__":
    # 원하는 크기의 배열로 지뢰가 랜덤배치 되는지 확인
    for i in MineDeployer.tileCreateOptimal((3, 9, 26), (0, 1)):
        print(i)
