import math
import os
import random
import sys

import pygame

W, H = 800, 600
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BEST_FILE = os.path.join(BASE_DIR, "best_score.txt")  # 최고 점수 저장 파일
ENEMY_SPRITE_SIZE = 44  # 적 이미지의 크기(px)
PLAYER_SPRITE_SIZE = 60  #내 비행기 이미지의 크기(px). 충돌 범위는 그대로
TITLE_SPRITE_SIZE = 130  # 타이틀 화면의 내 비행기 크기(px)
FADE_FRAMES = 60        # 보너스 라운드로 가기 전에 적이 사라지는 데 걸리는 시간(프레임)
GAME_TITLE = "Asteroid"  # 타이틀 화면과 창 제목에 쓰이는 게임 이름
TITLE_COUNTDOWN = 3        # 아무 버튼이나 누른 뒤 게임이 시작되기까지의 시간(초)
WINDOW_SCALE = 2  # 창 크기 배율
MAX_ENEMIES = 7    # 화면에 동시에 있을 수 있는 적의 최대 수 (노란 적은 제외)
YELLOW_SPAWN_INTERVAL = 4 * 60  # 노란 적이 나오는 간격(프레임). 미사일이 최대일 때부터 등장
YELLOW_MAX = 2                  # 노란 적이 동시에 있을 수 있는 최대 수
FPS = 60
RED_DROP_RATES = (0.01, 0.033)    # (P, R) 빨간 적: R이 잘 나옴
GREEN_DROP_RATES = (0.10, 0.03)  # (P, R) 초록 적: P가 잘 나옴
INVULN_TIME = 5 * FPS
BULLET_RADIUS = 4
MAX_POWER = 5
ENEMY_SCALE_SCORE = 100
START_POWER = 2
HEAL_UNLOCK_PICKUPS = 0  # P를 이만큼 먹은 뒤부터 R이 나옴 (0이면 처음부터)
MAX_HP = 5
SPAWN_SCORE = 100  # 이 점수를 얻을 때마다 한 번에 나오는 적이 1마리씩 늘어남
GREEN_RATE =0.25
BOMB_FUSE = 2 * FPS
BOMB_RADIUS = 70
S_UNLOCK_COUNT = 5  # 적 미사일이 이 개수 이상이면 S 아이템이 나옴
S_DROP_RATE = 0.20        # 적 미사일이 정확히 S_UNLOCK_COUNT개일 때
S_LATE_DROP_RATE = 0.005  # 그 이후(더 늘어난 뒤)
BLAST_RADIUS = 300
ENEMY_MAX_COUNT = 7  # 적 미사일 상한
B_START = 3          # 처음 가지고 있는 폭탄 B 개수
B_RADIUS = 150

