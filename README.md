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
- 폭탄: 마우스 오른쪽 버튼. B는 클릭하면 바로, S는 0.5초 꾹 눌러야 발동한다 (B부터 쓰고, B가 없으면 S). 꾹 누르는 동안 비행기 둘레의 고리가 차오르고, 중간에 떼면 취소된다
- 스페이스바: 일시정지 / 계속. 일시정지 화면의 "Go Home" 버튼을 클릭하면 타이틀(홈) 화면으로 나간다 (그때까지의 점수는 최고 점수에 반영).
- 보너스 라운드(상점): 1~3 키 또는 카드 클릭으로 물건을 고르면 구매 확인 화면이 나오고(Buy 또는 Enter: 구매 / Back 또는 Esc: 상점으로), Change(C)로 물건을 바꾸고, Continue(Enter)로 게임에 복귀
- 게임 오버 후 R: 다시 시작. 게임 오버 화면의 "Go Home" 버튼(`GAMEOVER_HOME`)을 누르면 난이도 화면부터 다시 시작한다 (점수는 이미 기록돼 있다)
- 숨겨진 기능: 전투기 소개 화면에서 "Fighter N"의 이름을 N번 누르면(1번 전투기는 1번, 2번은 2번, 3번은 3번) 이름 옆에 무지개 폭탄 아이콘이 생기고, 그 전투기로 S(무지개 폭탄) 1개를 들고 시작한다 (Back을 누르면 꺼진다).
- 이름 화면 (가장 먼저): 게임을 켜면 제목과 큰 비행기만 있고, 그 아래에 "Player's name", 이름을 입력하는 칸(클릭하면 입력할 수 있다. 한글도 입력되고 최대 12글자, Enter로 확인), 맨 아래에 "Play In Guest Mode" 버튼(이름 없이 "Guest"로 시작)이 있다. 이 화면은 게임을 켤 때 한 번만 나온다 (난이도 화면의 Back으로 돌아올 수는 있다).
- 첫 화면: 게임을 켜면 제목 아래에 큰 일반 비행기(1번 전투기), 난이도 버튼 Easy / Normal / Hard, 깜빡이는 "Press To Start" 바(테두리 없이 어두운 바탕만), "My best Score" 칸이 나온다 (바와 칸은 버튼 줄과 같은 길이). 왼쪽 위의 "← Back" 버튼(또는 Esc)을 누르면 이름 화면으로 돌아간다. 버튼을 누르거나 ← → 키로 난이도를 고르고(기본은 Normal), 그 밖의 아무 키나 클릭(최고 점수 칸 제외)하면 전투기 고르기 화면으로 간다. 최고 점수는 난이도마다 따로 저장된다. "My best Score" 칸을 누르면 바로 모드별 최고 기록 화면(Best Records)이 열린다 (모드 줄을 누르면 그 모드의 1~10위 순위표 "Top 10"이 열린다: 순위, 이름, 점수, 전투기, 레벨, 시간, 날짜). 기록 화면에는 모드마다 1위가 나온다: 모드별 점수, 기록을 세운 플레이어 이름(길면 …로 줄임), 전투기 종류(Normal/Tanker/Attack), 레벨, 플레이 시간, 날짜 (기록이 없으면 "-"). 첫 화면 왼쪽 위에 지금 플레이어 이름이 작게 보인다. 아무 키나 Back으로 닫는다. 일시정지 화면의 "Go Home"도 이 화면으로 온다.
- 조작법 화면(Tutorial): 난이도 화면 오른쪽 위의 "Tutorial" 버튼을 누르면 조작법을 3쪽으로 설명한다 (1. Move: 이동/발사/일시정지, 2. 아이템 P·R·B·S·C, 3. 알아두면 좋은 것: 상점, 빨강/초록/노랑 적). 그냥 "Press To Start"로 시작하면 조작법 없이 바로 전투기 고르기로 간다. Next(또는 Enter)로 넘기고, 오른쪽 위 "Skip →"을 누르면 설명을 건너뛰고 바로 전투기 고르기로 가며, 왼쪽 위 "← Back"(또는 Esc)은 이전 쪽/난이도 화면으로 돌아간다. 전투기 고르기 화면의 Back은 Tutorial을 보고 왔으면 조작법 마지막 쪽으로, 아니면 난이도 화면으로 돌아간다.
- 전투기 고르기 화면: 먼저 비행기 3종 중 하나를 고른다 (← → / A D / 1 2 3 키, 또는 비행기를 클릭; 고른 비행기는 노란 테두리로 표시된다. 각 전투기 아래에는 이름이 적힌다: 1번 Normal, 2번 Tanker, 3번 Attack (`SHIP_NAMES`)). 전투기 위에 마우스를 올리면 그 전투기가 1.2배(`HOVER_SCALE`)로 커지고, 아래에 공격/체력/스피드가 숫자 대신 채워진 정도를 보여주는 게이지로 나타난다. 그 밖의 아무 키나 빈 곳 클릭을 하면 능력치 소개 화면이 나온다(처음에는 전투기만 크게 보이고, 마우스 휠을 위로 굴리면 공격/체력/스피드 막대가 나타나며 아래로 굴리면 다시 사라진다. Back: 다시 고르기 / Select 또는 Enter: 시작). 3초 카운트다운 뒤 게임이 시작된다 (`TITLE_COUNTDOWN`). 아래의 "My best Score" 칸에 최고 점수가 표시된다. 3,2,1 카운트다운이 시작되면 게임 이름, 최고 점수 칸, 옆의 다른 비행기는 바로 사라지고, 카운트다운이 진행되는 동안 비행기가 게임 시작 위치로 내려와 작아지며 상단 표시(점수/체력/코인/폭탄)가 서서히 나타나 게임 시작 화면과 같아진다 (게임 오버 또는 창을 닫을 때 갱신, `best_score.txt`에 저장되며 git에는 올리지 않는다). 게임 이름은 `GAME_TITLE`.

