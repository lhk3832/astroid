"""배경음악 만들기: python make_bgm.py  ->  assets/music/bgm_a.ogg, bgm_b.ogg  (pip install soundfile numpy 가 필요하다)
직접 작곡해서 합성한 곡이다 (녹음 파일이 아니다). 처음과 끝이 이어지게 만들어서 계속 반복해도 끊기지 않는다.
  bgm_a "Starfighter": 150 BPM, 라단조(A minor), 32마디(약 51초). 킥/스네어/하이햇 + 베이스 + 아르페지오 + 패드 + 리드 멜로디. 빠르고 박력 있는 슈팅 게임풍
  bgm_b "Deep Space":  100 BPM, 레단조(D minor), 16마디(약 38초). 큰 패드 + 낮은 베이스 + 천천히 울리는 아르페지오 + 느린 멜로디. 깊고 넓은 우주풍
shooter.py 위쪽 BGM_CHOICE에서 a/b를 고른다."""
import os

import numpy as np
import soundfile as sf

SR = 44100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "music")


# ── 악기 ─────────────────────────────────────────────────
def mf(n):
    """MIDI 음 번호 -> 주파수(Hz). 69 = 라(A4) 440Hz"""
    return 440.0 * 2 ** ((n - 69) / 12)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def env(dur, a=0.005, d=0.2, s=0.0, r=0.02):
    """어택(a) -> 줄어듦(d) -> 유지(s) -> 끝에서 사라짐(r) 크기 곡선"""
    t = tt(dur)
    e = np.minimum(1.0, t / max(a, 1e-4)) * (s + (1 - s) * np.exp(-t / max(d, 1e-4)))
    n = len(t)
    rr = min(n, int(r * SR))
    if rr > 0:
        e[n - rr:] *= np.linspace(1, 0, rr)
    return e


def harm(f, dur, kind="saw", cutoff=9000, vib=0.0, vib_hz=5.5):
    """배음을 쌓아서 만든 소리(높은 소리가 깨지지 않게 cutoff 아래만 쌓는다). vib: 떨림 깊이(반음의 몇 분의 몇)"""
    t = tt(dur)
    ph = 2 * np.pi * f * t
    if vib:
        ph = ph + (vib * f / vib_hz * 0.06) * np.sin(2 * np.pi * vib_hz * t)
    top = max(1, min(40, int(cutoff / f)))
    out = np.zeros(len(t))
    for h in range(1, top + 1):
        if kind == "saw":
            out += np.sin(h * ph) / h
        elif kind == "square":
            if h % 2:
                out += np.sin(h * ph) / h
        elif kind == "tri":
            if h % 2:
                out += ((-1) ** ((h - 1) // 2)) * np.sin(h * ph) / (h * h)
        else:  # sine
            return np.sin(ph)
    return out * (0.62 if kind != "tri" else 1.0)


def kick(dur=0.32):
    t = tt(dur)
    f = 48 + 120 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) + 0.35 * np.exp(-t * 400) * np.sin(2 * np.pi * 900 * t)


def snare(rng, dur=0.26):
    t = tt(dur)
    nz = rng.uniform(-1, 1, len(t))
    nz = nz - np.concatenate(([0], nz[:-1]))  # 높은 소리만 남기기
    return 0.8 * nz * np.exp(-t * 20) + 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 28)


def hat(rng, dur=0.05, open_=False):
    n = int((0.22 if open_ else dur) * SR)
    t = np.arange(n) / SR
    nz = rng.uniform(-1, 1, n)
    nz = nz - np.concatenate(([0], nz[:-1]))
    return nz * np.exp(-t * (16 if open_ else 95)) * 0.55


# ── 놓기(마디 끝을 넘으면 처음으로 이어 붙인다) ───────────────────
class Bus:
    def __init__(self, n):
        self.n = n
        self.L = np.zeros(n)
        self.R = np.zeros(n)

    def put(self, x, t0, pan=0.0, gain=1.0):
        ang = (pan + 1) * np.pi / 4
        gl, gr = np.cos(ang) * gain, np.sin(ang) * gain
        i0 = int(round(t0 * SR)) % self.n
        end = i0 + len(x)
        if end <= self.n:
            self.L[i0:end] += x * gl
            self.R[i0:end] += x * gr
        else:
            k = self.n - i0
            self.L[i0:] += x[:k] * gl
            self.R[i0:] += x[:k] * gr
            self.L[:end - self.n] += x[k:] * gl
            self.R[:end - self.n] += x[k:] * gr


