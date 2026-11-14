import math
import random
import sys

import pygame

W, H = 800, 600
WINDOW_SCALE = 2   # 창 크기 배율
MAX_ENEMIES = 7    # 화면에 동시에 있을 수 있는 적의 최대 수
FPS = 60
RED_DROP_RATES = (0.02, 0.10)    # (P, R) 빨간 적: R이 잘 나옴
GREEN_DROP_RATES = (0.10, 0.05)  # (P, R) 초록 적: P가 잘 나옴
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
S_DROP_RATE = 0.10        # 적 미사일이 정확히 S_UNLOCK_COUNT개일 때
S_LATE_DROP_RATE = 0.005  # 그 이후(더 늘어난 뒤)
BLAST_RADIUS = 300
ENEMY_MAX_COUNT = 7  # 적 미사일 상한
B_START = 3          # 처음 가지고 있는 폭탄 B 개수
B_RADIUS = 150

B_DROP_RATE = 0.01  # 적 처치 시 B 아이템이 나올 확률
COIN_DROP_RATE = 0.06  # 적 처치 시 코인 아이템이 나올 확률
COIN_VALUE = 100       # 코인 아이템 1개가 주는 코인
BONUS_INTERVAL = 60    # 보너스 라운드(상점)가 열리는 간격(초, 플레이 시간 기준)
SHOP_ITEMS = [  # (이름, 가격, 종류) - 상점에는 3개만 있음
    ("하트 +1", 100, "heart"),
    ("폭탄 B +1", 200, "b"),
    ("미사일 +1", 300, "power"),
]
SHOP_CARDS = [pygame.Rect(40 + i * 250, 190, 220, 210) for i in range(3)]
SHOP_CONTINUE = pygame.Rect(300, 450, 200, 50)
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
pygame.display.set_caption("My Shooter")
clock = pygame.time.Clock()
font = pygame.font.SysFont("malgungothic", 24)
big = pygame.font.SysFont("malgungothic", 56, bold=True)


def draw_bomb_icon(center, rainbow=False, r=11):
    cx, cy = center
    for dy in range(-r, r + 1):
        hw = int(math.sqrt(r * r - dy * dy))
        color = RAINBOW[(dy + r) * len(RAINBOW) // (2 * r + 1)] if rainbow else (50, 50, 62)
        pygame.draw.line(screen, color, (cx - hw, cy + dy), (cx + hw, cy + dy))
    pygame.draw.circle(screen, (220, 220, 230), center, r, 2)
    pygame.draw.line(screen, (200, 170, 120), (cx + 5, cy - r + 2), (cx + 11, cy - r - 5), 2)
    pygame.draw.circle(screen, (255, 200, 60), (cx + 12, cy - r - 6), 3)


def draw_coin_icon(center, r=11):
    pygame.draw.circle(screen, (255, 220, 70), center, r)
    pygame.draw.circle(screen, (140, 100, 10), center, r, 2)
    pygame.draw.circle(screen, (200, 150, 20), center, r - 5, 2)


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
        x, y = self.pos
        pygame.draw.polygon(screen, (80, 200, 255), [(x, y - 18), (x - 14, y + 14), (x + 14, y + 14)])


class Enemy:
    def __init__(self, level, green=False):
        self.green = green
        self.radius = 16
        self.pos = pygame.Vector2(random.randint(30, W - 30), -20)
        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(1.2, 2.2 + level * 0.2))
        self.hp = 1 + level // 4
        self.shoot = random.randint(60, 150)

    def update(self):
        self.pos += self.vel
        if self.pos.x < 20 or self.pos.x > W - 20:
            self.vel.x *= -1
        self.shoot -= 1

    def draw(self):
        fill, edge = ((70, 210, 90), (20, 90, 30)) if self.green else ((255, 90, 90), (120, 20, 20))
        pygame.draw.circle(screen, fill, self.pos, self.radius)
        pygame.draw.circle(screen, edge, self.pos, self.radius, 3)


