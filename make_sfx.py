"""효과음 만들기: python make_sfx.py [이름...]  ->  assets/sfx/*.ogg  (pip install soundfile numpy 가 필요하다)
녹음 파일이 아니라 직접 합성한다: 잡음 + 낮은 쿵 소리 + 필터 + 잔향(울림) + 살짝 찌그러뜨리기(포화)로 실제 총소리/폭발음에 가깝게 만든다.
소리마다 a, b 두 가지를 만든다. 마음에 드는 쪽은 shooter.py 위쪽 SFX_CHOICE에서 고른다.
예: python make_sfx.py hit  -> hit_*만 새로 저장한다. 웹 빌드(pygbag)가 WAV를 받지 않고 OGG만 받아서 OGG로 저장한다."""
import math
import os
import random
import sys

SR = 44100  # 샘플 속도
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sfx")
random.seed(7)  # 만들 때마다 같은 소리가 나오게
ONLY = sys.argv[1:]


# ── 기본 재료 ────────────────────────────────────────────
def noise(n):
    return [random.uniform(-1, 1) for _ in range(n)]


def env(n, decay, attack=0.002):
    """빠르게 커졌다가 지수로 줄어드는 크기 곡선."""
    out = []
    for i in range(n):
        t = i / SR
        out.append((min(1.0, t / attack) if attack > 0 else 1.0) * math.exp(-t * decay))
    return out


def sweep_phase(f0, f1, n, curve=1.0):
    ph, out = 0.0, []
    for i in range(n):
        t = i / max(1, n - 1)
        ph += 2 * math.pi * (f0 + (f1 - f0) * (t ** curve)) / SR
        out.append(ph)
    return out


def lowpass(x, cutoffs):
    """한 극 저역 필터. cutoffs는 숫자 하나(Hz) 또는 샘플마다의 목록 (점점 어두워지는 소리를 만들 때)."""
    y, out = 0.0, []
    for i, v in enumerate(x):
        fc = cutoffs[i] if isinstance(cutoffs, list) else cutoffs
        a = 1.0 - math.exp(-2 * math.pi * fc / SR)
        y += a * (v - y)
        out.append(y)
    return out


def highpass(x, fc):
    lp = lowpass(x, fc)
    return [v - l for v, l in zip(x, lp)]


def bandpass(x, lo, hi):
    return lowpass(highpass(x, lo), hi)


def sat(x, drive):
    """살짝 찌그러뜨려서 묵직하고 꽉 찬 소리로 만든다 (tanh)."""
    k = 1.0 / math.tanh(drive)
    return [math.tanh(v * drive) * k for v in x]


def reverb(x, wet=0.3, size=1.0, tail=0.4):
    """슈뢰더 잔향: 소리가 공간에서 울리는 느낌. tail은 여운 길이(초)."""
    delays = [int(d * size) for d in (1557, 1617, 1491, 1422)]
    n = len(x) + int(tail * SR)
    xi = x + [0.0] * (n - len(x))
    comb_sum = [0.0] * n
    for d in delays:
        g = 0.001 ** (d / SR / max(0.05, tail))  # 여운 길이에 맞는 되먹임
        buf = [0.0] * n
        for i in range(n):
            buf[i] = xi[i] + (buf[i - d] * g if i >= d else 0.0)
        for i in range(n):
            comb_sum[i] += buf[i] * 0.25
    out = comb_sum
    for d, g in ((225, 0.5), (556, 0.5)):  # 올패스로 반사음을 퍼뜨린다
        buf = [0.0] * n
        res = [0.0] * n
        for i in range(n):
            delayed = buf[i - d] if i >= d else 0.0
            buf[i] = out[i] + g * delayed
            res[i] = -g * buf[i] + delayed
        out = res
    return [xi[i] * (1.0 - wet) + out[i] * wet * 2.0 for i in range(n)]


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
    return [v * k for v in a]


def delay(a, sec):
    return [0.0] * int(sec * SR) + a


