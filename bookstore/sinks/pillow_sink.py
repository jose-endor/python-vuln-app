"""Image open — older Pillow in requirements for SCA CVEs."""
from __future__ import annotations

import os

from PIL import Image  # SCA: Pillow 8.4.0 (demonstration)


def read_cover_meta(base_dir: str, relpath: str) -> str:
    p = os.path.join(base_dir, relpath)
    with Image.open(p) as im:
        return f"{p}: {im.format} {im.size}"
