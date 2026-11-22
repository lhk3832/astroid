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


def norm(x):
    m = max(abs(v) for v in x) or 1.0
    return [v / m for v in x]


def rumble(n, fc, passes=2):
    """낮은 웅웅거림: 잡음을 낮은 소리만 남기게 여러 번 걸러서(passes번) 만든다. 북소리처럼 음높이가 있는 쿵이 아니라 거친 낮은 덩어리."""
    x = noise(n)
    for _ in range(passes):
        x = lowpass(x, fc)
    x = norm(highpass(x, 35))  # 35Hz 아래는 스피커로 거의 안 들리고 소리 크기만 잡아먹어서 뺀다
    wob = norm(lowpass(noise(n), 22))  # 소리 크기가 자연스럽게 출렁이게 (참고 소리처럼 +-3dB 정도)
    return [v * (1.0 + 0.22 * w) for v, w in zip(x, wob)]


def hold_env(n, hold, decay, attack=0.004):
    """한동안 크게 이어지다가(hold초) 지수로 줄어드는 크기 곡선: 폭발의 "웅~" 하고 이어지는 부분."""
    out = []
    for i in range(n):
        t = i / SR
        a = min(1.0, t / attack) if attack > 0 else 1.0
        out.append(a * (1.0 if t < hold else math.exp(-(t - hold) * decay)))
    return out


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

# ── 폭탄 터질 때 / 적을 맞혔을 때 / 내가 맞았을 때: 낮게 웅웅거리는 폭발음 ───────────────
# 참고 소리(Explosionnn!.mp3)를 분석해 보니 150Hz 아래의 낮은 소리가 약 75%이고, 1초 가까이 크게 이어지다가 천천히 줄어든다.
# 사인파 "쿵"(북소리 같음) 대신 낮은 잡음 덩어리(rumble)를 오래 이어 붙이고, 중저음 몸통과 약간의 갈라짐을 얹는다.
# 작은 스피커는 아주 낮은 소리를 못 내서, 찌그러뜨리기(sat)로 높은 배음을 만들어 들리게 한다. 길이는 모두 0.5~1초.
def explosion(dur, tail, sub_fc, hold, decay, mid_w, mid_decay, crack_w, crack_decay, drive, extra=None):
    n = int(SR * dur)
    sub = mul(rumble(n, sub_fc, 2), hold_env(n, hold, decay))
    body = mul(rumble(n, 420, 2), hold_env(n, hold * 0.35, mid_decay))
    crack = mul(bandpass(noise(n), 700, 5000), env(n, crack_decay, 0.0008))
    click = mul(highpass(noise(n), 3000), env(n, 500, 0.0001))
    layers = [scale(sub, 1.0), scale(body, mid_w), scale(norm(crack), crack_w), scale(norm(click), 0.18)]
    if extra:
        layers.append(extra(n))
    x = sat(mix(*layers), drive)
    return reverb(x, wet=0.16, size=0.7, tail=tail)


# bomb_a: 큰 폭발 약 1초. 낮은 웅웅거림이 0.35초 이어지다 줄어든다
save("bomb_a", explosion(0.85, 0.15, 110, 0.35, 8.5, 0.5, 9, 0.25, 35, 3.0))
# bomb_b: 더 깊고 오래 이어지는 폭발 (낮은 소리가 더 낮고, 중저음 거친 소리가 조금 더 많다)
save("bomb_b", explosion(0.9, 0.1, 85, 0.45, 7.5, 0.7, 7, 0.2, 30, 3.2))
# hit_a: 적을 맞혔을 때 0.5초. 짧게 웅! 하고 줄어든다 (자주 나는 소리라 짧게)
save("hit_a", explosion(0.42, 0.08, 120, 0.08, 14, 0.7, 16, 0.35, 45, 3.0))
# hit_b: 더 무겁고 낮은 쪽
save("hit_b", explosion(0.45, 0.05, 95, 0.12, 11, 0.5, 13, 0.25, 40, 3.2))


def hull_clang(n):
    """비행기 몸체(철판)가 울리는 작은 금속 소리"""
    out = [0.0] * n
    for f, amp, dec in ((300, 0.5, 14), (520, 0.4, 17), (880, 0.3, 20)):
        f2 = f * (1 + random.uniform(-0.02, 0.02))
        for i in range(n):
            t = i / SR
            out[i] += amp * math.sin(2 * math.pi * f2 * t) * math.exp(-t * dec)
    return scale(norm(out), 0.22)


def zap_buzz(n):
    """합선되어 전기가 튀는 지직 소리 (60Hz로 끊김)"""
    gate = [1.0 if (i / SR * 60) % 1.0 < 0.5 else 0.12 for i in range(n)]
    return scale(norm(mul(mul(bandpass(noise(n), 1200, 4500), gate), env(n, 8, 0.001))), 0.45)


# hurt_a: 내가 맞았을 때 약 0.8초. hit보다 길고 크고, 철판 울림이 섞인다
save("hurt_a", explosion(0.68, 0.12, 130, 0.18, 9, 0.8, 11, 0.4, 40, 3.2, hull_clang))
# hurt_b: 합선되어 지직거리는 소리가 섞인 쪽
save("hurt_b", explosion(0.68, 0.12, 110, 0.15, 9, 0.7, 10, 0.35, 38, 3.2, zap_buzz))