def save(name, samples, peak=0.8):  # 0.8: OGG로 압축하면 조금 튀어서 여유를 둔다
    if ONLY and not any(name.startswith(o) for o in ONLY):
        return
    import numpy as np
    import soundfile as sf
    m = max(abs(v) for v in samples) or 1.0
    k = peak / m
    n = len(samples)
    fade = int(SR * 0.01)  # 끝을 줄여서 딱 소리(클릭)가 나지 않게
    data = np.array([v * k * (min(1.0, (n - i) / fade) if fade else 1.0) for i, v in enumerate(samples)], dtype="float32")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".ogg")
    sf.write(path, data, SR, format="OGG", subtype="VORBIS")
    print("%-10s %.2fs %5.1f KB" % (name, n / SR, os.path.getsize(path) / 1024))


# ── 총알 쏠 때: 실제 총소리처럼 "탕/타다닥" (자주 나는 소리라 짧게) ──────────
# a: 소총 "탕" = 날카로운 총성(고음 잡음) + 몸통 + 낮은 반동 + 짧은 울림
n = int(SR * 0.16)
crack = mul(highpass(noise(n), 1800), env(n, 170, 0.0003))
body = mul(lowpass(noise(n), 1200), env(n, 38, 0.0005))
kick = mul(sine(sweep_phase(240, 70, n, 0.5)), env(n, 42, 0.0005))
shot = sat(mix(scale(crack, 1.0), scale(body, 0.9), scale(kick, 0.8)), 1.8)
save("shoot_a", reverb(shot, wet=0.22, size=0.7, tail=0.18))
# b: 권총 "탁" = 더 작고 건조한 소리 (울림 거의 없음)
n = int(SR * 0.1)
crack = mul(highpass(noise(n), 2500), env(n, 230, 0.0003))
body = mul(bandpass(noise(n), 300, 2500), env(n, 55, 0.0004))
kick = mul(sine(sweep_phase(420, 150, n, 0.5)), env(n, 60, 0.0004))
save("shoot_b", sat(mix(scale(crack, 1.0), scale(body, 0.8), scale(kick, 0.5)), 1.6))

# ── 폭탄 터질 때: 실제 폭발음 (갈라지는 소리 → 쾅 → 낮게 울리며 사라지는 소리) ─────
# a: 가까운 폭발: 번쩍 갈라지는 소리 + 점점 낮아지는 쾅 + 아주 낮은 쿵 + 파편 튀는 소리 + 공간 울림
n = int(SR * 1.3)
crack = mul(highpass(noise(n), 1500), env(n, 55, 0.0003))
cutoffs = [4500 * math.exp(-i / SR * 5.5) + 140 for i in range(n)]
boom = mul(lowpass(noise(n), cutoffs), env(n, 3.4, 0.0015))
sub = mul(sine(sweep_phase(95, 28, n, 0.45)), env(n, 5.0, 0.002))
rumble = mul(bandpass(noise(n), 40, 220), env(n, 2.2, 0.01))
debris = delay([(random.uniform(-1, 1) * 0.9 if random.random() < 0.0035 else 0.0) * math.exp(-i / SR * 3.2) for i in range(n)], 0.05)[:n]
debris = highpass(debris, 600)
bomb = sat(mix(scale(crack, 0.5), scale(boom, 1.0), scale(sub, 1.2), scale(rumble, 0.9), scale(debris, 0.35)), 2.2)
save("bomb_a", reverb(bomb, wet=0.33, size=1.2, tail=0.7))
# b: 멀리서 크게 터지는 폭발: 갈라지는 소리가 둔하고, 낮은 울림이 훨씬 길다
n = int(SR * 1.9)
cutoffs = [2600 * math.exp(-i / SR * 3.2) + 90 for i in range(n)]
boom = mul(lowpass(noise(n), cutoffs), env(n, 2.2, 0.012))
sub = mul(sine(sweep_phase(70, 24, n, 0.4)), env(n, 3.0, 0.01))
rumble = mul(bandpass(noise(n), 30, 160), env(n, 1.5, 0.03))
thud = mul(lowpass(noise(n), 400), env(n, 30, 0.002))
bomb = sat(mix(scale(boom, 1.0), scale(sub, 1.4), scale(rumble, 1.1), scale(thud, 0.7)), 2.0)
save("bomb_b", reverb(bomb, wet=0.42, size=1.5, tail=1.1))

