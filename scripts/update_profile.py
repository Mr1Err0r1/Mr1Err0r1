#!/usr/bin/env python3
"""Rebuilds assets/neofetch.svg and the project table in README.md.

    python scripts/update_profile.py             # live data from the GitHub API
    python scripts/update_profile.py --offline   # declared info only (no API calls)
    python scripts/update_profile.py --fixture f.json   # test with saved data

Normally the workflow .github/workflows/update-profile.yml runs this daily.
Only public, non-fork, non-archived repos are listed.
"""
import argparse, datetime as dt, json, os, re, sys, urllib.request
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frames as frames_mod

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
USER = os.environ.get("PROFILE_USER", "Mr1Err0r1")

# ------------------------------------------------------------ edit me
PROFILE = {
    "role": "developer · builder · CS student",
    "focus": "game dev · systems · networking",
    "stack": "Rust · Python · Java · C++ · C#",
    "env": "Linux · Git · terminal-first",
    "now_fallback": "rush_protocol",
}
EXCLUDE_REPOS = {USER.lower()}        # the profile repo itself; add more names here
MAX_PROJECTS = 8                      # rows in the README project table
SHOW_FORKS = False
# ----------------------------------------------------------------------

LANG_COLORS = {
    "Rust": "#dea584", "Python": "#3572A5", "Java": "#b07219", "C++": "#f34b7d",
    "C#": "#178600", "C": "#8a8a8a", "GDScript": "#4f8fb8", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#9b6bd6", "Shell": "#89e051",
    "Go": "#00ADD8", "Kotlin": "#A97BFF", "Lua": "#6a6aff",
}


