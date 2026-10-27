"""Cut one shot from a source clip with a smooth speed ramp.

Frames are interpolated to 120 fps (motion-compensated), then sampled along
a speed curve so the shot eases between real time and slow motion. Output is
1080x1920, 30 fps, H.264, no audio.

usage: shot.py SRC START OUT.mp4 SEGMENTS_JSON [--zoom Z] [--cx X] [--cy Y]
SEGMENTS_JSON: [[out_seconds, speed_from, speed_to], ...]
"""
import json
import subprocess
import sys

W_SRC, H_SRC = 478, 850
FPS_IN, FPS_OUT = 120, 30


def smooth(t):
    return t * t * (3 - 2 * t)


def source_times(segments):
    """Source time offset (s) for each output frame."""
    times, t = [], 0.0
    for dur, s0, s1 in segments:
        n = int(round(dur * FPS_OUT))
        for i in range(n):
            times.append(t)
            speed = s0 + (s1 - s0) * smooth(i / max(n - 1, 1))
            t += speed / FPS_OUT
    return times, t


def main():
    src, start, out, segs = sys.argv[1], float(sys.argv[2]), sys.argv[3], json.loads(sys.argv[4])
    args = sys.argv[5:]
    opt = {args[i]: float(args[i + 1]) for i in range(0, len(args), 2)}
    zoom, cx, cy = opt.get("--zoom", 1.0), opt.get("--cx", 0.5), opt.get("--cy", 0.5)

    times, span = source_times(segs)
    slow = any(min(s0, s1) < 0.999 for _, s0, s1 in segs)
    vf = "minterpolate=fps=120:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" if slow else "fps=120"
    reader = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-ss", f"{start}", "-t", f"{span + 0.2}", "-i", src,
         "-vf", f"scale={W_SRC}:{H_SRC},{vf}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE)

    cw, ch = W_SRC / zoom, H_SRC / zoom
    x = min(max(cx * W_SRC - cw / 2, 0), W_SRC - cw)
    y = min(max(cy * H_SRC - ch / 2, 0), H_SRC - ch)
    crop = f"crop={cw:.0f}:{ch:.0f}:{x:.0f}:{y:.0f}," if zoom > 1.0 else ""
    writer = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W_SRC}x{H_SRC}", "-r", f"{FPS_OUT}", "-i", "-",
         "-vf", f"{crop}scale=1080:1920:flags=lanczos,unsharp=5:5:0.6:5:5:0.0",
         "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", out],
        stdin=subprocess.PIPE)

    frame_bytes = W_SRC * H_SRC * 3
    idx, frame = -1, None
    for t in times:
        want = int(round(t * FPS_IN))
        while idx < want:
            buf = reader.stdout.read(frame_bytes)
            if len(buf) < frame_bytes:
                break
            frame, idx = buf, idx + 1
        writer.stdin.write(frame)
    writer.stdin.close()
    writer.wait()
    reader.kill()
    print(f"{out}: {len(times) / FPS_OUT:.2f}s from {span:.2f}s of source")


if __name__ == "__main__":
    main()