# ── 내가 적을 맞혔을 때: 약한 폭탄이 터지는 "펑!" (bomb보다 작고 짧게) ──────────────
# a: 또렷한 펑: 짧은 갈라짐 + 빠르게 어두워지는 쾅 + 낮은 쿵 + 작은 울림
n = int(SR * 0.3)
crack = mul(highpass(noise(n), 2000), env(n, 160, 0.0003))
cutoffs = [4500 * math.exp(-i / SR * 24) + 220 for i in range(n)]
puff = mul(lowpass(noise(n), cutoffs), env(n, 17, 0.0008))
thump = mul(sine(sweep_phase(170, 60, n, 0.5)), env(n, 20, 0.001))
hit = sat(mix(scale(crack, 0.45), scale(puff, 1.0), scale(thump, 1.1)), 1.9)
save("hit_a", reverb(hit, wet=0.2, size=0.8, tail=0.22))
# b: 둥근 펑(퐁): 낮은 소리가 중심이고 잡음이 부드럽다
n = int(SR * 0.33)
cutoffs = [1800 * math.exp(-i / SR * 20) + 160 for i in range(n)]
puff = mul(lowpass(noise(n), cutoffs), env(n, 14, 0.002))
thump = mul(sine(sweep_phase(125, 48, n, 0.6)), env(n, 13, 0.0015))
hit = sat(mix(scale(puff, 0.8), scale(thump, 1.3)), 1.7)
save("hit_b", reverb(hit, wet=0.24, size=0.9, tail=0.26))

# ── 내가 공격받았을 때: 비행기 몸체가 얻어맞는 충격음 ───────────────────────────────
# a: 쾅 + 철판이 울리는 소리: 낮은 충격 + 갈라짐 + 금속 울림(여러 높이의 소리가 길게 남는다) + 찌그러짐
n = int(SR * 0.7)
thud = mul(sine(sweep_phase(150, 42, n, 0.5)), env(n, 11, 0.001))
crunch = mul(bandpass(noise(n), 200, 3500), env(n, 26, 0.0006))
metal = [0.0] * n
for f, amp, dec in ((312, 0.5, 9), (523, 0.4, 11), (877, 0.3, 14), (1290, 0.25, 17), (2130, 0.15, 22)):
    f2 = f * (1 + random.uniform(-0.02, 0.02))
    for i in range(n):
        t = i / SR
        metal[i] += amp * math.sin(2 * math.pi * f2 * t) * math.exp(-t * dec)
hurt = sat(mix(scale(thud, 1.2), scale(crunch, 0.9), scale(metal, 0.5)), 2.6)
save("hurt_a", reverb(hurt, wet=0.22, size=0.9, tail=0.35))
# b: 쾅 + 전기가 튀는 지직 소리 (합선되는 느낌)
n = int(SR * 0.6)
thud = mul(sine(sweep_phase(120, 40, n, 0.5)), env(n, 12, 0.001))
burst = mul(lowpass(noise(n), 1500), env(n, 30, 0.0006))
buzz_src = bandpass(noise(n), 1200, 4500)
gate = [1.0 if (i / SR * 70) % 1.0 < 0.5 else 0.15 for i in range(n)]  # 70Hz로 끊기는 지직거림
zap = mul(mul(buzz_src, gate), env(n, 9, 0.0008))
hurt = sat(mix(scale(thud, 1.1), scale(burst, 0.9), scale(zap, 0.6)), 2.4)
save("hurt_b", reverb(hurt, wet=0.18, size=0.8, tail=0.3))