def main():
    player = Player()
    bullets, enemy_bullets, enemies, particles, items = [], [], [], [], []
    bombs, explosions = [], []
    score, level, spawn = 0, 1, 0
    max_power_score = None  # 미사일이 최대가 된 시점의 점수
    game_over = False
    paused = False
    shop, shop_msg, play_frames = False, "", 0
    star_ms = 0
    stars = [(random.randint(0, W), random.randint(0, H), random.randint(1, 3)) for _ in range(60)]

    while True:
        blast = False
        buy_idx = None
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
                blast = True
            if e.type == pygame.KEYDOWN and game_over and e.key == pygame.K_r:
                return
            if e.type == pygame.KEYDOWN and not game_over and not shop and e.key == pygame.K_SPACE:
                paused = not paused
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

        if not (game_over or paused or shop):
            play_frames += 1
            if play_frames % (BONUS_INTERVAL * FPS) == 0:
                shop = True
                shop_msg = ""

        if not game_over and not paused and not shop:
            player.update(keys)
            if pygame.mouse.get_pressed()[0] and player.cooldown == 0:
                gap = 10 + 2 * BULLET_RADIUS
                for i in range(player.power):
                    x = player.pos.x + (i - (player.power - 1) / 2) * gap
                    bullets.append([pygame.Vector2(x, player.pos.y - 20), BULLET_RADIUS])
                player.cooldown = 10

            spawn -= 1
            if spawn <= 0 and len(enemies) < MAX_ENEMIES:
                for _ in range(min(1 + score // SPAWN_SCORE, MAX_ENEMIES - len(enemies))):
                    enemies.append(Enemy(level, random.random() < GREEN_RATE))
                spawn = max(20, 70 - level * 5)

            for b in bullets:
                b[0].y -= 11
            bullets = [b for b in bullets if b[0].y > -30]

            for it in items:
                it[0].y += 2
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
                enemy_bullets = [eb for eb in enemy_bullets if eb[0].distance_to(player.pos) > B_RADIUS]
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
                hit = any(en.pos.distance_to(player.pos) < en.radius + 10 for en in enemies)
                hit_b = [eb for eb in enemy_bullets if eb[0].distance_to(player.pos) < 12]
                if hit or hit_b or bomb_hit:
                    player.hp -= 1
                    player.invuln = INVULN_TIME
                    enemy_bullets = [eb for eb in enemy_bullets if eb not in hit_b]
                    if player.hp <= 0:
                        game_over = True

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
        for bm in bombs:
            blink = (bm[2] // 6) % 2 == 0 or bm[2] > 40
            pygame.draw.circle(screen, (255, 80, 80), bm[1], BOMB_RADIUS, 1)
            pygame.draw.circle(screen, (255, 60, 60) if blink and bm[2] <= 40 else (40, 40, 50), bm[0], 9)
            pygame.draw.circle(screen, (200, 200, 210), bm[0], 9, 2)
        for ex in explosions:
            t = ex[1] / ex[3]
            pygame.draw.circle(screen, (255, 170, 60), ex[0], ex[2] * (1.2 - 0.2 * t))
            pygame.draw.circle(screen, (255, 240, 160), ex[0], ex[2] * 0.5 * t)
        for pos, kind in items:
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
            pygame.draw.circle(screen, (255, 160, 60), eb[0], 5)
        for en in enemies:
            en.draw()
        for p in particles:
            pygame.draw.circle(screen, (255, 200, 120), p[0], max(1, p[2] // 8))
        if not game_over:
            player.draw()

        screen.blit(font.render(f"점수 {score}   레벨 {level}   미사일 {player.power}", True, (230, 230, 240)), (12, 10))
        screen.blit(font.render("♥ " * player.hp, True, (255, 100, 120)), (W - 150, 10))
        draw_coin_icon((W - 138, 54))
        screen.blit(font.render(f"{player.coins}", True, (255, 220, 70)), (W - 118, 41))
        draw_bomb_icon((24, 56))
        screen.blit(font.render(f"× {player.b_count}", True, (255, 210, 120)), (44, 43))
        if player.has_s:
            draw_bomb_icon((24, 92), rainbow=True)
            screen.blit(font.render("오른쪽 클릭!", True, (180, 220, 255)), (44, 79))

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
            t = font.render("일시정지 — 스페이스바로 계속", True, (230, 230, 240))
            screen.blit(t, t.get_rect(center=(W / 2, H / 2 + 50)))

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


while True:
    main()