게임 안 글씨(Score, Level, Missiles, 상점 등)는 모두 영어다.

창은 게임 화면(800x600)을 2배(`WINDOW_SCALE`)로 확대해서 보여준다. 화면 높이가 모자라면 자동으로 줄어든다.

## 총알 판정

내 총알은 적 전투기의 그림(날개 포함)과 같은 크기의 직사각형에 닿으면 맞는다 (`bullet_hits`). 적과 부딪히는 판정(원)은 따로이다.

## 폭발 효과

- 내 총알이 적 전투기를 맞히면 맞힌 자리에 작은 폭발이 터지고, 적이 쓰러지면 전투기가 폭발 그림(`assets/explosion.png`, 픽셀 아트 폭발이 커지며 사라진다)과 파편으로 터진다. 폭탄(B/S)의 폭발은 반투명하게 그려져서 S처럼 큰 폭발에서도 뒤가 보인다.
- 내가 적의 총알(미사일)이나 폭탄에 맞거나 적과 부딪히면, 내 비행기 위에 작은 폭발이 터진다. 부딪힐 때는 부딪힌 자리에서도 폭발이 터진다 (둘 다 피해를 입는 규칙은 그대로).
- 체력이 0이 되면 내 전투기가 크게 폭발한 뒤 GAME OVER가 나온다.
- 폭발은 보기만 하는 효과라 피해나 판정에는 영향이 없다 (`add_fx`, `explode_enemy`, `draw_fx`).

## 점수

