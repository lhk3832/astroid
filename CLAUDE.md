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
- 오른쪽 클릭: B가 있으면 B(반경 `B_RADIUS`), 없고 S가 있으면 S(`BLAST_RADIUS`). 둘 다 처치한 적은 아이템을 떨어뜨리지 않는다.
- 변수 이름 주의: `bombs`는 초록 적이 던지는 폭탄 리스트이고, 플레이어의 B는 `player.b_count`.

## 확인 방법

화면 없이 스모크 테스트: `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 5 python shooter.py` (종료 코드 124면 오류 없이 돌아간 것).
화면 확인이 필요하면 임시 사본에서 `pygame.image.save(screen, ...)`로 캡처하고, 확률·조건은 임시 사본에서 상수를 바꿔 검증한다 (원본은 건드리지 않는다).
실제 플레이 감각(난이도, 판정)은 사용자가 직접 확인해야 한다.
