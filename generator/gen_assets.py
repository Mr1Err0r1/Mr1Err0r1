import math, random

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets") + os.sep
FONT = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

# ---------------------------------------------------------------- black hole
random.seed(11)
W, H = 800, 420
cw, ch = 6.0, 11.0
cols, rows = int(W / cw), int(H / ch)
cx, cy = W / 2, H / 2
ramp = " .:-=+*#%@"
N = 14                       # angular sectors for the rotating glow
RH = 60                      # event horizon radius (px)
RD, TILT = 335, 0.17         # accretion disk size / tilt

sectors = [[] for _ in range(N)]
stars = [[], [], []]

def tier(i):
    return min(4, int(i * 5))

for r in range(rows):
    for c in range(cols):
        x, y = (c + 0.5) * cw, (r + 0.5) * ch
        dx, dy = x - cx, y - cy
        rad = math.hypot(dx, dy)

        # disk (flat ellipse)
        e = math.hypot(dx / RD, dy / (RD * TILT))
        disk = 0.0
        if 0.22 <= e <= 1.0:
            disk = (1 - e) ** 0.6
            disk *= 1 + 0.35 * (-dx / RD)          # doppler: left side brighter
        # lensed halo + photon ring
        halo = 0.0
        if rad >= RH:
            halo = 0.95 * math.exp(-(rad - RH) / 20)
        intensity = max(disk, halo)

        inside_hole = rad < RH
        front = dy > 0
        if inside_hole and not (front and disk > 0):
            intensity = 0.0
        if RH <= rad < RH + 7:
            intensity = 1.0                           # photon ring

        intensity += random.uniform(-0.12, 0.12) if intensity > 0 else 0
        intensity = max(0.0, min(1.0, intensity))

        if intensity > 0.07:
            ang = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
            s = min(N - 1, int(ang * N))
            glyph = ramp[min(len(ramp) - 1, int(intensity * (len(ramp) - 1) + 0.5))]
            if glyph != " ":
                sectors[s].append((x, y + 3.5, tier(intensity), glyph))
        elif not inside_hole and random.random() < 0.011:
            stars[random.randrange(3)].append((x, y + 3.5, random.choice(".+*'")))

pal = ["#4a1f08", "#8f3a0b", "#d96a1a", "#ffab40", "#fff4cc"]
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ASCII black hole">',
       "<style>",
       f"text{{font-family:{FONT};font-size:10px;text-anchor:middle}}"]
for i, col in enumerate(pal):
    svg.append(f".c{i}{{fill:{col}}}")
svg += [".s{animation:pulse 6s ease-in-out infinite}",
        "@keyframes pulse{0%,100%{opacity:.18}15%{opacity:1}40%{opacity:.35}}",
        ".t{fill:#7d8590;animation:tw 4s ease-in-out infinite}",
        "@keyframes tw{0%,100%{opacity:.15}50%{opacity:.85}}",
        "</style>",
        f'<rect width="{W}" height="{H}" fill="#05060a"/>']
for k, grp in enumerate(stars):
    svg.append(f'<g class="t" style="animation-delay:-{k*1.3:.1f}s"><text>')
    svg += [f'<tspan x="{x:.1f}" y="{y:.1f}">{g}</tspan>' for x, y, g in grp]
    svg.append("</text></g>")
for s, grp in enumerate(sectors):
    svg.append(f'<g class="s" style="animation-delay:-{s*6/N:.2f}s"><text>')
    svg += [f'<tspan class="c{t}" x="{x:.1f}" y="{y:.1f}">{g}</tspan>' for x, y, t, g in grp]
    svg.append("</text></g>")
svg.append("</svg>")
open(OUT + "blackhole.svg", "w").write("\n".join(svg))

# ---------------------------------------------------------------- matrix banner
random.seed(5)
W2, H2, step, lh = 900, 150, 15, 15
glyphs = "0123456789ABCDEF{}[]()/=+*#$%;:"
cols2 = W2 // step
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}" width="{W2}" height="{H2}" role="img" aria-label="Mr1Err0r1">',
       "<defs>",
       '<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05060a"/><stop offset=".25" stop-color="#05060a" stop-opacity="0"/><stop offset=".75" stop-color="#05060a" stop-opacity="0"/><stop offset="1" stop-color="#05060a"/></linearGradient>',
       '<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
       "</defs>",
       "<style>",
       f"text{{font-family:{FONT};font-size:13px;text-anchor:middle}}",
       ".col{animation:fall linear infinite}",
       "@keyframes fall{from{transform:translateY(-250px)}to{transform:translateY(170px)}}",
       ".cur{animation:blink 1s steps(1) infinite}",
       "@keyframes blink{50%{opacity:0}}",
       f".title{{font-size:34px;font-weight:700;letter-spacing:3px;fill:#00ff9c;text-anchor:middle}}",
       "</style>",
       f'<rect width="{W2}" height="{H2}" fill="#05060a"/>']
for i in range(cols2):
    n = random.randint(7, 15)
    dur = random.uniform(3.5, 8.5)
    delay = -random.uniform(0, dur)
    x = i * step + step / 2
    svg.append(f'<g class="col" style="animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s"><text>')
    for j in range(n):
        head = j == n - 1
        fill = "#d6ffee" if head else "#00ff9c"
        op = 1 if head else (j + 1) / n * 0.75
        svg.append(f'<tspan x="{x}" y="{j*lh}" fill="{fill}" fill-opacity="{op:.2f}">{random.choice(glyphs)}</tspan>')
    svg.append("</text></g>")
svg += [f'<rect width="{W2}" height="{H2}" fill="url(#fade)"/>',
        f'<rect x="{W2/2-215}" y="{H2/2-36}" width="430" height="72" rx="6" fill="#05060a" fill-opacity=".78" stroke="#00ff9c" stroke-opacity=".45"/>',
        f'<text class="title" x="{W2/2}" y="{H2/2+12}" filter="url(#glow)">Mr1Err0r1<tspan class="cur">_</tspan></text>',
        "</svg>"]
open(OUT + "matrix.svg", "w").write("\n".join(svg))
print("ok")