B_DROP_RATE = 0.01  # 적 처치 시 B 아이템이 나올 확률
COIN_DROP_RATE = 0.005         # 빨간/초록 적 처치 시 코인 아이템이 나올 확률
YELLOW_COIN_DROP_RATE = 0.1   # 노란 적 처치 시 코인 아이템이 나올 확률 (노란 적은 코인만 떨어뜨림)
MAGNET_RADIUS = 60  # 이 거리 안에 들어온 아이템은 나에게 빨려 들어옴
MAGNET_SPEED = 5
COIN_VALUE = 100      # 코인 아이템 1개가 주는 코인
BONUS_INTERVAL = 60    # 보너스 라운드(상점)가 열리는 간격(초, 플레이 시간 기준)
SHOP_ITEMS = [  # (이름, 가격, 종류) - 상점에는 3개만 있음
    ("하트 +1", 100, "heart"),
    ("폭탄 B +1", 200, "b"),
    ("미사일 +1", 300, "power"),
]
SHOP_CARDS = [pygame.Rect(40 + i * 250, 190, 220, 210) for i in range(3)]
SHOP_CONTINUE = pygame.Rect(300, 450, 200, 50)
PAUSE_HOME = pygame.Rect(300, 390, 200, 50)  # 일시정지 화면의 "Go to Home" 버튼
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
desktop_h = pygame.display.get_desktop_sizes()[0][1]
scale = min(WINDOW_SCALE, desktop_h * 0.9 / H)
window = pygame.display.set_mode((int(W * scale), int(H * scale)))
screen = pygame.Surface((W, H))
pygame.display.set_caption(GAME_TITLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont("malgungothic", 24)
big = pygame.font.SysFont("malgungothic", 56, bold=True)
title_font = pygame.font.SysFont("malgungothic", 84, bold=True)

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
selected_ship = 0  # 타이틀에서 고른 비행기 번호(0~2)


def fade_color(color, alpha):
    """배경색 쪽으로 alpha(0~1)만큼 섞어서 서서히 사라지는 색을 만든다."""
    bg = (10, 10, 30)
    return tuple(int(bg[i] + (color[i] - bg[i]) * alpha) for i in range(3))


def load_best():
    try:
        with open(BEST_FILE, encoding="utf-8") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


best_score = load_best()


def save_best(score):
    global best_score
    if score > best_score:
        best_score = score
        try:
            with open(BEST_FILE, "w", encoding="utf-8") as f:
                f.write(str(best_score))
        except OSError:
            pass  # 저장하지 못해도 게임은 계속한다


def draw_bomb_icon(center, rainbow=False, r=11, surf=None):
    surf = screen if surf is None else surf
    cx, cy = center
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


def draw_hud(surf, score, level, player):
    """게임 화면의 점수/체력/코인/폭탄 표시. 타이틀에서 게임 화면으로 넘어갈 때도 같은 걸 쓴다."""
    surf.blit(font.render(f"점수 {score}   레벨 {level}   미사일 {player.power}", True, (230, 230, 240)), (12, 10))
    surf.blit(font.render("♥ " * player.hp, True, (255, 100, 120)), (W - 150, 10))
    draw_coin_icon((W - 138, 54), surf=surf)
    surf.blit(font.render(f"{player.coins}", True, (255, 220, 70)), (W - 118, 41))
    draw_bomb_icon((24, 56), surf=surf)
    surf.blit(font.render(f"× {player.b_count}", True, (255, 210, 120)), (44, 43))
    if player.has_s:
        draw_bomb_icon((24, 92), rainbow=True, surf=surf)
        surf.blit(font.render("오른쪽 클릭!", True, (180, 220, 255)), (44, 79))


class Player:
    speed = 5
    radius = 14

    def __init__(self):
        self.pos = pygame.Vector2(W / 2, H - 80)
        self.cooldown = 0
        self.hp = MAX_HP
        self.invuln = 0
        self.power = START_POWER
        self.has_s = False
        self.b_count = B_START
        self.coins = 0

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


def title_screen():
    global selected_ship
    stars = [(random.randint(0, W), random.randint(0, H), random.randint(1, 3)) for _ in range(60)]
    started = None  # 시작 버튼을 누른 시각(ms)
    preview_player = Player()  # 게임 시작 때와 같은 상단 표시(체력, 폭탄 등)를 미리 보여주기 위한 값
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
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_a):  # 비행기 고르기
                    selected_ship = max(0, selected_ship - 1)
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    selected_ship = min(2, selected_ship + 1)
                elif pygame.K_1 <= e.key <= pygame.K_3:
                    selected_ship = e.key - pygame.K_1
                else:  # 그 밖의 아무 키나 누르면 시작
                    started = pygame.time.get_ticks()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mouse = (e.pos[0] / scale, e.pos[1] / scale)
                clicked = [i for i, r in enumerate(slot_rects) if r.collidepoint(mouse)]
                if clicked:  # 비행기를 클릭하면 선택, 빈 곳을 클릭하면 시작
                    selected_ship = clicked[0]
                else:
                    started = pygame.time.get_ticks()

        now = pygame.time.get_ticks()
        left = None if started is None else TITLE_COUNTDOWN - (now - started) / 1000
        if left is not None and left <= 0:
            return

        screen.fill((10, 10, 30))
        for x, y, s in stars:
            pygame.draw.circle(screen, (90, 90, 130), (x, (y + now * s // 40) % H), s)

        if left is None:  # 카운트다운 중에는 게임 이름과 최고 점수 칸을 지운다
            t = title_font.render(GAME_TITLE, True, (120, 210, 255))
            screen.blit(t, t.get_rect(center=(W / 2, 110)))

        # 카운트다운이 진행될수록(0→1) 게임 시작 화면과 같아진다: 비행기가 시작 위치로 내려가며 작아지고, 상단 표시가 나타난다
        p = 0.0 if left is None else min(1.0, 1 - left / TITLE_COUNTDOWN)
        e = p * p * (3 - 2 * p)
        for i in range(3):
            chosen = i == selected_ship
            if left is not None and not chosen:  # 시작하면 고르지 않은 비행기는 사라진다
                alpha = 1 - e
                if alpha <= 0:
                    continue
            else:
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
                k = 0.8  # 고르지 않은 비행기는 조금 작고 흐리게
                alpha *= 0.55
            if sprite:
                ship = pygame.transform.smoothscale(
                    sprite, (round(sprite.get_width() * k), round(sprite.get_height() * k)))
                if alpha < 1:
                    ship.set_alpha(int(255 * alpha))
                screen.blit(ship, ship.get_rect(center=(cx, cy)))
            else:
                pygame.draw.polygon(screen, (80, 200, 255), [(cx, cy - 40), (cx - 32, cy + 32), (cx + 32, cy + 32)])
            if left is None:
                t = font.render(str(i + 1), True, (255, 220, 70) if chosen else (140, 140, 170))
                screen.blit(t, t.get_rect(center=(slot_x[i], row_y + 112)))

        if left is None:
            t = font.render("Choose your ship", True, (170, 175, 205))
            screen.blit(t, t.get_rect(center=(W / 2, row_y + 140)))

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
            box = pygame.Rect(0, 0, 360, 46)  # 최고 점수 칸
            box.center = (W / 2, H - 55)
            pygame.draw.rect(screen, (24, 28, 56), box, border_radius=8)
            pygame.draw.rect(screen, (255, 220, 70), box, 2, border_radius=8)
            t = font.render(f"My best Score  {best_score}", True, (255, 240, 170))
            screen.blit(t, t.get_rect(center=box.center))

        window.blit(pygame.transform.smoothscale(screen, window.get_size()), (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


def main():
    player = Player()
    bullets, enemy_bullets, enemies, particles, items = [], [], [], [], []
    bombs, explosions = [], []
    score, level, spawn = 0, 1, 0
    max_power_score = None  # 미사일이 최대가 된 시점의 점수
    game_over = False
    paused = False
    shop, shop_msg, play_frames = False, "", 0
    yellow_spawn = 0
    fade = 0  # 보너스 라운드로 가기 전 적이 사라지는 중이면 남은 프레임
    star_ms = 0
    stars = [(random.randint(0, W), random.randint(0, H), random.randint(1, 3)) for _ in range(60)]

    while True:
        blast = False
        buy_idx = None
        was_shop = shop
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_best(score)  # 플레이 도중 창을 닫아도 최고 점수는 남긴다
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
                    save_best(score)  # 홈으로 나가도 그때까지의 점수는 최고 점수에 반영
                    return "home"
            if shop and e.type == pygame.KEYDOWN:
                if pygame.K_1 <= e.key <= pygame.K_3:
                    buy_idx = e.key - pygame.K_1
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                    shop = False
            if shop and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse = (e.pos[0] / scale, e.pos[1] / scale)
                if SHOP_CONTINUE.collidepoint(mouse):
                    shop = False
                for i, card in enumerate(SHOP_CARDS):
                    if card.collidepoint(mouse):
                        buy_idx = i

        if was_shop and not shop:  # 다음 라운드는 처음처럼 위에서부터 적이 나타난다
            spawn = 0
            yellow_spawn = YELLOW_SPAWN_INTERVAL

        if shop and buy_idx is not None:
            name, price, kind = SHOP_ITEMS[buy_idx]
            if player.coins < price:
                shop_msg = "코인이 부족해요"
            elif kind == "heart" and player.hp >= MAX_HP:
                shop_msg = "체력이 가득 차 있어요"
            elif kind == "power" and player.power >= MAX_POWER:
                shop_msg = "미사일이 이미 최대예요"
            else:
                player.coins -= price
                if kind == "heart":
                    player.hp += 1
                elif kind == "b":
                    player.b_count += 1
                else:
                    player.power += 1
                    if player.power == MAX_POWER:
                        max_power_score = score
                shop_msg = f"{name} 구매!"

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
                it[0].y += 2
            fade -= 1
            if fade == 0:
                enemies.clear()
                enemy_bullets.clear()
                bombs.clear()
                explosions.clear()
                shop = True
                shop_msg = ""

        if not game_over and not paused and not shop and not fade:
            player.update(keys)
            if pygame.mouse.get_pressed()[0] and player.cooldown == 0:
                gap = 10 + 2 * BULLET_RADIUS
                for i in range(player.power):
                    x = player.pos.x + (i - (player.power - 1) / 2) * gap
                    bullets.append([pygame.Vector2(x, player.pos.y - 20), BULLET_RADIUS])
                player.cooldown = 10

            spawn -= 1
            normal_count = sum(1 for en in enemies if not en.yellow)  # 노란 적은 세지 않음
            if spawn <= 0 and normal_count < MAX_ENEMIES:
                for _ in range(min(1 + score // SPAWN_SCORE, MAX_ENEMIES - normal_count)):
                    enemies.append(Enemy(level, random.random() < GREEN_RATE))
                spawn = max(20, 70 - level * 5)

            yellow_spawn -= 1
            if player.power >= MAX_POWER and yellow_spawn <= 0:  # 미사일이 최대가 되면 등장
                if sum(1 for en in enemies if en.yellow) < YELLOW_MAX:
                    enemies.append(Enemy(level, yellow=True))
                yellow_spawn = YELLOW_SPAWN_INTERVAL

            for b in bullets:
                b[0].y -= 11
            bullets = [b for b in bullets if b[0].y > -30]

            for it in items:
                it[0].y += 2
                to_player = player.pos - it[0]
                dist = to_player.length()
                if 0 < dist < MAGNET_RADIUS:  # 가까워질수록 빨라지며 빨려 들어옴
                    pull = MAGNET_SPEED * (1.5 - dist / MAGNET_RADIUS)
                    it[0] += to_player.normalize() * min(pull, dist)
                if it[0].distance_to(player.pos) < 12 + player.radius:
                    if it[1] == "P":
                        if player.power < MAX_POWER:
                            player.power += 1
                            if player.power == MAX_POWER:
                                max_power_score = score
                    elif it[1] == "R":
                        player.hp = min(MAX_HP, player.hp + 1)
                    elif it[1] == "B":
                        player.b_count += 1
                    elif it[1] == "C":
                        player.coins += COIN_VALUE
                    else:
                        player.has_s = True
                    it[0].y = H + 999
            items = [it for it in items if it[0].y < H + 20]

            blast_radius = None
            if blast and player.b_count > 0:  # B가 있으면 B부터 사용
                player.b_count -= 1
                blast_radius = B_RADIUS
                enemy_bullets.clear()  # 적은 범위 안만, 적 총알은 화면 전체에서 사라진다
            elif blast and player.has_s:
                player.has_s = False
                blast_radius = BLAST_RADIUS
                enemy_bullets.clear()
            if blast_radius:
                explosions.append([player.pos.copy(), 30, blast_radius, 30])
                for en in enemies:
                    if en.pos.distance_to(player.pos) < blast_radius + en.radius:
                        en.hp = 0
                        score += 10
                        for _ in range(14):
                            a = random.uniform(0, math.tau)
                            s = random.uniform(1, 5)
                            particles.append([en.pos.copy(), pygame.Vector2(math.cos(a), math.sin(a)) * s, 30])
                enemies = [en for en in enemies if en.hp > 0]

            enemy_count = player.power
            if max_power_score is not None:
                enemy_count += (score - max_power_score) // ENEMY_SCALE_SCORE
            enemy_count = min(ENEMY_MAX_COUNT, enemy_count)

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
                        if v.length_squared():
                            enemy_bullets.append([en.pos.copy(), v.normalize() * 7])
                    elif v.length_squared():
                        aim = v.normalize()
                        for i in range(enemy_count):
                            angle = (i - (enemy_count - 1) / 2) * 12
                            enemy_bullets.append([en.pos.copy(), aim.rotate(angle) * 4])
            for eb in enemy_bullets:
                eb[0] += eb[1]
            enemy_bullets = [eb for eb in enemy_bullets if -20 < eb[0].x < W + 20 and -20 < eb[0].y < H + 20]

            bomb_hit = False
            for bm in bombs:
                to_target = bm[1] - bm[0]
                if to_target.length() > 5:
                    bm[0] += to_target.normalize() * 5
                bm[2] -= 1
                if bm[2] <= 0:
                    explosions.append([bm[0].copy(), 15, BOMB_RADIUS, 15])
                    if bm[0].distance_to(player.pos) < BOMB_RADIUS + player.radius:
                        bomb_hit = True
            bombs = [bm for bm in bombs if bm[2] > 0]
            for ex in explosions:
                ex[1] -= 1
            explosions = [ex for ex in explosions if ex[1] > 0]

            # 플레이어 총알 vs 적
            for en in enemies:
                for b in bullets:
                    if en.pos.distance_to(b[0]) < en.radius + b[1]:
                        b[0].y = -999
                        en.hp -= 1
                        if en.hp <= 0:
                            score += 10
                            if en.yellow:  # 노란 적은 코인만 떨어뜨린다
                                if random.random() < YELLOW_COIN_DROP_RATE:
                                    items.append([en.pos.copy(), "C"])
                            else:
                                p_rate, r_rate = GREEN_DROP_RATES if en.green else RED_DROP_RATES
                                roll = random.random()
                                if roll < p_rate:
                                    if player.power < MAX_POWER:
                                        items.append([en.pos.copy(), "P"])
                                elif player.power >= START_POWER + HEAL_UNLOCK_PICKUPS and roll < p_rate + r_rate:
                                    items.append([en.pos.copy(), "R"])
                                elif enemy_count >= S_UNLOCK_COUNT and player.b_count == 0 and not player.has_s and roll < p_rate + r_rate + (
                                    S_DROP_RATE if enemy_count == S_UNLOCK_COUNT else S_LATE_DROP_RATE
                                ):
                                    items.append([en.pos.copy(), "S"])
                                if random.random() < B_DROP_RATE:
                                    items.append([en.pos.copy() + (0, 14), "B"])
                                if random.random() < COIN_DROP_RATE:
                                    items.append([en.pos.copy() + (-14, 0), "C"])
                            for _ in range(14):
                                a = random.uniform(0, math.tau)
                                s = random.uniform(1, 5)
                                particles.append([en.pos.copy(), pygame.Vector2(math.cos(a), math.sin(a)) * s, 30])
                        break
            enemies = [en for en in enemies if en.hp > 0 and en.pos.y < H + 30]
            level = 1 + score // 150

            # 피격 처리
            if not player.invuln:
                # 적 비행기와 닿는 것은 괜찮고, 총알이나 폭탄에 맞을 때만 체력이 깎인다
                hit_b = [eb for eb in enemy_bullets if eb[0].distance_to(player.pos) < 12]
                if hit_b or bomb_hit:
                    player.hp -= 1
                    player.invuln = INVULN_TIME
                    enemy_bullets = [eb for eb in enemy_bullets if eb not in hit_b]
                    if player.hp <= 0:
                        game_over = True
                        save_best(score)

        if not paused and not shop:
            for p in particles:
                p[0] += p[1]
                p[2] -= 1
            particles = [p for p in particles if p[2] > 0]

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
        for ex in explosions:
            t = ex[1] / ex[3]
            pygame.draw.circle(screen, (255, 170, 60), ex[0], ex[2] * (1.2 - 0.2 * t))
            pygame.draw.circle(screen, (255, 240, 160), ex[0], ex[2] * 0.5 * t)
        for pos, kind in items:
            fill, edge = ITEM_COLORS[kind]
            dist = pos.distance_to(player.pos)
            k = 1.0
            if dist < MAGNET_RADIUS:  # 빨려 들어오는 동안 점점 작아지고 꼬리가 생김
                k = max(0.5, dist / MAGNET_RADIUS)
                tail = pos - (player.pos - pos).normalize() * (16 * (1 - k) * 2 + 6) if dist else pos
                pygame.draw.line(screen, fill, pos, tail, max(1, int(8 * k)))
            if kind == "B":  # 총알 모양
                rect = pygame.Rect(0, 0, int(18 * k), int(30 * k))
                rect.center = pos
                pygame.draw.rect(screen, fill, rect, border_radius=int(9 * k))
                pygame.draw.rect(screen, edge, rect, max(1, int(3 * k)), border_radius=int(9 * k))
            else:
                pygame.draw.circle(screen, fill, pos, 12 * k)
                pygame.draw.circle(screen, edge, pos, 12 * k, max(1, int(3 * k)))
            t = font.render("$" if kind == "C" else kind, True, edge)
            if k < 1:
                t = pygame.transform.smoothscale(t, (max(1, int(t.get_width() * k)), max(1, int(t.get_height() * k))))
            screen.blit(t, t.get_rect(center=pos))
        for eb in enemy_bullets:
            pygame.draw.circle(screen, fade_color((255, 160, 60), enemy_alpha), eb[0], 5)
        for en in enemies:
            en.draw(enemy_alpha)
        for p in particles:
            pygame.draw.circle(screen, (255, 200, 120), p[0], max(1, p[2] // 8))
        if not game_over:
            player.draw()

        draw_hud(screen, score, level, player)

        if game_over:
            t = big.render("GAME OVER", True, (255, 90, 90))
            screen.blit(t, t.get_rect(center=(W / 2, H / 2 - 20)))
            t = font.render("R 키로 다시 시작", True, (230, 230, 240))
            screen.blit(t, t.get_rect(center=(W / 2, H / 2 + 30)))

        if paused:
            dim = pygame.Surface((W, H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 150))
            screen.blit(dim, (0, 0))
            pygame.draw.rect(screen, (240, 240, 250), (W / 2 - 38, H / 2 - 70, 24, 80), border_radius=4)
            pygame.draw.rect(screen, (240, 240, 250), (W / 2 + 14, H / 2 - 70, 24, 80), border_radius=4)
            t = big.render("Pause", True, (240, 240, 250))
            screen.blit(t, t.get_rect(center=(W / 2, 170)))
            t = font.render("Press Space to Resume", True, (230, 230, 240))
            screen.blit(t, t.get_rect(center=(W / 2, H / 2 + 50)))
            hover = PAUSE_HOME.collidepoint(pygame.mouse.get_pos()[0] / scale, pygame.mouse.get_pos()[1] / scale)
            pygame.draw.rect(screen, (70, 90, 150) if hover else (40, 50, 90), PAUSE_HOME, border_radius=10)
            pygame.draw.rect(screen, (150, 190, 255), PAUSE_HOME, 2, border_radius=10)
            t = font.render("Go to Home", True, (240, 245, 255))
            screen.blit(t, t.get_rect(center=PAUSE_HOME.center))

        if shop:
            dim = pygame.Surface((W, H), pygame.SRCALPHA)
            dim.fill((0, 0, 20, 200))
            screen.blit(dim, (0, 0))
            t = big.render("보너스 라운드", True, (255, 220, 70))
            screen.blit(t, t.get_rect(center=(W / 2, 90)))
            draw_coin_icon((W / 2 - 50, 150))
            screen.blit(font.render(f"{player.coins} 코인", True, (255, 240, 170)), (W / 2 - 30, 137))
            for i, ((name, price, kind), card) in enumerate(zip(SHOP_ITEMS, SHOP_CARDS)):
                blocked = (
                    (kind == "heart" and player.hp >= MAX_HP)
                    or (kind == "power" and player.power >= MAX_POWER)
                )
                affordable = player.coins >= price and not blocked
                pygame.draw.rect(screen, (30, 34, 60) if affordable else (24, 24, 36), card, border_radius=10)
                pygame.draw.rect(screen, (255, 220, 70) if affordable else (80, 80, 100), card, 3, border_radius=10)
                cx = card.centerx
                if kind == "heart":
                    t = big.render("♥", True, (255, 100, 120))
                    screen.blit(t, t.get_rect(center=(cx, card.y + 60)))
                elif kind == "b":
                    draw_bomb_icon((cx - 6, card.y + 66), r=20)
                else:
                    pygame.draw.ellipse(screen, (255, 240, 120), (cx - 22, card.y + 30, 18, 56))
                    pygame.draw.ellipse(screen, (255, 240, 120), (cx + 4, card.y + 30, 18, 56))
                col = (230, 230, 240) if affordable else (120, 120, 140)
                t = font.render(f"[{i + 1}] {name}", True, col)
                screen.blit(t, t.get_rect(center=(cx, card.y + 125)))
                draw_coin_icon((cx - 36, card.y + 168), r=9)
                t = font.render(f"{price}", True, (255, 220, 70) if affordable else (120, 120, 140))
                screen.blit(t, t.get_rect(midleft=(cx - 20, card.y + 168)))
                if blocked:
                    t = font.render("최대", True, (255, 130, 130))
                    screen.blit(t, t.get_rect(center=(cx, card.y + 195)))
            if shop_msg:
                t = font.render(shop_msg, True, (180, 255, 190))
                screen.blit(t, t.get_rect(center=(W / 2, 425)))
            pygame.draw.rect(screen, (60, 120, 90), SHOP_CONTINUE, border_radius=10)
            t = font.render("계속하기 (Enter)", True, (240, 255, 245))
            screen.blit(t, t.get_rect(center=SHOP_CONTINUE.center))

        window.blit(pygame.transform.smoothscale(screen, window.get_size()), (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


title_screen()
while True:
    if main() == "home":  # 일시정지 화면에서 홈으로 나온 경우
        title_screen()
