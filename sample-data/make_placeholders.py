#!/usr/bin/env python3
"""Generate neutral synthetic placeholder PNGs (no real data, stdlib only).

Creates flat-tone images with a soft foot-shaped oval so downstream code has
something 'foot-like' to process, without any camera or patient content.
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

W, H = 480, 640


def _png(pixels: bytes, width: int, height: int) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    # add filter byte (0) at the start of each row
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(pixels[y * stride : (y + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def make(name: str, base=(210, 205, 198), oval=(196, 170, 150)) -> None:
    cx, cy, rx, ry = W // 2, H // 2, W // 3.2, H // 2.6
    px = bytearray()
    for y in range(H):
        for x in range(W):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            inside = nx * nx + ny * ny <= 1.0
            r, g, b = oval if inside else base
            px += bytes((r, g, b))
    out = Path(__file__).with_name(name)
    out.write_bytes(_png(bytes(px), W, H))
    print("wrote", out)


if __name__ == "__main__":
    make("neutral-right-plantar.png")
    make("neutral-left-plantar.png")
