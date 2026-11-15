# My Shooter

Pygame 슈팅 게임. 단일 파일 `shooter.py`, 실행은 `python shooter.py`. 소통은 한국어로. 규칙과 수치는 README.md가 기준.

## 구조

- `Player`(hp, power, b_count, has_s, coins), `Enemy(level, green)` 클래스 + `main()` 루프 하나 (게임 오버 후 R이면 `main()` 재호출).
- 게임은 800x600 `screen` 캔버스에 그리고, 마지막에 `window`(확대 창)로 `smoothscale`해서 보여준다. 창 좌표 → 캔버스 좌표는 `/ scale` (상점 클릭에서 사용).
- 수치는 파일 위쪽 상수로 모여 있다 (README의 "조정용 상수" 목록 참고).
- 데이터 모양: 플레이어 총알 `[Vector2, 반경]`, 적 총알 `[Vector2, 속도]`, 적 폭탄 `bombs` `[현재위치, 목표위치, 남은 프레임]`, 폭발 `[위치, 남은 프레임, 반경, 전체 프레임]`, 아이템 `[Vector2, 종류]` (종류: P/R/B/S/C).
- 총알 제거는 `b[0].y = -999` 후 필터링하는 방식.
- 상태 플래그: `paused`(스페이스), `shop`(보너스 라운드), `game_over`. 업데이트 블록은 셋 다 아닐 때만 돈다.
- 적 총알 수 `enemy_count` = `player.power` + (최대가 된 시점의 점수 `max_power_score` 이후 `ENEMY_SCALE_SCORE`점마다 1), 상한 `ENEMY_MAX_COUNT`.
- 오른쪽 클릭: B가 있으면 B(적은 반경 `B_RADIUS` 안만), 없고 S가 있으면 S(`BLAST_RADIUS`). 둘 다 적 총알은 화면 전체를 지운다. 둘 다 범위 안 적을 바로 처치하고 총알로 잡을 때와 같이 `drop_items()`로 아이템을 떨어뜨린다 (드롭 규칙은 이 함수 한 곳에 있다).
- 변수 이름 주의: `bombs`는 초록 적이 던지는 폭탄 리스트이고, 플레이어의 B는 `player.b_count`.

- 시작 흐름: 파일 맨 아래에서 `title_screen()`을 한 번 호출한 뒤 `main()`을 반복한다 (게임 오버 후 R은 타이틀 없이 바로 `main()` 재시작). 일시정지 화면의 "Go to Home" 버튼(`PAUSE_HOME`)을 누르면 `main()`이 `"home"`을 반환하고, 맨 아래 루프가 `title_screen()`을 다시 부른다.

- 이미지: `assets/player_{1,2,3}.png`(내 비행기 3종, 위를 보는 그대로 사용. 모듈 변수 `selected_ship`이 고른 번호(0~2)이고 `title_screen()`이 바꾼다) 와 `assets/{red,green,yellow}_enemy.png` (위를 보는 그림이라 `load_sprite()`에서 180도 돌려 쓴다, 배경이 투명한 PNG). `ENEMY_SPRITES` 딕셔너리에 담기고, 파일이 없으면 색깔 원으로 대신 그린다.
- 보너스 라운드 진입: `play_frames`가 `BONUS_INTERVAL`(45초)이 되면 바로 `shop`이 아니라 `fade`(남은 프레임)가 켜진다. 그동안 적은 이동만 하고 `enemy_alpha`로 흐려지며, 끝나면 적/적 총알/폭탄/폭발을 비우고 `shop = True`. 상점이 닫히면 `spawn = 0`으로 다시 시작한다.
- 최고 점수: `best_score.txt`(`.gitignore`), `load_best()`/`save_best(score)`. 게임 오버와 창 닫기에서 저장한다.

- 비행기 능력치: `SHIP_STATS`(공격, 체력, 스피드)가 `Player.__init__`에서 `fire_delay`/`hp`/`speed`로 바뀌고, 시작 체력이 `max_hp`(최대 하트)가 된다. R/Full Heal은 `max_hp`까지만 채우고, 상점의 Max Heart +1만 `max_hp`를 늘린다(절대 상한 `HP_CAP`). `start_with_s`(S)와 `start_with_change`(Change Ticket)는 서로 배타적이라 하나가 켜져 있으면 다른 하나는 켜지지 않는다. 타이틀은 `phase`("choose" → "stats" → Select로 카운트다운)로 진행되고 전투기 소개 화면은 `draw_stats_screen(ship, now)`가 그린다 (이름, 큰 전투기, Back/Select만). 숨겨진 기능: `STATS_TITLE`(이름)을 `selected_ship + 1`번 누르면 `start_with_change = True`, 다음 `main()`이 `player.rerolls = 1`을 주고 끈다. `Change Ticket`은 `SHOP_POOL`의 가장 비싼 물건(kind "change")이고, 상점의 `SHOP_CHANGE` 버튼/C 키가 `rerolls`를 1 쓰고 `reroll_shop()`으로 `shop_offers`를 새로 뽑는다. 고르기 화면에서 전투기에 마우스를 올리면 `hover[i]`(0~1)가 부드럽게 올라가 1.2배로 커지고 `draw_hover_stats()`가 `draw_gauge()`로 공격/체력/스피드 게이지를 그린다.
- 상단 표시(HUD)는 `draw_hud(surf, score, level, player)` 하나로 그린다. 타이틀의 카운트다운에서도 같은 함수로 서서히 나타나게 한다.

- 상점: 보너스 라운드가 열릴 때 `roll_shop(player)`가 `SHOP_POOL`에서 3개를 가중치로 뽑아 `shop_offers`에 둔다. 구매 효과는 main의 `buy_idx` 처리 블록, 구매 가능 여부는 `shop_available()`, 카드 그림은 `draw_shop_icon()`. 새 물건은 `SHOP_POOL`, `UNAVAILABLE_MSG`, `shop_available`, 구매 블록, `draw_shop_icon` 다섯 곳을 같이 고친다.
- 게임 안 글씨는 영어로 통일했다 (주석은 한국어).

- 숨겨진 기능: 타이틀에서 `BEST_BOX`를 `SECRET_CLICKS`번 클릭하면 `start_with_s = True`, 다음 `main()`이 시작할 때 `player.has_s`를 주고 플래그를 끈다. 켜지면 칸 오른쪽에 무지개 폭탄 아이콘이 보인다.

## 확인 방법

화면 없이 스모크 테스트: `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 5 python shooter.py` (종료 코드 124면 오류 없이 돌아간 것). 단 이제 타이틀 화면에서 키 입력을 기다리므로 이 명령은 `main()`까지 가지 않는다. 게임 본편을 돌리려면 임시 사본에서 맨 아래 `title_screen()` 호출을 지우고 돌린다.
화면 확인이 필요하면 임시 사본에서 `pygame.image.save(screen, ...)`로 캡처하고, 확률·조건은 임시 사본에서 상수를 바꿔 검증한다 (원본은 건드리지 않는다).
실제 플레이 감각(난이도, 판정)은 사용자가 직접 확인해야 한다.
