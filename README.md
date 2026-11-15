# My Shooter

Pygame으로 만든 세로 스크롤 슈팅 게임.

## 실행

```
pip install -r requirements.txt
python shooter.py
```

## 조작

- 이동: 방향키 / WASD
- 발사: 마우스 왼쪽 버튼 (누르고 있으면 연사)
- 폭탄: 마우스 오른쪽 버튼 (B부터 쓰고, B가 없으면 S)
- 스페이스바: 일시정지 / 계속. 일시정지 화면의 "Go to Home" 버튼을 클릭하면 타이틀(홈) 화면으로 나간다 (그때까지의 점수는 최고 점수에 반영).
- 보너스 라운드(상점): 1~3 키 또는 카드 클릭으로 구매, Enter 또는 "계속하기" 버튼으로 복귀
- 게임 오버 후 R: 다시 시작
- 숨겨진 기능 2: 전투기 소개 화면에서 "Fighter N"의 이름을 N번 누르면(1번 전투기는 1번, 2번은 2번, 3번은 3번) 이름 옆에 Change 아이콘이 생기고, 그 전투기로 Change Ticket 1개를 들고 시작한다 (Back을 누르면 꺼진다). 숨겨진 기능 1(S)과 2(Change Ticket)는 함께 받을 수 없다: 하나를 켜면 다른 하나는 켜지지 않는다.
- 숨겨진 기능 1: 타이틀 화면에서 "My best Score" 칸을 7번 클릭하면(`SECRET_CLICKS`) 칸 오른쪽에 무지개 폭탄 표시가 생기고, 다음 게임을 S 1개를 들고 시작한다 (한 번만 적용).
- 타이틀 화면: 먼저 비행기 3종 중 하나를 고른다 (← → / A D / 1 2 3 키, 또는 비행기를 클릭; 고른 비행기는 노란 테두리로 표시되고 아래 번호 대신 "ATK 3  HP 3  SPD 3" 같은 능력치 요약이 나온다. 안내 문구는 "Choose your Fighter"). 전투기 위에 마우스를 올리면 그 전투기가 1.2배(`HOVER_SCALE`)로 커지고, 아래에 공격/체력/스피드가 숫자 대신 채워진 정도를 보여주는 게이지로 나타난다. 그 밖의 아무 키나 빈 곳 클릭을 하면 능력치 소개 화면이 나온다(처음에는 전투기만 크게 보이고, 마우스 휠을 위로 굴리면 공격/체력/스피드 막대가 나타나며 아래로 굴리면 다시 사라진다. Back: 다시 고르기 / Select 또는 Enter: 시작). 3초 카운트다운 뒤 게임이 시작된다 (`TITLE_COUNTDOWN`). 아래의 "My best Score" 칸에 최고 점수가 표시된다. 3,2,1 카운트다운이 시작되면 게임 이름, 최고 점수 칸, 옆의 다른 비행기는 바로 사라지고, 카운트다운이 진행되는 동안 비행기가 게임 시작 위치로 내려와 작아지며 상단 표시(점수/체력/코인/폭탄)가 서서히 나타나 게임 시작 화면과 같아진다 (게임 오버 또는 창을 닫을 때 갱신, `best_score.txt`에 저장되며 git에는 올리지 않는다). 게임 이름은 `GAME_TITLE`.

게임 안 글씨(Score, Level, Missiles, 상점 등)는 모두 영어다.

창은 게임 화면(800x600)을 2배(`WINDOW_SCALE`)로 확대해서 보여준다. 화면 높이가 모자라면 자동으로 줄어든다.

## 플레이어