def echo(bus, delay_s, fb, taps=5):
    """좌우로 번갈아 울리는 메아리 (순환해서 곡이 이어진다)"""
    L, R = bus.L.copy(), bus.R.copy()
    for k in range(1, taps + 1):
        d = int(delay_s * k * SR)
        a = fb ** k
        if k % 2:
            L += a * np.roll(bus.R, d)
            R += a * np.roll(bus.L, d)
        else:
            L += a * np.roll(bus.L, d)
            R += a * np.roll(bus.R, d)
    bus.L, bus.R = L, R


def reverb(bus, wet, rt, seed):
    """울림(잔향): 줄어드는 잡음을 겹쳐 대는 방식. 곡 길이만큼 순환시켜서 곡의 끝 울림이 처음으로 이어진다"""
    rng = np.random.default_rng(seed)
    n = int(rt * SR)
    t = np.arange(n) / SR
    outs = []
    for ch in (bus.L, bus.R):
        ir = rng.normal(0, 1, n) * np.exp(-t * (6.9 / rt))
        ir = np.concatenate(([0.0], np.convolve(ir, np.ones(40) / 40, mode="same")[1:]))
        ir /= np.sqrt(np.sum(ir ** 2))
        spec = np.fft.rfft(ch) * np.fft.rfft(ir, n=bus.n)
        outs.append(np.fft.irfft(spec, n=bus.n))
    bus.L = bus.L * (1 - wet) + outs[0] * wet * 1.6
    bus.R = bus.R * (1 - wet) + outs[1] * wet * 1.6


def chord(root, kind):
    """root(MIDI)에서 시작하는 3화음의 세 음. kind: min / maj"""
    return [root, root + (3 if kind == "min" else 4), root + 7]


A_MINOR = [0, 2, 3, 5, 7, 8, 10]  # 자연 단음계(으뜸음으로부터의 반음 거리)


def scale_note(tonic, idx):
    """tonic에서 시작하는 단음계의 idx번째 음(음수/7 이상이면 옥타브가 넘어간다)"""
    o, k = divmod(idx, 7)
    return tonic + 12 * o + A_MINOR[k]


def master(bus, drive=1.25, rms_db=-14.0, peak=0.9):
    """두 곡의 평균 크기를 같게(rms_db) 맞추고, 가장 센 소리가 peak를 넘지 않게 한다"""
    x = np.stack([bus.L, bus.R], axis=1)
    x = np.tanh(x * drive) / np.tanh(drive)
    x *= 10 ** (rms_db / 20) / np.sqrt(np.mean(x ** 2))
    x *= min(1.0, peak / np.max(np.abs(x)))
    return x


