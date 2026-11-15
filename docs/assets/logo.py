#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Generate the Orama Lake logo: the O of Orama, holding a lake.

Usage: python3 docs/assets/logo.py docs/assets
Writes logo-light.svg and logo-dark.svg (the mark alone, 120 x 120), and
lockup-light.svg and lockup-dark.svg (the mark, the name and the slogan, 450 x 120).
"""
import sys

OUT = sys.argv[1]

# The same teal, blue and violet the architecture diagram uses for liquid, lake and zetta.
THEMES = {
    "light": ("#14b8a6", "#2f7bf6", "#7c3aed"),
    "dark": ("#2dd4bf", "#58a6ff", "#a78bfa"),
}
# Name and slogan colours per theme.
INK = {"light": ("#101828", "#59636e"), "dark": ("#e6edf3", "#9198a1")}
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"


def build(colors, ink=None):
    a, b, c = colors
    width = 450 if ink else 120
    title = "Orama Lake: the sovereign AI stack" if ink else "Orama Lake"
    words = ""
    if ink:
        words = (
            f'<text x="144" y="68" font-family="{FONT}" font-size="50" font-weight="700" letter-spacing="-1.4" '
            f'fill="{ink[0]}">Orama <tspan fill="url(#g)">Lake</tspan></text>\n'
            f'<text x="146" y="98" font-family="{FONT}" font-size="15.5" font-weight="600" letter-spacing="3.1" '
            f'fill="{ink[1]}">THE SOVEREIGN AI STACK</text>\n'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 120" width="{width}" height="120" role="img" '
        'aria-labelledby="t">\n'
        f'<title id="t">{title}</title>\n'
        '<defs>\n'
        '<linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{a}"/><stop offset="0.5" stop-color="{b}"/>'
        f'<stop offset="1" stop-color="{c}"/></linearGradient>\n'
        '<clipPath id="c"><circle cx="60" cy="60" r="30"/></clipPath>\n'
        '</defs>\n'
        # the O
        '<circle cx="60" cy="60" r="44" fill="none" stroke="url(#g)" stroke-width="12"/>\n'
        # the lake
        '<g clip-path="url(#c)" fill="url(#g)"><path d="M20 64q10 -9 20 0t20 0t20 0t20 0V110H20Z"/></g>\n'
        # the sun over it
        '<circle cx="71" cy="45" r="6.5" fill="url(#g)"/>\n'
        + words +
        '</svg>\n'
    )


for name, colors in THEMES.items():
    with open(f"{OUT}/logo-{name}.svg", "w") as f:
        f.write(build(colors))
    with open(f"{OUT}/lockup-{name}.svg", "w") as f:
        f.write(build(colors, INK[name]))
print("written")
