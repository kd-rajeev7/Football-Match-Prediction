"""Mix the soundtrack: music bed, each shot's own natural sound, two soft effects.

Natural sound plays at real speed from the shot's source point, faded at
every cut. The mix is mastered to -14 LUFS for TikTok and Instagram.
usage: mix.py FOOTAGE_DIR OUT.wav
"""
import glob
import os
import subprocess
import sys

SFX = "/root/.claude/plugins/cache/hyperframes/hyperframes/0.8.192/skills/media-use/audio/assets/sfx"
LENGTH = 24.5
MUSIC_GAIN = 0.42

# clip id, source start, timeline start, duration, gain
NATURAL = [
    ("760ac984", 2.0, 0.00, 2.2, 1.5),
    ("e3bb5075", 1.0, 2.20, 1.4, 1.0),
    ("f06dda4d", 3.0, 3.60, 1.1, 1.0),
    ("dc6b277f", 0.3, 4.70, 1.4, 1.0),
    ("5a8662de", 0.2, 6.10, 1.0, 1.0),
    ("dda8da9c", 3.0, 7.10, 2.8, 1.6),
    ("cf83c2dd", 1.8, 9.90, 1.6, 1.5),
    ("12ac73d5", 1.8, 11.50, 1.2, 0.35),
    ("5d4a1366", 3.4, 12.30, 1.4, 0.6),
    ("7f7ccc6b", 0.0, 13.70, 1.0, 1.0),
    ("760ac984", 6.5, 14.70, 4.5, 1.5),
    ("760ac984", 11.2, 19.20, 2.3, 1.2),
]
EFFECTS = [("whoosh-short.mp3", 6.02, 0.25), ("chime.mp3", 21.35, 0.3)]


def main():
    footage, out = sys.argv[1], sys.argv[2]
    inputs = ["-i", "assets/audio/music.wav"]
    chains = [f"[0:a]volume={MUSIC_GAIN}[m]"]
    labels = ["[m]"]
    for k, (clip, src, at, dur, gain) in enumerate(NATURAL, start=1):
        path = glob.glob(os.path.join(footage, f"{clip}-*.mp4"))[0]
        inputs += ["-ss", f"{src}", "-t", f"{dur}", "-i", path]
        fade = min(0.12, dur / 4)
        chains.append(
            f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={gain},"
            f"afade=t=in:d={fade},afade=t=out:st={dur - fade}:d={fade},"
            f"adelay={int(at * 1000)}:all=1[n{k}]")
        labels.append(f"[n{k}]")
    base = len(NATURAL) + 1
    for k, (name, at, gain) in enumerate(EFFECTS):
        inputs += ["-i", os.path.join(SFX, name)]
        chains.append(
            f"[{base + k}:a]aformat=sample_rates=44100:channel_layouts=stereo,"
            f"volume={gain},adelay={int(at * 1000)}:all=1[e{k}]")
        labels.append(f"[e{k}]")
    chains.append(
        f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,"
        f"atrim=0:{LENGTH},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chains),
                    "-map", "[out]", "-ar", "44100", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
