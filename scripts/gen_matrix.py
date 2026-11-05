"""Generates assets/matrix.svg (animated matrix-rain banner). Run: python scripts/gen_matrix.py"""
import os, random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets") + os.sep
FONT = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

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