# ── 곡 a: Starfighter (150 BPM, 라단조, 32마디) ────────────────────
def make_a():
    bpm, bars = 150, 32
    beat = 60.0 / bpm
    bar = beat * 4
    N = int(bars * bar * SR)
    rng = np.random.default_rng(11)
    drums, bass, arp, pad, lead = (Bus(N) for _ in range(5))
    A = 57  # 라(A3)
    pa = [(A - 12, "min"), (A - 16, "maj"), (A - 9, "maj"), (A - 14, "maj"),
          (A - 12, "min"), (A - 16, "maj"), (A - 14, "maj"), (A - 8, "maj")]            # Am F C G | Am F G E
    pb = [(A - 7, "min"), (A - 16, "maj"), (A - 9, "maj"), (A - 14, "maj"),
          (A - 7, "min"), (A - 16, "maj"), (A - 8, "maj"), (A - 8, "maj")]              # Dm F C G | Dm F E E
    progs = [pa, pa, pb, pa]  # 8마디씩 네 구간
    motifs = [[4, 2, 3, 5, 4, 2], [5, 3, 4, 6, 5, 3]]  # 멜로디 (음계 안의 오르내림)
    rhythm = [(0, 0.75), (0.75, 0.75), (1.5, 0.5), (2, 1.0), (3, 0.5), (3.5, 0.5)]
    for b in range(bars):
        sec, bi = divmod(b, 8)
        root, kind = progs[sec][bi]
        t0 = b * bar
        ch = chord(root + 12, kind)  # 한 옥타브 위의 화음
        # 드럼
        for q in range(4):
            drums.put(kick(), t0 + q * beat, 0.0, 0.95)
            if q in (1, 3):
                drums.put(snare(rng), t0 + q * beat, 0.0, 0.8)
        for e8 in range(8):
            drums.put(hat(rng), t0 + e8 * beat / 2, 0.25 if e8 % 2 else -0.25, 0.5 if e8 % 2 == 0 else 0.35)
        if sec >= 1:  # 16분음표 하이햇과 열린 하이햇
            for s16 in range(16):
                if s16 % 2:
                    drums.put(hat(rng), t0 + s16 * beat / 4, 0.3, 0.22)
            drums.put(hat(rng, open_=True), t0 + 1.5 * beat, -0.2, 0.4)
            drums.put(hat(rng, open_=True), t0 + 3.5 * beat, 0.2, 0.4)
        if bi == 7:  # 8마디마다 마지막 박에 스네어 연타
            for s16 in range(4):
                drums.put(snare(rng, 0.18), t0 + 3 * beat + s16 * beat / 4, 0.0, 0.5 + 0.12 * s16)
        # 베이스: 8분음표
        pat = [0, 0, 12, 0, 0, 12, 0, 7]
        for e8 in range(8):
            f = mf(root + pat[e8])
            x = harm(f, beat / 2 * 0.95, "saw", 900) * env(beat / 2 * 0.95, 0.003, 0.18, 0.35, 0.02)
            bass.put(x, t0 + e8 * beat / 2, 0.0, 0.8)
        # 아르페지오: 16분음표, 좌우로 번갈아
        order = [0, 1, 2, 1, 2, 1, 0, 1, 2, 1, 2, 1, 2, 1, 0, 1]
        for s16 in range(16):
            f = mf(ch[order[s16] % 3] + (12 if s16 % 4 == 3 else 0))
            x = harm(f, 0.16, "square", 6000) * env(0.16, 0.002, 0.07, 0.0, 0.01)
            arp.put(x, t0 + s16 * beat / 4, -0.45 if s16 % 2 else 0.45, 0.36 if sec else 0.28)
        # 패드: 화음을 길게
        for i, n in enumerate(ch):
            for det in (-0.07, 0.07):
                f = mf(n) * 2 ** (det / 12)
                x = harm(f, bar * 1.02, "saw", 2500) * env(bar * 1.02, 0.25, 0.9, 0.55, 0.15)
                pad.put(x, t0, (i - 1) * 0.5, 0.17)
        # 리드 멜로디: 둘째 구간부터
        if sec >= 1:
            tonic = 57
            base = {0: 4, 1: 3, 2: 4, 3: 3}
            ridx = {A - 12: 0, A - 16: 5, A - 9: 2, A - 14: 6, A - 7: 3, A - 8: 4}.get(root, 0)
            m = motifs[(b % 2) if sec != 2 else (b + 1) % 2]
            for (st, du), off in zip(rhythm, m):
                n = scale_note(tonic, ridx + off + (3 if sec == 2 else 0))
                f = mf(n + 12)
                d = du * beat * 0.95
                x = (harm(f, d, "saw", 5000, vib=0.8) * 0.6 + harm(f, d, "square", 5000, vib=0.8) * 0.4) * env(d, 0.01, 0.4, 0.55, 0.04)
                lead.put(x, t0 + st * beat, 0.0, 0.5)
    echo(lead, beat * 0.75, 0.38)
    echo(arp, beat * 0.5, 0.3, 3)
    reverb(pad, 0.35, 1.6, 1)
    reverb(lead, 0.25, 1.2, 2)
    mix = Bus(N)
    for b_, g in ((drums, 1.0), (bass, 0.9), (arp, 0.8), (pad, 0.75), (lead, 0.85)):
        mix.L += b_.L * g
        mix.R += b_.R * g
    return master(mix)