# ------------------------------------------------------------ data
def api(path, token):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-updater",
                 **({"Authorization": f"Bearer {token}"} if token else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect(token):
    user = api(f"/users/{USER}", token)
    repos, page = [], 1
    while True:
        chunk = api(f"/users/{USER}/repos?per_page=100&type=owner&sort=pushed&page={page}", token)
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    repos = [r for r in repos
             if r["name"].lower() not in EXCLUDE_REPOS and not r["archived"]
             and (SHOW_FORKS or not r["fork"])]
    repos.sort(key=lambda r: r["pushed_at"], reverse=True)
    for r in repos:
        try:
            r["languages"] = api(f"/repos/{USER}/{r['name']}/languages", token)
        except Exception:
            r["languages"] = {}
    return {"user": user, "repos": repos}


def language_shares(repos, top=4):
    total = {}
    for r in repos:
        for lang, b in (r.get("languages") or {}).items():
            total[lang] = total.get(lang, 0) + b
    s = sum(total.values()) or 1
    return [(l, 100 * b / s) for l, b in sorted(total.items(), key=lambda x: -x[1])[:top]]


def account_age(created):
    d = dt.datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
    now = dt.datetime.now(dt.timezone.utc)
    months = (now.year - d.year) * 12 + now.month - d.month
    y, m = divmod(max(months, 0), 12)
    return f"{y}y {m}m" if y else f"{m}m"


# ------------------------------------------------------------ SVG card
FONT = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
FS, CW, LH = 12, 7.2, 14.5            # font size, char width, line height (left panel)
PITCH = 19                            # line pitch (right panel)


def build_rows(data):
    rows = [("header",), ("sep",),
            ("kv", "Role", PROFILE["role"]),
            ("kv", "Focus", PROFILE["focus"]),
            ("kv", "Stack", PROFILE["stack"]),
            ("kv", "Env", PROFILE["env"]), ("gap",)]
    if data:
        repos, user = data["repos"], data["user"]
        stars = sum(r["stargazers_count"] for r in repos)
        rows += [("kv", "Uptime", account_age(user["created_at"])),
                 ("kv", "Repos", f"{len(repos)} public · {stars} ★")]
        if repos:
            r = repos[0]
            rows += [("kv", "Now", r["name"] + (f" · {r['language']}" if r.get("language") else "")),
                     ("kv", "Last push", r["pushed_at"][:10])]
        shares = language_shares(repos)
        if shares:
            rows += [("gap",), ("kv", "Languages", "")] + [("bar", l, p) for l, p in shares]
    else:
        rows += [("kv", "Now", PROFILE["now_fallback"])]
    rows += [("gap",), ("palette",)]
    return rows


def render_svg(data, frames, fps):
    n = len(frames)
    cols = max(len(r) for f in frames for r in f)
    nrows = max(len(f) for f in frames)
    rows = build_rows(data)
    right_h = sum({"gap": 10, "palette": 36, "sep": 12}.get(r[0], PITCH) for r in rows)
    body_h = max(nrows * LH, right_h)
    TOP, PADX, GAP = 36, 28, 40
    left_w = cols * CW
    xr = PADX + left_w + GAP                 # right panel x
    W = int(xr + 470 + PADX)
    H = int(TOP + 24 + body_h + 44)
    y0 = TOP + 24
    T = n / fps
    p = 100 / n
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(USER)} profile card">')
    o.append("<defs>"
             f'<clipPath id="win"><rect width="{W}" height="{H}" rx="10"/></clipPath>'
             f'<linearGradient id="lg" gradientUnits="userSpaceOnUse" x1="{PADX}" y1="{y0}" x2="{PADX+left_w}" y2="{y0+nrows*LH}">'
             '<stop offset="0" stop-color="#00ff9c"/><stop offset="1" stop-color="#2fc4ff"/></linearGradient></defs>')
    o.append("<style>"
             f"text{{font-family:{FONT};font-size:{FS}px}}"
             ".a{fill:url(#lg)}.k{fill:#00ff9c;font-weight:700}.v{fill:#c9d1d9}.d{fill:#8b949e}"
             ".f{opacity:0;animation:show " + f"{T:.3f}s linear infinite}}.f0{{opacity:1}}"
             f"@keyframes show{{0%{{opacity:1}}{p:.3f}%{{opacity:1}}{p+0.01:.3f}%{{opacity:0}}100%{{opacity:0}}}}"
             ".cur{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
             "</style>")
    o.append(f'<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="#0d1117"/>'
             f'<rect width="{W}" height="{TOP}" fill="#161b22"/>'
             f'<circle cx="22" cy="18" r="6" fill="#ff5f56"/><circle cx="42" cy="18" r="6" fill="#ffbd2e"/><circle cx="62" cy="18" r="6" fill="#27c93f"/>'
             f'<text class="d" x="{W/2}" y="22" text-anchor="middle">{escape(USER.lower())}@github: ~</text></g>')
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="#30363d"/>')

    # left: animated ASCII frames
    for i, fr in enumerate(frames):
        o.append(f'<g class="f f{i}" style="animation-delay:{i*T/n:.3f}s">')
        for j, line in enumerate(fr):
            s = line.rstrip()
            lead = len(s) - len(s.lstrip())
            s = s.strip()
            if not s:
                continue
            o.append(f'<text class="a" x="{PADX+lead*CW:.1f}" y="{y0+(j+1)*LH-3:.1f}" textLength="{len(s)*CW:.1f}" lengthAdjust="spacing" xml:space="preserve">{escape(s)}</text>')
        o.append("</g>")

    # right: neofetch-style info
    y = y0
    for r in rows:
        kind = r[0]
        if kind == "header":
            y += PITCH
            o.append(f'<text x="{xr}" y="{y-5}"><tspan class="k" font-size="14">{escape(USER.lower())}</tspan><tspan class="v" font-size="14">@</tspan><tspan class="k" font-size="14">github</tspan></text>')
        elif kind == "sep":
            y += 12
            o.append(f'<line x1="{xr}" y1="{y-6}" x2="{xr+16*8.4:.0f}" y2="{y-6}" stroke="#30363d"/>')
        elif kind == "gap":
            y += 10
        elif kind == "kv":
            y += PITCH
            o.append(f'<text class="k" x="{xr}" y="{y-5}">{escape(r[1])}</text>')
            if r[2]:
                o.append(f'<text class="v" x="{xr+90}" y="{y-5}">{escape(r[2])}</text>')
        elif kind == "bar":
            y += PITCH
            name, pct = r[1], r[2]
            col = LANG_COLORS.get(name, "#8b949e")
            o.append(f'<text class="v" x="{xr+20}" y="{y-5}">{escape(name)}</text>'
                     f'<rect x="{xr+90}" y="{y-14}" width="230" height="9" rx="4.5" fill="#21262d"/>'
                     f'<rect x="{xr+90}" y="{y-14}" width="{max(6, 230*pct/100):.0f}" height="9" rx="4.5" fill="{col}"/>'
                     f'<text class="d" x="{xr+330}" y="{y-5}">{pct:.1f}%</text>')
        elif kind == "palette":
            y += 12
            cols_ = ["#484f58", "#ff5555", "#00ff9c", "#f1fa8c", "#6e9bff", "#bd93f9", "#2fc4ff", "#c9d1d9"]
            for k_, c_ in enumerate(cols_):
                o.append(f'<rect x="{xr+k_*26}" y="{y-6}" width="26" height="14" fill="{c_}"/>')
            y += 24

    py = H - 16
    o.append(f'<text class="d" x="{PADX}" y="{py}">{escape(USER.lower())}@github:~$ </text>'
             f'<rect class="cur" x="{PADX+(len(USER)+11)*CW:.0f}" y="{py-11}" width="7" height="13" fill="#00ff9c"/>')
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------ README table
def projects_table(data):
    repos = data["repos"][:MAX_PROJECTS] if data else []
    if not repos:
        return "_No public projects yet._"
    t = ["| Project | Description | Language | Updated |", "| :-- | :-- | :-- | :-- |"]
    for r in repos:
        desc = (r["description"] or "—").replace("|", "\\|").replace("\n", " ")
        t.append(f"| [**{r['name']}**]({r['html_url']}) | {desc} | {r['language'] or '—'} | {r['pushed_at'][:10]} |")
    return "\n".join(t)


def write_if_changed(path, text):
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old != text:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(text)
        print("updated", os.path.relpath(path, ROOT))
    else:
        print("unchanged", os.path.relpath(path, ROOT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--fixture")
    ap.add_argument("--out", default=ROOT, help="output root (default: repo root)")
    a = ap.parse_args()

    if a.fixture:
        data = json.load(open(a.fixture, encoding="utf-8"))
    elif a.offline:
        data = None
    else:
        data = collect(os.environ.get("GITHUB_TOKEN"))

    fr, fps = frames_mod.load_frames()
    write_if_changed(os.path.join(a.out, "assets", "neofetch.svg"), render_svg(data, fr, fps))

    readme = os.path.join(a.out, "README.md")
    if data is not None and os.path.exists(readme):
        text = open(readme, encoding="utf-8").read()
        pat = re.compile(r"(<!--START_SECTION:projects-->)(.*?)(<!--END_SECTION:projects-->)", re.S)
        if pat.search(text):
            write_if_changed(readme, pat.sub(lambda m: f"{m.group(1)}\n{projects_table(data)}\n{m.group(3)}", text))
        else:
            print("README has no project markers - table not updated")


if __name__ == "__main__":
    main()
