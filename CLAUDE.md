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
- 오른쪽 클릭: B가 있으면 B(적은 반경 `B_RADIUS` 안만), 없고 S가 있으면 S(`BLAST_RADIUS`). 둘 다 적 총알은 화면 전체를 지운다. 둘 다 처치한 적은 아이템을 떨어뜨리지 않는다.
- 변수 이름 주의: `bombs`는 초록 적이 던지는 폭탄 리스트이고, 플레이어의 B는 `player.b_count`.

- 시작 흐름: 파일 맨 아래에서 `title_screen()`을 한 번 호출한 뒤 `main()`을 반복한다 (게임 오버 후 R은 타이틀 없이 바로 `main()` 재시작). 일시정지 화면의 "Go to Home" 버튼(`PAUSE_HOME`)을 누르면 `main()`이 `"home"`을 반환하고, 맨 아래 루프가 `title_screen()`을 다시 부른다.

- 이미지: `assets/player_{1,2,3}.png`(내 비행기 3종, 위를 보는 그대로 사용. 모듈 변수 `selected_ship`이 고른 번호(0~2)이고 `title_screen()`이 바꾼다) 와 `assets/{red,green,yellow}_enemy.png` (위를 보는 그림이라 `load_sprite()`에서 180도 돌려 쓴다, 배경이 투명한 PNG). `ENEMY_SPRITES` 딕셔너리에 담기고, 파일이 없으면 색깔 원으로 대신 그린다.
- 보너스 라운드 진입: `play_frames`가 1분이 되면 바로 `shop`이 아니라 `fade`(남은 프레임)가 켜진다. 그동안 적은 이동만 하고 `enemy_alpha`로 흐려지며, 끝나면 적/적 총알/폭탄/폭발을 비우고 `shop = True`. 상점이 닫히면 `spawn = 0`으로 다시 시작한다.
- 최고 점수: `best_score.txt`(`.gitignore`), `load_best()`/`save_best(score)`. 게임 오버와 창 닫기에서 저장한다.

- 상단 표시(HUD)는 `draw_hud(surf, score, level, player)` 하나로 그린다. 타이틀의 카운트다운에서도 같은 함수로 서서히 나타나게 한다.

## 확인 방법

화면 없이 스모크 테스트: `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 5 python shooter.py` (종료 코드 124면 오류 없이 돌아간 것). 단 이제 타이틀 화면에서 키 입력을 기다리므로 이 명령은 `main()`까지 가지 않는다. 게임 본편을 돌리려면 임시 사본에서 맨 아래 `title_screen()` 호출을 지우고 돌린다.
화면 확인이 필요하면 임시 사본에서 `pygame.image.save(screen, ...)`로 캡처하고, 확률·조건은 임시 사본에서 상수를 바꿔 검증한다 (원본은 건드리지 않는다).
실제 플레이 감각(난이도, 판정)은 사용자가 직접 확인해야 한다.