- 적 1마리를 무찌를 때마다 얻는 점수는 난이도마다 다르다 (총알, 부딪힘, 폭탄 모두 같다. `MODES`의 `kill_score`): **Easy 15점, Normal 10점, Hard 10점**.
- 노란 적은 모든 난이도에서 다른 적의 **1.5배**(`YELLOW_SCORE_MULT`)이다: Easy 22.5점(소수 그대로 표시), Normal·Hard 15점.
- **R 보너스**: 체력이 꽉 찬 상태로 R을 3개(`R_BONUS_COUNT`) 먹을 때마다 보너스 **+100점**(`R_BONUS_POINTS`)을 받는다. 모든 난이도 공통이다. 화면에 "R Bonus +100!"이 잠깐 나온다. 체력이 모자란 채로 먹은 R은 세지 않는다.
- **P 보너스**: 미사일이 최대(5개)인 상태로 P를 3개(`P_BONUS_COUNT`) 먹을 때마다 보너스 **+100점**(`P_BONUS_POINTS`)을 받는다. 모든 난이도 공통이고 "P Bonus +100!"이 잠깐 나온다. 미사일이 최대여도 P가 떨어진다.
- 레벨, 한 번에 나오는 적 수, 적 총알 수의 증가는 점수에 묶여 있다. 단, R·P 보너스 점수는 점수에만 더해지고 이 난이도 증가에는 반영되지 않는다 (`bonus_total`).
- **게스트 모드**(이름 화면의 "Play In Guest Mode")로 한 판은 기록에 영향을 주지 않는다: 최고 점수/순위표(파일, 브라우저 저장소, 공용 순위표)에 남지 않는다. 이름을 입력하고 시작해야 기록된다 (이름을 "Guest"라고 쓰는 건 게스트 모드가 아니라 그 이름으로 기록된다).
- **순위 기록**: 게임 한 판이 끝날 때(게임 오버, 홈으로 나가기, 창 닫기 중 먼저 오는 한 번) 그 점수가 그 모드의 10위 안에 들면 순위표에 이름과 함께 올라간다 (같은 판이 두 번 올라가지 않는다). 점수가 0이거나 10위 밖이면 기록하지 않는다.
- **기록할 때의 점수**: 점수가 xxxx.5처럼 .5로 끝나면 기록(기록 화면, 최고 점수 칸, 순위표)에는 0.5를 뺀 점수로 적는다 (예: 37.5 → 37). 화면에 보이는 점수는 그대로다.

## 난이도

우리가 처음부터 만들어 온 규칙이 **Normal**이다. 나머지는 아래 값만 다르다 (`MODES`).

| 항목 | Easy | Normal | Hard |
|---|---|---|---|
| 적이 나오는 간격 | ×1.4 (느림) | ×1.0 | ×0.75 (빠름) |
| 동시에 나오는 적 | 5 | 7 | 9 |
| 적 이동 속도 | ×0.8 | ×1.0 | ×1.25 |
| 적 체력 | 그대로 | 그대로 | +1 |
| 적 총알 속도 | 3.2 | 4.0 | 5.0 |
| 적이 한 번에 쏘는 총알 상한 | 5 | 7 | 9 |
| P / R / B 드롭률 | ×1.5 | ×1.0 | ×0.7 |
| 적 1마리 점수 (노란 적 ×1.5) | 15 (22.5) | 10 (15) | 10 (15) |

코인과 S의 드롭률, 상점, 전투기 능력치는 모든 난이도에서 같다. 일시정지 화면에 지금 난이도가 표시된다.

## 플레이어

- 내 비행기는 타이틀에서 고른 `assets/player_1.png`~`player_3.png` 중 하나로 그려진다 (크기 `PLAYER_SPRITE_SIZE` = 72px, 타이틀 화면에서는 `TITLE_SPRITE_SIZE`). 3종은 능력치가 다르다 (`SHIP_STATS`, (공격, 체력, 스피드)): 1번 (3,3,3), 2번 (2,5,2), 3번 (5,2,5). 공격 = 연사 속도(발사 간격 `16 - 2*공격` 프레임), 체력 = 시작 체력, 스피드 = 이동 속도(`2 + 스피드` px/프레임). 시작 체력이 최대 하트이며, 늘리려면 상점의 Max Heart +1을 써야 한다. 충돌 범위는 이미지 크기와 무관하게 그대로.
- 미사일 2개로 시작 (`START_POWER`), 최대 5개 (`MAX_POWER`). 미사일 반경은 고정.
- 최대 하트는 전투기의 시작 체력으로 정해진다 (1번 3, 2번 5, 3번 2). 이 값은 R 아이템이 채워줄 수 있는 한계이고, 상점의 "Max Heart +1"로만 늘릴 수 있다 (절대 상한 `HP_CAP` = 8). 하트는 오른쪽 위에 최대 개수만큼 칸으로 보이고, 잃은 칸은 어둡게 표시된다. 적 총알은 내 비행기 그림 모양(날개, 꼬리 끝까지)에 겹치면 맞고, 총알이나 폭탄에 맞으면 체력이 1 깎이고 1초간 무적 (`INVULN_TIME`). 적 비행기와 부딪히면 나도 체력이 1 깎이고, 부딪힌 적도 함께 1 피해를 입는다 (적이 쓰러지면 총알로 잡은 것처럼 점수와 아이템). 무적인 동안(피격 직후, Shield)에는 부딪혀도 서로 피해가 없다. 무적인 동안에도 적 총알은 비행기를 통과하지 않고 닿으면 피해 없이 사라진다.

