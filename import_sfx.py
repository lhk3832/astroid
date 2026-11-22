"""녹음된 효과음 가져오기: python import_sfx.py <Kenney Sci-Fi Sounds를 푼 폴더> [<25 CC0 bang / firework SFX를 푼 폴더>]
두 CC0 묶음에서 필요한 소리를 골라 잘라서 겹쳐 assets/sfx/에 넣는다 (스테레오: 소리마다 좌우 자리를 달리해서 더 생생하게).
  Kenney "Sci-Fi Sounds"  https://opengameart.org/content/sci-fi-sounds   (CC0)
  rubberduck "25 CC0 bang / firework SFX" https://opengameart.org/content/25-cc0-bang-firework-sfx (CC0, 직접 녹음한 폭음과 총소리)
  shoot    <- 직접 녹음된 총소리 shot_03 / shot_02
  bomb     <- 녹음된 폭음(cannon) + 길고 낮은 울림 + 갈라지는 소리 + 파편 소리를 겹친 약 2초의 폭발
  hit      <- 녹음된 짧은 폭음(bang) + 낮은 폭발음의 앞부분 (0.4초)
  hurt     <- 금속 충격음 + 낮은 폭발음 + 녹음된 총소리의 갈라지는 소리
  gameover <- 여러 폭음과 낮은 울림을 가장 크게 겹친 약 2.4초의 가장 강렬한 폭발
원본 파일은 저장소에 넣지 않고, 잘라 겹친 결과(.ogg)만 assets/sfx/에 둔다. (pip install soundfile numpy 필요)"""
import math
import os
import sys

import numpy as np
import soundfile as sf

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get("TEMP", "."), "kenney_files", "Audio")
BANG = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.environ.get("TEMP", "."), "oga_bang", "x")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sfx")
RATE = 44100  # 모든 소리를 이 속도로 맞춘다


def load(name):
    d, sr = sf.read(os.path.join(SRC, name + ".ogg"))
    if d.ndim > 1:
        d = d.mean(axis=1)  # 스테레오는 모노로 합친다
    return d, sr


def cut(d, sr, start, dur):
    return d[int(start * sr):int((start + dur) * sr)].copy()


def fades(x, sr, fade_in, fade_out, curve=2.0):
    """앞은 fade_in초 동안 커지고, 뒤는 fade_out초 동안 부드럽게 사라진다 (딱 소리가 나지 않게). 모노/스테레오 모두 된다."""
    n = len(x)
    a, b = int(fade_in * sr), int(fade_out * sr)
    g = np.ones(n)
    if a > 0:
        g[:a] = np.linspace(0, 1, a) ** 1.5
    if b > 0:
        g[n - b:] *= np.linspace(1, 0, b) ** curve
    return x * (g[:, None] if x.ndim == 2 else g)


def whoosh(x, sr, rise, fall):
    """미사일이 날아 지나가는 "슝": rise초 동안 커졌다가 fall초 동안 줄어든다."""
    n = len(x)
    t = np.arange(n) / sr
    peak = rise
    g = np.where(t < peak, (t / peak) ** 1.5, np.exp(-(t - peak) * (4.0 / fall)))
    return x * g



def load_any(folder, name, rate=RATE):
    """folder의 name.ogg를 모노로 읽어서 rate로 맞춘다 (속도가 다르면 보간)."""
    d, sr = sf.read(os.path.join(folder, name + ".ogg"))
    if d.ndim > 1:
        d = d.mean(axis=1)
    if sr != rate:
        n = int(len(d) * rate / sr)
        d = np.interp(np.linspace(0, len(d) - 1, n), np.arange(len(d)), d)
    return d


