"""Write the preview image of saves as PNG, rows in the right order.

Usage: save_preview.py OUT_DIR SAVE.sav [...]

Read only. The preview in the save stream is raw RGB8 with the bottom row first (the game's
`.jpg` next to the save is the same picture, right way up and three times larger). The header's
flag byte before the preview size is 0 in about half the saves we looked at even though the image is there, so
the flag is ignored and the size is checked against width * height * 3 instead. See docs/header.md, "Preview".

The images are the save authors' pictures. Keep them out of this repo (see CLAUDE.md).
"""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from save_header import read_header  # noqa: E402
from tf3save import decompress  # noqa: E402


def png_bytes(width, height, rgb):
    """PNG file for raw RGB8 rows given top row first."""
    raw = b"".join(b"\x00" + rgb[y * width * 3:(y + 1) * width * 3] for y in range(height))

    def chunk(tag, body):
        crc = zlib.crc32(tag + body) & 0xFFFFFFFF
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", crc)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def preview_png(path):
    """PNG bytes of the save's preview, or None if the save has no usable one."""
    data = decompress(open(path, "rb").read())
    h = read_header(path, data)
    w, ht = h["preview_size"]
    off, n = h["preview_offset"], h["preview_bytes"]
    if not w or not ht or n != w * ht * 3:
        return None
    rgb = data[off:off + n]
    rows = [rgb[y * w * 3:(y + 1) * w * 3] for y in range(ht)]
    return png_bytes(w, ht, b"".join(reversed(rows)))


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    for path in sys.argv[2:]:
        try:
            png = preview_png(path)
        except Exception as e:  # report and carry on with the next save
            print(f"FAILED {path}: {e}")
            continue
        if png is None:
            print(f"no preview: {path}")
            continue
        dest = os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + ".png")
        open(dest, "wb").write(png)
        print(dest)


if __name__ == "__main__":
    main()