## 적

- 화면에 동시에 최대 7마리 (`MAX_ENEMIES`). 점수 100점마다 한 번에 나오는 적이 1마리씩 늘어난다 (`SPAWN_SCORE`).
- 점수 150점마다 레벨 상승: 적이 더 자주, 빠르고, 단단하게 나온다.
- 적은 모두 비행기 이미지로 그려진다 (`assets/red_enemy.png`, `green_enemy.png`, `yellow_enemy.png`, 크기 `ENEMY_SPRITE_SIZE`). 이미지가 없으면 색깔 원으로 대신 그려진다.
- 빨간 적: 내 위치를 향해 총알을 쏜다. 한 번에 쏘는 총알 수 = 내 미사일 개수. 내 미사일이 최대(5개)가 된 뒤로는 점수 100점마다 1발씩 늘어나며, 상한은 7발 (`ENEMY_MAX_COUNT`).
- 노란 적: 내 미사일이 최대(5개)가 되면 4초마다 등장(동시에 최대 2마리, `YELLOW_SPAWN_INTERVAL`, `YELLOW_BULLET_SPEED`, `YELLOW_BULLET_COUNT`, `YELLOW_BULLET_SPREAD`, `YELLOW_MAX`). 빠르고 체력이 높으며, 다른 적보다 빠른 총알(`YELLOW_BULLET_SPEED` = 9, 난이도의 총알 속도 배율이 곱해진다)을 한 번에 2발(`YELLOW_BULLET_COUNT`, 9도 간격 `YELLOW_BULLET_SPREAD`) 쏜다. 화면 적 수 상한(7마리)에 포함되지 않는다.
- 초록 적(전체의 25%): 2초 뒤 터지는 폭탄을 던진다. 빨간 원이 폭발 범위.

## 아이템 (적 처치 시 드롭)

| 아이템 | 효과 | 드롭 |
|---|---|---|
| P (초록) | 미사일 +1 (최대 5). 최대일 때 먹으면 3개마다 보너스 +100점 | 빨간 적 2%, 초록 적 10% |
| R (분홍) | 체력 +1 (그 전투기의 현재 최대 하트까지) | 빨간 적 10%, 초록 적 5% (`HEAL_UNLOCK_PICKUPS`로 P 몇 개 뒤부터 나올지 조절, 0이면 처음부터) |
| B (총알 모양) | 폭탄 B +1 | 1% |
| $ (코인) | 100코인 | 빨간/초록 적 3%, 노란 적 35% (노란 적은 코인만 드롭) |
| S (무지개 폭탄) | 1회용 광범위 폭발 | 적 미사일이 5개일 때 약 6.7%(`S_DROP_RATE`), 6개 이상이면 약 0.67%(`S_LATE_DROP_RATE`). S를 안 가졌을 때만. B를 가지고 있어도 나오지만 확률이 1/4로 줄어든다(`S_WITH_B_FACTOR`, 약 1.7% / 0.17%) |

## 폭탄

- **B**: 처음에 3개. 오른쪽 클릭으로 내 주변(반경 150)의 적을 처치하고, 폭발에 닿은 적 총알만 제거 (화면 전체를 지우지 않는다).
- **S**: 오른쪽 마우스 버튼을 0.5초(`S_HOLD_FRAMES`) 꾹 누르고 있으면 광범위 폭발(반경 600 = B의 4배, 화면 대부분을 덮는다; `BLAST_RADIUS`), 범위 안 적과 모든 적 총알을 제거.
- 내가 터뜨린 폭탄(B/S)의 폭발에 닿은 총알도 사라진다: 폭발 범위 안에 있던 총알과, 폭발이 남아 있는 동안(약 0.5초) 범위 안으로 날아오는 총알만 사라지고 범위 밖의 총알은 그대로 날아간다. 폭발에 닿은 상대편(초록 적)의 폭탄도 터지지 못하고 사라진다. 폭탄에 닿은 적은 바로 사라지고, 총알로 잡은 것과 똑같이 점수를 주고 아이템도 떨어뜨린다. 오른쪽 클릭은 B부터 쓴다.
- 왼쪽 위에 B는 검은 폭탄 아이콘(`assets/item_bomb.png`) × 개수, S는 무지개 폭탄 아이콘(`assets/item_bomb_rainbow.png`)으로 표시된다. 같은 그림이 상점 카드와 최고 점수 칸의 S 표시에도 쓰인다.

