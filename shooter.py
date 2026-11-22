import asyncio
import datetime
import json
import math
import os
import random
import re
import sys

import pygame

W, H = 800, 600
WEB = sys.platform == "emscripten"  # 브라우저(pygbag)에서 도는 중인가
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BEST_FILE = os.path.join(BASE_DIR, "best_score.txt")  # 최고 점수 저장 파일
ENEMY_SPRITE_SIZE = 44  # 적 이미지의 크기(px)
PLAYER_SPRITE_SIZE = 72  #내 비행기 이미지의 크기(px). 충돌 범위는 그대로
SPLASH_SPRITE_SIZE = 210 # 첫 화면의 큰 비행기 크기(px)
TITLE_SPRITE_SIZE = 130 # 타이틀 화면의 내 비행기 크기(px)
FADE_FRAMES = 60        # 보너스 라운드로 가기 전에 적이 사라지는 데 걸리는 시간(프레임)
GAME_TITLE = "Asteroid"  # 타이틀 화면과 창 제목에 쓰이는 게임 이름
TITLE_COUNTDOWN = 3        # 아무 버튼이나 누른 뒤 게임이 시작되기까지의 시간(초)
WINDOW_SCALE = 2  # 창 크기 배율
MAX_ENEMIES = 7    # 화면에 동시에 있을 수 있는 적의 최대 수 (노란 적은 제외)
YELLOW_SPAWN_INTERVAL = 4 * 60  # 노란 적이 나오는 간격(프레임). 미사일이 최대일 때부터 등장
YELLOW_BULLET_SPEED = 9      # 노란 적의 총알 속도 (예전 7). 난이도의 총알 속도 배율이 곱해진다
YELLOW_BULLET_COUNT = 2      # 노란 적이 한 번에 쏘는 총알 수 (예전 1)
YELLOW_BULLET_SPREAD = 9     # 노란 적 총알 사이의 각도(도)
YELLOW_MAX = 2                  # 노란 적이 동시에 있을 수 있는 최대 수
FPS = 60
RED_DROP_RATES = (0.01, 0.033)    # (P, R) 빨간 적: R이 잘 나옴
GREEN_DROP_RATES = (0.10, 0.03)  # (P, R) 초록 적: P가 잘 나옴
INVULN_TIME = 1 * FPS
BULLET_RADIUS = 4
PLAYER_HIT_W = 18  # 내 비행기의 피격 범위 반폭(px). 날개 쪽까지 (비행기 그림 72px). 적 총알은 크기(ENEMY_BULLET_RADIUS)만큼 더해서 닿으면 맞는다
PLAYER_HIT_H = 26  # 내 비행기의 피격 범위 반높이(px). 코부터 꼬리까지
ENEMY_BULLET_RADIUS = 5  # 적 총알의 크기(그림과 판정)
MAX_POWER = 5
ENEMY_SCALE_SCORE = 100
START_POWER = 2
HEAL_UNLOCK_PICKUPS = 0  # P를 이만큼 먹은 뒤부터 R이 나옴 (0이면 처음부터)
HP_CAP = 8  # 상점에서 하트를 늘려도 넘을 수 없는 절대 상한 (R 아이템/회복은 그 전투기의 현재 최대 하트까지만)
SHIP_NAMES = ["Normal", "Tanker", "Attack"]  # 고르기 화면에서 전투기 아래에 보이는 이름
SHIP_STATS = [(3, 3, 3), (2, 5, 2), (5, 2, 5)]  # 비행기 1~3번의 (공격, 체력, 스피드)
SPAWN_SCORE = 100  # 이 점수를 얻을 때마다 한 번에 나오는 적이 1마리씩 늘어남
GREEN_RATE =0.25
BOMB_FUSE = 2 * FPS
BOMB_RADIUS = 70
S_UNLOCK_COUNT = 5  # 적 미사일이 이 개수 이상이면 S 아이템이 나옴
S_DROP_RATE = 0.20 / 3    # 적 미사일이 정확히 S_UNLOCK_COUNT개일 때 (약 6.7%)
S_LATE_DROP_RATE = 0.02 / 3  # 그 이후(더 늘어난 뒤) (약 0.67%)
S_WITH_B_FACTOR = 0.25    # B를 가지고 있을 때 S 드롭 확률에 곱하는 비율 (0.25 = B가 있으면 1/4로 줄어듦)
BLAST_RADIUS = 600  # S 폭발 반경 (B의 4배, 화면 대부분을 덮는다)
R_BONUS_COUNT = 3     # 체력이 꽉 찬 상태로 R을 이만큼 먹으면
R_BONUS_POINTS = 100  # 이만큼 보너스 점수 (적이 늘어나는 난이도에는 반영하지 않는다)
P_BONUS_COUNT = 3     # 미사일이 최대인 상태로 P를 이만큼 먹으면
P_BONUS_POINTS = 100  # 이만큼 보너스 점수 (이것도 난이도에는 반영하지 않는다)
S_HOLD_FRAMES = FPS // 2  # S는 오른쪽 마우스 버튼을 이만큼(0.5초) 꾹 눌러야 발동한다
ENEMY_MAX_COUNT = 7  # 적 미사일 상한
MODES = {  # 맨 앞 화면에서 고르는 난이도. Normal이 우리가 처음부터 만들어 온 기본 규칙이다
    "Easy": dict(spawn_mult=1.4, max_enemies=5, enemy_speed=0.8, enemy_hp_bonus=0,
                 bullet_speed=3.2, enemy_max_count=5, drop_mult=1.5, kill_score=15),
    "Normal": dict(spawn_mult=1.0, max_enemies=MAX_ENEMIES, enemy_speed=1.0, enemy_hp_bonus=0,
                   bullet_speed=4.0, enemy_max_count=ENEMY_MAX_COUNT, drop_mult=1.0, kill_score=10),
    "Hard": dict(spawn_mult=0.75, max_enemies=9, enemy_speed=1.25, enemy_hp_bonus=1,
                 bullet_speed=5.0, enemy_max_count=9, drop_mult=0.7, kill_score=10),
}
YELLOW_SCORE_MULT = 1.5  # 노란 적은 다른 적 점수의 1.5배
# spawn_mult: 적이 나오는 간격에 곱함 / max_enemies: 동시에 나올 수 있는 적 / enemy_speed: 적 속도에 곱함
# enemy_hp_bonus: 적 체력에 더함 / bullet_speed: 적 총알 속도 / enemy_max_count: 적이 한 번에 쏘는 총알 수 상한
# drop_mult: P/R/B 아이템 드롭률에 곱함 (코인과 S는 그대로) / kill_score: 적 1마리를 무찌를 때 얻는 점수
game_mode = "Normal"  # 지금 고른 난이도
player_name = "Guest"  # 맨 앞 화면에서 입력한 플레이어 이름 (게스트면 "Guest")
B_START = 3          # 처음 가지고 있는 폭탄 B 개수
B_RADIUS = 150