- 내 비행기는 타이틀에서 고른 `assets/player_1.png`~`player_3.png` 중 하나로 그려진다 (크기 `PLAYER_SPRITE_SIZE`, 타이틀 화면에서는 `TITLE_SPRITE_SIZE`). 3종은 능력치가 다르다 (`SHIP_STATS`, (공격, 체력, 스피드)): 1번 (3,3,3), 2번 (2,5,2), 3번 (5,2,5). 공격 = 연사 속도(발사 간격 `16 - 2*공격` 프레임), 체력 = 시작 체력, 스피드 = 이동 속도(`2 + 스피드` px/프레임). 시작 체력이 최대 하트이며, 늘리려면 상점의 Max Heart +1을 써야 한다. 충돌 범위는 이미지 크기와 무관하게 그대로.
- 미사일 2개로 시작 (`START_POWER`), 최대 5개 (`MAX_POWER`). 미사일 반경은 고정.
- 최대 하트는 전투기의 시작 체력으로 정해진다 (1번 3, 2번 5, 3번 2). 이 값은 R 아이템이 채워줄 수 있는 한계이고, 상점의 "Max Heart +1"로만 늘릴 수 있다 (절대 상한 `HP_CAP` = 8). 하트는 오른쪽 위에 최대 개수만큼 칸으로 보이고, 잃은 칸은 어둡게 표시된다. 적 총알이나 폭탄에 맞으면 체력이 1 깎이고 5초간 무적 (`INVULN_TIME`). 적 비행기에 닿기만 하는 것은 피해가 없다.

## 적

- 화면에 동시에 최대 7마리 (`MAX_ENEMIES`). 점수 100점마다 한 번에 나오는 적이 1마리씩 늘어난다 (`SPAWN_SCORE`).
- 점수 150점마다 레벨 상승: 적이 더 자주, 빠르고, 단단하게 나온다.
- 적은 모두 비행기 이미지로 그려진다 (`assets/red_enemy.png`, `green_enemy.png`, `yellow_enemy.png`, 크기 `ENEMY_SPRITE_SIZE`). 이미지가 없으면 색깔 원으로 대신 그려진다.
- 빨간 적: 내 위치를 향해 총알을 쏜다. 한 번에 쏘는 총알 수 = 내 미사일 개수. 내 미사일이 최대(5개)가 된 뒤로는 점수 100점마다 1발씩 늘어나며, 상한은 7발 (`ENEMY_MAX_COUNT`).
- 노란 적: 내 미사일이 최대(5개)가 되면 4초마다 등장(동시에 최대 2마리, `YELLOW_SPAWN_INTERVAL`, `YELLOW_MAX`). 빠르고 체력이 높으며 빠른 총알을 1발씩 쏜다. 화면 적 수 상한(7마리)에 포함되지 않는다.
- 초록 적(전체의 25%): 2초 뒤 터지는 폭탄을 던진다. 빨간 원이 폭발 범위.

## 아이템 (적 처치 시 드롭)

| 아이템 | 효과 | 드롭 |
|---|---|---|
| P (초록) | 미사일 +1 (최대 5) | 빨간 적 2%, 초록 적 10% |
| R (분홍) | 체력 +1 (그 전투기의 현재 최대 하트까지) | 빨간 적 10%, 초록 적 5% (`HEAL_UNLOCK_PICKUPS`로 P 몇 개 뒤부터 나올지 조절, 0이면 처음부터) |
| B (총알 모양) | 폭탄 B +1 | 1% |
| $ (코인) | 100코인 | 빨간/초록 적 2%, 노란 적 30% (노란 적은 코인만 드롭) |
| S (무지개 폭탄) | 1회용 광범위 폭발 | 적 미사일이 5개일 때 20%(`S_DROP_RATE`), 6개 이상이면 1%(`S_LATE_DROP_RATE`). S를 안 가졌을 때만. B를 가지고 있어도 나오지만 확률이 1/4로 줄어든다(`S_WITH_B_FACTOR`) |

## 폭탄

- **B**: 처음에 3개. 오른쪽 클릭으로 내 주변(반경 150)의 적을 처치하고, 화면의 적 총알을 모두 제거.
- **S**: 오른쪽 클릭으로 광범위 폭발(반경 300), 범위 안 적과 모든 적 총알을 제거.
- 폭탄(B/S)에 닿은 적은 바로 사라지고, 총알로 잡은 것과 똑같이 점수를 주고 아이템도 떨어뜨린다. 오른쪽 클릭은 B부터 쓴다.
- 왼쪽 위에 B는 폭탄 아이콘 × 개수, S는 무지개색 폭탄 아이콘으로 표시된다.