- 아이템 자석: 내 주변 `MAGNET_RADIUS`(60px) 안에 들어온 아이템은 모양 그대로, 가만히 있다가 점점 빨라지며(`MAGNET_ACCEL`, 상한 `MAGNET_MAX_SPEED`) 자석에 붙듯 끌려온다. **한 번 끌리기 시작한 아이템은 내가 멀리 도망가도 계속 따라와서 결국 붙는다** (끌리는 속도 상한 14가 내 최고 이동 속도 9보다 빨라서 놓치지 않는다). 범위 밖의 아이템은 천천히 떨어진다.

## 보너스 라운드 (상점 화면 제목: "Star Market")

**구매 확인 화면**: 상점에서 물건을 고르면 바로 사지 않고 새 화면이 나온다. 맨 위에 "Buy (물건 이름)?", 그 아래 큰 물건 그림, 그 아래 물건의 특징 설명(영어, `ITEM_DESC`), 가격과 가진 코인, 맨 아래에 **Back**(상점으로)과 **Buy**(구매) 버튼이 있다. 코인이 모자라거나 이미 최대라 못 사면 화면에 남아서 이유가 나온다. 사면 상점으로 돌아가 "(이름) purchased!"가 보이고, 하트를 사면 "Hearts 4/4"처럼 현재/최대 하트도 같이 나온다. 상점 화면 위쪽(코인 옆)과 하트 관련 확인 화면에도 현재 하트(현재/최대)가 표시된다.

상점 카드의 하트(Max Heart +1, Full Heal), 보호막(Shield 10s), 티켓(Change Ticket)은 그림(`assets/item_heart.png`, `item_shield.png`, `item_change.png`)으로 표시된다. Change Ticket 그림은 왼쪽 위 개수 표시와 전투기 소개 화면의 숨겨진 기능 표시에도 쓰인다.

- 실제 플레이 시간 45초마다 열리고(`BONUS_INTERVAL`) 게임이 멈춘다. 열리기 전 1초(`FADE_FRAMES`) 동안 모든 적과 적 총알이 계속 움직이면서 스르륵 사라지고(이때는 공격도 충돌도 없다), 상점이 닫히면 다음 라운드는 처음처럼 위에서부터 적이 나타난다.
- 코인은 오른쪽 위에 표시되며 라운드가 지나도 쌓인다. 같은 물건을 여러 번 살 수 있다.
- 상점에는 매번 물건 3개(`SHOP_SLOTS`)만 나온다. 아래 9종 중에서 가중치에 따른 확률로 뽑히고(`SHOP_POOL`), 이미 최대라서 살 수 없는 물건은 먼저 제외된다. 상점 아래의 "Change" 버튼(또는 C 키)을 누르면 Change Ticket 1개를 써서 물건 3개를 새로 뽑는다 (가진 Change Ticket 개수는 왼쪽 위에도 표시된다). 

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

`GAME_TITLE`, `MODES`, `YELLOW_SCORE_MULT`, `R_BONUS_COUNT`, `R_BONUS_POINTS`, `P_BONUS_COUNT`, `P_BONUS_POINTS`, `SPLASH_SPRITE_SIZE`, `ENEMY_SPRITE_SIZE`, `PLAYER_SPRITE_SIZE`, `TITLE_SPRITE_SIZE`, `FADE_FRAMES`, `TITLE_COUNTDOWN`, `WINDOW_SCALE`, `MAX_ENEMIES`, `YELLOW_SPAWN_INTERVAL`, `YELLOW_MAX`, `SPAWN_SCORE`, `GREEN_RATE`, `START_POWER`, `MAX_POWER`, `HP_CAP`, `SHIP_STATS`, `INVULN_TIME`, `BULLET_RADIUS`,
`ENEMY_MAX_COUNT`, `ENEMY_SCALE_SCORE`, `BOMB_FUSE`, `BOMB_RADIUS`,
`RED_DROP_RATES`, `GREEN_DROP_RATES`, `HEAL_UNLOCK_PICKUPS`, `B_START`, `B_DROP_RATE`, `B_RADIUS`,
`S_UNLOCK_COUNT`, `S_DROP_RATE`, `S_HOLD_FRAMES`, `S_LATE_DROP_RATE`, `S_WITH_B_FACTOR`, `BLAST_RADIUS`,
`MAGNET_RADIUS`, `MAGNET_ACCEL`, `MAGNET_MAX_SPEED`, `COIN_DROP_RATE`, `YELLOW_COIN_DROP_RATE`, `COIN_VALUE`, `BONUS_INTERVAL`, `HOVER_SCALE`, `SHOP_TITLE`, `SHOP_POOL`, `SHOP_SLOTS`, `SHIELD_TIME`, `MAX_SPEED`, `MIN_FIRE_DELAY`