# ── 곡 b: Deep Space (100 BPM, 레단조, 16마디) ─────────────────────
def make_b():
    bpm, bars = 100, 16
    beat = 60.0 / bpm
    bar = beat * 4
    N = int(bars * bar * SR)
    rng = np.random.default_rng(23)
    drums, bass, arp, pad, lead = (Bus(N) for _ in range(5))
    D = 50  # 레(D3)
    prog = [(D, "min"), (D - 4, "maj"), (D - 9, "maj"), (D - 2, "maj")]  # Dm Bb F C (2마디씩)
    mel_idx = {D: 0, D - 4: 5, D - 9: 2, D - 2: 6}
    mel = [[4, 5, 4, 2], [3, 4, 2, 1], [2, 4, 5, 4], [1, 2, 0, -1]]
    for b in range(bars):
        root, kind = prog[(b // 2) % 4]
        t0 = b * bar
        ch = chord(root + 12, kind)
        # 부드러운 드럼
        for q in (0, 2):
            drums.put(kick() * 0.9, t0 + q * beat, 0.0, 0.75)
        drums.put(snare(rng, 0.3), t0 + 3 * beat, 0.0, 0.35)
        for e8 in range(8):
            drums.put(hat(rng), t0 + e8 * beat / 2, 0.3 if e8 % 2 else -0.3, 0.25)
        # 길고 낮은 베이스
        f = mf(root - 12)
        x = harm(f, bar * 0.98, "saw", 500) * env(bar * 0.98, 0.02, 1.4, 0.7, 0.2)
        bass.put(x, t0, 0.0, 0.7)
        # 큰 패드: 4음
        for i, n in enumerate(ch + [ch[0] + 12]):
            for det in (-0.09, 0.0, 0.09):
                x = harm(mf(n) * 2 ** (det / 12), bar * 1.05, "saw", 2200) * env(bar * 1.05, 0.7, 1.6, 0.75, 0.4)
                pad.put(x, t0, (i - 1.5) * 0.45, 0.12)
        # 천천히 울리는 아르페지오 (8분음표, 메아리가 길다)
        for e8 in range(8):
            f = mf(ch[[0, 1, 2, 1, 2, 1, 0, 2][e8] % 3] + 12)
            x = harm(f, 0.3, "tri", 4000) * env(0.3, 0.003, 0.18, 0.0, 0.02)
            arp.put(x, t0 + e8 * beat / 2, -0.5 if e8 % 2 else 0.5, 0.42)
        # 느린 멜로디: 2마디에 4음
        if b % 2 == 0:
            idx = mel_idx[root]
            for k, off in enumerate(mel[(b // 2) % 4]):
                n = scale_note(D, idx + off + 7)
                f = mf(n)
                d = beat * 1.9
                x = (harm(f, d, "tri", 3500, vib=0.7) * 0.7 + harm(f, d, "saw", 3500, vib=0.7) * 0.25) * env(d, 0.08, 1.2, 0.5, 0.25)
                lead.put(x, t0 + k * beat * 2, 0.1, 0.55)
    echo(lead, beat * 0.75, 0.45, 6)
    echo(arp, beat * 0.75, 0.5, 6)
    reverb(pad, 0.45, 2.4, 3)
    reverb(lead, 0.4, 2.0, 4)
    reverb(arp, 0.35, 1.6, 5)
    mix = Bus(N)
    for b_, g in ((drums, 0.9), (bass, 0.95), (arp, 0.8), (pad, 0.9), (lead, 0.85)):
        mix.L += b_.L * g
        mix.R += b_.R * g
    return master(mix, 1.15)


def save(name, x):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".ogg")
    for _ in range(6):
        # 긴 소리를 한 번에 쓰면 soundfile(Vorbis)이 죽어서(stack overflow) 1초씩 나눠서 쓴다
        with sf.SoundFile(path, "w", samplerate=SR, channels=2, format="OGG", subtype="VORBIS") as f:
            for i in range(0, len(x), SR):
                f.write(x[i:i + SR].astype("float32"))
        back, _sr = sf.read(path)
        if np.max(np.abs(back)) < 0.97:
            break
        x = x * 0.92
    print("%-6s %.1fs %5.0f KB" % (name, len(x) / SR, os.path.getsize(path) / 1024))


if __name__ == "__main__":
    save("bgm_a", make_a())
    save("bgm_b", make_b())
