"""효과음 들어 보기: python sfx_preview.py  (소리마다 a, b를 차례로 들려준다)
마음에 드는 쪽을 shooter.py 위쪽 SFX_CHOICE에서 고른다."""
import os
import time

import pygame

pygame.mixer.init()
import sys
if "music" in sys.argv[1:]:  # python sfx_preview.py music: 배경음악 두 곡을 15초씩
    for v in ("a", "b"):
        print("배경음악 [%s] 15초" % v, flush=True)
        pygame.mixer.music.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "music", "bgm_%s.ogg" % v))
        pygame.mixer.music.play()
        time.sleep(15)
        pygame.mixer.music.stop()
    raise SystemExit
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sfx")
labels = {"shoot": "총알 쏠 때(총소리)", "bomb": "폭탄 터질 때", "hit": "내가 적을 맞혔을 때", "hurt": "내가 맞았을 때", "gameover": "게임 오버(가장 강렬한 폭발)"}
for name, label in labels.items():
    for variant in ("a", "b"):
        print("%s  [%s]" % (label, variant), flush=True)
        snd = pygame.mixer.Sound(os.path.join(base, "%s_%s.ogg" % (name, variant)))
        snd.play()
        time.sleep(snd.get_length() + 0.6)
    time.sleep(0.5)
