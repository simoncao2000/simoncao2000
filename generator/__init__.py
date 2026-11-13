"""Generate the GitHub profile README artwork.

Run from the repository root:

    pip install -r generator/requirements.txt
    python -m generator

Layout:
    content.py       every piece of text on the profile (edit this one)
    palette.py       Catppuccin colours mapped to drawing roles
    fonts.py         font download, text measurement and outlines
    svg.py           shared SVG building blocks
    leetcode_api.py  fetch LeetCode stats
    blocks/          one module per image on the profile
    __main__.py      writes every image to assets/<theme>/
"""
