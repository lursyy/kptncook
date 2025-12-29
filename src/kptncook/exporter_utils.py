import re
import shutil
import zipfile
from pathlib import Path
from typing import Iterable

from unidecode import unidecode

from kptncook.models import Image

ZipContent = bytes | str | Path


def asciify_string(s: str) -> str:
    s = unidecode(s)
    s = re.sub(r"[^\w\s]", "_", s)
    s = re.sub(r"\s+", "_", s)
    return s


def get_cover(image_list: list[Image] | None) -> Image | None:
    if not isinstance(image_list, list):
        return None
    covers = [image for image in image_list if image.type == "cover"]
    if len(covers) != 1:
        return None
    return covers[0]

def replace_timers_in_step(step, text: str) -> str:
    """Replace <timer> placeholders in `text` using timers from `step`.

    Uses the step.timers list and the timer.min_or_exact field. Consumes timers in order
    without mutating the original list. Assumes timers have a `min_or_exact` value.
    """
    timers = list(getattr(step, "timers", []) or [])
    timer_iter = iter(timers)
    def repl(match, _it=timer_iter):
        t = next(_it, None)
        if t is None:
            return match.group(0)
        return f"{t.min_or_exact}m"
    return re.sub(r"<timer>", repl, text)

def move_to_target_dir(source: str | Path, target: str | Path) -> str:
    return shutil.move(str(source), str(target))


def write_zip(zip_path: Path, entries: Iterable[tuple[str, ZipContent]]) -> None:
    with zipfile.ZipFile(
        zip_path, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True
    ) as zip_file:
        for arcname, content in entries:
            if isinstance(content, Path):
                zip_file.write(content, arcname=arcname)
            else:
                zip_file.writestr(arcname, content)
