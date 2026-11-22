"""효과음 들어 보기: python sfx_preview.py  (소리마다 a, b를 차례로 들려준다)
마음에 드는 쪽을 shooter.py 위쪽 SFX_CHOICE에서 고른다."""
import os
import time

import pygame

pygame.mixer.init()
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sfx")
labels = {"shoot": "총알 쏠 때(미사일 나는 소리)", "bomb": "폭탄 터질 때", "hit": "내가 적을 맞혔을 때", "hurt": "내가 맞았을 때"}
for name, label in labels.items():
    for variant in ("a", "b"):
        print("%s  [%s]" % (label, variant), flush=True)
        snd = pygame.mixer.Sound(os.path.join(base, "%s_%s.ogg" % (name, variant)))
        snd.play()
        time.sleep(snd.get_length() + 0.6)
    time.sleep(0.5)
