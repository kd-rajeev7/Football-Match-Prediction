"""Compose the original music bed: warm electric-piano lounge, 80 BPM, D major.

Every sound is synthesised here, so the track is fully owned and safe for
commercial use. usage: music.py OUT.wav SECONDS
"""
import sys
import wave

import numpy as np

SR = 44100
BEAT = 60 / 80
BAR = 4 * BEAT
rng = np.random.default_rng(7)  # seeded: the same track every run


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def place(buf, sig, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n] * gain


def epiano(midi, dur, vel=1.0):
    t = np.arange(int(dur * SR)) / SR
    f = hz(midi)
    tone = (np.sin(2 * np.pi * f * t)
            + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.6)
            + 0.12 * np.sin(2 * np.pi * 4.07 * f * t) * np.exp(-t / 0.15))
    env = np.minimum(t / 0.008, 1) * np.exp(-t / 1.7)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    return tone * env * trem * vel


def pad(midis, dur):
    t = np.arange(int(dur * SR)) / SR
    sig = np.zeros_like(t)
    for m in midis:
        for cents in (-4, 4):
            sig += np.sin(2 * np.pi * hz(m) * 2 ** (cents / 1200) * t)
    env = np.minimum(t / 0.9, 1) * np.minimum((dur - t) / 0.9, 1)
    return sig * env / (2 * len(midis))


def bass(midi, dur):
    t = np.arange(int(dur * SR)) / SR
    f = hz(midi)
    sig = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return sig * np.minimum(t / 0.02, 1) * np.exp(-t / 0.9)


def kick():
    t = np.arange(int(0.35 * SR)) / SR
    f = 50 + 70 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)


def shaker():
    n = int(0.09 * SR)
    noise = rng.standard_normal(n)
    noise = np.diff(np.concatenate([[0], noise]))  # tilt toward highs
    t = np.arange(n) / SR
    return noise * np.minimum(t / 0.01, 1) * np.exp(-t / 0.03)


def reverb(x, seconds=2.2, mix=0.28):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = []
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t / (seconds / 5))
        ir[0] = 0
        size = 1 << int(np.ceil(np.log2(len(x) + n)))
        wet = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x)]
        wet /= np.max(np.abs(wet)) + 1e-9
        out.append(x * (1 - mix) + wet * mix * np.max(np.abs(x)))
    return np.stack(out, axis=1)


def main():
    out, length = sys.argv[1], float(sys.argv[2])
    total = length + 3
    keys = np.zeros(int(total * SR))
    low = np.zeros_like(keys)
    perc = np.zeros_like(keys)

    # Dmaj9, Bm9, Gmaj9, A6/9 — then home to Dmaj9 for the logo.
    chords = [
        (50, [62, 66, 69, 73, 76]),
        (47, [62, 66, 69, 73]),
        (43, [59, 62, 66, 69]),
        (45, [61, 64, 66, 71]),
    ]
    bars = int(length // BAR)  # the last bar (home chord) lands under the logo
    for b in range(bars):
        root, notes = chords[b % 4] if b < bars - 1 else chords[0]
        t0 = b * BAR
        last = b == bars - 1
        for k, m in enumerate(notes):
            place(keys, epiano(m, BAR + 2.5, 0.55), t0 + k * 0.018)
        if not last:
            for k, m in enumerate(notes[1:]):
                place(keys, epiano(m, 2.0, 0.28), t0 + 2.5 * BEAT + k * 0.015)
        place(keys, pad(notes[:3], BAR + (2.5 if last else 0.6)), t0, 0.5)
        place(low, bass(root, 2 * BEAT), t0, 0.8)
        if not last:
            place(low, bass(root + 7, BEAT), t0 + 2.5 * BEAT, 0.45)
        if 0 < b < bars - 1:
            place(perc, kick(), t0, 0.55)
            place(perc, kick(), t0 + 2.5 * BEAT, 0.3)
            for e in range(8):
                place(perc, shaker(), t0 + e * BEAT / 2, 0.10 if e % 2 else 0.05)

    # A sparse melody from bar 3, D major pentatonic.
    melody = [(2, 0, 78), (2, 1.5, 76), (2, 3, 74), (3, 0, 74), (3, 2, 71),
              (4, 0, 73), (4, 1.5, 74), (4, 3, 76), (5, 0, 78), (5, 2, 81),
              (6, 0, 79), (6, 2, 78), (6, 3, 76), (7, 0, 78)]
    for b, beat, m in melody:
        if b < bars:
            place(keys, epiano(m, 2.5, 0.42), b * BAR + beat * BEAT)

    mix = keys * 0.5 + low * 0.55 + perc * 0.6
    stereo = reverb(mix)
    stereo[:, 0] += perc * 0.08
    stereo[:, 1] -= perc * 0.08
    fade_in = np.minimum(np.arange(len(stereo)) / (0.25 * SR), 1)
    stereo *= fade_in[:, None]
    stereo = stereo[:int(length * SR)]
    tail = int(1.5 * SR)
    stereo[-tail:] *= np.linspace(1, 0, tail)[:, None] ** 2
    stereo /= np.max(np.abs(stereo)) / 0.89
    pcm = (stereo * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"{out}: {length:.1f}s, {bars} bars")


if __name__ == "__main__":
    main()