## 아이디어 목록

- 보스, 방어막 같은 새 아이템
- 효과음 / 배경음악, 이미지 스프라이트
- 최고 점수 저장
- 상점 물건 늘리기, 보너스 라운드를 코인 줍기 스테이지로 확장

## 웹 버전 (브라우저에서 하기)

- 주소: https://lhk3832.github.io/astroid/ (GitHub Pages가 `docs/` 폴더를 보여준다. 저장소 Settings → Pages에서 Branch `main`, 폴더 `/docs`로 한 번 켜야 한다)
- 만들기: `python build_web.py` (pygbag이 필요하다: `pip install pygbag`). `shooter.py`와 `assets/`를 pygbag으로 빌드해서 `docs/`에 넣는다. 게임을 고친 뒤에는 다시 빌드해서 `docs/`까지 커밋해야 웹에도 반영된다.
- 웹에서 다른 점: 글꼴이 pygame 기본 글꼴이고(한글 이름은 안 보일 수 있다), 최고 기록은 파일 대신 그 브라우저의 저장소(localStorage, 키 `astroid_best`)에 저장돼서 새로고침하거나 다시 들어와도 남는다 (같은 브라우저에서만 보이고, 사이트 데이터를 지우거나 시크릿 창이면 사라진다). 처음 열 때 게임 엔진을 내려받느라 몇 초 걸린다.

## 공용 순위표 (웹 버전, Supabase)

- 지금은 켜져 있다 (`SUPABASE_URL`, `SUPABASE_KEY`에 프로젝트 주소와 publishable 키가 들어 있다). 다시 켜거나 바꾸는 법: `shooter.py` 위쪽 `SUPABASE_URL`, `SUPABASE_KEY`(공개 키)에 값을 넣고 `python build_web.py` → `docs/` 푸시. 둘 중 하나라도 비어 있으면 꺼져 있고(웹도 그 브라우저에만 기록), 데스크톱은 늘 내 컴퓨터 파일(`best_score.txt`)에 저장한다.
- 켜져 있으면: 웹에서 한 판이 끝날 때(게임 오버/홈/창 닫기 중 먼저) 점수(1 이상)를 서버 표 `scores`에 보낸다 (이름은 10자까지, 안 쓰면 Guest). 순위 화면(Best Records / Top 10)과 최고 점수 칸("Top Score")은 모든 플레이어의 점수에서 모드별 1~10위를 서버에서 불러와 보여 준다 (시작할 때, 점수를 보낸 직후, 그 뒤 30초마다 새로 불러온다). 인터넷이 안 되면 점수를 보내지 못하지만 게임은 그대로 된다.
- 서버 표 만들기 (Supabase SQL Editor에서 한 번):

```sql
create table scores (
  id bigint generated always as identity primary key,
  mode text not null check (mode in ('Easy','Normal','Hard')),
  score int not null check (score between 1 and 1000000),
  player text not null check (char_length(player) between 1 and 10),
  ship text,
  level int,
  play_time int,
  created_at timestamptz default now()
);
alter table scores enable row level security;
create policy "anyone can read" on scores for select using (true);
create policy "anyone can add" on scores for insert with check (true);
grant usage on schema public to anon;
grant select, insert on public.scores to anon;
grant usage, select on all sequences in schema public to anon;
```

  (이미 이름 길이 20으로 만들었다면: `alter table scores drop constraint scores_player_check; alter table scores add constraint scores_player_check check (char_length(player) between 1 and 10);`)
