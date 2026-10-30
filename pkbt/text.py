"""Read Pokemon dialogue from a GBA screenshot.

Uses the pkmngba_en training file with Tesseract's legacy engine. The file
belongs in the tessdata directory from config.
"""

import pytesseract
from PIL import Image, ImageOps

from pkbt.config import TESSDATA_DIR, TESSERACT

pytesseract.pytesseract.tesseract_cmd = TESSERACT
LANG = "pkmngba_en"
# Tesseract reads this font reliably once the crop is about this tall.
MIN_HEIGHT = 200

# left, top, right, bottom on a 240x160 frame.
# The message pane beside FIGHT / BAG / POKEMON / RUN.
BATTLE_TEXT_BOX = (10, 121, 118, 151)
# The wide box used by "Wild X appeared!" before the command menu opens.
FULL_DIALOGUE_BOX = (10, 121, 230, 151)
# Status text on the player's battle panel, inside the frame.
PLAYER_PKMN_STATUS_BOX = (142, 96, 162, 107)


def read_text(source, box: tuple[int, int, int, int]) -> str:
    """Return the text inside box. source is an image or a path to one."""
    traineddata = TESSDATA_DIR / f"{LANG}.traineddata"
    if not traineddata.is_file():
        raise FileNotFoundError(
            f"Missing {traineddata}. The GBA English training file is pkmngba_en.traineddata."
        )
    image = _open(source)
    prepared = _prepare(image, box)
    config = f"--tessdata-dir {TESSDATA_DIR} --oem 0 --psm 6"
    return pytesseract.image_to_string(prepared, lang=LANG, config=config).strip()


def _open(source) -> Image.Image:
    if isinstance(source, Image.Image):
        return source
    return Image.open(source)


def _prepare(image: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    image = image.convert("L").crop(box)
    image = ImageOps.autocontrast(image)
    scale = max(1.0, MIN_HEIGHT / image.height)
    if scale > 1:
        image = image.resize(
            (int(image.width * scale), int(image.height * scale)),
            Image.Resampling.BILINEAR,
        )
    return image
