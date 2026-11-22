# My Shooter

Pygame 슈팅 게임. 단일 파일 `shooter.py`, 실행은 `python shooter.py`. 소통은 한국어로. 규칙과 수치는 README.md가 기준.

## 구조

- `Player`(hp, power, b_count, has_s, coins), `Enemy(level, green)` 클래스 + `main()` 루프 하나 (게임 오버 후 R이면 `main()` 재호출).
- 게임은 800x600 `screen` 캔버스에 그리고, 마지막에 `window`(확대 창)로 `smoothscale`해서 보여준다. 창 좌표 → 캔버스 좌표는 `/ scale` (상점 클릭에서 사용).
- 수치는 파일 위쪽 상수로 모여 있다 (README의 "조정용 상수" 목록 참고).
- 데이터 모양: 플레이어 총알 `[Vector2, 반경]`, 적 총알 `[Vector2, 속도]`, 적 폭탄 `bombs` `[현재위치, 목표위치, 남은 프레임]`, 폭발 `[위치, 남은 프레임, 반경, 전체 프레임]`, 아이템 `[Vector2, 종류, 속도, 끌리는 중인가]` (종류: P/R/B/S/C. 속도와 끌림 여부는 `move_item()`이 처음 움직일 때 붙인다; 한 번 끌리기 시작하면 거리와 상관없이 계속 따라온다).
- 총알 제거는 `b[0].y = -999` 후 필터링하는 방식.
- 상태 플래그: `paused`(스페이스), `shop`(보너스 라운드), `game_over`. 업데이트 블록은 셋 다 아닐 때만 돈다.
- 적 총알 수 `enemy_count` = `player.power` + (최대가 된 시점의 점수 `max_power_score` 이후 `ENEMY_SCALE_SCORE`점마다 1), 상한 `ENEMY_MAX_COUNT`.
- 오른쪽 버튼: B가 있으면 클릭 즉시 B(적은 반경 `B_RADIUS` 안만), 없고 S가 있으면 S(`BLAST_RADIUS`)인데 S는 `S_HOLD_FRAMES`(0.5초) 꾹 눌러야 한다 (`s_charging`/`s_charge`, 떼거나 멈추면 취소, 충전 고리는 비행기를 그린 뒤에 그린다). 둘 다 적 총알은 폭발 범위에 닿은 것만 지운다 (터뜨릴 때 화면 전체를 지우지 않고, 아래 `explosions` 5번째 값이 `True`인 폭발이 매 프레임 범위 안 총알을 지운다). 둘 다 범위 안 적을 바로 처치하고 총알로 잡을 때와 같이 `drop_items()`로 아이템을 떨어뜨린다 (드롭 규칙은 이 함수 한 곳에 있다).
- 변수 이름 주의: `bombs`는 초록 적이 던지는 폭탄 리스트이고, 플레이어의 B는 `player.b_count`.