B_DROP_RATE = 0.01  # 적 처치 시 B 아이템이 나올 확률
COIN_DROP_RATE = 0.03         # 빨간/초록 적 처치 시 코인 아이템이 나올 확률
YELLOW_COIN_DROP_RATE = 0.35   # 노란 적 처치 시 코인 아이템이 나올 확률 (노란 적은 코인만 떨어뜨림)
MAGNET_RADIUS = 60  # 이 거리 안에 들어온 아이템은 나에게 빨려 들어옴
MAGNET_ACCEL = 0.9      # 자석에 끌릴 때의 가속(px/프레임²). 가까울수록 최대 2배
MAGNET_MAX_SPEED = 14   # 끌려오는 속도의 상한(px/프레임)
COIN_VALUE = 100      # 코인 아이템 1개가 주는 코인
BONUS_INTERVAL = 45    #보너스 라운드(상점)가 열리는 간격(초, 플레이 시간 기준)
SHOP_SLOTS = 3  # 상점에는 한 번에 물건이 3개만 나온다
SHOP_POOL = [  # (이름, 가격, 종류, 나올 가중치): 보너스 라운드마다 이 중 3개가 가중치에 따른 확률로 뽑힌다
    ("Max Heart +1", 100, "heart", 30),  # 최대 하트와 현재 하트를 1 늘린다
    ("Bomb B +1", 200, "b", 25),
    ("Missile +1", 300, "power", 18),
    ("Shield 10s", 200, "shield", 14),
    ("Speed +1", 200, "speed", 12),
    ("Rapid Fire", 300, "rapid", 12),
    ("Full Heal", 400, "heal", 6),
    ("Rainbow Bomb", 500, "rainbow", 4),
    ("Change Ticket", 600, "change", 4),  # 상점 물건을 바꿀 수 있는 아이템. 가장 비싸다
]
SHIELD_TIME = 10 * FPS  # Shield 물건의 무적 시간(프레임)
MAX_SPEED = 9           # Speed +1로 올릴 수 있는 이동 속도 상한
MIN_FIRE_DELAY = 3      # Rapid Fire로 줄일 수 있는 발사 간격 하한(프레임)
UNAVAILABLE_MSG = {     # 이미 최대라서 살 수 없을 때 보여주는 말
    "heart": "Hearts are at the maximum", "heal": "HP is already full",
    "power": "Missiles are already maxed", "speed": "Speed is already maxed",
    "rapid": "Fire rate is already maxed", "rainbow": "You already have a Rainbow Bomb",
}
SHOP_CARDS = [pygame.Rect(40 + i * 250, 190, 220, 210) for i in range(3)]
SHOP_CHANGE = pygame.Rect(W // 2 - 230, 450, 220, 50)    # 상점 아래의 "Change" 버튼 (Change Ticket을 써서 물건을 바꾼다)
SHOP_CONTINUE = pygame.Rect(W // 2 + 10, 450, 220, 50)
CONFIRM_BACK = pygame.Rect(W // 2 - 210, 525, 180, 50)  # 구매 확인 화면의 Back 버튼
CONFIRM_BUY = pygame.Rect(W // 2 + 30, 525, 180, 50)    # 구매 확인 화면의 Buy 버튼
STATS_TITLE = pygame.Rect(W // 2 - 190, 45, 380, 70)       # 능력치 소개 화면의 "Fighter N" 이름. 숨겨진 기능의 클릭 자리
HOVER_SCALE = 0.2  # 타이틀에서 전투기에 마우스를 올렸을 때 더 커지는 비율(0.2 = 1.2배)
SHOP_TITLE = "Star Market" # 보너스 라운드 상점 화면의 제목
MODE_BUTTONS = [pygame.Rect(W // 2 - 215 + i * 150, 392, 130, 42) for i in range(3)]  # 첫 화면의 Easy / Normal / Hard 버튼 (가로 430px)
PRESS_BAR = pygame.Rect(W // 2 - 215, 448, 430, 60)  # 첫 화면의 "Press To Start" 바: 모드 버튼 줄과 같은 길이
RECORDS_BACK = pygame.Rect(W // 2 - 90, 505, 180, 50)  # 기록 화면의 Back 버튼
NAME_BOX = pygame.Rect(W // 2 - 215, 418, 430, 48)      # 이름 화면의 이름 입력 칸
GUEST_BUTTON = pygame.Rect(W // 2 - 215, 505, 430, 52)  # 이름 화면의 "Play In Guest Mode" 버튼
NAME_MAX = 10  # 이름 최대 글자 수
SPLASH_BACK = pygame.Rect(12, 38, 92, 34)  # 난이도 화면 왼쪽 위의 Back 버튼 (이름 화면으로)
MODE_COLORS = {"Easy": (90, 210, 120), "Normal": (110, 170, 255), "Hard": (255, 100, 100)}
BEST_BOX = pygame.Rect(0, 0, 430, 46)  # 모드 버튼 줄과 같은 길이
BEST_BOX.center = (W // 2, H - 55)  # 타이틀의 최고 점수 칸
STATS_BACK = pygame.Rect(W // 2 - 210, 500, 180, 50)    # 능력치 소개 화면의 Back 버튼
STATS_SELECT = pygame.Rect(W // 2 + 30, 500, 180, 50)   # 능력치 소개 화면의 Select 버튼
PAUSE_HOME = pygame.Rect(300, 390, 200, 50)  # 일시정지 화면의 "Go Home" 버튼
GAMEOVER_HOME = pygame.Rect(300, H // 2 + 65, 200, 50)  # 게임 오버 화면의 "Go Home" 버튼
RAINBOW = [(255, 60, 60), (255, 150, 40), (255, 230, 60), (80, 210, 90), (70, 140, 255), (170, 90, 230)]
ITEM_COLORS = {  # (채움색, 테두리색)
    "B": ((255, 210, 120), (120, 70, 10)),
    "P": ((90, 255, 140), (20, 100, 50)),
    "R": ((255, 130, 160), (130, 20, 50)),
    "S": ((120, 200, 255), (20, 60, 130)),
    "C": ((255, 220, 70), (140, 100, 10)),
}

pygame.init()
# 게임은 W x H 캔버스에 그리고, 창에는 WINDOW_SCALE배로 확대해서 보여준다.
# 화면이 작아서 안 들어가면 바탕화면 높이의 90%에 맞춰 줄인다.
if WEB:
    scale = 1.0
else:
    desktop_h = pygame.display.get_desktop_sizes()[0][1]
    scale = min(WINDOW_SCALE, desktop_h * 0.9 / H)
window = pygame.display.set_mode((int(W * scale), int(H * scale)))
screen = pygame.Surface((W, H))
pygame.display.set_caption(GAME_TITLE)
clock = pygame.time.Clock()
def make_font(size, bold=False):
    """데스크톱은 맑은 고딕. 웹(브라우저)에는 없어서 assets/fonts의 Noto Sans KR(한글 2350자 + 영문)을 쓴다.
    그것도 없으면 pygame 기본 글꼴."""
    if WEB:
        path = os.path.join(BASE_DIR, "assets", "fonts", "NotoSansKR-" + ("Bold" if bold else "Regular") + ".ttf")
        try:
            return pygame.font.Font(path, size)
        except (pygame.error, FileNotFoundError, OSError):
            f = pygame.font.Font(None, round(size * 1.3))
            f.set_bold(bold)
            return f
    return pygame.font.SysFont("malgungothic", size, bold=bold)


font = make_font(24)
GLYPHS_OK = all(m is not None for m in font.metrics("♥←→…"))  # 이 글꼴에 ♥ ← → … 글자가 있나 (기본 글꼴에는 없다)
ELLIPSIS = "…" if GLYPHS_OK else "..."
ARROW_L = "←" if GLYPHS_OK else "<"
ARROW_R = "→" if GLYPHS_OK else ">"
big = make_font(56, True)
title_font = make_font(84, True)
small_font = make_font(18)
mid_font = make_font(30, True)
press_font = make_font(46, True)  # 첫 화면의 Press To Start 바 안 글씨

# 효과음: assets/sfx/{이름}_{a 또는 b}.ogg. 소리마다 두 가지를 만들어 뒀고 아래에서 마음에 드는 쪽을 고른다 (make_sfx.py로 다시 만들 수 있다).
SFX_CHOICE = {"shoot": "a", "bomb": "a", "hit": "a", "hurt": "a"}  # shoot 총알 쏠 때 / bomb 폭탄 터질 때 / hit 내가 적을 맞혔을 때 / hurt 내가 맞았을 때
SFX_VOLUME = {"shoot": 0.25, "bomb": 0.7, "hit": 0.3, "hurt": 0.8}  # 소리 크기(0~1). 자주 나는 소리는 작게
_sfx_cache = {}


def play_sfx(name):
    """효과음 하나를 재생한다. 소리 장치가 없거나 파일이 없어도 게임은 그대로 간다."""
    snd = _sfx_cache.get(name, 0)
    if snd == 0:
        try:
            snd = pygame.mixer.Sound(os.path.join(BASE_DIR, "assets", "sfx", "%s_%s.ogg" % (name, SFX_CHOICE[name])))
            snd.set_volume(SFX_VOLUME[name])
        except Exception:
            snd = None
        _sfx_cache[name] = snd
    if snd:
        try:
            snd.play()
        except Exception:
            pass


def load_sprite(filename, size, angle=0):
    """이미지를 가장 긴 변이 size(px)가 되게 불러온다. 파일이 없으면 None (도형으로 대신 그림)."""
    try:
        img = pygame.image.load(os.path.join(BASE_DIR, "assets", filename)).convert_alpha()
    except (pygame.error, FileNotFoundError):
        return None
    k = size / max(img.get_size())
    img = pygame.transform.smoothscale(img, (round(img.get_width() * k), round(img.get_height() * k)))
    return pygame.transform.rotate(img, angle) if angle else img


# 적 그림은 위를 보고 있어서 아래를 향하도록 180도 돌린다.
ENEMY_SPRITES = {
    "red": load_sprite("red_enemy.png", ENEMY_SPRITE_SIZE, 180),
    "green": load_sprite("green_enemy.png", ENEMY_SPRITE_SIZE, 180),
    "yellow": load_sprite("yellow_enemy.png", ENEMY_SPRITE_SIZE, 180),
}
# 고를 수 있는 내 비행기 3종 (1, 2, 3번). 게임 안(작게)과 타이틀 화면(크게)용
PLAYER_SPRITES = [load_sprite(f"player_{i}.png", PLAYER_SPRITE_SIZE) for i in (1, 2, 3)]
TITLE_SPRITES = [load_sprite(f"player_{i}.png", TITLE_SPRITE_SIZE) for i in (1, 2, 3)]
SPLASH_SPRITE = load_sprite("player_1.png", SPLASH_SPRITE_SIZE)  # 첫 화면의 큰 일반 비행기(1번)
EXPLOSION_SPRITE = load_sprite("explosion.png", 208)  # 적 전투기가 폭발할 때의 그림(원본 크기, 그릴 때 크기를 바꾼다)
selected_ship = 0  # 타이틀에서 고른 비행기 번호(0~2)
start_with_s = False  # 능력치 화면의 숨겨진 기능으로 켜지면 다음 게임을 S(무지개 폭탄) 1개와 함께 시작


def fade_color(color, alpha):
    """배경색 쪽으로 alpha(0~1)만큼 섞어서 서서히 사라지는 색을 만든다."""
    bg = (10, 10, 30)
    return tuple(int(bg[i] + (color[i] - bg[i]) * alpha) for i in range(3))


def empty_record():
    return {"score": 0, "date": "", "ship": "", "level": 0, "time": 0, "player": ""}


def num(v):
    """저장된 점수를 읽는다: 소수가 없으면 정수로 (22.5 같은 점수는 그대로)."""
    f = float(v)
    return int(f) if f == int(f) else f


RANK_SIZE = 10  # 모드마다 기록하는 순위 수 (1~10위)


def to_record(v):
    """저장 파일의 한 항목(기록 dict, 또는 예전의 점수 숫자)을 기록 dict로 바꾼다."""
    rec = empty_record()
    if isinstance(v, dict):
        for key in rec:
            if key in v:
                rec[key] = v[key]
        rec["score"] = num(rec["score"])
    else:
        rec["score"] = num(v)
    return rec


STORAGE_KEY = "astroid_best"  # 웹에서 기록을 넣어 두는 브라우저 저장소(localStorage)의 이름


def read_saved_text():
    """저장된 기록 글자를 읽는다: 웹은 브라우저 저장소(새로고침해도 남는다), 데스크톱은 best_score.txt."""
    if WEB:
        import platform
        return str(platform.window.localStorage.getItem(STORAGE_KEY) or "")
    with open(BEST_FILE, encoding="utf-8") as f:
        return f.read()


def write_saved_text(text):
    if WEB:
        import platform
        platform.window.localStorage.setItem(STORAGE_KEY, text)
    else:
        with open(BEST_FILE, "w", encoding="utf-8") as f:
            f.write(text)


def load_best():
    """모드별 순위표 {"Easy": [1위, 2위, ...], "Normal": [...], "Hard": [...]} (점수 높은 순, 최대 RANK_SIZE개).
    기록 하나는 점수/날짜/전투기/레벨/플레이 시간(초)/플레이어 이름. 예전 파일(모드별 기록 하나, 점수 숫자)도 읽는다."""
    ranks = {name: [] for name in MODES}
    try:
        data = json.loads(read_saved_text().strip())
        if not isinstance(data, dict):
            data = {"Normal": data}  # 예전 파일: 점수 숫자 하나는 Normal 점수
        for name in ranks:
            v = data.get(name)
            items = v if isinstance(v, list) else ([] if v is None else [v])
            recs = [to_record(x) for x in items]
            recs = [r for r in recs if r["score"] > 0]
            recs.sort(key=lambda r: -r["score"])
            ranks[name] = recs[:RANK_SIZE]
    except Exception:
        pass  # 파일/저장소가 없거나 깨져 있으면 빈 순위표로 시작한다
    return ranks


rankings = load_best()


def top_record(mode):
    """그 모드의 1위 기록 (기록이 없으면 점수 0인 빈 기록)."""
    return rankings[mode][0] if rankings[mode] else empty_record()


# 공용 순위표 (웹 버전 전용): Supabase 표 scores에 점수를 보내고 불러온다. 아래 두 값이 비어 있으면 꺼진다(웹도 지금처럼 그 탭에서만 기록).
# 주소와 anon(공개) 키는 코드에 넣어도 된다. 순위표 표는 읽기/추가만 허용하도록 만들어져 있다 (README의 "공용 순위표" 참고). service_role 키는 절대 넣지 않는다.
SUPABASE_URL = "https://wlftptadnfnmbebobibe.supabase.co"
SUPABASE_KEY = "sb_publishable_IZzdzvJFrvAZwzmfK4za0g_Ti5aotXq"  # 공개(publishable) 키: 코드에 넣어도 되는 키 (읽기/점수 추가만 가능)
ONLINE = WEB and bool(SUPABASE_URL) and bool(SUPABASE_KEY)
_online_frames = 0


def _js(code):
    import platform  # 브라우저(pygbag)에서만 있는 모듈
    return platform.window.eval(code)


def online_setup():
    """브라우저에 서버와 주고받는 작은 자바스크립트 함수를 만들어 둔다 (파이썬은 결과를 window 변수에서 읽는다)."""
    if not ONLINE:
        return
    _js("""
    window.astroid_top = {}; window.astroid_post_state = "";
    window.astroid_hdr = function(){
      var k = %s, h = {"apikey": k};
      if (k.indexOf("eyJ") === 0) h["Authorization"] = "Bearer " + k;  // 예전 JWT 형식 키만 Authorization도 보낸다 (sb_publishable_ 키는 apikey만)
      return h;
    };
    window.astroid_post = function(body){
      var h = window.astroid_hdr(); h["Content-Type"] = "application/json"; h["Prefer"] = "return=minimal";
      fetch(%s + "/rest/v1/scores", {method: "POST", headers: h, body: body})
        .then(function(r){ window.astroid_post_state = r.ok ? "ok" : "fail"; })
        .catch(function(){ window.astroid_post_state = "fail"; });
    };
    window.astroid_fetch = function(mode){
      fetch(%s + "/rest/v1/scores?mode=eq." + mode + "&select=score,player,ship,level,play_time,created_at&order=score.desc,created_at.asc&limit=%d",
            {headers: window.astroid_hdr()})
        .then(function(r){ return r.text(); })
        .then(function(t){ window.astroid_top[mode] = t; })
        .catch(function(){});
    };
    """ % (json.dumps(SUPABASE_KEY), json.dumps(SUPABASE_URL), json.dumps(SUPABASE_URL), RANK_SIZE))


def online_refresh():
    """세 모드의 1~10위를 서버에서 다시 불러오라고 시킨다 (도착하면 online_tick이 rankings에 넣는다)."""
    if ONLINE:
        for mode in MODES:
            _js("window.astroid_fetch(%s)" % json.dumps(mode))


def online_post(score, level, seconds):
    """이번 판의 점수를 서버에 보낸다 (실패해도 게임은 계속한다)."""
    if not ONLINE:
        return
    # 서버가 받는 이름 글자는 영문, 숫자, 한글, 공백, _ . - 뿐이라 나머지는 뺀다 (비면 Guest)
    name = re.sub(r"[^A-Za-z0-9가-힣 _.\-]", "", player_name or "").strip()[:NAME_MAX].strip() or "Guest"
    body = {"mode": game_mode, "score": int(score), "player": name,
            "ship": SHIP_NAMES[selected_ship], "level": int(level), "play_time": int(seconds)}
    _send_score(body)


_last_body = [None, False]  # 마지막으로 보낸 점수, Guest로 다시 보내 봤는가


def _send_score(body):
    _last_body[0] = body
    try:
        _js("window.astroid_post_state = ''; window.astroid_post(%s)" % json.dumps(json.dumps(body)))
    except Exception:
        pass


def online_tick():
    """프레임마다 부른다: 보낸 점수가 도착했으면 순위표를 다시 불러오고, 도착한 순위표를 rankings에 넣는다. 30초마다 다시 불러온다."""
    global _online_frames
    if not ONLINE:
        return
    _online_frames += 1
    if _online_frames % 20:
        return
    try:
        state = _js("window.astroid_post_state")
        if state == "ok":
            _js("window.astroid_post_state = ''")
            _last_body[:] = [None, False]
            online_refresh()
        elif state == "fail" and _last_body[0] and not _last_body[1]:
            # 서버가 거절했다 (예: 이름이 금칙어): 점수는 남도록 이름만 Guest로 바꿔 한 번 더 보낸다
            _last_body[1] = True
            _send_score(dict(_last_body[0], player="Guest"))
        if _online_frames % (FPS * 30) == 0:
            online_refresh()
        for mode in MODES:
            text = _js("(window.astroid_top[%s] || '')" % json.dumps(mode))
            if text:
                _js("window.astroid_top[%s] = ''" % json.dumps(mode))
                recs = []
                for row in json.loads(text):
                    recs.append({"score": int(row.get("score", 0)), "date": str(row.get("created_at", ""))[:10],
                                 "ship": row.get("ship") or "", "level": int(row.get("level") or 0),
                                 "time": int(row.get("play_time") or 0), "player": row.get("player") or ""})
                rankings[mode] = recs[:RANK_SIZE]
    except Exception:
        pass  # 인터넷이 안 되거나 응답이 이상해도 게임은 계속한다


def save_best(score, level=0, seconds=0):
    """게임 한 판의 결과를 현재 모드의 순위표(1~10위)에 넣고 파일에 저장한다 (점수, 오늘 날짜, 고른 전투기, 레벨, 플레이 시간, 이름).
    점수가 xxxx.5처럼 .5로 끝나면 기록할 때는 0.5를 뺀 점수로 적는다 (화면에 보이는 점수는 그대로).
    10위 안에 들지 못하면 기록하지 않는다."""
    if score != int(score):
        score -= 0.5
    score = int(score)
    if ONLINE:  # 공용 순위표: 서버에 보낸다 (순위 판단과 저장은 서버 쪽 표가 한다)
        if score > 0:
            online_post(score, level, seconds)
        return
    ranks = rankings[game_mode]
    if score <= 0 or (len(ranks) >= RANK_SIZE and score <= ranks[-1]["score"]):
        return
    ranks.append({"score": score, "date": datetime.date.today().isoformat(), "ship": SHIP_NAMES[selected_ship],
                  "level": level, "time": int(seconds), "player": player_name})
    ranks.sort(key=lambda r: -r["score"])  # 같은 점수는 먼저 낸 기록이 위
    del ranks[RANK_SIZE:]
    try:
        write_saved_text(json.dumps(rankings, ensure_ascii=False))
    except Exception:
        pass  # 저장하지 못해도 게임은 계속한다 (브라우저가 저장소를 막아 둔 경우 등)


PLAYER_MASKS = [pygame.mask.from_surface(sp, 60) if sp else None for sp in PLAYER_SPRITES]  # 내 비행기 그림의 모양(투명한 곳은 빼고)
_bullet_surf = pygame.Surface((ENEMY_BULLET_RADIUS * 2, ENEMY_BULLET_RADIUS * 2), pygame.SRCALPHA)
pygame.draw.circle(_bullet_surf, (255, 255, 255, 255), (ENEMY_BULLET_RADIUS, ENEMY_BULLET_RADIUS), ENEMY_BULLET_RADIUS)
ENEMY_BULLET_MASK = pygame.mask.from_surface(_bullet_surf)  # 적 총알(원)의 모양


def enemy_bullet_hits_player(eb, player):
    """적 총알 eb가 내 비행기 그림에 닿았는가. 화면에 보이는 그림 모양 그대로(날개, 꼬리까지) 겹치면 맞는다.
    빠른 총알이 한 프레임에 건너뛰지 않게 이번 프레임에 지나온 길을 따라 여러 점을 본다. 그림이 없으면 직사각형으로 본다."""
    mask = PLAYER_MASKS[selected_ship]
    r = ENEMY_BULLET_RADIUS
    if mask is None:
        for k in range(4):
            pos = eb[0] - eb[1] * (k / 3)
            if abs(pos.x - player.pos.x) < PLAYER_HIT_W + r and abs(pos.y - player.pos.y) < PLAYER_HIT_H + r:
                return True
        return False
    left, top = PLAYER_SPRITES[selected_ship].get_rect(center=player.pos).topleft  # 그림이 그려지는 자리
    for k in range(4):
        pos = eb[0] - eb[1] * (k / 3)
        if mask.overlap(ENEMY_BULLET_MASK, (int(pos.x - r - left), int(pos.y - r - top))):
            return True
    return False


def bullet_hits(en, b):
    """내 총알 b가 적 en의 그림에 맞았는가. 그림이 옆으로 넓어서(날개) 원이 아니라 그림 크기의 직사각형으로 판정한다."""
    return (abs(en.pos.x - b[0].x) < ENEMY_SPRITE_SIZE * 0.5 + b[1]
            and abs(en.pos.y - b[0].y) < ENEMY_SPRITE_SIZE * 0.45 + b[1])


def fmt_score(x):
    """점수 표시: 정수면 그대로, 22.5처럼 소수가 있으면 소수 첫째 자리까지."""
    return str(int(x)) if x == int(x) else f"{x:.1f}"


def kill_points(en):
    """적 en을 무찔렀을 때 얻는 점수. 난이도의 kill_score(Easy 15, Normal·Hard 10)이고, 노란 적은 그 1.5배(22.5는 소수 그대로)."""
    base = MODES[game_mode]["kill_score"]
    if not en.yellow:
        return base
    v = base * YELLOW_SCORE_MULT
    return int(v) if v == int(v) else v


def move_item(it, player):
    """아이템 한 개를 한 프레임 움직인다. 아이템은 [위치, 종류, 속도, 끌리는 중인가].
    평소에는 천천히 떨어지다가 내 주변(MAGNET_RADIUS)에 들어오면 자석에 붙듯 끌리기 시작한다.
    한 번 끌리기 시작한 아이템은 내가 멀리 도망가도 거리와 상관없이 계속 따라와서 결국 붙는다
    (끌리는 속도의 상한 MAGNET_MAX_SPEED가 내 이동 속도 상한보다 빨라서 놓치지 않는다)."""
    while len(it) < 4:
        it.append(pygame.Vector2(0, 0) if len(it) == 2 else False)  # it[2]: 끌릴 때의 속도, it[3]: 끌리는 중인가
    vel = it[2]
    to_player = player.pos - it[0]
    dist = to_player.length()
    if not it[3] and 0 < dist < MAGNET_RADIUS:
        it[3] = True  # 이제부터 계속 따라온다
    if it[3] and dist > 0:
        pull = max(1.0, min(2.0, 2 - dist / MAGNET_RADIUS))  # 가까울수록 세게(최대 2배), 멀어도 최소 1배
        vel += to_player.normalize() * MAGNET_ACCEL * pull
        if vel.length() > MAGNET_MAX_SPEED:
            vel.scale_to_length(MAGNET_MAX_SPEED)
        it[0] += vel
    elif not it[3]:
        it[0].y += 2  # 끌리기 전에는 천천히 떨어진다


def add_fx(fx, pos, radius, life, kind="fire"):
    """폭발 그림을 하나 더한다 (피해는 없고 보기만 하는 효과). kind: "fire"는 그려 만든 불덩이, "boom"은 폭발 이미지."""
    fx.append([pygame.Vector2(pos), 0, life, radius, kind])


def explode_enemy(en, particles, fx):
    """적 전투기가 쓰러질 때의 큰 폭발: 불꽃 + 사방으로 튀는 파편."""
    add_fx(fx, en.pos, 46, 26, "boom" if EXPLOSION_SPRITE else "fire")
    for _ in range(18):
        a = random.uniform(0, math.tau)
        s = random.uniform(1.5, 6)
        particles.append([en.pos.copy(), pygame.Vector2(math.cos(a), math.sin(a)) * s, 30])


def draw_fx(fx):
    """폭발 그림: 중심의 흰 섬광, 주황·노랑 불덩이, 퍼져 나가는 고리가 점점 커지며 사라진다."""
    for pos, age, life, r, kind in fx:
        t = age / life  # 0 → 1
        if kind == "boom":  # 폭발 이미지: 빠르게 커지며 점점 투명해진다 (픽셀 그림이라 확대는 각진 채로)
            height = max(2, int(r * 2.6 * (0.55 + 0.65 * t ** 0.5)))
            width = max(2, int(height * EXPLOSION_SPRITE.get_width() / EXPLOSION_SPRITE.get_height()))
            img = pygame.transform.scale(EXPLOSION_SPRITE, (width, height))
            img.set_alpha(int(255 * (1 - t) ** 0.7))
            screen.blit(img, img.get_rect(center=pos))
            continue
        a = int(255 * (1 - t) ** 0.6)  # 끝까지 또렷하다가 빠르게 사라진다
        size = int(r * 3.4)
        layer = pygame.Surface((size, size), pygame.SRCALPHA)
        c = (size // 2, size // 2)
        pygame.draw.circle(layer, (255, 90, 20, int(a * 0.9)), c, max(1, int(r * (0.4 + 0.9 * t))))   # 바깥 불꽃(주황빨강)
        pygame.draw.circle(layer, (255, 170, 40, a), c, max(1, int(r * (0.3 + 0.6 * t))))              # 안쪽 불덩이(주황)
        pygame.draw.circle(layer, (255, 235, 120, a), c, max(1, int(r * (0.15 + 0.3 * t))))            # 속(노랑)
        if t < 0.45:  # 첫 섬광: 흰색에서 노란빛으로 변하며 작아진다 (투명도로 줄이면 회색으로 보여서 색으로 줄인다)
            k = t / 0.45
            pygame.draw.circle(layer, (255, 255 - int(70 * k), 255 - int(190 * k), a), c, max(1, int(r * 0.55 * (1 - t))))
        pygame.draw.circle(layer, (255, 220, 120, int(a * 0.8)), c, max(2, int(r * (0.55 + 1.0 * t))), 3)  # 퍼지는 고리
        screen.blit(layer, (pos.x - size / 2, pos.y - size / 2))


def draw_bomb_icon(center, rainbow=False, r=11, surf=None):
    """폭탄 아이콘: 검은 폭탄(B) 또는 무지개 폭탄(S) 이미지. center는 폭탄 몸통의 중심, r은 몸통 반지름.
    이미지가 없으면 도형으로 대신 그린다."""
    surf = screen if surf is None else surf
    cx, cy = center
    icon = item_icon("bomb_rainbow" if rainbow else "bomb", int(r * 3.2))
    if icon:  # 이미지에서 몸통 중심은 가로 46%, 세로 65% 지점 (심지와 불꽃이 위쪽에 있다)
        surf.blit(icon, (cx - icon.get_width() * 0.46, cy - icon.get_height() * 0.65))
        return
    for dy in range(-r, r + 1):
        hw = int(math.sqrt(r * r - dy * dy))
        color = RAINBOW[(dy + r) * len(RAINBOW) // (2 * r + 1)] if rainbow else (50, 50, 62)
        pygame.draw.line(surf, color, (cx - hw, cy + dy), (cx + hw, cy + dy))
    pygame.draw.circle(surf, (220, 220, 230), center, r, 2)
    pygame.draw.line(surf, (200, 170, 120), (cx + 5, cy - r + 2), (cx + 11, cy - r - 5), 2)
    pygame.draw.circle(surf, (255, 200, 60), (cx + 12, cy - r - 6), 3)


def draw_coin_icon(center, r=11, surf=None):
    surf = screen if surf is None else surf
    pygame.draw.circle(surf, (255, 220, 70), center, r)
    pygame.draw.circle(surf, (140, 100, 10), center, r, 2)
    pygame.draw.circle(surf, (200, 150, 20), center, r - 5, 2)


_icon_cache = {}


def item_icon(name, size):
    """상점 물건 그림(assets/item_{name}.png)을 가장 긴 변이 size(px)가 되게 돌려준다. 파일이 없으면 None."""
    key = (name, size)
    if key not in _icon_cache:
        _icon_cache[key] = load_sprite(f"item_{name}.png", size)
    return _icon_cache[key]


def draw_change_icon(center, r=10, surf=None, color=(190, 225, 255)):
    """Change Ticket 그림: 노란 티켓 이미지. 이미지가 없으면 한 바퀴 도는 화살표로 대신 그린다."""
    surf = screen if surf is None else surf
    icon = item_icon("change", int(r * 3))
    if icon:
        surf.blit(icon, icon.get_rect(center=center))
        return
    rect = pygame.Rect(0, 0, 2 * r, 2 * r)
    rect.center = center
    pygame.draw.arc(surf, color, rect, 0.7, 5.6, max(2, r // 4))
    ax, ay = center[0] + r * math.cos(0.7), center[1] - r * math.sin(0.7)  # 호의 끝에 화살촉
    pygame.draw.polygon(surf, color, [(ax + r * 0.55, ay + r * 0.15), (ax - r * 0.25, ay - r * 0.7), (ax - r * 0.35, ay + r * 0.45)])


def render_hearts(fnt, text, color):
    """글자 ♥가 들어간 문구를 그린다. 글꼴에 ♥가 없으면(웹 기본 글꼴) 모양을 직접 그려 넣는다."""
    if GLYPHS_OK or "♥" not in text:
        return fnt.render(text, True, color)
    h = fnt.get_height()
    rest = text.replace("♥", "", 1).strip()
    tail = fnt.render(rest, True, color) if rest else None
    out = pygame.Surface((h + (tail.get_width() + 6 if tail else 0), h), pygame.SRCALPHA)
    r = h * 0.22
    cx, cy = h / 2, h * 0.42
    pygame.draw.circle(out, color, (cx - r, cy), r)
    pygame.draw.circle(out, color, (cx + r, cy), r)
    pygame.draw.polygon(out, color, [(cx - r * 1.95, cy + r * 0.3), (cx + r * 1.95, cy + r * 0.3), (cx, cy + r * 3.1)])
    if tail:
        out.blit(tail, (h + 6, 0))
    return out


def draw_hud(surf, score, level, player):
    """게임 화면의 점수/체력/코인/폭탄 표시. 타이틀에서 게임 화면으로 넘어갈 때도 같은 걸 쓴다."""
    surf.blit(font.render(f"Score {fmt_score(score)}   Level {level}   Missiles {player.power}", True, (230, 230, 240)), (12, 10))
    x = W - 12  # 하트는 오른쪽 끝에서부터 그린다. 최대 하트까지 칸을 보여주고, 잃은 칸은 어둡게 둔다
    for i in range(player.max_hp - 1, -1, -1):
        heart = render_hearts(font, "♥", (255, 100, 120) if i < player.hp else (70, 50, 75))
        x -= heart.get_width() + 4
        surf.blit(heart, (x, 10))
    draw_coin_icon((W - 138, 54), surf=surf)
    surf.blit(font.render(f"{player.coins}", True, (255, 220, 70)), (W - 118, 41))
    draw_bomb_icon((24, 62), surf=surf)
    surf.blit(font.render(f"× {player.b_count}", True, (255, 210, 120)), (44, 49))
    y = 100
    if player.has_s:
        draw_bomb_icon((24, y), rainbow=True, surf=surf)
        surf.blit(font.render("Hold Right Click!", True, (180, 220, 255)), (44, y - 13))
        y += 36
    if player.rerolls:  # Change Ticket을 가지고 있으면 개수 표시 (상점에서 사용)
        draw_change_icon((24, y), 10, surf=surf)
        surf.blit(font.render(f"Change × {player.rerolls}", True, (190, 225, 255)), (44, y - 13))


class Player:
    radius = 14

    def __init__(self):
        self.pos = pygame.Vector2(W / 2, H - 80)
        attack, hp, speed = SHIP_STATS[selected_ship]  # 고른 비행기의 능력치
        self.speed = 2 + speed          # 이동 속도(px/프레임)
        self.fire_delay = 16 - 2 * attack  # 발사 간격(프레임). 공격이 높을수록 빨리 쏜다
        self.cooldown = 0
        self.hp = hp
        self.max_hp = hp  # 그 전투기의 최대 하트. R 아이템은 여기까지만 채워주고, 상점에서만 늘릴 수 있다
        self.invuln = 0
        self.power = START_POWER
        self.has_s = False
        self.b_count = B_START
        self.coins = 0
        self.rerolls = 0  # Change Ticket 개수 (상점 물건을 바꿀 수 있는 횟수)

    def update(self, keys):
        d = pygame.Vector2(
            (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a]),
            (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w]),
        )
        if d.length_squared():
            self.pos += d.normalize() * self.speed
        self.pos.x = max(self.radius, min(W - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(H - self.radius, self.pos.y))
        self.cooldown = max(0, self.cooldown - 1)
        self.invuln = max(0, self.invuln - 1)

    def draw(self):
        if self.invuln and (self.invuln // 4) % 2:
            return
        sprite = PLAYER_SPRITES[selected_ship]
        if sprite:
            screen.blit(sprite, sprite.get_rect(center=self.pos))
            return
        x, y = self.pos
        pygame.draw.polygon(screen, (80, 200, 255), [(x, y - 18), (x - 14, y + 14), (x + 14, y + 14)])


class Enemy:
    def __init__(self, level, green=False, yellow=False):
        self.green = green
        self.yellow = yellow
        self.radius = 16
        self.pos = pygame.Vector2(random.randint(30, W - 30), -20)
        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(1.2, 2.2 + level * 0.2))
        self.hp = 1 + level // 4
        if yellow:  # 빠르고 단단하며, 빠른 총알을 쏜다
            self.vel = pygame.Vector2(random.choice((-1, 1)) * random.uniform(1.5, 2.5), random.uniform(2.5, 3.5))
            self.hp = 2 + level // 4
        m = MODES[game_mode]  # 난이도에 따라 속도와 체력이 달라진다
        self.vel *= m["enemy_speed"]
        self.hp += m["enemy_hp_bonus"]
        self.shoot = random.randint(60, 150)

    def update(self):
        self.pos += self.vel
        if self.pos.x < 20 or self.pos.x > W - 20:
            self.vel.x *= -1
        self.shoot -= 1

    def draw(self, alpha=1.0):
        kind = "yellow" if self.yellow else "green" if self.green else "red"
        sprite = ENEMY_SPRITES[kind]
        if sprite:
            if alpha < 1:
                sprite = sprite.copy()
                sprite.set_alpha(int(255 * alpha))
            screen.blit(sprite, sprite.get_rect(center=self.pos))
            return
        fill, edge = {
            "yellow": ((255, 225, 60), (140, 110, 10)),
            "green": ((70, 210, 90), (20, 90, 30)),
            "red": ((255, 90, 90), (120, 20, 20)),
        }[kind]
        pygame.draw.circle(screen, fade_color(fill, alpha), self.pos, self.radius)
        pygame.draw.circle(screen, fade_color(edge, alpha), self.pos, self.radius, 3)


def shop_available(kind, player):
    """지금 살 수 있는 물건인가 (이미 최대인 것은 살 수 없다)."""
    return not (
        (kind == "heart" and player.max_hp >= HP_CAP)
        or (kind == "heal" and player.hp >= player.max_hp)
        or (kind == "power" and player.power >= MAX_POWER)
        or (kind == "speed" and player.speed >= MAX_SPEED)
        or (kind == "rapid" and player.fire_delay <= MIN_FIRE_DELAY)
        or (kind == "rainbow" and player.has_s)
    )


def roll_shop(player):
    """보너스 라운드에 나올 물건 SHOP_SLOTS개를 가중치 확률로 뽑는다. 살 수 있는 물건을 먼저 뽑고, 모자라면 나머지로 채운다."""
    pool = [it for it in SHOP_POOL if shop_available(it[2], player)]
    rest = [it for it in SHOP_POOL if it not in pool]
    chosen = []
    while len(chosen) < SHOP_SLOTS and pool:
        it = random.choices(pool, weights=[x[3] for x in pool])[0]
        chosen.append(it)
        pool.remove(it)
    chosen += rest[:SHOP_SLOTS - len(chosen)]
    return [(name, price, kind) for name, price, kind, _ in chosen]


def reroll_shop(player, current):
    """Change 버튼: 지금과 다른 물건 구성으로 다시 뽑는다 (여러 번 해도 같게 나오면 마지막 결과를 쓴다)."""
    old = {kind for _, _, kind in current}
    for _ in range(10):
        offers = roll_shop(player)
        if {kind for _, _, kind in offers} != old:
            break
    return offers


def drop_items(en, player, enemy_count, items):
    """적 en을 처치했을 때 떨어뜨릴 아이템을 items에 추가한다 (총알로 잡든 폭탄으로 잡든 같다)."""
    if en.yellow:  # 노란 적은 코인만 떨어뜨린다
        if random.random() < YELLOW_COIN_DROP_RATE:
            items.append([en.pos.copy(), "C"])
        return
    p_rate, r_rate = GREEN_DROP_RATES if en.green else RED_DROP_RATES
    drop_mult = MODES[game_mode]["drop_mult"]  # 난이도별 아이템 드롭 배율 (Easy는 더 잘 나오고 Hard는 덜 나온다)
    p_rate, r_rate = p_rate * drop_mult, r_rate * drop_mult
    s_rate = 0.0  # S는 적 미사일이 S_UNLOCK_COUNT개 이상이고 아직 S가 없을 때만 나온다
    if enemy_count >= S_UNLOCK_COUNT and not player.has_s:
        s_rate = S_DROP_RATE if enemy_count == S_UNLOCK_COUNT else S_LATE_DROP_RATE
        if player.b_count > 0:  # B가 있어도 나오지만 확률은 낮아진다
            s_rate *= S_WITH_B_FACTOR
    roll = random.random()
    if roll < p_rate:  # 미사일이 최대여도 P는 떨어진다 (그때 먹은 P는 보너스 점수로 센다)
        items.append([en.pos.copy(), "P"])
    elif player.power >= START_POWER + HEAL_UNLOCK_PICKUPS and roll < p_rate + r_rate:
        items.append([en.pos.copy(), "R"])
    elif roll < p_rate + r_rate + s_rate:
        items.append([en.pos.copy(), "S"])
    if random.random() < B_DROP_RATE * drop_mult:
        items.append([en.pos.copy() + (0, 14), "B"])
    if random.random() < COIN_DROP_RATE:
        items.append([en.pos.copy() + (-14, 0), "C"])


def draw_shop_icon(kind, cx, cy):
    """상점 카드에 그리는 물건 그림."""
    if kind in ("heart", "heal"):
        heart = item_icon("heart", 72)
        if heart:
            screen.blit(heart, heart.get_rect(center=(cx, cy)))
        else:
            t = render_hearts(big, "♥", (255, 100, 120))
            screen.blit(t, t.get_rect(center=(cx, cy)))
        if kind == "heal":
            t = font.render("+", True, (255, 255, 255))
            screen.blit(t, t.get_rect(center=(cx + 36, cy - 28)))
    elif kind == "b":
        draw_bomb_icon((cx - 4, cy + 14), r=26)
    elif kind == "rainbow":
        draw_bomb_icon((cx - 4, cy + 14), rainbow=True, r=26)
    elif kind == "power":
        pygame.draw.ellipse(screen, (255, 240, 120), (cx - 22, cy - 28, 18, 56))
        pygame.draw.ellipse(screen, (255, 240, 120), (cx + 4, cy - 28, 18, 56))
    elif kind == "shield":
        shield = item_icon("shield", 72)
        if shield:
            screen.blit(shield, shield.get_rect(center=(cx, cy)))
        else:
            pygame.draw.circle(screen, (90, 200, 255), (cx, cy), 28, 4)
            pygame.draw.circle(screen, (60, 130, 200), (cx, cy), 18, 2)
    elif kind == "speed":
        for dx in (-14, 8):
            pygame.draw.lines(screen, (90, 210, 255), False, [(cx + dx, cy - 27), (cx + dx + 18, cy), (cx + dx, cy + 20)], 6)
    elif kind == "rapid":
        for i, dx in enumerate((-24, 0, 24)):
            pygame.draw.ellipse(screen, (255, 240, 120), (cx + dx - 6, cy - 24 + (i % 2) * 14, 12, 34))
    elif kind == "change":
        draw_change_icon((cx, cy), 26)


ITEM_DESC = {  # 구매 확인 화면에 보여줄 물건 설명 (영어)
    "heart": f"Adds 1 to your maximum hearts and restores 1 HP right away. The upper limit is {HP_CAP} hearts.",
    "heal": "Restores your HP up to your current maximum hearts.",
    "b": f"Gives you 1 Bomb B. Right-click to blast the enemies and bullets near you (radius {B_RADIUS}).",
    "power": f"Adds 1 missile to every shot you fire (up to {MAX_POWER} missiles).",
    "shield": f"Makes you invincible for {SHIELD_TIME // FPS} seconds. Bullets, bombs and collisions cannot hurt you.",
    "speed": f"Your fighter moves 1 step faster (up to speed {MAX_SPEED}).",
    "rapid": f"Fires faster: the delay between shots drops by 1 frame (minimum {MIN_FIRE_DELAY}).",
    "rainbow": f"Gives you 1 Rainbow Bomb S. Hold the right mouse button for {S_HOLD_FRAMES / FPS:g} seconds to unleash a huge blast (radius {BLAST_RADIUS}).",
    "change": "A ticket that changes the items in this shop. Press the Change button (or C) to get a new set of items.",
}


def wrap_text(text, fnt, width):
    """공백 기준으로 줄을 바꿔서 각 줄이 width(px)를 넘지 않게 나눈다."""
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if fnt.size(trial)[0] <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_shop_icon_big(kind, cx, cy):
    """구매 확인 화면의 큰 물건 그림."""
    global screen
    if kind in ("heart", "heal"):
        heart = item_icon("heart", 150)
        if heart:
            screen.blit(heart, heart.get_rect(center=(cx, cy)))
        if kind == "heal":
            t = big.render("+", True, (255, 255, 255))
            screen.blit(t, t.get_rect(center=(cx + 78, cy - 55)))
    elif kind == "shield" and item_icon("shield", 150):
        shield = item_icon("shield", 150)
        screen.blit(shield, shield.get_rect(center=(cx, cy)))
    elif kind == "change":
        draw_change_icon((cx, cy), 52)
    elif kind in ("b", "rainbow"):
        draw_bomb_icon((cx - 6, cy + 30), rainbow=(kind == "rainbow"), r=48)
    else:  # 도형으로 그리는 물건은 작게 그려서 크게 늘린다
        layer = pygame.Surface((110, 110), pygame.SRCALPHA)
        saved, screen = screen, layer
        try:
            draw_shop_icon(kind, 55, 55)
        finally:
            screen = saved
        bigger = pygame.transform.smoothscale(layer, (190, 190))
        screen.blit(bigger, bigger.get_rect(center=(cx, cy)))


def draw_confirm_screen(offer, player, msg):
    """상점에서 물건을 고르면 나오는 구매 확인 화면: 질문, 큰 그림, 설명, 가격, Back / Buy 버튼."""
    name, price, kind = offer
    screen.fill((10, 10, 30))
    t = big.render(f"Buy {name}?", True, (255, 220, 70))
    screen.blit(t, t.get_rect(center=(W / 2, 65)))
    draw_shop_icon_big(kind, W / 2, 190)
    for i, line in enumerate(wrap_text(ITEM_DESC[kind], font, 620)):
        t = font.render(line, True, (225, 228, 240))
        screen.blit(t, t.get_rect(center=(W / 2, 305 + i * 30)))
    enough = player.coins >= price
    draw_coin_icon((W / 2 - 150, 425), r=11)
    t = font.render(f"{price}", True, (255, 220, 70) if enough else (255, 130, 130))
    screen.blit(t, t.get_rect(midleft=(W / 2 - 132, 425)))
    t = font.render(f"You have {player.coins}", True, (190, 195, 215))
    screen.blit(t, t.get_rect(midleft=(W / 2 - 30, 425)))
    if kind in ("heart", "heal"):
        t = render_hearts(font, f"♥ {player.hp}/{player.max_hp}", (255, 130, 150))
        screen.blit(t, t.get_rect(midleft=(W / 2 + 135, 425)))
    if msg:
        t = font.render(msg, True, (255, 170, 170))
        screen.blit(t, t.get_rect(center=(W / 2, 480)))
    mouse = pygame.mouse.get_pos()
    mouse = (mouse[0] / scale, mouse[1] / scale)
    for rect, text, edge in ((CONFIRM_BACK, "Back", (150, 190, 255)), (CONFIRM_BUY, "Buy", (255, 220, 70))):
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (70, 90, 150) if hover else (40, 50, 90), rect, border_radius=10)
        pygame.draw.rect(screen, edge, rect, 2, border_radius=10)
        t = font.render(text, True, (240, 245, 255))
        screen.blit(t, t.get_rect(center=rect.center))


STAT_COLORS = [(255, 150, 60), (255, 100, 120), (90, 210, 255)]  # 공격, 체력, 스피드 막대 색


def draw_gauge(surf, x, y, w, h, value, color, amt=1.0):
    """능력치(0~5)만큼 채워진 게이지. 왼쪽은 어둡고 오른쪽은 밝은 그라데이션에 윗부분 하이라이트와 5등분 눈금이 있다.
    amt(0~1)는 채워지는 애니메이션 진행도."""
    r = h // 2
    pygame.draw.rect(surf, (28, 32, 60), (x, y, w, h), border_radius=r)  # 빈 틀
    fill_w = int(w * value / 5 * amt)
    if fill_w > 1:
        fill = pygame.Surface((fill_w, h), pygame.SRCALPHA)
        for px in range(fill_w):
            f = 0.5 + 0.5 * px / max(1, fill_w - 1)
            pygame.draw.line(fill, tuple(int(c * f) for c in color), (px, 0), (px, h))
        pygame.draw.line(fill, tuple(min(255, c + 90) for c in color), (r, 2), (max(r, fill_w - r), 2))  # 윗부분 하이라이트
        mask = pygame.Surface((fill_w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, fill_w, h), border_radius=r)
        fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)  # 둥근 모서리로 자르기
        surf.blit(fill, (x, y))
    for k in range(1, 5):  # 5등분 눈금
        tx = x + w * k // 5
        pygame.draw.line(surf, (10, 10, 30), (tx, y + 1), (tx, y + h - 2))
    pygame.draw.rect(surf, (95, 100, 150), (x, y, w, h), 1, border_radius=r)  # 테두리


def draw_hover_stats(ship, cx, top, amt):
    """마우스를 올린 전투기 아래에 공격/체력/스피드를 게이지로 보여준다. amt(0~1)로 서서히 나타나고 게이지가 차오른다."""
    layer = pygame.Surface((200, 84), pygame.SRCALPHA)
    for n, (label, color) in enumerate(zip(("Attack", "HP", "Speed"), STAT_COLORS)):
        y = n * 28
        layer.blit(small_font.render(label, True, (225, 228, 240)), (0, y))
        draw_gauge(layer, 62, y + 3, 128, 14, SHIP_STATS[ship][n], color, amt)
    layer.set_alpha(int(255 * min(1.0, amt * 1.5)))
    screen.blit(layer, (cx - 100, top))


def draw_stats_screen(ship, now):
    """고른 비행기 소개 화면: 이름(Fighter N)과 전투기, 아래에 Back / Select 버튼이 있다."""
    t = big.render(f"Fighter {ship + 1}", True, (120, 210, 255))
    title_rect = t.get_rect(center=STATS_TITLE.center)
    screen.blit(t, title_rect)
    if start_with_s:  # 숨겨진 기능이 켜졌다는 표시: 이름 오른쪽에 무지개 폭탄 아이콘
        draw_bomb_icon((title_rect.right + 34, title_rect.centery + 8), rainbow=True, r=13)

    sprite = TITLE_SPRITES[ship]
    if sprite:
        big_ship = pygame.transform.smoothscale(sprite, (int(sprite.get_width() * 1.9), int(sprite.get_height() * 1.9)))
        screen.blit(big_ship, big_ship.get_rect(center=(W / 2, 290 + math.sin(now / 300) * 6)))

    mouse = pygame.mouse.get_pos()
    mouse = (mouse[0] / scale, mouse[1] / scale)
    for rect, text in ((STATS_BACK, "Back"), (STATS_SELECT, "Select")):
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (70, 90, 150) if hover else (40, 50, 90), rect, border_radius=10)
        pygame.draw.rect(screen, (255, 220, 70) if text == "Select" else (150, 190, 255), rect, 2, border_radius=10)
        t = font.render(text, True, (240, 245, 255))
        screen.blit(t, t.get_rect(center=rect.center))


def draw_best_box():
    """최고 점수 칸(My best Score). 첫 화면과 전투기 고르기 화면에 똑같이 나오고, 누르면 기록 화면이 열린다."""
    pygame.draw.rect(screen, (24, 28, 56), BEST_BOX, border_radius=8)
    pygame.draw.rect(screen, (255, 220, 70), BEST_BOX, 2, border_radius=8)
    t = font.render(f"{'Top' if ONLINE else 'My best'} Score  {fmt_score(top_record(game_mode)['score'])}", True, (255, 240, 170))
    screen.blit(t, t.get_rect(center=BEST_BOX.center))


def fit_text(fnt, text, max_w):
    """글자가 max_w(px)를 넘으면 끝을 잘라서 "…"을 붙인다."""
    if fnt.size(text)[0] <= max_w:
        return text
    while text and fnt.size(text + ELLIPSIS)[0] > max_w:
        text = text[:-1]
    return text + ELLIPSIS


def format_time(seconds):
    return f"{seconds // 60}:{seconds % 60:02d}"


async def records_screen():
    """모드별 최고 기록 화면: 점수, 전투기, 레벨, 플레이 시간, 날짜. 아무 키나 Back 버튼으로 닫는다."""
    stars = [(random.randint(0, W), random.randint(0, H), random.randint(1, 3)) for _ in range(60)]
    cols = {"mode": 40, "score": 178, "player": 292, "ship": 402, "level": 477, "time": 542, "date": 668}  # 각 칸의 x (mode만 왼쪽 맞춤)
    cards = [pygame.Rect(30, 215 + i * 90 - 36, 740, 72) for i in range(len(MODES))]  # 모드별 1위 줄 (누르면 그 모드의 1~10위)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                return
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse = (e.pos[0] / scale, e.pos[1] / scale)
                if RECORDS_BACK.collidepoint(mouse):
                    return
                for name, card in zip(MODES, cards):
                    if card.collidepoint(mouse):  # 모드 줄을 누르면 그 모드의 1~10위
                        await ranking_screen(name)

        now = pygame.time.get_ticks()
        screen.fill((10, 10, 30))
        for x, y, s in stars:
            pygame.draw.circle(screen, (90, 90, 130), (x, (y + now * s // 40) % H), s)
        t = big.render("Best Records", True, (255, 220, 70))
        screen.blit(t, t.get_rect(center=(W / 2, 70)))

        for key, label in (("mode", "Mode"), ("score", "Score"), ("player", "Player"), ("ship", "Fighter"), ("level", "Level"), ("time", "Time"), ("date", "Date")):
            t = small_font.render(label, True, (150, 155, 185))
            screen.blit(t, (cols[key], 140) if key == "mode" else t.get_rect(center=(cols[key], 150)))
        for i, name in enumerate(MODES):
            y = 215 + i * 90
            rec = top_record(name)
            card = cards[i]
            color = MODE_COLORS[name]
            hovered = card.collidepoint(pygame.mouse.get_pos()[0] / scale, pygame.mouse.get_pos()[1] / scale)
            pygame.draw.rect(screen, tuple(int(c * (0.28 if hovered else 0.18)) for c in color), card, border_radius=10)
            pygame.draw.rect(screen, color if name == game_mode else tuple(int(c * 0.55) for c in color), card, 3 if name == game_mode else 2, border_radius=10)
            screen.blit(font.render(name, True, color), (cols["mode"], y - 14))
            has = rec["score"] > 0  # 기록이 없으면 칸을 "-"로 둔다
            cells = {
                "score": (mid_font, fmt_score(rec["score"])),
                "player": (small_font, rec["player"] if has and rec["player"] else "-"),
                "ship": (font, rec["ship"] if has and rec["ship"] else "-"),
                "level": (font, f"Lv {rec['level']}" if has and rec["level"] else "-"),
                "time": (font, format_time(rec["time"]) if has and rec["time"] else "-"),
                "date": (font, rec["date"] if has and rec["date"] else "-"),
            }
            for key, (fnt, text) in cells.items():
                if key == "player":
                    text = fit_text(fnt, text, 100)  # 이름이 길면 칸을 넘지 않게 줄인다
                t = fnt.render(text, True, (255, 240, 170) if key == "score" else (225, 228, 240))
                screen.blit(t, t.get_rect(center=(cols[key], y)))

        t = small_font.render("Click a mode to see its Top 10", True, (150, 155, 185))
        screen.blit(t, t.get_rect(center=(W / 2, 478)))
        hover = RECORDS_BACK.collidepoint(pygame.mouse.get_pos()[0] / scale, pygame.mouse.get_pos()[1] / scale)
        pygame.draw.rect(screen, (70, 90, 150) if hover else (40, 50, 90), RECORDS_BACK, border_radius=10)
        pygame.draw.rect(screen, (150, 190, 255), RECORDS_BACK, 2, border_radius=10)
        t = font.render("Back", True, (240, 245, 255))
        screen.blit(t, t.get_rect(center=RECORDS_BACK.center))

        window.blit(pygame.transform.smoothscale(screen, window.get_size()), (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        online_tick()
        await asyncio.sleep(0)  # 웹에서 브라우저에 제어를 넘긴다


MEDAL_SIZE = 42


def _medal_shine(surf, img, center, now, strong):
    """메달 위로 비스듬한 빛줄기가 지나가고(메달 모양 안에서만) 모서리에서 별빛이 반짝인다. strong이면 금메달용으로 더 세고 자주."""
    period, sweep = (1500, 0.45) if strong else (2600, 0.35)
    t = (now % period) / period
    w, h = img.get_size()
    key = ("medalmask", id(img))
    if key not in _icon_cache:
        _icon_cache[key] = pygame.mask.from_surface(img, 120).to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    if t < sweep:  # 빛줄기: 왼쪽 아래에서 오른쪽 위로 지나간다
        k = t / sweep
        x = -w * 0.5 + k * w * 2
        band = pygame.Surface((w, h), pygame.SRCALPHA)
        a = 150 if strong else 80
        pygame.draw.polygon(band, (255, 255, 255, a), [(x, h), (x + w * 0.28, h), (x + w * 0.28 + h * 0.6, 0), (x + h * 0.6, 0)])
        band.blit(_icon_cache[key], (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(band, band.get_rect(center=center))
    # 별빛: 빛줄기가 지나간 직후에 오른쪽 위에서 커졌다 작아진다
    u = (t - sweep * 0.8) / 0.25
    if 0 <= u <= 1:
        size = (7 if strong else 5) * math.sin(u * math.pi)
        sx, sy = center[0] + w * 0.30, center[1] - h * 0.30
        col = (255, 252, 220)
        pygame.draw.line(surf, col, (sx - size, sy), (sx + size, sy), 2 if strong else 1)
        pygame.draw.line(surf, col, (sx, sy - size), (sx, sy + size), 2 if strong else 1)


def draw_medal(surf, center, i, now):
    """1~3위 메달 (i = 0 금, 1 은, 2 동). 그림(assets/medal_*.png)을 쓰고, 금메달이 가장 크다. 그림이 없으면 도형으로 그린다."""
    cx, cy = center
    key = ("medal", i)
    if key not in _icon_cache:  # assets/medal_{gold,silver,bronze}.png (셋 다 같은 크기)
        _icon_cache[key] = load_sprite(f"medal_{('gold', 'silver', 'bronze')[i]}.png", MEDAL_SIZE)
    img = _icon_cache[key]
    if img:
        surf.blit(img, img.get_rect(center=(cx, cy)))
        if i == 0:  # 금메달만 번쩍이는 효과 (은·동메달은 그대로)
            _medal_shine(surf, img, (cx, cy), now, strong=True)
        return
    rim, face, shine = [((170, 120, 20), (255, 210, 60), (255, 245, 170)),
                        ((120, 125, 140), (205, 210, 225), (250, 252, 255)),
                        ((120, 70, 30), (205, 130, 70), (240, 190, 140))][i]
    if i == 0:
        pulse = 0.5 + 0.5 * math.sin(now / 250)
        glow = pygame.Surface((80, 80), pygame.SRCALPHA)
        for r, a in ((38, 25), (30, 40), (24, 55)):
            pygame.draw.circle(glow, (255, 220, 90, int(a + 25 * pulse)), (40, 40), r)
        surf.blit(glow, glow.get_rect(center=(cx, cy)))
        r = 16
    else:
        r = 12
    pygame.draw.circle(surf, rim, (cx, cy), r)
    pygame.draw.circle(surf, face, (cx, cy), r - 3)
    pygame.draw.circle(surf, shine, (cx - r // 4, cy - r // 4), max(2, r // 4))
    if i == 0:  # 별 무늬 테두리와 반짝임
        for k in range(8):
            a = k * math.pi / 4 + now / 1500
            pygame.draw.circle(surf, (255, 250, 200), (int(cx + math.cos(a) * (r - 1.5)), int(cy + math.sin(a) * (r - 1.5))), 1)
        for k in range(4):
            a = k * math.pi / 2 + now / 600
            sx, sy = cx + math.cos(a) * (r + 7), cy + math.sin(a) * (r + 7)
            pygame.draw.line(surf, (255, 250, 210), (sx - 3, sy), (sx + 3, sy), 1)
            pygame.draw.line(surf, (255, 250, 210), (sx, sy - 3), (sx, sy + 3), 1)
    t = (font if i == 0 else small_font).render(str(i + 1), True, tuple(c // 2 for c in rim))
    surf.blit(t, t.get_rect(center=(cx, cy + 1)))


async def ranking_screen(mode):
    """한 모드의 1~10위 화면: 순위, 이름, 점수, 전투기, 레벨, 플레이 시간, 날짜. 아무 키나 Back 버튼으로 닫는다."""
    stars = [(random.randint(0, W), random.randint(0, H), random.randint(1, 3)) for _ in range(60)]
    color = MODE_COLORS[mode]
    medal = [(255, 215, 80), (210, 215, 230), (215, 150, 90)]  # 1~3위 색 (금, 은, 동)
    cols = {"rank": 50, "player": 100, "score": 300, "ship": 410, "level": 495, "time": 565, "date": 685}  # 각 칸의 x (player만 왼쪽 맞춤)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                return
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if RECORDS_BACK.collidepoint(e.pos[0] / scale, e.pos[1] / scale):
                    return

        now = pygame.time.get_ticks()
        screen.fill((10, 10, 30))
        for x, y, s in stars:
            pygame.draw.circle(screen, (90, 90, 130), (x, (y + now * s // 40) % H), s)
        t = big.render(f"{mode} Top {RANK_SIZE}", True, color)
        screen.blit(t, t.get_rect(center=(W / 2, 48)))
        for key, label in (("player", "Player"), ("score", "Score"), ("ship", "Fighter"), ("level", "Level"), ("time", "Time"), ("date", "Date")):
            t = small_font.render(label, True, (150, 155, 185))
            screen.blit(t, (cols[key], 100) if key == "player" else t.get_rect(center=(cols[key], 110)))
        rows = rankings[mode]
        for i in range(RANK_SIZE):
            y = 142 + i * 33
            band = pygame.Rect(30, y - 15, 740, 30)
            pygame.draw.rect(screen, tuple(int(c * (0.36 if i % 2 == 0 else 0.22)) for c in color), band, border_radius=6)
            rank_color = medal[i] if i < 3 else (200, 205, 225)
            if i < 3:
                pass  # 메달은 줄무늬와 테두리를 다 그린 뒤 맨 위에 그린다 (아래 줄이 덮지 않게)
            else:  # 4위부터는 숫자를 메달과 같은 세로줄(가운데)에 맞춘다
                t = font.render(str(i + 1), True, rank_color)
                screen.blit(t, t.get_rect(center=(cols["rank"] + 6, y)))
            if i < len(rows):
                rec = rows[i]
                cells = {
                    "player": (fit_text(font, rec["player"] or "-", 170), "left", rank_color if i < 3 else (225, 228, 240)),
                    "score": (fmt_score(rec["score"]), "center", (255, 240, 170)),
                    "ship": (rec["ship"] or "-", "center", (225, 228, 240)),
                    "level": (f"Lv {rec['level']}" if rec["level"] else "-", "center", (225, 228, 240)),
                    "time": (format_time(rec["time"]) if rec["time"] else "-", "center", (225, 228, 240)),
                    "date": (rec["date"] or "-", "center", (225, 228, 240)),
                }
                for key, (text, align, col) in cells.items():
                    t = font.render(text, True, col)
                    pos = t.get_rect(midleft=(cols[key], y)) if align == "left" else t.get_rect(center=(cols[key], y))
                    screen.blit(t, pos)
            else:  # 아직 기록이 없는 순위
                t = font.render("-", True, tuple(int(c * 0.55) for c in color))
                screen.blit(t, t.get_rect(midleft=(cols["player"], y)))

        pygame.draw.rect(screen, tuple(int(c * 0.7) for c in color), pygame.Rect(30, 127, 740, 33 * RANK_SIZE + 3), 2, border_radius=8)  # 순위표 테두리
        for i in range(3):  # 1~3위 메달: 줄무늬와 테두리 위에
            draw_medal(screen, (cols["rank"] + 6, 142 + i * 33), i, now)
        hover = RECORDS_BACK.collidepoint(pygame.mouse.get_pos()[0] / scale, pygame.mouse.get_pos()[1] / scale)
        pygame.draw.rect(screen, tuple(int(c * (0.45 if hover else 0.3)) for c in color), RECORDS_BACK, border_radius=10)
        pygame.draw.rect(screen, color, RECORDS_BACK, 2, border_radius=10)
        t = font.render("Back", True, (240, 245, 255))
        screen.blit(t, t.get_rect(center=RECORDS_BACK.center))

        window.blit(pygame.transform.smoothscale(screen, window.get_size()), (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        online_tick()
        await asyncio.sleep(0)  # 웹에서 브라우저에 제어를 넘긴다


async def name_screen():
    """게임을 켜면 가장 먼저 나오는 화면: 제목과 비행기, 그 아래에 "Player's name", 이름을 입력하는 칸, "Play In Guest Mode" 버튼.
    칸을 클릭하면 이름을 입력할 수 있고(Enter로 확인), 버튼을 누르면 이름 없이(Guest) 시작한다."""
    global player_name
    stars = [(random.randint(0, W), random.randint(0, H), random.randint(1, 3)) for _ in range(60)]
    text = "" if player_name == "Guest" else player_name  # 다시 돌아오면 지난 이름을 채워 둔다
    active = False  # 입력 칸을 클릭해서 입력 중인가
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse = (e.pos[0] / scale, e.pos[1] / scale)
                if GUEST_BUTTON.collidepoint(mouse):
                    player_name = "Guest"
                    pygame.key.stop_text_input()
                    return
                active = NAME_BOX.collidepoint(mouse)
                if active:
                    pygame.key.start_text_input()
                else:
                    pygame.key.stop_text_input()
            elif active and e.type == pygame.TEXTINPUT:  # 글자 입력 (한글 등 IME 입력 포함)
                text = (text + e.text)[:NAME_MAX]
            elif active and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and text.strip():
                    player_name = text.strip()
                    pygame.key.stop_text_input()
                    return
                elif e.key == pygame.K_ESCAPE:
                    active = False
                    pygame.key.stop_text_input()

        now = pygame.time.get_ticks()
        screen.fill((10, 10, 30))
        for x, y, s in stars:
            pygame.draw.circle(screen, (90, 90, 130), (x, (y + now * s // 40) % H), s)
        t = title_font.render(GAME_TITLE, True, (120, 210, 255))
        screen.blit(t, t.get_rect(center=(W / 2, 100)))
        if SPLASH_SPRITE:
            screen.blit(SPLASH_SPRITE, SPLASH_SPRITE.get_rect(center=(W / 2, 250 + math.sin(now / 300) * 6)))

        t = font.render("Player's name", True, (200, 205, 225))
        screen.blit(t, t.get_rect(center=(W / 2, 400)))
        pygame.draw.rect(screen, (24, 28, 56), NAME_BOX, border_radius=8)  # 이름 입력 칸
        pygame.draw.rect(screen, (255, 220, 70) if active else (120, 125, 160), NAME_BOX, 3 if active else 2, border_radius=8)
        if text:
            t = font.render(text, True, (255, 255, 255))
            screen.blit(t, t.get_rect(midleft=(NAME_BOX.x + 16, NAME_BOX.centery)))
            cursor_x = NAME_BOX.x + 16 + t.get_width() + 3
        else:
            t = font.render("Click here and type", True, (110, 115, 145))
            screen.blit(t, t.get_rect(midleft=(NAME_BOX.x + 16, NAME_BOX.centery)))
            cursor_x = NAME_BOX.x + 16
        if active and (now // 500) % 2 == 0:  # 깜빡이는 입력 커서
            pygame.draw.line(screen, (255, 255, 255), (cursor_x, NAME_BOX.y + 10), (cursor_x, NAME_BOX.bottom - 10), 2)
        if active and text:
            t = small_font.render("Press Enter to continue", True, (150, 155, 185))
            screen.blit(t, t.get_rect(center=(W / 2, NAME_BOX.bottom + 18)))

        mouse = pygame.mouse.get_pos()
        hover = GUEST_BUTTON.collidepoint(mouse[0] / scale, mouse[1] / scale)
        pygame.draw.rect(screen, (60, 75, 125) if hover else (40, 50, 90), GUEST_BUTTON, border_radius=10)
        pygame.draw.rect(screen, (150, 190, 255), GUEST_BUTTON, 2, border_radius=10)
        t = font.render("Play In Guest Mode", True, (240, 245, 255))
        screen.blit(t, t.get_rect(center=GUEST_BUTTON.center))

        window.blit(pygame.transform.smoothscale(screen, window.get_size()), (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        online_tick()
        await asyncio.sleep(0)  # 웹에서 브라우저에 제어를 넘긴다


def draw_nav_back():
    """왼쪽 위의 "← Back" 버튼 (난이도 화면, 조작법 화면, 전투기 고르기 화면이 같이 쓴다)."""
    mx, my = pygame.mouse.get_pos()
    hover = SPLASH_BACK.collidepoint(mx / scale, my / scale)
    pygame.draw.rect(screen, (60, 75, 125) if hover else (35, 42, 80), SPLASH_BACK, border_radius=8)
    pygame.draw.rect(screen, (150, 190, 255), SPLASH_BACK, 2, border_radius=8)
    t = small_font.render(ARROW_L + " Back", True, (230, 235, 250))
    screen.blit(t, t.get_rect(center=SPLASH_BACK.center))


# 조작법 화면의 쪽: (제목, [(왼쪽 표시, 한 줄 제목, 설명), ...]). 왼쪽 표시가 "P" 같은 아이템 글자면 색 동그라미, 아니면 키 이름 상자
CONTROL_PAGES = [
    ("Move", [
        ("W A S D", "Move", "Or use the arrow keys"),
        ("Left Click", "Shoot", "Hold it to keep firing"),
        ("Space", "Pause", "Press again to continue"),
    ]),
    ("Items", [
        ("P", "Missile +1", "Shoot more bullets (enemies fire more too)"),
        ("R", "Heal", "Restores 1 heart"),
        ("B", "Bomb", "Right Click: blasts nearby enemies and bullets"),
        ("S", "Rainbow Bomb", "Hold Right Click 0.5s: a huge blast"),
        ("C", "Coin", "Spend coins in the Bonus Round shop"),
    ]),
    ("Good To Know", [
        ("Shop", "Bonus Round", f"Every {BONUS_INTERVAL}s a shop opens to buy upgrades"),
        ("Red", "Red enemies", "The basic ones. They often drop R (heal)"),
        ("Green", "Green enemies", "They throw bombs, so keep away from the blast"),
        ("Yellow", "Yellow enemies", "Fast and tough, but they drop coins"),
    ]),
]
CONTROLS_NEXT = pygame.Rect(W // 2 - 130, 505, 260, 50)
CONTROLS_SKIP = pygame.Rect(W - 104, 38, 92, 34)  # 오른쪽 위: 설명을 건너뛰고 전투기 고르기로
CONTROL_START = [0]  # 조작법 화면을 처음 열 쪽 (전투기 고르기에서 Back으로 오면 마지막 쪽)


async def controls_screen(page=0):
    """전투기를 고르기 전의 조작법 설명 (3쪽). Next / Enter로 다음 쪽, Back / Esc로 이전 쪽.
    첫 쪽에서 Back이면 "back"(난이도 화면으로), 마지막 쪽에서 Next면 None(전투기 고르기로)을 돌려준다."""
    stars = [(random.randint(0, W), random.randint(0, H), random.randint(1, 3)) for _ in range(60)]
    last = len(CONTROL_PAGES) - 1
    while True:
        go = None  # "next" / "prev"
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_RIGHT, pygame.K_d):
                    go = "next"
                elif e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_LEFT, pygame.K_a):
                    go = "prev"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse = (e.pos[0] / scale, e.pos[1] / scale)
                if CONTROLS_SKIP.collidepoint(mouse):
                    return  # 설명 넘기기: 바로 전투기 고르기로
                if CONTROLS_NEXT.collidepoint(mouse):
                    go = "next"
                elif SPLASH_BACK.collidepoint(mouse):
                    go = "prev"
        if go == "next":
            if page == last:
                return
            page += 1
        elif go == "prev":
            if page == 0:
                return "back"
            page -= 1

        now = pygame.time.get_ticks()
        screen.fill((10, 10, 30))
        for x, y, s in stars:
            pygame.draw.circle(screen, (90, 90, 130), (x, (y + now * s // 40) % H), s)
        draw_nav_back()
        mx, my = pygame.mouse.get_pos()
        hover = CONTROLS_SKIP.collidepoint(mx / scale, my / scale)
        pygame.draw.rect(screen, (60, 75, 125) if hover else (35, 42, 80), CONTROLS_SKIP, border_radius=8)
        pygame.draw.rect(screen, (150, 190, 255), CONTROLS_SKIP, 2, border_radius=8)
        t = small_font.render("Skip " + ARROW_R, True, (230, 235, 250))
        screen.blit(t, t.get_rect(center=CONTROLS_SKIP.center))
        heading, rows = CONTROL_PAGES[page]
        t = big.render(heading, True, (120, 210, 255))
        screen.blit(t, t.get_rect(center=(W / 2, 75)))
        for i, (badge, head, desc) in enumerate(rows):
            cy = 160 + i * 70
            panel = pygame.Rect(70, cy - 30, 660, 60)
            pygame.draw.rect(screen, (24, 28, 56), panel, border_radius=10)
            pygame.draw.rect(screen, (60, 70, 120), panel, 2, border_radius=10)
            if len(badge) == 1 and badge in ITEM_COLORS:  # 아이템은 게임 속 모양(색 동그라미 + 글자)으로
                fill, edge = ITEM_COLORS[badge]
                pygame.draw.circle(screen, edge, (130, cy), 22)
                pygame.draw.circle(screen, fill, (130, cy), 19)
                t = font.render(badge, True, edge)
                screen.blit(t, t.get_rect(center=(130, cy)))
            else:  # 키 이름 상자
                t = small_font.render(badge, True, (255, 230, 120))
                box = pygame.Rect(0, 0, max(70, t.get_width() + 24), 34)
                box.center = (130, cy)
                pygame.draw.rect(screen, (40, 46, 90), box, border_radius=8)
                pygame.draw.rect(screen, (255, 220, 70), box, 2, border_radius=8)
                screen.blit(t, t.get_rect(center=box.center))
            screen.blit(font.render(head, True, (235, 238, 250)), (215, cy - 24))
            screen.blit(small_font.render(desc, True, (160, 165, 195)), (215, cy + 4))
        for i in range(len(CONTROL_PAGES)):  # 쪽 표시 점
            pygame.draw.circle(screen, (255, 220, 70) if i == page else (70, 75, 110), (int(W // 2 + (i - last / 2) * 24), 486), 6)
        mx, my = pygame.mouse.get_pos()
        hover = CONTROLS_NEXT.collidepoint(mx / scale, my / scale)
        pygame.draw.rect(screen, (60, 75, 125) if hover else (35, 42, 80), CONTROLS_NEXT, border_radius=10)
        pygame.draw.rect(screen, (150, 190, 255), CONTROLS_NEXT, 2, border_radius=10)
        t = font.render("Choose Fighter" if page == last else "Next", True, (240, 245, 255))
        screen.blit(t, t.get_rect(center=CONTROLS_NEXT.center))

        window.blit(pygame.transform.smoothscale(screen, window.get_size()), (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        online_tick()
        await asyncio.sleep(0)  # 웹에서 브라우저에 제어를 넘긴다


async def splash_screen():
    """게임을 켜면 가장 먼저 나오는 화면: 제목, 큰 일반 비행기(1번), Easy/Normal/Hard 버튼, "Press To Start", 최고 점수.
    버튼(또는 ← →)으로 난이도를 고르고, 그 밖의 아무 키나 클릭을 하면 전투기 고르기 화면으로 간다.
    최고 점수 칸을 누르면 모드별 최고 기록 화면이 열린다. 왼쪽 위의 Back 버튼(또는 Esc)을 누르면 "back"을 돌려줘서 이름 화면으로 돌아간다."""
    global game_mode
    stars = [(random.randint(0, W), random.randint(0, H), random.randint(1, 3)) for _ in range(60)]
    names = list(MODES)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_a):  # 난이도 고르기
                    game_mode = names[max(0, names.index(game_mode) - 1)]
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    game_mode = names[min(len(names) - 1, names.index(game_mode) + 1)]
                elif e.key == pygame.K_ESCAPE:
                    return "back"
                else:
                    return
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse = (e.pos[0] / scale, e.pos[1] / scale)
                clicked = [name for name, r in zip(names, MODE_BUTTONS) if r.collidepoint(mouse)]
                if SPLASH_BACK.collidepoint(mouse):
                    return "back"
                if clicked:  # 버튼을 누르면 그 난이도를 고른다
                    game_mode = clicked[0]
                elif BEST_BOX.collidepoint(mouse):  # 최고 점수 칸을 누르면 기록 화면
                    await records_screen()
                else:
                    return

        now = pygame.time.get_ticks()
        screen.fill((10, 10, 30))
        for x, y, s in stars:
            pygame.draw.circle(screen, (90, 90, 130), (x, (y + now * s // 40) % H), s)

        t = title_font.render(GAME_TITLE, True, (120, 210, 255))
        screen.blit(t, t.get_rect(center=(W / 2, 100)))
        screen.blit(small_font.render(f"Player: {player_name}", True, (150, 155, 185)), (12, 10))
        draw_nav_back()
        if SPLASH_SPRITE:
            screen.blit(SPLASH_SPRITE, SPLASH_SPRITE.get_rect(center=(W / 2, 262 + math.sin(now / 300) * 6)))
        mouse = pygame.mouse.get_pos()
        mouse = (mouse[0] / scale, mouse[1] / scale)
        for name, rect in zip(names, MODE_BUTTONS):  # Easy / Normal / Hard 버튼
            chosen = name == game_mode
            hover = rect.collidepoint(mouse)
            color = MODE_COLORS[name]
            fill = tuple(int(c * (0.45 if chosen else 0.22 if not hover else 0.32)) for c in color)
            pygame.draw.rect(screen, fill, rect, border_radius=10)
            pygame.draw.rect(screen, color if chosen else tuple(int(c * 0.6) for c in color), rect, 3 if chosen else 2, border_radius=10)
            t = font.render(name, True, (255, 255, 255) if chosen else (190, 195, 215))
            screen.blit(t, t.get_rect(center=rect.center))
        pygame.draw.rect(screen, (24, 28, 56), PRESS_BAR, border_radius=10)  # 모드 버튼 줄과 같은 길이의 바
        if (now // 500) % 2 == 0:  # 깜빡이는 문구
            t = press_font.render("Press To Start", True, (230, 230, 240))
            screen.blit(t, t.get_rect(center=PRESS_BAR.center))
        draw_best_box()

        window.blit(pygame.transform.smoothscale(screen, window.get_size()), (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        online_tick()
        await asyncio.sleep(0)  # 웹에서 브라우저에 제어를 넘긴다


async def title_screen():
    global selected_ship, start_with_s
    name_clicks = 0    # 능력치 화면에서 전투기 이름(Fighter N)을 클릭한 횟수
    stars = [(random.randint(0, W), random.randint(0, H), random.randint(1, 3)) for _ in range(60)]
    phase = "choose"  # "choose": 비행기 고르기, "stats": 능력치 소개 화면
    hover = [0.0, 0.0, 0.0]  # 전투기마다 마우스를 올린 정도(0~1): 1.2배로 커지고 능력치 게이지가 나타난다
    started = None  # Select를 눌러 카운트다운을 시작한 시각(ms)
    preview_player = None  # 카운트다운 때 게임 시작과 같은 상단 표시(체력, 폭탄 등)를 미리 보여주기 위한 값
    row_y = H / 2 - 30  # 비행기 3개가 놓이는 줄의 높이
    slot_x = [W / 2 + (i - 1) * 230 for i in range(3)]  # 비행기 3개가 놓이는 자리
    slot_rects = [pygame.Rect(0, 0, 170, 190) for _ in range(3)]
    for r, x in zip(slot_rects, slot_x):
        r.center = (x, row_y)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if started is not None:
                continue
            if phase == "stats":  # 능력치 소개 화면: Select면 시작, Back이면 다시 고르기
                go = None
                if e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        go = "select"
                    elif e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        go = "back"
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mouse = (e.pos[0] / scale, e.pos[1] / scale)
                    if STATS_SELECT.collidepoint(mouse):
                        go = "select"
                    elif STATS_BACK.collidepoint(mouse):
                        go = "back"
                    elif STATS_TITLE.collidepoint(mouse):  # 숨겨진 기능: Fighter N의 이름을 N번 누르면 S를 들고 시작
                        name_clicks += 1
                        if name_clicks == selected_ship + 1:
                            start_with_s = True
                if go == "select":
                    started = pygame.time.get_ticks()
                    preview_player = Player()
                    preview_player.has_s = start_with_s
                elif go == "back":
                    phase = "choose"
                    start_with_s = False  # 다른 전투기를 고를 수 있으니 숨겨진 기능은 다시 켜야 한다
                continue
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_a):  # 비행기 고르기
                    selected_ship = max(0, selected_ship - 1)
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    selected_ship = min(2, selected_ship + 1)
                elif pygame.K_1 <= e.key <= pygame.K_3:
                    selected_ship = e.key - pygame.K_1
                elif e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):  # 조작법 화면으로 돌아간다
                    return "back"
                else:  # 그 밖의 아무 키나 누르면 능력치 소개 화면으로
                    phase = "stats"
                    name_clicks = 0
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:  # 휠 굴리기(버튼 4, 5)나 오른쪽 클릭은 무시
                mouse = (e.pos[0] / scale, e.pos[1] / scale)
                clicked = [i for i, r in enumerate(slot_rects) if r.collidepoint(mouse)]
                if SPLASH_BACK.collidepoint(mouse):
                    return "back"
                if clicked:  # 비행기를 클릭하면 선택, 빈 곳을 클릭하면 능력치 소개 화면으로
                    selected_ship = clicked[0]
                elif BEST_BOX.collidepoint(mouse):  # 최고 점수 칸을 누르면 기록 화면
                    await records_screen()
                else:
                    phase = "stats"
                    name_clicks = 0

        now = pygame.time.get_ticks()
        left = None if started is None else TITLE_COUNTDOWN - (now - started) / 1000
        if left is not None and left <= 0:
            return

        screen.fill((10, 10, 30))
        for x, y, s in stars:
            pygame.draw.circle(screen, (90, 90, 130), (x, (y + now * s // 40) % H), s)

        if phase == "stats" and left is None:
            draw_stats_screen(selected_ship, now)
            window.blit(pygame.transform.smoothscale(screen, window.get_size()), (0, 0))
            pygame.display.flip()
            clock.tick(FPS)
            online_tick()
            await asyncio.sleep(0)  # 웹에서 브라우저에 제어를 넘긴다
            continue

        if left is None:  # 카운트다운 중에는 게임 이름과 최고 점수 칸을 지운다
            t = title_font.render(GAME_TITLE, True, (120, 210, 255))
            screen.blit(t, t.get_rect(center=(W / 2, 110)))
            draw_nav_back()

        # 카운트다운이 진행될수록(0→1) 게임 시작 화면과 같아진다: 비행기가 시작 위치로 내려가며 작아지고, 상단 표시가 나타난다
        p = 0.0 if left is None else min(1.0, 1 - left / TITLE_COUNTDOWN)
        e = p * p * (3 - 2 * p)
        mouse = pygame.mouse.get_pos()
        mouse = (mouse[0] / scale, mouse[1] / scale)
        for i in range(3):  # 마우스를 올린 전투기는 서서히 커지고 능력치가 나타난다
            target = 1.0 if (left is None and phase == "choose" and slot_rects[i].collidepoint(mouse)) else 0.0
            hover[i] += (target - hover[i]) * 0.25
            if abs(target - hover[i]) < 0.01:
                hover[i] = target
        for i in range(3):
            chosen = i == selected_ship
            if left is not None and not chosen:  # 시작하면 고르지 않은 옆 비행기는 바로 지운다
                continue
            alpha = 1.0
            sprite = TITLE_SPRITES[i]
            bob = math.sin(now / 300) * 6 if chosen else 0  # 고른 비행기는 살짝 위아래로 떠다님
            cx = slot_x[i] + (W / 2 - slot_x[i]) * e if chosen else slot_x[i]  # 고른 비행기는 시작 위치로 이동
            cy = (row_y + bob * (1 - e)) * (1 - e) + (H - 80) * e if chosen else row_y
            if chosen:
                if left is None:  # 선택 표시 테두리
                    pygame.draw.rect(screen, (255, 220, 70), slot_rects[i], 3, border_radius=12)
                k = (TITLE_SPRITE_SIZE + (PLAYER_SPRITE_SIZE - TITLE_SPRITE_SIZE) * e) / TITLE_SPRITE_SIZE
            else:
                k = 0.8  # 고르지 않은 비행기는 조금 작고 흐리게 (마우스를 올리면 또렷해진다)
                alpha *= 0.55 + 0.45 * hover[i]
            k *= 1 + HOVER_SCALE * hover[i]  # 마우스를 올리면 HOVER_SCALE만큼 더 커진다
            if sprite:
                ship = pygame.transform.smoothscale(
                    sprite, (round(sprite.get_width() * k), round(sprite.get_height() * k)))
                if alpha < 1:
                    ship.set_alpha(int(255 * alpha))
                screen.blit(ship, ship.get_rect(center=(cx, cy)))
            else:
                pygame.draw.polygon(screen, (80, 200, 255), [(cx, cy - 40), (cx - 32, cy + 32), (cx + 32, cy + 32)])
            if left is None:
                if hover[i] > 0.02:  # 마우스를 올리면 이름 대신 능력치 게이지
                    draw_hover_stats(i, slot_x[i], row_y + 98, hover[i])
                else:  # 평소에는 전투기 이름 (고른 것은 노란색)
                    t = font.render(SHIP_NAMES[i], True, (255, 220, 70) if chosen else (140, 140, 170))
                    screen.blit(t, t.get_rect(center=(slot_x[i], row_y + 112)))

        if left is not None:
            hud = pygame.Surface((W, H), pygame.SRCALPHA)
            draw_hud(hud, 0, 1, preview_player)
            hud.set_alpha(int(255 * e))
            screen.blit(hud, (0, 0))

        if left is None:
            if (now // 500) % 2 == 0:  # 깜빡이는 문구
                t = big.render("Press To Start", True, (230, 230, 240))
                screen.blit(t, t.get_rect(center=(W / 2, H - 135)))
        else:
            t = big.render(str(int(left) + 1), True, (255, 220, 70))
            screen.blit(t, t.get_rect(center=(W / 2, 200)))

        if left is None:
            draw_best_box()  # 최고 점수 칸 (카운트다운 중에는 지운다)

        window.blit(pygame.transform.smoothscale(screen, window.get_size()), (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        online_tick()
        await asyncio.sleep(0)  # 웹에서 브라우저에 제어를 넘긴다


async def main():
    global start_with_s
    player = Player()
    if start_with_s:  # 능력치 화면의 숨겨진 기능: 시작하자마자 S 1개 (한 번만)
        player.has_s = True
        start_with_s = False
    bullets, enemy_bullets, enemies, particles, items = [], [], [], [], []
    bombs, explosions = [], []
    fx = []  # 폭발 그림(보기만 하는 효과): [위치, 나이, 수명, 반경]
    score, level, spawn = 0, 1, 0
    max_power_score = None  # 미사일이 최대가 된 시점의 난이도 점수(score - bonus_total)
    bonus_total = 0   # R 보너스로 받은 점수의 합. 점수에는 더하지만 난이도(레벨, 적 수, 적 총알 수)에는 반영하지 않는다
    r_full, p_full = 0, 0  # 체력이 꽉 찬 채로 먹은 R 개수, 미사일이 최대인 채로 먹은 P 개수
    bonus_flash, bonus_text = 0, ""  # 보너스 안내("R Bonus +100!" 등)를 보여줄 남은 프레임과 글
    game_over = False
    paused = False
    shop, shop_msg, play_frames = False, "", 0
    shop_offers = []  # 지금 상점에 나온 물건 [(이름, 가격, 종류), ...]
    confirm_idx = None  # 구매 확인 화면에 띄운 물건 번호 (없으면 None)
    yellow_spawn = 0
    fade = 0  # 보너스 라운드로 가기 전 적이 사라지는 중이면 남은 프레임
    s_charging, s_charge = False, 0  # S를 꾹 눌러 충전하는 중인가, 지금까지 누른 프레임
    saved = False  # 이번 판의 점수를 순위표에 이미 넣었는가
    star_ms = 0

    def save_run():
        """이번 판의 점수를 순위표에 한 번만 넣는다."""
        nonlocal saved
        if not saved:
            saved = True
            save_best(score, level, play_frames // FPS)

    stars = [(random.randint(0, W), random.randint(0, H), random.randint(1, 3)) for _ in range(60)]

    while True:
        blast = False
        buy_idx = None
        change_req = False  # 상점의 Change 버튼(또는 C 키)을 눌렀는가
        open_idx, do_buy = None, False  # 고른 물건을 구매 확인 화면으로 열기 / 확인 화면에서 Buy를 눌렀는가
        was_shop = shop
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_run()  # 플레이 도중 창을 닫아도 점수는 남긴다
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
                blast = True
            if e.type == pygame.KEYDOWN and game_over and e.key == pygame.K_r:
                return
            if e.type == pygame.KEYDOWN and not game_over and not shop and e.key == pygame.K_SPACE:
                paused = not paused
            if paused and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if PAUSE_HOME.collidepoint(e.pos[0] / scale, e.pos[1] / scale):
                    save_run()  # 홈으로 나가도 그때까지의 점수는 기록에 반영
                    return "home"
            if game_over and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:  # 게임 오버 화면의 홈 버튼
                if GAMEOVER_HOME.collidepoint(e.pos[0] / scale, e.pos[1] / scale):
                    save_run()  # 게임 오버 때 이미 저장됐으면 다시 저장하지 않는다
                    return "home"
            if shop and confirm_idx is not None:  # 구매 확인 화면: Buy면 구매, Back이면 상점으로
                if e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        do_buy = True
                    elif e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        confirm_idx = None
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mouse = (e.pos[0] / scale, e.pos[1] / scale)
                    if CONFIRM_BUY.collidepoint(mouse):
                        do_buy = True
                    elif CONFIRM_BACK.collidepoint(mouse):
                        confirm_idx = None
            elif shop:
                if e.type == pygame.KEYDOWN:
                    if pygame.K_1 <= e.key <= pygame.K_3:
                        open_idx = e.key - pygame.K_1
                    elif e.key == pygame.K_c:
                        change_req = True
                    elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                        shop = False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mouse = (e.pos[0] / scale, e.pos[1] / scale)
                    if SHOP_CONTINUE.collidepoint(mouse):
                        shop = False
                    elif SHOP_CHANGE.collidepoint(mouse):
                        change_req = True
                    for i, card in enumerate(SHOP_CARDS):
                        if card.collidepoint(mouse):
                            open_idx = i

        if not shop:
            confirm_idx = None
        if open_idx is not None and confirm_idx is None and open_idx < len(shop_offers):  # 물건을 고르면 바로 사지 않고 확인 화면을 연다
            confirm_idx = open_idx
            shop_msg = ""
        if do_buy and confirm_idx is not None:
            buy_idx = confirm_idx  # 아래 구매 처리가 이 번호의 물건을 산다

        if paused or shop or game_over:
            s_charging = False  # 멈추거나 끝나면 S 충전은 취소
        if was_shop and not shop:  # 다음 라운드는 처음처럼 위에서부터 적이 나타난다
            spawn = 0
            yellow_spawn = YELLOW_SPAWN_INTERVAL

        if shop and change_req:  # Change Ticket을 하나 써서 상점 물건을 새로 뽑는다
            if player.rerolls > 0:
                player.rerolls -= 1
                shop_offers = reroll_shop(player, shop_offers)
                shop_msg = "Items changed!"
            else:
                shop_msg = "You have no Change Ticket"

        if shop and buy_idx is not None and buy_idx < len(shop_offers):
            name, price, kind = shop_offers[buy_idx]
            bought = False
            if player.coins < price:
                shop_msg = "Not enough coins"
            elif not shop_available(kind, player):
                shop_msg = UNAVAILABLE_MSG[kind]
            else:
                player.coins -= price
                if kind == "heart":  # 상점에서만 최대 하트를 늘릴 수 있다
                    player.max_hp += 1
                    player.hp += 1
                elif kind == "heal":
                    player.hp = player.max_hp
                elif kind == "b":
                    player.b_count += 1
                elif kind == "power":
                    player.power += 1
                    if player.power == MAX_POWER:
                        max_power_score = int(score - bonus_total)
                elif kind == "shield":
                    player.invuln = max(player.invuln, SHIELD_TIME)
                elif kind == "speed":
                    player.speed += 1
                elif kind == "rapid":
                    player.fire_delay -= 1
                elif kind == "rainbow":
                    player.has_s = True
                elif kind == "change":
                    player.rerolls += 1
                shop_msg = f"{name} purchased!"
                if kind in ("heart", "heal"):
                    shop_msg += f"  Hearts {player.hp}/{player.max_hp}"
                bought = True
            if bought:
                confirm_idx = None  # 샀으면 상점으로 돌아간다 (못 샀으면 확인 화면에 남아서 이유를 보여준다)

        keys = pygame.key.get_pressed()

        if not paused and not shop:
            star_ms += clock.get_time()

        if not (game_over or paused or shop or fade):
            play_frames += 1
            if play_frames % (BONUS_INTERVAL * FPS) == 0:
                fade = FADE_FRAMES  # 적이 스르륵 사라진 뒤 상점이 열린다

        if fade and not (game_over or paused or shop):
            # 적은 계속 움직이며 흐려지고, 공격도 충돌도 하지 않는다
            player.update(keys)
            for en in enemies:
                en.update()
            for eb in enemy_bullets:
                eb[0] += eb[1]
            for b in bullets:
                b[0].y -= 11
            bullets = [b for b in bullets if b[0].y > -30]
            for it in items:
                move_item(it, player)
            fade -= 1
            if fade == 0:
                enemies.clear()
                enemy_bullets.clear()
                bombs.clear()
                explosions.clear()
                shop = True
                shop_msg = ""
                shop_offers = roll_shop(player)  # 이번 보너스 라운드에 나올 물건

        if not game_over and not paused and not shop and not fade:
            player.update(keys)
            if pygame.mouse.get_pressed()[0] and player.cooldown == 0:
                gap = 10 + 2 * BULLET_RADIUS
                for i in range(player.power):
                    x = player.pos.x + (i - (player.power - 1) / 2) * gap
                    bullets.append([pygame.Vector2(x, player.pos.y - int(PLAYER_SPRITE_SIZE * 0.33)), BULLET_RADIUS])  # 총알은 비행기 코에서 나온다
                player.cooldown = player.fire_delay
                play_sfx("shoot")

            spawn -= 1
            normal_count = sum(1 for en in enemies if not en.yellow)  # 노란 적은 세지 않음
            m = MODES[game_mode]  # 난이도별 규칙
            if spawn <= 0 and normal_count < m["max_enemies"]:
                for _ in range(min(1 + int(score - bonus_total) // SPAWN_SCORE, m["max_enemies"] - normal_count)):
                    enemies.append(Enemy(level, random.random() < GREEN_RATE))
                spawn = int(max(20, 70 - level * 5) * m["spawn_mult"])

            yellow_spawn -= 1
            if player.power >= MAX_POWER and yellow_spawn <= 0:  # 미사일이 최대가 되면 등장
                if sum(1 for en in enemies if en.yellow) < YELLOW_MAX:
                    enemies.append(Enemy(level, yellow=True))
                yellow_spawn = YELLOW_SPAWN_INTERVAL

            for b in bullets:
                b[0].y -= 11
            bullets = [b for b in bullets if b[0].y > -30]

            for it in items:
                move_item(it, player)  # 떨어지거나, 자석에 끌려온다
                if it[0].distance_to(player.pos) < 12 + player.radius:
                    if it[1] == "P":
                        if player.power < MAX_POWER:
                            player.power += 1
                            if player.power == MAX_POWER:
                                max_power_score = int(score - bonus_total)
                        else:  # 미사일이 이미 최대면 보너스로 센다
                            p_full += 1
                            if p_full >= P_BONUS_COUNT:
                                p_full = 0
                                score += P_BONUS_POINTS
                                bonus_total += P_BONUS_POINTS  # 점수에만 더하고 적이 늘어나는 난이도에는 반영하지 않는다
                                bonus_flash = 90
                                bonus_text = f"P Bonus +{P_BONUS_POINTS}!"
                    elif it[1] == "R":
                        if player.hp >= player.max_hp:  # 체력이 꽉 찬 상태로 먹은 R은 보너스로 센다
                            r_full += 1
                            if r_full >= R_BONUS_COUNT:
                                r_full = 0
                                score += R_BONUS_POINTS
                                bonus_total += R_BONUS_POINTS
                                bonus_flash = 90
                                bonus_text = f"R Bonus +{R_BONUS_POINTS}!"
                        player.hp = min(player.max_hp, player.hp + 1)
                    elif it[1] == "B":
                        player.b_count += 1
                    elif it[1] == "C":
                        player.coins += COIN_VALUE
                    else:
                        player.has_s = True
                    it[0].y = H + 999
            items = [it for it in items if it[0].y < H + 20]

            enemy_count = player.power  # 적이 한 번에 쏘는 총알 수 (아이템 드롭 조건에도 쓴다)
            if max_power_score is not None:
                enemy_count += (int(score - bonus_total) - max_power_score) // ENEMY_SCALE_SCORE
            enemy_count = min(m["enemy_max_count"], enemy_count)

            blast_radius = None
            if blast and player.b_count > 0:  # B가 있으면 B부터 사용
                player.b_count -= 1
                blast_radius = B_RADIUS  # 폭발 범위에 닿은 적 총알만 사라진다 (화면 전체를 지우지 않는다)
            elif blast and player.has_s and not s_charging:  # S는 오른쪽 버튼을 꾹 눌러야 한다: 누르는 순간부터 충전 시작
                s_charging = True
                s_charge = 0
            if s_charging:
                if player.has_s and pygame.mouse.get_pressed()[2]:  # 계속 누르고 있으면 충전, 중간에 떼면 취소
                    s_charge += 1
                    if s_charge >= S_HOLD_FRAMES:  # 0.5초를 채우면 발동
                        s_charging = False
                        player.has_s = False
                        blast_radius = BLAST_RADIUS
                else:
                    s_charging = False
            if blast_radius:
                explosions.append([player.pos.copy(), 30, blast_radius, 30, True])  # 마지막 True: 내가 터뜨린 폭발
                play_sfx("bomb")
                for en in enemies:
                    if en.pos.distance_to(player.pos) < blast_radius + en.radius:  # 폭탄에 닿은 적은 바로 사라지고, 총알로 잡은 것처럼 아이템도 떨어뜨린다
                        en.hp = 0
                        score += kill_points(en)
                        drop_items(en, player, enemy_count, items)
                        explode_enemy(en, particles, fx)
                enemies = [en for en in enemies if en.hp > 0]

            for en in enemies:
                en.update()
                if en.shoot <= 0:
                    en.shoot = random.randint(80, 160)
                    v = player.pos - en.pos
                    if en.green:
                        en.shoot = random.randint(150, 210)
                        bombs.append([en.pos.copy(), player.pos.copy(), BOMB_FUSE])
                    elif en.yellow:
                        en.shoot = random.randint(50, 90)
                        if v.length_squared():  # 빠른 총알을 조금씩 벌려서 YELLOW_BULLET_COUNT발 쏜다
                            aim = v.normalize()
                            for i in range(YELLOW_BULLET_COUNT):
                                angle = (i - (YELLOW_BULLET_COUNT - 1) / 2) * YELLOW_BULLET_SPREAD
                                enemy_bullets.append([en.pos.copy(), aim.rotate(angle) * YELLOW_BULLET_SPEED * m["bullet_speed"] / 4])
                    elif v.length_squared():
                        aim = v.normalize()
                        for i in range(enemy_count):
                            angle = (i - (enemy_count - 1) / 2) * 12
                            enemy_bullets.append([en.pos.copy(), aim.rotate(angle) * m["bullet_speed"]])
            for eb in enemy_bullets:
                eb[0] += eb[1]
            enemy_bullets = [eb for eb in enemy_bullets if -20 < eb[0].x < W + 20 and -20 < eb[0].y < H + 20]
            for ex in explosions:  # 날아오던 총알이 내가 터뜨린 폭탄(B/S)의 폭발에 닿으면 사라진다
                if len(ex) > 4 and ex[4]:
                    enemy_bullets = [eb for eb in enemy_bullets if eb[0].distance_to(ex[0]) > ex[2] + 5]
                    bombs = [bm for bm in bombs if bm[0].distance_to(ex[0]) > ex[2] + 9]  # 상대편 폭탄도 폭발에 닿으면 터지지 못하고 사라진다

            bomb_hit = False
            for bm in bombs:
                to_target = bm[1] - bm[0]
                if to_target.length() > 5:
                    bm[0] += to_target.normalize() * 5
                bm[2] -= 1
                if bm[2] <= 0:
                    explosions.append([bm[0].copy(), 15, BOMB_RADIUS, 15])
                    play_sfx("bomb")
                    if bm[0].distance_to(player.pos) < BOMB_RADIUS + player.radius:
                        bomb_hit = True
            bombs = [bm for bm in bombs if bm[2] > 0]
            for ex in explosions:
                ex[1] -= 1
            explosions = [ex for ex in explosions if ex[1] > 0]

            # 플레이어 총알 vs 적
            hit_sound = False
            for en in enemies:
                for b in bullets:
                    if bullet_hits(en, b):
                        hit_sound = True
                        add_fx(fx, b[0], 16, 10)  # 맞힌 자리에 작은 폭발
                        b[0].y = -999
                        en.hp -= 1
                        if en.hp <= 0:
                            score += kill_points(en)
                            drop_items(en, player, enemy_count, items)
                            explode_enemy(en, particles, fx)  # 쓰러지면 전투기가 크게 폭발
                        break
            if hit_sound:
                play_sfx("hit")
            enemies = [en for en in enemies if en.hp > 0 and en.pos.y < H + 30]
            level = 1 + int(score - bonus_total) // 150

            # 피격 처리
            if player.invuln:  # 무적(피격 직후, Shield)일 때도 총알은 비행기를 통과하지 않는다: 닿으면 피해 없이 사라진다
                blocked = [eb for eb in enemy_bullets if enemy_bullet_hits_player(eb, player)]
                for eb in blocked:
                    add_fx(fx, eb[0], 10, 8)  # 막힌 자리에 작은 불꽃
                enemy_bullets = [eb for eb in enemy_bullets if eb not in blocked]
            if not player.invuln:
                # 총알/폭탄에 맞거나 적 비행기와 부딪히면 체력이 깎인다. 부딪힌 적도 함께 피해를 입는다
                hit_b = [eb for eb in enemy_bullets if enemy_bullet_hits_player(eb, player)]
                rammed = [en for en in enemies if en.pos.distance_to(player.pos) < en.radius + player.radius]
                if hit_b or bomb_hit or rammed:
                    player.hp -= 1
                    play_sfx("hurt")
                    player.invuln = INVULN_TIME
                    add_fx(fx, player.pos, 20, 18, "boom" if EXPLOSION_SPRITE else "fire")  # 맞거나 부딪힌 내 비행기에 작은 폭발
                    enemy_bullets = [eb for eb in enemy_bullets if eb not in hit_b]
                    for en in rammed:  # 부딪힌 적도 1 피해, 쓰러지면 총알로 잡은 것과 같이 점수와 아이템
                        add_fx(fx, (en.pos + player.pos) / 2, 34, 20)  # 부딪힌 자리에서 폭발
                        en.hp -= 1
                        if en.hp <= 0:
                            score += kill_points(en)
                            drop_items(en, player, enemy_count, items)
                            explode_enemy(en, particles, fx)
                    enemies = [en for en in enemies if en.hp > 0]
                    if player.hp <= 0:
                        game_over = True
                        add_fx(fx, player.pos, 70, 40)  # 내 전투기가 쓰러지는 큰 폭발
                        save_run()

        if not paused and not shop:
            for p in particles:
                p[0] += p[1]
                p[2] -= 1
            particles = [p for p in particles if p[2] > 0]
            bonus_flash = max(0, bonus_flash - 1)
            for f in fx:  # 폭발 그림의 나이를 먹인다
                f[1] += 1
            fx = [f for f in fx if f[1] < f[2]]

        # 그리기
        screen.fill((10, 10, 30))
        for x, y, s in stars:
            pygame.draw.circle(screen, (90, 90, 130), (x, (y + star_ms * s // 40) % H), s)
        for b in bullets:
            pygame.draw.ellipse(screen, (255, 240, 120), (b[0].x - b[1], b[0].y - b[1] * 2, b[1] * 2, b[1] * 4))
        enemy_alpha = fade / FADE_FRAMES if fade else 1.0  # 사라지는 중이면 점점 흐려진다
        for bm in bombs:
            blink = (bm[2] // 6) % 2 == 0 or bm[2] > 40
            pygame.draw.circle(screen, fade_color((255, 80, 80), enemy_alpha), bm[1], BOMB_RADIUS, 1)
            pygame.draw.circle(screen, fade_color((255, 60, 60) if blink and bm[2] <= 40 else (40, 40, 50), enemy_alpha), bm[0], 9)
            pygame.draw.circle(screen, fade_color((200, 200, 210), enemy_alpha), bm[0], 9, 2)
        if explosions:  # 폭탄 폭발: 반투명하게 그려서 S처럼 화면을 덮는 큰 폭발에서도 뒤가 보인다
            blast_layer = pygame.Surface((W, H), pygame.SRCALPHA)
            for ex in explosions:
                t = ex[1] / ex[3]  # 1 → 0
                big_blast = ex[2] > 200
                pygame.draw.circle(blast_layer, (255, 120, 20, int((70 if big_blast else 150) * t + 20)), ex[0], ex[2] * (1.2 - 0.2 * t))
                pygame.draw.circle(blast_layer, (255, 170, 40, int((130 if big_blast else 220) * t + 20)), ex[0], max(1, ex[2] * 0.5 * t))  # 낮은 투명도의 밝은 색은 회색으로 보여서 주황 계열로 둔다
                pygame.draw.circle(blast_layer, (255, 230, 150, int(220 * t + 35)), ex[0], ex[2] * (1.2 - 0.2 * t), 6 if big_blast else 3)  # 바깥 고리
            screen.blit(blast_layer, (0, 0))
        for it in items:  # 끌려오는 동안에도 모양은 그대로 (크기를 줄이거나 꼬리를 달지 않는다)
            pos, kind = it[0], it[1]
            fill, edge = ITEM_COLORS[kind]
            if kind == "B":  # 총알 모양
                rect = pygame.Rect(0, 0, 18, 30)
                rect.center = pos
                pygame.draw.rect(screen, fill, rect, border_radius=9)
                pygame.draw.rect(screen, edge, rect, 3, border_radius=9)
            else:
                pygame.draw.circle(screen, fill, pos, 12)
                pygame.draw.circle(screen, edge, pos, 12, 3)
            t = font.render("$" if kind == "C" else kind, True, edge)
            screen.blit(t, t.get_rect(center=pos))
        for eb in enemy_bullets:
            pygame.draw.circle(screen, fade_color((255, 160, 60), enemy_alpha), eb[0], ENEMY_BULLET_RADIUS)
        for en in enemies:
            en.draw(enemy_alpha)
        if not game_over:  # 내 비행기를 폭발 그림보다 먼저 그려서, 내가 맞았을 때의 폭발이 비행기 위에 보이게 한다
            player.draw()
            if s_charging:  # S 충전 표시: 비행기 둘레의 고리가 0.5초 동안 한 바퀴 채워진다
                ring = pygame.Rect(0, 0, 90, 90)
                ring.center = player.pos
                pygame.draw.circle(screen, (60, 70, 110), player.pos, 45, 3)
                pygame.draw.arc(screen, (170, 230, 255), ring, math.pi / 2, math.pi / 2 + math.tau * s_charge / S_HOLD_FRAMES, 6)
        draw_fx(fx)
        for p in particles:
            pygame.draw.circle(screen, (255, 200, 120), p[0], max(1, p[2] // 8))

        draw_hud(screen, score, level, player)
        if bonus_flash:  # R 보너스 안내: 위에서 잠깐 보였다가 사라진다
            t = big.render(bonus_text, True, (255, 150, 170) if bonus_text.startswith("R") else (255, 230, 120))
            t.set_alpha(min(255, bonus_flash * 8))
            screen.blit(t, t.get_rect(center=(W / 2, 150 - (90 - bonus_flash) * 0.3)))

        if game_over:
            t = big.render("GAME OVER", True, (255, 90, 90))
            screen.blit(t, t.get_rect(center=(W / 2, H / 2 - 20)))
            t = font.render("Press R to Restart", True, (230, 230, 240))
            screen.blit(t, t.get_rect(center=(W / 2, H / 2 + 30)))
            hover = GAMEOVER_HOME.collidepoint(pygame.mouse.get_pos()[0] / scale, pygame.mouse.get_pos()[1] / scale)
            pygame.draw.rect(screen, (70, 90, 150) if hover else (40, 50, 90), GAMEOVER_HOME, border_radius=10)
            pygame.draw.rect(screen, (150, 190, 255), GAMEOVER_HOME, 2, border_radius=10)
            t = font.render("Go Home", True, (240, 245, 255))
            screen.blit(t, t.get_rect(center=GAMEOVER_HOME.center))

        if paused:
            dim = pygame.Surface((W, H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 150))
            screen.blit(dim, (0, 0))
            pygame.draw.rect(screen, (240, 240, 250), (W / 2 - 38, H / 2 - 70, 24, 80), border_radius=4)
            pygame.draw.rect(screen, (240, 240, 250), (W / 2 + 14, H / 2 - 70, 24, 80), border_radius=4)
            t = big.render("Pause", True, (240, 240, 250))
            screen.blit(t, t.get_rect(center=(W / 2, 165)))
            t = font.render(f"{game_mode} Mode", True, MODE_COLORS[game_mode])
            screen.blit(t, t.get_rect(center=(W / 2, 208)))
            t = font.render("Press Space to Resume", True, (230, 230, 240))
            screen.blit(t, t.get_rect(center=(W / 2, H / 2 + 50)))
            hover = PAUSE_HOME.collidepoint(pygame.mouse.get_pos()[0] / scale, pygame.mouse.get_pos()[1] / scale)
            pygame.draw.rect(screen, (70, 90, 150) if hover else (40, 50, 90), PAUSE_HOME, border_radius=10)
            pygame.draw.rect(screen, (150, 190, 255), PAUSE_HOME, 2, border_radius=10)
            t = font.render("Go Home", True, (240, 245, 255))
            screen.blit(t, t.get_rect(center=PAUSE_HOME.center))

        if shop:
            dim = pygame.Surface((W, H), pygame.SRCALPHA)
            dim.fill((0, 0, 20, 200))
            screen.blit(dim, (0, 0))
            t = big.render(SHOP_TITLE, True, (255, 220, 70))
            screen.blit(t, t.get_rect(center=(W / 2, 90)))
            draw_coin_icon((W / 2 - 50, 150))
            screen.blit(font.render(f"{player.coins} Coins", True, (255, 240, 170)), (W / 2 - 30, 137))
            screen.blit(render_hearts(font, f"♥ {player.hp}/{player.max_hp}", (255, 130, 150)), (W / 2 + 105, 137))  # 지금 하트(현재/최대)
            for i, ((name, price, kind), card) in enumerate(zip(shop_offers, SHOP_CARDS)):
                blocked = not shop_available(kind, player)
                affordable = player.coins >= price and not blocked
                pygame.draw.rect(screen, (30, 34, 60) if affordable else (24, 24, 36), card, border_radius=10)
                pygame.draw.rect(screen, (255, 220, 70) if affordable else (80, 80, 100), card, 3, border_radius=10)
                cx = card.centerx
                draw_shop_icon(kind, cx, card.y + 62)
                col = (230, 230, 240) if affordable else (120, 120, 140)
                t = font.render(f"[{i + 1}] {name}", True, col)
                screen.blit(t, t.get_rect(center=(cx, card.y + 125)))
                draw_coin_icon((cx - 36, card.y + 168), r=9)
                t = font.render(f"{price}", True, (255, 220, 70) if affordable else (120, 120, 140))
                screen.blit(t, t.get_rect(midleft=(cx - 20, card.y + 168)))
                if blocked:
                    t = font.render("Maxed", True, (255, 130, 130))
                    screen.blit(t, t.get_rect(center=(cx, card.y + 195)))
            if shop_msg:
                t = font.render(shop_msg, True, (180, 255, 190))
                screen.blit(t, t.get_rect(center=(W / 2, 425)))
            has_change = player.rerolls > 0  # 가진 Change Ticket이 없으면 흐리게
            pygame.draw.rect(screen, (50, 90, 150) if has_change else (35, 38, 60), SHOP_CHANGE, border_radius=10)
            pygame.draw.rect(screen, (150, 200, 255) if has_change else (80, 85, 110), SHOP_CHANGE, 2, border_radius=10)
            t = font.render(f"Change (C) × {player.rerolls}", True, (240, 248, 255) if has_change else (120, 125, 150))
            screen.blit(t, t.get_rect(center=SHOP_CHANGE.center))
            pygame.draw.rect(screen, (60, 120, 90), SHOP_CONTINUE, border_radius=10)
            t = font.render("Continue (Enter)", True, (240, 255, 245))
            screen.blit(t, t.get_rect(center=SHOP_CONTINUE.center))
            if confirm_idx is not None and confirm_idx < len(shop_offers):
                draw_confirm_screen(shop_offers[confirm_idx], player, shop_msg)

        window.blit(pygame.transform.smoothscale(screen, window.get_size()), (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        online_tick()
        await asyncio.sleep(0)  # 웹에서 브라우저에 제어를 넘긴다


async def front_screens(skip_name=False):
    """이름 화면 → 난이도 화면 → 조작법(3쪽) → 전투기 고르기. 각 화면의 Back은 바로 앞 화면으로 돌아간다."""
    step = "splash" if skip_name else "name"
    while True:
        if step == "name":
            await name_screen()  # 가장 먼저: 이름 입력(또는 게스트)
            step = "splash"
        elif step == "splash":
            step = "name" if await splash_screen() == "back" else "controls"
        elif step == "controls":
            step = "splash" if await controls_screen(CONTROL_START[0]) == "back" else "title"
            CONTROL_START[0] = 0
        else:
            if await title_screen() == "back":
                CONTROL_START[0] = len(CONTROL_PAGES) - 1  # 전투기 고르기에서 Back이면 조작법의 마지막 쪽으로
                step = "controls"
            else:
                return


async def run():
    online_setup()
    online_refresh()
    await front_screens()
    while True:
        if await main() == "home":  # 일시정지 화면에서 홈으로 나온 경우: 난이도 화면부터 다시 (거기서 Back이면 이름 화면)
            await front_screens(skip_name=True)


asyncio.run(run())