- 아이템 자석: 내 주변 `MAGNET_RADIUS`(60px) 안에 들어온 아이템은 점점 작아지고 꼬리를 끌며 빨려 들어온다 (`MAGNET_SPEED`).

## 보너스 라운드 (상점 화면 제목: "Star Market")

- 실제 플레이 시간 45초마다 열리고(`BONUS_INTERVAL`) 게임이 멈춘다. 열리기 전 1초(`FADE_FRAMES`) 동안 모든 적과 적 총알이 계속 움직이면서 스르륵 사라지고(이때는 공격도 충돌도 없다), 상점이 닫히면 다음 라운드는 처음처럼 위에서부터 적이 나타난다.
- 코인은 오른쪽 위에 표시되며 라운드가 지나도 쌓인다. 같은 물건을 여러 번 살 수 있다.
- 상점에는 매번 물건 3개(`SHOP_SLOTS`)만 나온다. 아래 9종 중에서 가중치에 따른 확률로 뽑히고(`SHOP_POOL`), 이미 최대라서 살 수 없는 물건은 먼저 제외된다. 상점 아래의 "Change" 버튼(또는 C 키)을 누르면 Change Ticket 1개를 써서 물건 3개를 새로 뽑는다 (가진 Change Ticket 개수는 왼쪽 위에도 표시된다). 1~3 키 또는 카드 클릭으로 구매, Enter 또는 버튼으로 계속.

| 물건 | 가격 | 가중치 | 효과 |
|---|---|---|---|
| Max Heart +1 | 100 | 30 | 최대 하트 +1 (체력도 +1), `HP_CAP`까지 |
| Bomb B +1 | 200 | 25 | 폭탄 B +1 |
| Missile +1 | 300 | 18 | 미사일 +1 (최대 5) |
| Shield 10s | 200 | 14 | 10초 무적 |
| Speed +1 | 200 | 12 | 이동 속도 +1 (최대 `MAX_SPEED`) |
| Rapid Fire | 300 | 12 | 발사 간격 -1프레임 (최소 `MIN_FIRE_DELAY`) |
| Full Heal | 400 | 6 | 체력을 현재 최대 하트까지 채움 |
| Rainbow Bomb | 500 | 4 | S 폭탄 1개 (이미 가졌으면 제외) |
| Change Ticket | 600 | 4 | Change Ticket 1개 (가장 비싸다) |

## 조정용 상수 (shooter.py 상단)

`GAME_TITLE`, `ENEMY_SPRITE_SIZE`, `PLAYER_SPRITE_SIZE`, `TITLE_SPRITE_SIZE`, `FADE_FRAMES`, `TITLE_COUNTDOWN`, `WINDOW_SCALE`, `MAX_ENEMIES`, `YELLOW_SPAWN_INTERVAL`, `YELLOW_MAX`, `SPAWN_SCORE`, `GREEN_RATE`, `START_POWER`, `MAX_POWER`, `HP_CAP`, `SHIP_STATS`, `INVULN_TIME`, `BULLET_RADIUS`,
`ENEMY_MAX_COUNT`, `ENEMY_SCALE_SCORE`, `BOMB_FUSE`, `BOMB_RADIUS`,
`RED_DROP_RATES`, `GREEN_DROP_RATES`, `HEAL_UNLOCK_PICKUPS`, `B_START`, `B_DROP_RATE`, `B_RADIUS`,
`S_UNLOCK_COUNT`, `S_DROP_RATE`, `S_LATE_DROP_RATE`, `S_WITH_B_FACTOR`, `BLAST_RADIUS`,
`MAGNET_RADIUS`, `MAGNET_SPEED`, `COIN_DROP_RATE`, `YELLOW_COIN_DROP_RATE`, `COIN_VALUE`, `BONUS_INTERVAL`, `HOVER_SCALE`, `SHOP_TITLE`, `SHOP_POOL`, `SHOP_SLOTS`, `SHIELD_TIME`, `MAX_SPEED`, `MIN_FIRE_DELAY`

## 아이디어 목록

- 보스, 방어막 같은 새 아이템
- 효과음 / 배경음악, 이미지 스프라이트
- 최고 점수 저장
- 상점 물건 늘리기, 보너스 라운드를 코인 줍기 스테이지로 확장