- 점수: 적을 무찌르면 `score += kill_points(en)` (난이도의 `kill_score`: Easy 15, Normal·Hard 10, 노란 적은 모든 난이도에서 ×`YELLOW_SCORE_MULT`, 22.5처럼 소수 그대로이고 `fmt_score()`로 표시, 저장 점수는 `num()`으로 읽는다). 무찌르는 곳은 총알/부딪힘/폭탄 세 군데다. 레벨/적 수/적 총알 수 증가는 `score - bonus_total`(R 보너스를 뺀 점수)에 묶여 있다. R 보너스: 체력이 꽉 찬 채로 먹은 R을 `r_full`로 세어 `R_BONUS_COUNT`개마다 `score`와 `bonus_total`에 `R_BONUS_POINTS`를 더한다. P 보너스: 미사일이 최대일 때 먹은 P를 `p_full`로 세어 `P_BONUS_COUNT`개마다 같은 방식으로 더한다 (그래서 `drop_items`는 미사일이 최대여도 P를 떨어뜨린다). 안내 글은 `bonus_text`. 내 총알의 적 판정은 `bullet_hits()`(그림 크기의 직사각형).
- 난이도: `MODES`(Easy/Normal/Hard) 딕셔너리와 전역 `game_mode`. Normal은 기본 규칙(`MAX_ENEMIES`, `ENEMY_MAX_COUNT` 등)을 그대로 쓰고 Easy/Hard는 배율/값만 다르다. 쓰는 곳: `Enemy.__init__`(속도·체력), main의 스폰/`enemy_count`/총알 속도, `drop_items`(P/R/B 배율). 기록 한 개는 score/date/ship/level/time/player이다. .5로 끝나는 점수는 기록할 때 0.5를 빼고 정수로 적는다. 최고 점수 칸을 누르면 바로 `records_screen()`이 열리고, 아무 키나 Back으로 바로 닫힌다. 첫 화면 버튼은 `MODE_BUTTONS`.
- 내가 터뜨린 폭발은 `explosions`에 5번째 값 `True`를 달고, 그 폭발 범위에 닿는 `enemy_bullets`와 초록 적의 `bombs`는 매 프레임 지워진다.
- 시작 흐름: 파일 맨 아래의 `front_screens(skip_name)`가 `name_screen()` → `splash_screen()` → `controls_screen()`(조작법 3쪽, `CONTROL_PAGES`; 쪽 이동은 Next/Back, 첫 쪽 Back이면 난이도 화면) → `title_screen()`을 단계(step)로 이어 부르고, 각 화면의 Back(`SPLASH_BACK`, `draw_nav_back()`로 같은 모양)이 `"back"`을 돌려주면 바로 앞 화면으로 돌아간다 (전투기 고르기의 Back은 조작법 마지막 쪽으로, `CONTROL_START`). 아래는 `name_screen()`(가장 먼저, 한 번만: 이름 입력 칸 `NAME_BOX`는 `TEXTINPUT`/`KEYDOWN`으로 입력, `GUEST_BUTTON`은 "Guest"; 결과는 전역 `player_name`이고 `save_best`가 기록의 `player`에 저장) → `splash_screen()`(첫 화면: 제목, 큰 1번 전투기, Press, 최고 점수) → `controls_screen()` → `title_screen()`(전투기 고르기) 순서로 한 번씩 부른 뒤 `main()`을 반복한다 (게임 오버 후 R은 타이틀 없이 바로 `main()` 재시작). 일시정지 화면의 "Go Home" 버튼(`PAUSE_HOME`)이나 게임 오버 화면의 "Go Home" 버튼(`GAMEOVER_HOME`)을 누르면 `main()`이 `"home"`을 반환하고, 맨 아래 루프가 `front_screens(skip_name=True)`로 난이도 화면부터 다시 한다. 최고 점수 칸은 `draw_best_box()`를 두 화면이 같이 쓴다. 적과 부딪히면(`rammed`) 플레이어와 그 적이 함께 1 피해를 입는다(무적일 때는 없음).

- 이미지: `assets/player_{1,2,3}.png`(내 비행기 3종, 위를 보는 그대로 사용. 모듈 변수 `selected_ship`이 고른 번호(0~2)이고 `title_screen()`이 바꾼다) 와 `assets/{red,green,yellow}_enemy.png` (위를 보는 그림이라 `load_sprite()`에서 180도 돌려 쓴다, 배경이 투명한 PNG). `ENEMY_SPRITES` 딕셔너리에 담기고, 상점 물건 그림은 `assets/item_{heart,shield,change,bomb,bomb_rainbow}.png`를 `item_icon(name, size)`가 캐시해서 쓰며 (`draw_change_icon()`은 티켓, `draw_bomb_icon()`은 폭탄 그림을 쓴다), 파일이 없으면 색깔 원으로 대신 그린다.
- 보너스 라운드 진입: `play_frames`가 `BONUS_INTERVAL`(45초)이 되면 바로 `shop`이 아니라 `fade`(남은 프레임)가 켜진다. 그동안 적은 이동만 하고 `enemy_alpha`로 흐려지며, 끝나면 적/적 총알/폭탄/폭발을 비우고 `shop = True`. 상점이 닫히면 `spawn = 0`으로 다시 시작한다.
- 최고 기록: `best_score.txt`(`.gitignore`)는 모드별 순위표 `{"Easy": [기록, ...], ...}` JSON이다 (`rankings`, 점수 높은 순, `RANK_SIZE` = 10개; 예전 형식도 읽는다). `save_best(score, level, seconds)`가 10위 안에 들면 넣고, main의 `save_run()`이 한 판에 한 번만 부른다 (게임 오버 / 홈 / 창 닫기 중 먼저). 1위는 `top_record(mode)`. 기록 화면의 모드 줄을 누르면 `ranking_screen(mode)`(1~10위, 이름 포함).

