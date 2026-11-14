#!/usr/bin/env python3
"""Generate the Orama Lake logo: the O of Orama, holding a lake.

Usage: python3 docs/assets/logo.py docs/assets
Writes logo-light.svg and logo-dark.svg (the mark alone, 120 x 120).
"""
import sys

OUT = sys.argv[1]

# The same teal, blue and violet the architecture diagram uses for liquid, lake and zetta.
THEMES = {
    "light": ("#14b8a6", "#2f7bf6", "#7c3aed"),
    "dark": ("#2dd4bf", "#58a6ff", "#a78bfa"),
}


def build(colors):
    a, b, c = colors
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120" role="img" '
        'aria-labelledby="t">\n'
        '<title id="t">Orama Lake</title>\n'
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
        '</svg>\n'
    )


for name, colors in THEMES.items():
    with open(f"{OUT}/logo-{name}.svg", "w") as f:
        f.write(build(colors))
print("written")
