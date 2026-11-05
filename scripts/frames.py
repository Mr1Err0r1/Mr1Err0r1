"""ASCII frames for the left side of assets/neofetch.svg.

Default: a spinning ASCII donut (procedural, no dependencies).
Your own animation: convert a GIF into assets/frames.json (needs Pillow):

    pip install pillow
    python scripts/frames.py my_animation.gif --cols 44

update_profile.py uses assets/frames.json automatically when it exists.
"""
import argparse, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES_JSON = os.path.join(HERE, "..", "assets", "frames.json")
COLS, ROWS = 44, 22


def donut_frames(n=48, w=COLS, h=ROWS):
    """One seamless rotation loop of the classic ASCII donut."""
    chars = ".,-~:;=!*#$@"
    r1, r2, k2 = 1.0, 2.0, 5.0
    k1 = w * 0.66
    frames = []
    for k in range(n):
        a, b = 2 * math.pi * k / n, 4 * math.pi * k / n
        ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
        out = [[" "] * w for _ in range(h)]
        zbuf = [[0.0] * w for _ in range(h)]
        theta = 0.0
        while theta < 2 * math.pi:
            ct, st = math.cos(theta), math.sin(theta)
            phi = 0.0
            while phi < 2 * math.pi:
                cp, sp = math.cos(phi), math.sin(phi)
                cx, cy = r2 + r1 * ct, r1 * st
                x = cx * (cb * cp + sa * sb * sp) - cy * ca * sb
                y = cx * (sb * cp - sa * cb * sp) + cy * ca * cb
                z = k2 + ca * cx * sp + cy * sa
                ooz = 1 / z
                xp = int(w / 2 + k1 * ooz * x)
                yp = int(h / 2 - k1 * 0.5 * ooz * y)
                lum = cp * ct * sb - ca * ct * sp - sa * st + cb * (ca * st - ct * sa * sp)
                if 0 <= xp < w and 0 <= yp < h and lum > 0 and ooz > zbuf[yp][xp]:
                    zbuf[yp][xp] = ooz
                    out[yp][xp] = chars[min(len(chars) - 1, int(lum * 8))]
                phi += 0.03
            theta += 0.07
        frames.append(["".join(r) for r in out])
    # start on a mid-rotation frame so a non-animating viewer shows a nice donut
    frames = frames[n // 4:] + frames[:n // 4]
    return frames, 14


def load_frames(path=FRAMES_JSON):
    """Returns (frames, fps). Uses assets/frames.json if present, else the donut."""
    if os.path.exists(path):
        data = json.load(open(path, encoding="utf-8"))
        return data["frames"], data.get("fps", 12)
    return donut_frames()


def gif_to_frames(src, cols=COLS, max_frames=60, invert=False):
    from PIL import Image, ImageSequence

    ramp = " .:-=+*#%@"
    im = Image.open(src)
    rows = max(1, min(30, round(cols * im.height / im.width * 0.5)))
    fps = max(4, min(24, round(1000 / (im.info.get("duration") or 80))))
    all_frames = [f.copy() for f in ImageSequence.Iterator(im)]
    step = max(1, math.ceil(len(all_frames) / max_frames))
    frames = []
    for fr in all_frames[::step]:
        bg = Image.new("RGBA", fr.size, (0, 0, 0, 255))
        g = Image.alpha_composite(bg, fr.convert("RGBA")).convert("L").resize((cols, rows))
        px = g.load()
        lines = []
        for y in range(rows):
            line = ""
            for x in range(cols):
                v = px[x, y] / 255
                v = 1 - v if invert else v
                line += ramp[min(len(ramp) - 1, int(v * len(ramp)))]
            lines.append(line)
        frames.append(lines)
    return frames, max(4, fps // step)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Convert a GIF into assets/frames.json")
    ap.add_argument("gif")
    ap.add_argument("--cols", type=int, default=COLS)
    ap.add_argument("--invert", action="store_true", help="use for dark-on-light GIFs")
    ap.add_argument("--max-frames", type=int, default=60)
    a = ap.parse_args()
    fr, fps = gif_to_frames(a.gif, a.cols, a.max_frames, a.invert)
    json.dump({"fps": fps, "frames": fr}, open(FRAMES_JSON, "w", encoding="utf-8"))
    print(f"{len(fr)} frames, {fps} fps -> {os.path.normpath(FRAMES_JSON)}")
    print("Now run: python scripts/update_profile.py --offline   (or let the workflow do it)")
