# Generates the "AaBb" hero image for the README.
# Run from the root level of the repository, after `make build`
# (or with the committed fonts in fonts/variable/):
# $ python3 docs/image1.py --output docs/image1.png
#
# Adapted from googlefonts/googlefonts-project-template
# documentation/image1.py for a monospace variable font:
# the display size is derived from the fixed advance width so the
# text always fills the frame exactly.

from drawbot_skia.drawbot import *
from fontTools.ttLib import TTFont
from fontTools.misc.fixedTools import floatToFixedToStr

import subprocess
import argparse

# Constants, these are the main "settings" for the image
WIDTH, HEIGHT, MARGIN = 2048, 1024, 128
FONT_PATH = "fonts/variable/BuenaMono-VF.ttf"
FONT_LICENSE = "OFL v1.1"
AUXILIARY_FONT = FONT_PATH  # captions set in Buena Mono itself
AUXILIARY_FONT_SIZE = 48

BIG_TEXT = "AaBb"
BIG_TEXT_SIDE_MARGIN = MARGIN * 1
BIG_TEXT_BOTTOM_MARGIN = MARGIN * 2

GRID_VIEW = False  # Toggle this for a grid overlay

# Handle the "--output" flag
parser = argparse.ArgumentParser()
parser.add_argument("--output", metavar="PNG", help="where to write the PNG file")
args = parser.parse_args()

# Load the font with fontTools
ttFont = TTFont(FONT_PATH)

# Constants that are worked out dynamically
MY_URL = subprocess.check_output("git remote get-url origin", shell=True).decode()
MY_URL = MY_URL.strip().replace("https://", "").removesuffix(".git")
MY_HASH = subprocess.check_output("git rev-parse --short HEAD", shell=True).decode()
FONT_NAME = ttFont["name"].getDebugName(4)
FONT_VERSION = "v%s" % floatToFixedToStr(ttFont["head"].fontRevision, 16)

# Monospace: every glyph has the same advance, so the biggest size
# that fits the frame is exact, not trial and error.
UPM = ttFont["head"].unitsPerEm
ADVANCE = ttFont["hmtx"]["A"][0]
BIG_TEXT_FONT_SIZE = (WIDTH - MARGIN * 2) / (len(BIG_TEXT) * ADVANCE / UPM)


# Draws a grid
def grid():
    stroke(1, 0, 0, 0.75)
    strokeWidth(2)
    STEP_X, STEP_Y = 0, 0
    INCREMENT_X, INCREMENT_Y = MARGIN / 2, MARGIN / 2
    rect(MARGIN, MARGIN, WIDTH - (MARGIN * 2), HEIGHT - (MARGIN * 2))
    for x in range(29):
        polygon((MARGIN + STEP_X, MARGIN), (MARGIN + STEP_X, HEIGHT - MARGIN))
        STEP_X += INCREMENT_X
    for y in range(29):
        polygon((MARGIN, MARGIN + STEP_Y), (WIDTH - MARGIN, MARGIN + STEP_Y))
        STEP_Y += INCREMENT_Y
    polygon((WIDTH / 2, 0), (WIDTH / 2, HEIGHT))
    polygon((0, HEIGHT / 2), (WIDTH, HEIGHT / 2))


# Draw the page/frame and a grid if "GRID_VIEW" is set to "True"
def draw_background():
    newPage(WIDTH, HEIGHT)
    fill(0)
    rect(-2, -2, WIDTH + 2, HEIGHT + 2)
    if GRID_VIEW:
        grid()


# Draw main text
def draw_main_text():
    fill(1)
    stroke(None)
    font(FONT_PATH)
    fontSize(BIG_TEXT_FONT_SIZE)
    text(BIG_TEXT, (BIG_TEXT_SIDE_MARGIN, BIG_TEXT_BOTTOM_MARGIN))


# Divider lines
def draw_divider_lines():
    stroke(1)
    strokeWidth(5)
    lineCap("round")
    line((MARGIN, HEIGHT - (MARGIN * 1.5)), (WIDTH - MARGIN, HEIGHT - (MARGIN * 1.5)))
    line((MARGIN, MARGIN + (MARGIN / 2)), (WIDTH - MARGIN, MARGIN + (MARGIN / 2)))
    stroke(None)


# Draw text describing the font and its git status & repo URL
def draw_auxiliary_text():
    font(AUXILIARY_FONT)
    fontSize(AUXILIARY_FONT_SIZE)
    POS_TOP_LEFT = (MARGIN, HEIGHT - MARGIN * 1.25)
    POS_TOP_RIGHT = (WIDTH - MARGIN, HEIGHT - MARGIN * 1.25)
    POS_BOTTOM_LEFT = (MARGIN, MARGIN)
    POS_BOTTOM_RIGHT = (WIDTH - MARGIN * 0.95, MARGIN)
    URL_AND_HASH = MY_URL + " at commit " + MY_HASH
    URL_AND_HASH = URL_AND_HASH.replace("\n", " ").strip()
    text(FONT_NAME, POS_TOP_LEFT, align="left")
    text(FONT_VERSION, POS_TOP_RIGHT, align="right")
    text(URL_AND_HASH, POS_BOTTOM_LEFT, align="left")
    text(FONT_LICENSE, POS_BOTTOM_RIGHT, align="right")


# Build and save the image
if __name__ == "__main__":
    draw_background()
    draw_main_text()
    draw_divider_lines()
    draw_auxiliary_text()
    saveImage(args.output)
    print("DrawBot: Done")
