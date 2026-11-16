#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Generate the Orama Lake architecture diagram as light and dark SVGs."""
import sys
from html import escape

OUT = sys.argv[1]
W, H = 1200, 880
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"

THEMES = {
    "light": dict(bg="#ffffff", panel="#f6f8fa", card="#ffffff", line="#d0d7de", text="#1f2328", mute="#59636e",
                  arrow="#8c959f", chip="#ffffff",
                  lake=("#0969da", "#ddf4ff"), liquid=("#0f766e", "#d7f5ef"), zetta=("#7c3aed", "#f0e9ff"),
                  ai=("#bf3989", "#ffeff7"), op=("#b45309", "#fff4d6"), api=("#1f2328", "#ffffff")),
    "dark": dict(bg="#0d1117", panel="#161b22", card="#0d1117", line="#30363d", text="#e6edf3", mute="#9198a1",
                 arrow="#6e7681", chip="#0d1117",
                 lake=("#58a6ff", "#0c2d6b"), liquid=("#2dd4bf", "#0b3b36"), zetta=("#a78bfa", "#2e1f5e"),
                 ai=("#f778ba", "#4a1535"), op=("#f0b040", "#4a3208"), api=("#e6edf3", "#0d1117")),
}


def build(t):
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
      f'aria-labelledby="t d" font-family="{FONT}">')
    a('<title id="t">How Orama Lake fits together</title>')
    a('<desc id="d">People, scripts and agents reach lake through one API served as REST, OpenAPI and MCP. '
      'lake holds AI Projects and the platform services. Under it are liquid for source control, builds and deploys, '
      'zetta as the engine for each workspace, and the agents and models. The operator runs all of it as '
      'infrastructure as software, from one management cluster to dedicated leaf clusters.</desc>')
    a(f'<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      f'<path d="M0 0L10 5L0 10z" fill="{t["arrow"]}"/></marker></defs>')
    a(f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>')

    def text(x, y, s, size=14, weight=400, fill=None, anchor="start", ls=None):
        extra = f' letter-spacing="{ls}"' if ls else ""
        a(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill or t["text"]}" '
          f'text-anchor="{anchor}"{extra}>{escape(s)}</text>')

    def rect(x, y, w, h, fill, stroke, r=12, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def chip(x, y, w, s, color, h=30):
        rect(x, y, w, h, t["chip"], color, r=h / 2, sw=1.25)
        text(x + w / 2, y + h / 2 + 4.5, s, 13, 500, anchor="middle")

    def arrow(x1, y1, x2, y2, both=False):
        m = ' marker-start="url(#ah)"' if both else ""
        a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["arrow"]}" stroke-width="1.75" marker-end="url(#ah)"{m}/>')

    def panel(x, y, w, h, key, name, tag):
        c, tint = t[key]
        rect(x, y, w, h, t["panel"], t["line"])
        a(f'<path d="M{x + 12} {y}h{w - 24}a12 12 0 0 1 12 12v4H{x}v-4a12 12 0 0 1 12 -12z" fill="{c}"/>')
        text(x + 22, y + 48, name, 22, 700)
        text(x + 22, y + 70, tag, 13.5, 400, t["mute"])
        return c, tint

    def bullets(x, y, lines, color):
        for i, s in enumerate(lines):
            yy = y + i * 25
            a(f'<circle cx="{x + 4}" cy="{yy - 4.5}" r="3.5" fill="{color}"/>')
            text(x + 17, yy, s, 13.5)

    # ---- callers
    for i, s in enumerate(["People", "Scripts", "Agents"]):
        x = 330 + i * 190
        rect(x, 24, 160, 42, t["panel"], t["line"], r=21)
        text(x + 80, 50.5, s, 15, 600, anchor="middle")
        arrow(x + 80, 68, x + 80, 96)

    # ---- one API
    c, _ = t["api"]
    rect(230, 100, 740, 52, t["api"][1], c, r=26, sw=2)
    text(262, 132, "One API", 16, 700)
    text(600, 132, "REST  ·  OpenAPI  ·  MCP", 15, 500, anchor="middle", ls="0.3")
    rect(826, 113, 122, 26, t["op"][1], t["op"][0], r=13, sw=1.25)
    text(887, 130.5, "100% coverage", 12.5, 600, anchor="middle")
    arrow(600, 154, 600, 182)

    # ---- lake
    c, tint = panel(60, 186, 1080, 224, "lake", "lake", "where your whole team designs, trains and ships AI")
    rect(84, 270, 640, 122, tint, c, r=10, sw=1.25)
    text(104, 298, "AI Project", 15.5, 700)
    text(190, 298, "one ensemble, working together for one purpose", 13, 400, t["mute"])
    for i, s in enumerate(["models", "workflows", "agents", "databases", "storage", "apps"]):
        chip(104 + i * 101, 316, 93, s, c)
    text(104, 378, "design it in one place  ·  ship it as one thing", 12.5, 400, t["mute"])
    for i, s in enumerate(["sign-in", "secrets", "registry", "search", "drive", "repositories"]):
        chip(752 + (i % 2) * 186, 276 + (i // 2) * 40, 176, s, t["line"])

    # ---- connectors
    arrow(230, 412, 230, 452)
    text(242, 437, "linked as a library", 12.5, 400, t["mute"])
    arrow(600, 412, 600, 452)
    text(612, 437, "one engine per workspace", 12.5, 400, t["mute"])
    arrow(970, 412, 970, 452, both=True)
    text(982, 437, "through the API", 12.5, 400, t["mute"])

    # ---- engines
    c, _ = panel(60, 456, 340, 178, "liquid", "liquid", "source control, builds and deploys")
    bullets(84, 568, ["every write captured and signed", "only what changed is rebuilt", "imports from Git, exports back"], c)
    c, _ = panel(430, 456, 340, 178, "zetta", "zetta", "the engine: equal peers, no leader")
    bullets(454, 568, ["data, SQL and full-text search", "machine learning, with explanations", "distributed training and inference"], c)
    c, _ = panel(800, 456, 340, 178, "ai", "agents and models", "AI that creates and ships AI")
    bullets(824, 568, ["agents that build agents and apps", "swarms and teams, on streams", "models you train and serve yourself"], c)

    # ---- operator
    for x in (230, 600, 970):
        arrow(x, 676, x, 638)
    c, tint = panel(60, 680, 1080, 150, "op", "the operator", "infrastructure as software: always reconciling, mutable at runtime")
    rect(560, 706, 196, 100, tint, c, r=10, sw=1.25)
    text(658, 750, "management", 14, 700, anchor="middle")
    text(658, 770, "cluster", 14, 700, anchor="middle")
    text(658, 792, "one helmfile", 12, 400, t["mute"], anchor="middle")
    for i in range(3):
        y = 708 + i * 34
        arrow(758, 756, 800, y + 14)
        rect(804, y, 150, 28, t["chip"], c, r=8, sw=1.25)
        text(879, y + 18.5, "leaf cluster", 12.5, 500, anchor="middle")
    for i, s in enumerate(["DNS", "buckets", "and more"]):
        chip(984, 708 + i * 34, 132, s, t["line"], h=28)
    bullets(84, 782, ["clusters, DNS and buckets, spun up on the fly", "hyperconverged: fewer machines, lower cost"], c)

    # ---- footer
    text(600, 862, "on-prem   ·   private cloud   ·   public cloud   ·   air-gapped", 14, 500, t["mute"], anchor="middle", ls="0.4")
    a("</svg>")
    return "\n".join(o) + "\n"


for name, t in THEMES.items():
    open(f"{OUT}/architecture-{name}.svg", "w").write(build(t))
print("written")
