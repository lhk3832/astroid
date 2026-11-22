"""효과음 만들기: python make_sfx.py  ->  assets/sfx/*.ogg  (pip install soundfile numpy 가 필요하다)
소리를 직접 합성해서 만든다. 소리마다 a, b 두 가지를 만든다. 마음에 드는 쪽은 shooter.py 위쪽 SFX_CHOICE에서 고른다.
웹 빌드(pygbag)가 WAV를 받지 않고 OGG만 받아서 OGG로 저장한다."""
import math
import os
import random
import sys

SR = 22050  # 샘플 속도 (작고 가볍게)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sfx")
random.seed(7)  # 만들 때마다 같은 소리가 나오게
ONLY = sys.argv[1:]  # 예: python make_sfx.py hit  -> hit_*만 새로 저장한다 (나머지 소리 파일은 그대로 둔다)


def sweep(f0, f1, dur, curve=1.0):
    """주파수가 f0에서 f1로 변하는 동안의 위상(라디안) 목록."""
    n = int(SR * dur)
    ph, out = 0.0, []
    for i in range(n):
        t = i / max(1, n - 1)
        f = f0 + (f1 - f0) * (t ** curve)
        ph += 2 * math.pi * f / SR
        out.append(ph)
    return out


def env(n, decay, attack=0.004):
    """빠르게 커졌다가 지수로 줄어드는 소리 크기 곡선."""
    out = []
    for i in range(n):
        t = i / SR
        a = min(1.0, t / attack) if attack > 0 else 1.0
        out.append(a * math.exp(-t * decay))
    return out


def lowpass_noise(n, alphas):
    """alphas(0~1, 클수록 높은 소리가 많다)에 따라 걸러진 잡음."""
    y, out = 0.0, []
    for i in range(n):
        a = alphas[i] if isinstance(alphas, list) else alphas
        y += a * (random.uniform(-1, 1) - y)
        out.append(y)
    return out


def square(ph, duty=0.5):
    return [1.0 if (p / (2 * math.pi)) % 1.0 < duty else -1.0 for p in ph]


def saw(ph):
    return [2.0 * ((p / (2 * math.pi)) % 1.0) - 1.0 for p in ph]


def tri(ph):
    return [2.0 * abs(2.0 * ((p / (2 * math.pi)) % 1.0) - 1.0) - 1.0 for p in ph]


def sine(ph):
    return [math.sin(p) for p in ph]


def mix(*tracks):
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for t in tracks:
        for i, v in enumerate(t):
            out[i] += v
    return out


def mul(a, b):
    return [x * y for x, y in zip(a, b)]


def scale(a, k):
    return [x * k for x in a]


def save(name, samples, peak=0.85):
    if ONLY and not any(name.startswith(o) for o in ONLY):
        return
    import numpy as np
    import soundfile as sf
    m = max(abs(v) for v in samples) or 1.0
    k = peak / m
    fade = int(SR * 0.004)  # 끝을 살짝 줄여서 딱 소리(클릭)가 나지 않게
    n = len(samples)
    data = np.array([v * k * (min(1.0, (n - i) / fade) if fade else 1.0) for i, v in enumerate(samples)], dtype="float32")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".ogg")
    sf.write(path, data, SR, format="OGG", subtype="VORBIS")
    print("%-10s %.2fs %5.1f KB" % (name, n / SR, os.path.getsize(path) / 1024))


# ── 총알 쏠 때 ────────────────────────────────────────
# a: 레이저 "퓨" (높은 소리에서 빠르게 내려오는 가는 펄스)
ph = sweep(1500, 380, 0.14, 0.6)
a = mul(square(ph, 0.25), env(len(ph), 24))
save("shoot_a", a)
# b: 짧고 부드러운 "삑" (삼각파 + 첫 순간의 작은 딸깍)
ph = sweep(1000, 640, 0.09)
b = mul(tri(ph), env(len(ph), 38))
click = [v * 0.5 for v in mul(lowpass_noise(len(ph), 0.7), env(len(ph), 300, 0))]
save("shoot_b", mix(b, click))

# ── 폭탄 터질 때 ──────────────────────────────────────
# a: 탕! 하고 단단하게 터지는 폭발 (잡음이 점점 낮아지고 낮은 쿵 소리가 받쳐 준다)
n = int(SR * 0.8)
alphas = [0.55 * math.exp(-i / SR * 5) + 0.03 for i in range(n)]
noise = mul(lowpass_noise(n, alphas), env(n, 4.5, 0.002))
thump = mul(sine(sweep(130, 38, 0.8, 0.5)), env(n, 7, 0.002))
save("bomb_a", mix(scale(noise, 1.0), scale(thump, 1.1)))
# b: 낮게 울리는 묵직한 폭발 (더 길고, 끝에 자글거리는 소리가 있다)
n = int(SR * 1.2)
rumble = mul(lowpass_noise(n, 0.07), env(n, 2.6, 0.02))
sub = mul(sine(sweep(62, 38, 1.2, 0.7)), env(n, 3.2, 0.015))
crackle = [(random.uniform(-1, 1) if random.random() < 0.012 else 0.0) * math.exp(-i / SR * 2.2) for i in range(n)]
save("bomb_b", mix(scale(rumble, 1.3), scale(sub, 1.0), scale(lowpass_noise(n, 0.5), 0.0), scale(crackle, 0.35)))

# ── 내가 적을 맞혔을 때: 약한 폭탄이 터지는 "펑!" (bomb보다 작고 짧다. 자주 나는 소리라 짧게) ──
# a: 펑! (잡음이 확 터졌다 빠르게 낮아지고, 낮은 쿵이 받쳐 준다)
n = int(SR * 0.25)
alphas = [0.5 * math.exp(-i / SR * 22) + 0.05 for i in range(n)]
puff = mul(lowpass_noise(n, alphas), env(n, 17, 0.001))
thump = mul(sine(sweep(170, 62, 0.25, 0.5)), env(n, 19, 0.001))
save("hit_a", mix(scale(puff, 0.9), scale(thump, 1.0)))
# b: 퐁! (더 둥글고 낮은 펑: 낮은 소리가 중심이고 잡음은 부드럽다)
n = int(SR * 0.28)
body = mul(sine(sweep(120, 52, 0.28, 0.6)), env(n, 13, 0.002))
soft = mul(lowpass_noise(n, 0.13), env(n, 24, 0.001))
save("hit_b", mix(body, scale(soft, 0.9)))

# ── 내가 공격받았을 때 ─────────────────────────────────
# a: 거친 톱니파가 낮게 떨어지는 "우웅" + 잡음
n = int(SR * 0.4)
body = mul(saw(sweep(260, 80, 0.4, 0.7)), env(n, 6, 0.002))
grit = mul(lowpass_noise(n, 0.3), env(n, 9, 0.001))
save("hurt_a", mix(body, scale(grit, 0.7)))
# b: 떨리며 내려가는 네모파 "워어" + 처음의 큰 잡음
n = int(SR * 0.45)
ph = sweep(430, 110, 0.45, 0.6)
vib = [p + 0.9 * math.sin(2 * math.pi * 24 * i / SR) for i, p in enumerate(ph)]
body = mul(square(vib, 0.5), env(n, 5.5, 0.002))
burst = mul(lowpass_noise(n, 0.7), env(n, 40, 0.001))
save("hurt_b", mix(scale(body, 0.8), scale(burst, 0.9)))
