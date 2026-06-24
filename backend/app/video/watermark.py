import os
import subprocess
import uuid

from app.config import STORAGE_PROCESSED
from app.models import Watermark

_POSITION_EXPR = {
    "top_left": "10:10",
    "top_right": "main_w-overlay_w-10:10",
    "bottom_left": "10:main_h-overlay_h-10",
    "bottom_right": "main_w-overlay_w-10:main_h-overlay_h-10",
}


def apply_watermark(video_path: str, watermark: Watermark) -> str:
    os.makedirs(STORAGE_PROCESSED, exist_ok=True)
    out_path = os.path.join(STORAGE_PROCESSED, f"{uuid.uuid4().hex}.mp4")
    overlay_xy = _POSITION_EXPR.get(watermark.position, _POSITION_EXPR["bottom_right"])

    filter_complex = (
        f"[1:v]format=rgba,colorchannelmixer=aa={watermark.opacity},"
        f"scale=iw*{watermark.scale}:-1[wm];"
        f"[0:v][wm]overlay={overlay_xy}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", watermark.file_path,
        "-filter_complex", filter_complex,
        "-codec:a", "copy",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path