- 한계: 코드가 브라우저에서 돌아서 마음먹으면 가짜 점수를 보낼 수 있다 (점수 1~1,000,000, 이름 10자로만 제한). 이름은 모두에게 공개된다. 점수를 고치거나 지우는 건 정책으로 막혀 있고, 지우려면 Supabase 화면에서 직접 한다.

### 가짜 점수와 이상한 이름 막기 (`supabase_hardening.sql`)

Supabase의 SQL Editor에서 `supabase_hardening.sql` 내용을 한 번 실행한다 (여러 번 해도 된다). 새로 들어오는 점수에만 적용되고 이미 있는 점수는 그대로다.

- 이름: 앞뒤 공백 없이 영문, 숫자, 한글, 공백, `_ . -`만 10자까지. 그 밖의 글자는 게임이 보내기 전에 뺀다 (비면 Guest). 욕설/링크 같은 금칙어가 들어 있으면 서버가 거절하고, 그러면 게임이 이름만 Guest로 바꿔 한 번 더 보낸다 (점수는 남는다).
- 점수 상한: 플레이 시간(1~86400초)이 있어야 하고 점수는 `플레이 시간 x 100 + 1000` 이하, 레벨은 1 이상 `점수 / 150 + 1` 이하, 전투기는 Normal/Tanker/Attack.
- 속도 제한: 같은 접속자는 1분에 5번까지 (접속 주소는 섞어서 줄인 값 `ip_hash`만 저장).
- 숨김: `scores` 표의 `hidden`을 true로 바꾸면 그 행이 순위표에서 빠진다 (Table Editor에서 직접).
- 공개 키로는 `ip_hash`/`hidden` 칸을 읽거나 쓸 수 없다.
- 한계: 시간과 점수를 맞춰서 보내는 사람은 막을 수 없다 (게임 규칙이 브라우저에서 돌기 때문). 눈에 띄는 가짜는 Table Editor에서 지우거나 숨긴다.

## 효과음

- 실제 소리에 가깝게 직접 합성했다 (잡음 + 낮은 쿵 소리 + 필터 + 잔향 + 살짝 찌그러뜨리기). 녹음 파일이 아니라서 진짜 녹음만큼 자연스럽진 않다.
- 소리 4종류를 각각 두 가지(a, b)로 만들어 `assets/sfx/`에 뒀다. 게임에는 `SFX_CHOICE`에서 고른 쪽이 나온다 (지금은 전부 a).
  - `shoot` 총알 쏠 때 (한 번 쏠 때 한 번): a = 소총 "탕!" (날카로운 총성 + 반동 + 짧은 울림), b = 권총 "탁" (더 작고 건조함)
  - `bomb` 폭탄 터질 때 (내 B/S, 초록 적의 폭탄): a = 가까운 폭발 (번쩍 갈라지는 소리 → 쾅 → 낮은 울림, 파편 소리, 약 2초), b = 멀리서 크게 터지는 폭발 (더 둔하고 낮은 울림이 길다, 약 3초)
  - `hit` 내가 적을 맞혔을 때 (한 프레임에 여러 번 맞아도 한 번): 묵직한 "쾅!" (딸깍 + 갈라짐 + 쾅 + 낮은 쿵 + 파편, 자주 나서 짧다). a = 또렷하고 단단한 쾅(금속 소리가 섞임), b = 더 무겁고 낮은 쿵
  - `hurt` 내가 맞았을 때 (적 총알/폭탄/부딪힘): hit보다 더 크고 긴 "쾅!". a = 충돌 + 철판이 찌그러지고 덜컹거리는 소리, b = 쾅 + 합선되어 전기가 튀는 지직 소리
- 들어 보기: `python sfx_preview.py` (소리마다 a, b를 차례로 들려준다). 고르는 곳은 `shooter.py` 위쪽 `SFX_CHOICE`, 크기는 `SFX_VOLUME`.
- 소리는 `python make_sfx.py`(또는 `python make_sfx.py hit`처럼 일부만)가 합성해서 `.ogg`로 만든다 (`pip install soundfile numpy` 필요). 웹 빌드(pygbag)가 WAV를 받지 않고 OGG만 받는다.
