"""녹음된 효과음 가져오기: python import_sfx.py <Kenney Sci-Fi Sounds를 푼 폴더>
Kenney의 "Sci-Fi Sounds"(CC0, https://opengameart.org/content/sci-fi-sounds)에서 필요한 소리를 골라 잘라서 assets/sfx/에 넣는다.
  shoot(미사일이 날아가는 소리) <- thrusterFire (로켓 분사음의 일부를 "슝" 하고 지나가게)
  bomb (폭탄 터지는 소리)      <- explosionCrunch_000 / _001
  hit  (적을 맞혔을 때)        <- explosionCrunch_000 / _002 의 앞부분
원본 파일은 저장소에 넣지 않고(받은 zip은 5.9MB), 잘라 낸 결과(.ogg)만 assets/sfx/에 둔다. (pip install soundfile numpy 필요)
hurt(내가 맞았을 때)는 make_sfx.py가 합성한다."""
import math
import os
import sys

import numpy as np
import soundfile as sf

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get("TEMP", "."), "kenney_files", "Audio")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sfx")


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


def save(name, x, sr, peak=0.8):
    x = x / (np.max(np.abs(x)) or 1.0) * peak
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".ogg")
    sf.write(path, x.astype("float32"), sr, format="OGG", subtype="VORBIS")
    print("%-8s %.2fs %5.1f KB" % (name, len(x) / sr, os.path.getsize(path) / 1024))


# 폭탄: a = 낮은 웅웅거림이 크게 이어지다 줄어드는 폭발 (0.78초), b = 더 오래 이어지는 폭발 (1초로 자름)
d, sr = load("explosionCrunch_000")
save("bomb_a", fades(d, sr, 0.0, 0.05), sr)
d, sr = load("explosionCrunch_001")
save("bomb_b", fades(cut(d, sr, 0.0, 1.0), sr, 0.0, 0.25), sr)

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
