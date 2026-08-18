"""Cover-art open helpers for catalog metadata."""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET

from PIL import Image


def read_cover_meta(base_dir: str, relpath: str) -> str:
    p = os.path.join(base_dir, relpath)
    # Publisher SVG jackets expose dimensions as XML attributes.
    if p.lower().endswith(".svg"):
        root = ET.parse(p).getroot()
        width = root.attrib.get("width", "?")
        height = root.attrib.get("height", "?")
        return f"{p}: SVG ({width}, {height})"

    # Raster jackets are inspected through Pillow for format and pixel dimensions.
    with Image.open(p) as im:
        return f"{p}: {im.format} {im.size}"