def layers(parts, drive=1.0):
    """(소리, 크기, 늦게 시작할 초) 목록을 겹친다. 소리마다 먼저 평균 크기(RMS)를 맞춘 뒤 크기를 곱하고,
    drive가 1보다 크면 살짝 찌그러뜨려서(tanh) 더 꽉 차고 크게 들리게 한다."""
    end = max(int(dl * RATE) + len(x) for x, g, dl in parts)
    out = np.zeros(end)
    for x, g, dl in parts:
        x = x / (np.sqrt(np.mean(x ** 2)) or 1.0) * 0.18 * g  # 소리마다 평균 크기(RMS)를 맞춘다: 갈라지는 순간이 낮은 울림에 묻히지 않게
        i0 = int(dl * RATE)
        out[i0:i0 + len(x)] += x
    out = np.tanh(out * drive) / np.tanh(drive)  # 겹쳐서 너무 커진 부분은 부드럽게 눌러 준다 (drive가 클수록 더 꽉 차고 크게 들린다)
    return out


def st_layers(parts, drive=1.0):
    """스테레오로 겹친다. parts = (소리, 크기, 늦게 시작할 초, 좌우 자리(-1 왼쪽 ~ 1 오른쪽), 넓히기).
    넓히기(True)는 낮은 울림처럼 퍼지는 소리용: 오른쪽을 12ms 늦춰서 양쪽에서 감싸듯 들리게 한다.
    소리마다 평균 크기(RMS)를 먼저 맞춘 뒤 크기를 곱하고, 마지막에 눌러서(tanh) 꽉 차게 한다."""
    wd = int(0.012 * RATE)
    end = max(int(dl * RATE) + len(x) + (wd if wide else 0) for x, g, dl, pan, wide in parts)
    left, right = np.zeros(end), np.zeros(end)
    for x, g, dl, pan, wide in parts:
        x = x / (np.sqrt(np.mean(x ** 2)) or 1.0) * 0.18 * g
        i0 = int(dl * RATE)
        if wide:
            left[i0:i0 + len(x)] += x * 0.8
            right[i0 + wd:i0 + wd + len(x)] += x * 0.8
        else:
            ang = (pan + 1) * np.pi / 4
            left[i0:i0 + len(x)] += x * np.cos(ang)
            right[i0:i0 + len(x)] += x * np.sin(ang)
    out = np.stack([left, right], axis=1)
    return np.tanh(out * drive) / np.tanh(drive)


def save(name, x, sr, peak=0.8):
    x = x / (np.max(np.abs(x)) or 1.0) * peak
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".ogg")
    for _ in range(6):  # OGG로 압축하면 소리가 조금 튀어서, 1을 넘으면(소리가 깨짐) 낮춰서 다시 저장한다
        sf.write(path, x.astype("float32"), sr, format="OGG", subtype="VORBIS")
        back, _sr = sf.read(path)
        if np.max(np.abs(back)) < 0.97:
            break
        x = x * 0.92
    print("%-10s %.2fs %s %5.1f KB" % (name, len(x) / sr, "스테레오" if x.ndim == 2 else "모노", os.path.getsize(path) / 1024))


def part(name, src, start=0.0, dur=None):
    """src 폴더의 소리를 읽어 start초부터 dur초만 잘라 낸다."""
    d = load_any(src, name)
    i0 = int(start * RATE)
    return d[i0:i0 + int(dur * RATE)] if dur else d[i0:]


# 쏘는 소리: 직접 녹음된 총소리 (한 번 쏠 때 한 번, 자주 나서 짧게). 마지막을 부드럽게 줄여 딸깍 소리를 막는다
save("shoot_a", fades(part("shot_03", BANG), RATE, 0.0, 0.06), RATE)
save("shoot_b", fades(part("shot_02", BANG, 0.0, 0.3), RATE, 0.0, 0.12), RATE)

# 폭탄(평소의 폭발, 약 2초): 녹음된 폭음의 갈라지는 순간 + 길고 낮은 울림(양쪽으로 퍼짐) + 갈라지는 소리 + 멀리 튀는 파편 소리
cn1, cn2, cn3 = part("cannon_01", BANG), part("cannon_02", BANG), part("cannon_03", BANG)
low0, low1 = part("lowFrequency_explosion_000", SRC), part("lowFrequency_explosion_001", SRC)
cr0, cr2, cr3, cr4 = (part("explosionCrunch_000", SRC), part("explosionCrunch_002", SRC),
                      part("explosionCrunch_003", SRC), part("explosionCrunch_004", SRC))