- 비행기 능력치: `SHIP_STATS`(공격, 체력, 스피드)가 `Player.__init__`에서 `fire_delay`/`hp`/`speed`로 바뀌고, 시작 체력이 `max_hp`(최대 하트)가 된다. R/Full Heal은 `max_hp`까지만 채우고, 상점의 Max Heart +1만 `max_hp`를 늘린다(절대 상한 `HP_CAP`). 타이틀은 `phase`("choose" → "stats" → Select로 카운트다운)로 진행되고 전투기 소개 화면은 `draw_stats_screen(ship, now)`가 그린다 (이름, 큰 전투기, Back/Select만). 숨겨진 기능: `STATS_TITLE`(이름)을 `selected_ship + 1`번 누르면 `start_with_s = True`(이름 옆에 무지개 폭탄 표시), 다음 `main()`이 `player.has_s = True`를 주고 끈다. `Change Ticket`은 `SHOP_POOL`의 가장 비싼 물건(kind "change")이고, 상점의 `SHOP_CHANGE` 버튼/C 키가 `rerolls`를 1 쓰고 `reroll_shop()`으로 `shop_offers`를 새로 뽑는다. 고르기 화면에서 전투기에 마우스를 올리면 `hover[i]`(0~1)가 부드럽게 올라가 1.2배로 커지고 `draw_hover_stats()`가 `draw_gauge()`로 공격/체력/스피드 게이지를 그린다.
- 상단 표시(HUD)는 `draw_hud(surf, score, level, player)` 하나로 그린다. 타이틀의 카운트다운에서도 같은 함수로 서서히 나타나게 한다.

- 구매 확인 화면: 상점에서 물건을 고르면(`open_idx`) `confirm_idx`가 켜져 `draw_confirm_screen()`이 상점 위에 확인 화면(질문, `draw_shop_icon_big()` 큰 그림, `ITEM_DESC` 설명, 가격, `CONFIRM_BACK`/`CONFIRM_BUY`)을 그린다. Buy(`do_buy`)면 기존 구매 블록이 `buy_idx = confirm_idx`로 사고, 샀을 때만(`bought`) 확인 화면을 닫는다. 새 물건을 추가하면 `ITEM_DESC`에도 설명을 넣는다.
- 상점: 보너스 라운드가 열릴 때 `roll_shop(player)`가 `SHOP_POOL`에서 3개를 가중치로 뽑아 `shop_offers`에 둔다. 구매 효과는 main의 `buy_idx` 처리 블록, 구매 가능 여부는 `shop_available()`, 카드 그림은 `draw_shop_icon()`. 새 물건은 `SHOP_POOL`, `UNAVAILABLE_MSG`, `shop_available`, 구매 블록, `draw_shop_icon` 다섯 곳과 `ITEM_DESC`를 같이 고친다.
- 게임 안 글씨는 영어로 통일했다 (주석은 한국어).


- 폭발 그림(`fx`, 보기만 하는 효과): `[위치, 나이, 수명, 반경]`을 `add_fx()`로 더하고 `draw_fx()`가 그린다. 적이 쓰러질 때는 `explode_enemy()`(`kind="boom"`: `assets/explosion.png`를 `draw_fx()`가 키우며 투명하게 그림 + 파편). 폭탄(`explosions`)은 반투명 레이어로 그린다. 내가 맞거나 부딪히면 피격 처리에서 내 위치에 작은 `"boom"`을 더한다 (그래서 내 비행기를 `draw_fx()`보다 먼저 그린다). 피해를 주는 `explosions`(폭탄)와는 별개다.

## 확인 방법

