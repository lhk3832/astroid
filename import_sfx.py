"""녹음된 효과음 가져오기: python import_sfx.py <Kenney Sci-Fi Sounds를 푼 폴더> [<25 CC0 bang / firework SFX를 푼 폴더>]
두 CC0 묶음에서 필요한 소리를 골라 잘라서 겹쳐 assets/sfx/에 넣는다.
  Kenney "Sci-Fi Sounds"  https://opengameart.org/content/sci-fi-sounds   (CC0)
  rubberduck "25 CC0 bang / firework SFX" https://opengameart.org/content/25-cc0-bang-firework-sfx (CC0, 직접 녹음한 폭음)
  shoot    <- thrusterFire (로켓 분사음의 일부를 "슝" 하고 지나가게)
  bomb     <- 실제 녹음된 폭음(cannon) + 길고 낮은 울림(lowFrequency_explosion / explosionCrunch)을 겹친 약 2초의 폭발
  hit      <- explosionCrunch_000 / _002 의 앞부분
  hurt     <- impactMetal_000 / _003 (금속에 부딪히는 소리) + 낮은 폭발음 lowFrequency_explosion_001
  gameover <- 여러 폭음과 낮은 울림을 가장 크게 겹친 약 2.6초의 가장 강렬한 폭발
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
    """앞은 fade_in초 동안 커지고, 뒤는 fade_out초 동안 부드럽게 사라진다 (딱 소리가 나지 않게)."""
    n = len(x)
    a, b = int(fade_in * sr), int(fade_out * sr)
    g = np.ones(n)
    if a > 0:
        g[:a] = np.linspace(0, 1, a) ** 1.5
    if b > 0:
        g[n - b:] *= np.linspace(1, 0, b) ** curve
    return x * g


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


def save(name, x, sr, peak=0.8):
    x = x / (np.max(np.abs(x)) or 1.0) * peak
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".ogg")
    sf.write(path, x.astype("float32"), sr, format="OGG", subtype="VORBIS")
    print("%-8s %.2fs %5.1f KB" % (name, len(x) / sr, os.path.getsize(path) / 1024))


# 폭탄(평소의 폭발, 약 2초): 실제로 녹음된 폭음의 갈라지는 순간과 몸통에 길고 낮은 울림을 겹쳐서 더 길고 실감 나게
# a = 대포 소리(cannon_01) + 늦게 부풀어 오르는 낮은 폭발음(lowFrequency_explosion_000) + explosionCrunch_000
cn1 = load_any(BANG, "cannon_01")
low0 = load_any(SRC, "lowFrequency_explosion_000")
cr0 = load_any(SRC, "explosionCrunch_000")
save("bomb_a", fades(layers([(cn1, 1.0, 0.0), (low0, 0.85, 0.0), (cr0, 0.5, 0.0)], 1.3), RATE, 0.0, 0.35), RATE)
# b = 더 깊은 대포 소리(cannon_02) + 길게 이어지는 explosionCrunch_003
cn2 = load_any(BANG, "cannon_02")
cr3 = load_any(SRC, "explosionCrunch_003")
save("bomb_b", fades(layers([(cn2, 1.0, 0.0), (cr3, 0.9, 0.05)], 1.3), RATE, 0.0, 0.35), RATE)

# 게임 오버(가장 강렬한 폭발, 약 2.6초): 여러 폭음과 낮은 울림을 가장 크게 겹치고 많이 찌그러뜨려서 꽉 차게
cr4 = load_any(SRC, "explosionCrunch_004")
bg10 = load_any(BANG, "bang_10")
save("gameover_a", fades(layers([(cn1, 1.0, 0.0), (cn2, 0.9, 0.12), (cr4, 1.0, 0.0), (low0, 1.0, 0.0), (bg10, 0.7, 0.35)], 1.9), RATE, 0.0, 0.5), RATE)
fw4 = load_any(BANG, "fw_04")
cn3 = load_any(BANG, "cannon_03")
save("gameover_b", fades(layers([(fw4, 0.9, 0.0), (cr4, 1.0, 0.0), (low0, 0.9, 0.1), (cn3, 0.8, 0.5)], 1.9), RATE, 0.0, 0.5), RATE)

# 적을 맞혔을 때: 작은 폭발 (자주 나서 0.5초로 짧게 자르고 뒤를 빠르게 줄인다)
d, sr = load("explosionCrunch_000")
save("hit_a", fades(cut(d, sr, 0.0, 0.5), sr, 0.0, 0.22), sr)
d, sr = load("explosionCrunch_002")
save("hit_b", fades(cut(d, sr, 0.0, 0.5), sr, 0.0, 0.22), sr)

# 미사일 나는 소리: 로켓 분사음에서 0.4초를 잘라 "슝" 하고 지나가게 (자주 나는 소리라 짧고, 크기는 게임에서 작게 한다)
d, sr = load("thrusterFire_004")
save("shoot_a", whoosh(cut(d, sr, 1.0, 0.45), sr, 0.06, 0.3), sr)
d, sr = load("thrusterFire_000")
save("shoot_b", whoosh(cut(d, sr, 1.0, 0.4), sr, 0.05, 0.25), sr)

# 내가 총알에 맞았을 때: 비행기 몸체가 얻어맞는 금속 충격음. a = 금속 충격 + 낮은 폭발음을 깔아서 묵직하게 (0.7초), b = 금속 충격 그대로 (0.78초)
d, sr = load("impactMetal_000")
metal = cut(d, sr, 0.0, 0.7)
low, _ = load("lowFrequency_explosion_001")
low = cut(low, sr, 0.0, 0.7)
low = low[:len(metal)] if len(low) >= len(metal) else np.pad(low, (0, len(metal) - len(low)))
mixed = metal / (np.max(np.abs(metal)) or 1.0) + 0.6 * low / (np.max(np.abs(low)) or 1.0)
save("hurt_a", fades(mixed, sr, 0.0, 0.2), sr)
d, sr = load("impactMetal_003")
save("hurt_b", fades(d, sr, 0.0, 0.1), sr)