save("bomb_a", fades(st_layers([(cn1, 1.0, 0.0, 0.0, False), (low0, 0.9, 0.0, 0.0, True), (cr0, 0.5, 0.0, 0.0, True),
                                (part("bang_06", BANG), 0.5, 0.03, -0.35, False), (part("fw_02", BANG), 0.35, 0.25, 0.4, False)], 1.4),
                     RATE, 0.0, 0.35), RATE)
save("bomb_b", fades(st_layers([(cn2, 1.0, 0.0, 0.0, False), (cr3, 0.9, 0.05, 0.0, True),
                                (part("bang_09", BANG), 0.5, 0.02, 0.3, False), (part("fw_06", BANG), 0.3, 0.3, -0.4, False)], 1.4),
                     RATE, 0.0, 0.35), RATE)

# 게임 오버(가장 강렬한 폭발, 약 2.4초)
bg10, fw4 = part("bang_10", BANG), part("fw_04", BANG)
save("gameover_a", fades(st_layers([(cn1, 1.0, 0.0, 0.0, False), (cn2, 0.9, 0.12, 0.2, False), (cr4, 1.0, 0.0, 0.0, True),
                                    (low0, 1.0, 0.0, 0.0, True), (bg10, 0.7, 0.35, -0.3, False), (part("fw_02", BANG), 0.4, 0.2, 0.5, False)], 1.9),
                         RATE, 0.0, 0.5), RATE)
save("gameover_b", fades(st_layers([(fw4, 0.9, 0.0, 0.0, True), (cr4, 1.0, 0.0, 0.0, True), (low0, 0.9, 0.1, 0.0, True),
                                    (cn3, 0.8, 0.5, 0.2, False), (cn1, 0.6, 0.9, -0.3, False)], 1.9),
                         RATE, 0.0, 0.5), RATE)

# 적을 맞혔을 때(0.4초, 자주 나서 짧게): 녹음된 짧은 폭음의 또렷한 앞부분 + 낮은 폭발음의 앞부분
save("hit_a", fades(st_layers([(part("bang_08", BANG, 0.0, 0.4), 1.0, 0.0, -0.15, False), (part("explosionCrunch_000", SRC, 0.0, 0.4), 0.8, 0.0, 0.0, True)], 1.5),
                    RATE, 0.0, 0.2), RATE)
save("hit_b", fades(st_layers([(part("bang_03", BANG, 0.0, 0.4), 1.0, 0.0, 0.15, False), (part("explosionCrunch_002", SRC, 0.0, 0.4), 0.7, 0.0, 0.0, True)], 1.5),
                    RATE, 0.0, 0.2), RATE)

# 내가 총알에 맞았을 때: 금속 충격음 + 낮은 폭발음 + 녹음된 총소리의 날카로운 갈라짐
save("hurt_a", fades(st_layers([(part("impactMetal_000", SRC), 1.0, 0.0, 0.0, False), (part("lowFrequency_explosion_001", SRC, 0.0, 0.63), 0.7, 0.0, 0.0, True),
                                (part("shot_01", BANG, 0.0, 0.2), 0.6, 0.0, 0.2, False)], 1.6), RATE, 0.0, 0.2), RATE)
save("hurt_b", fades(st_layers([(part("impactMetal_003", SRC), 1.0, 0.0, 0.0, False), (part("bang_05", BANG, 0.0, 0.5), 0.6, 0.0, -0.2, False),
                                (part("explosionCrunch_000", SRC, 0.0, 0.5), 0.4, 0.0, 0.0, True)], 1.6), RATE, 0.0, 0.15), RATE)
