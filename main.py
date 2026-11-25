"""Write the day's news image to /output/entry.png.

The image (news.png) is committed to this repository; this program copies
it byte-for-byte, so every run writes exactly the same bytes.
"""
import shutil
from pathlib import Path

OUT = Path("/output/entry.png")

def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(__file__).resolve().parent / "news.png", OUT)

if __name__ == "__main__":
    main()