화면 없이 스모크 테스트: `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 5 python shooter.py` (종료 코드 124면 오류 없이 돌아간 것). 단 이제 타이틀 화면에서 키 입력을 기다리므로 이 명령은 `main()`까지 가지 않는다. 게임 본편을 돌리려면 임시 사본에서 맨 아래 `front_screens()` 호출을 지우고 돌린다.
화면 확인이 필요하면 임시 사본에서 `pygame.image.save(screen, ...)`로 캡처하고, 확률·조건은 임시 사본에서 상수를 바꿔 검증한다 (원본은 건드리지 않는다).
실제 플레이 감각(난이도, 판정)은 사용자가 직접 확인해야 한다.
- 순위표(`ranking_screen`)의 1~3위는 `assets/medal_{gold,silver,bronze}.png`(투명 PNG)를 `draw_medal()`이 그린다 (셋 다 같은 크기, 금메달만 빛줄기가 번쩍이며 지나간다 (`_medal_shine`), 4위부터는 같은 세로줄에 숫자). 파일이 없으면 도형으로 대신 그린다.
- 웹 버전: 모든 화면 함수(`name_screen`, `splash_screen`, `controls_screen`, `title_screen`, `main`, `front_screens`, `records_screen`, `ranking_screen`)는 `async def`이고 프레임 끝에 `await asyncio.sleep(0)`이 있다 (pygbag 때문; 새 화면 루프도 똑같이 만들고 호출에 `await`을 붙인다). 시작은 `asyncio.run(run())`. `WEB`(= emscripten)이면 `scale = 1`, 글꼴은 `make_font()`가 기본 글꼴, ←/→/…/♥ 글자는 기본 글꼴에 없어서 `ARROW_L`/`ARROW_R`/`ELLIPSIS`/`render_hearts()`로 대신한다 (새 특수문자를 쓰면 웹에서 네모로 보인다). `build_web.py`가 `docs/`를 만든다 (GitHub Pages, 빌드 결과도 커밋한다).
- 배포 규칙: 사용자가 "이제부터 모든 내용을 커밋하고 푸시해 줘"라고 했으므로, 하나를 고치거나 만들 때마다(요청 하나가 끝날 때마다) 따로 묻지 않고 바로 커밋하고 푸시한다. 여러 개를 모아서 한 번에 올리지 않는다 (`.gitignore`의 `best_score.txt` 같은 개인 파일은 제외). `shooter.py`나 `assets/`가 바뀐 경우 먼저 `python build_web.py`로 웹 버전을 다시 만들고 `docs/`까지 같이 커밋·푸시한다 (사이트: https://lhk3832.github.io/astroid/). 빌드 전에 테스트용 서버(포트 8000/8001)가 떠 있으면 끈다. 커밋 메시지 끝에는 `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`를 붙인다.
- 공용 순위표(웹): `SUPABASE_URL`/`SUPABASE_KEY`가 있으면 `ONLINE`. `save_best`는 서버에 보내기만 하고(`online_post`), 순위는 `online_refresh()`로 받아 `online_tick()`(모든 화면 루프의 프레임 끝)이 `rankings`에 넣는다. 서버와는 `platform.window.eval`로 만든 자바스크립트 함수(`window.astroid_post`/`astroid_fetch`)와 결과 변수로 주고받는다. 이름 최대 `NAME_MAX` = 10. 테스트는 가짜 서버(CORS 허용, `/rest/v1/scores` POST/GET)를 띄우고 임시 사본의 URL을 바꿔 한다.
- 내가 맞는 판정: 적 총알(반지름 `ENEMY_BULLET_RADIUS`)이 내 비행기 그림의 모양(`PLAYER_MASKS`, 투명한 곳 제외)과 겹치면 맞는다 (`enemy_bullet_hits_player`, 이번 프레임에 지나온 길의 4점을 본다; 그림 파일이 없으면 `PLAYER_HIT_W`/`PLAYER_HIT_H` 직사각형). 부딪힘(`rammed`)은 `radius`로 따로 본다.
- 무적(`player.invuln`: 피격 직후, Shield)일 때 적 총알이 비행기 그림에 닿으면 피해 없이 사라진다 (main의 피격 처리 앞, 작은 불꽃 `add_fx`). 폭탄과 부딪힘은 무적이면 그대로 피해가 없다.
- 기록 저장: `read_saved_text()`/`write_saved_text()`가 데스크톱은 `best_score.txt`, 웹은 브라우저 localStorage(`STORAGE_KEY` = astroid_best)를 쓴다 (새로고침해도 남음). 공용 순위표(`ONLINE`)가 켜져 있으면 서버가 우선이다.
- 공용 순위표 보호: `supabase_hardening.sql`(제약, 금칙어/속도 제한 트리거, hidden/ip_hash 칸, 칸 단위 권한)을 사용자가 Supabase에서 실행한다. 그래서 `online_post`는 이름에서 허용 글자(영문/숫자/한글/공백/_.-) 밖을 빼고, 서버가 거절하면(`fail`) `online_tick`이 이름을 Guest로 바꿔 한 번만 다시 보낸다 (`_last_body`). 서버 규칙을 바꾸면 이 두 곳도 같이 맞춘다.
- 효과음: `play_sfx(name)`(`shoot`/`bomb`/`hit`/`hurt`)이 `assets/sfx/{name}_{a|b}.ogg`를 `SFX_CHOICE`대로 불러 `SFX_VOLUME` 크기로 재생한다 (소리 장치나 파일이 없어도 예외를 삼키고 게임은 계속). 부르는 곳: 총알 쏠 때(`player.cooldown = ...` 다음), 폭탄 터질 때(`explosions.append` 두 군데), 내가 적을 맞힐 때(`hit_sound`, 프레임당 한 번), 내가 맞을 때(`player.hp -= 1` 다음). 새 소리는 `make_sfx.py`에 합성 코드를 추가하고 `.ogg`로 저장한다 (pygbag은 WAV를 거절한다).

