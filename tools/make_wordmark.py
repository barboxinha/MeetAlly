"""Generate pencil-style handwritten 'MeetAlly' GIFs (pure Python, no deps).

Usage (from repo root): python tools/make_wordmark.py website/static/website
Writes meetally-{light,dark}.gif (animated, plays once) and
meetally-{light,dark}-static.gif (final frame, for reduced motion).
Keep the THEMES colors in sync with --accent / --bg in style.css.
"""
import math
import os
import random
import re
import struct
import sys

# Cursive strokes in design units (baseline y=100, x-height ~y=72, ascender ~y=42).
# Each string is one pen-down stroke; strokes are drawn in order.
STROKES = [
    # M e e t
    "M 6 100 C 10 86, 16 56, 22 44 C 25 39, 29 42, 29 50 C 29 64, 27 84, 26 100"
    " C 30 76, 36 48, 42 44 C 47 41, 50 46, 49 56 C 48 70, 46 88, 47 96"
    " C 48 101, 54 100, 58 96"
    " C 64 90, 72 82, 71 76 C 70 71, 63 72, 61 78 C 59 86, 62 99, 70 100"
    " C 76 101, 80 96, 84 92"
    " C 90 86, 96 80, 95 75 C 94 70, 87 71, 85 77 C 83 85, 86 99, 94 100"
    " C 100 101, 104 96, 108 90"
    " C 110 80, 112 64, 114 54 C 112 70, 110 86, 110 94 C 110 100, 116 101, 122 96",
    # t cross
    "M 104 69 C 110 68, 118 67, 126 66",
    # A l l y
    "M 167 46 C 158 38, 142 44, 138 62 C 134 78, 136 98, 146 99"
    " C 154 100, 160 88, 164 70 C 166 60, 167 50, 168 44"
    " C 166 62, 164 84, 166 96 C 167 101, 173 100, 178 94"
    " C 184 84, 190 62, 190 50 C 190 42, 186 40, 184 46 C 181 56, 180 84, 182 96"
    " C 183 101, 189 100, 194 94"
    " C 200 84, 206 62, 206 50 C 206 42, 202 40, 200 46 C 197 56, 196 84, 198 96"
    " C 199 101, 205 100, 210 92"
    " C 212 86, 213 78, 214 74 C 214 84, 214 98, 221 99 C 226 99, 230 90, 232 74"
    " C 231 92, 229 112, 226 124 C 223 132, 214 131, 215 122 C 216 114, 228 106, 240 96",
]

SCALE = 1.6          # pixels per design unit (image is shown at about half size for hi-DPI)
PAD = 6              # design units of padding
PEN_RADIUS = 4.6     # pixels
WRITE_SECONDS = 2.2
FRAME_CS = 4         # frame delay in 1/100 s
LIFT_SECONDS = 0.15  # pause for each pen lift

THEMES = {
    # accent, page background, contrast direction for the darkest graphite tone
    "light": ("#1f88a8", "#f6f8fa", "#000000"),
    "dark": ("#3aa9cc", "#0f1419", "#ffffff"),
}


def parse_path(d):
    tokens = re.findall(r"[MC]|-?\d+(?:\.\d+)?", d)
    segs, i, cur = [], 0, None
    while i < len(tokens):
        cmd = tokens[i]
        i += 1
        if cmd == "M":
            cur = (float(tokens[i]), float(tokens[i + 1]))
            i += 2
        while i < len(tokens) and tokens[i] not in "MC":
            pts = [(float(tokens[i + k]), float(tokens[i + k + 1])) for k in (0, 2, 4)]
            i += 6
            segs.append((cur, *pts))
            cur = pts[2]
    return segs


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
                 for a, b, c, d in zip(p0, p1, p2, p3))


def sample_strokes():
    """Return a list of strokes, each a list of evenly spaced (x, y) pixel points."""
    strokes = []
    for d in STROKES:
        dense = []
        for seg in parse_path(d):
            for k in range(200):
                dense.append(bezier(*seg, k / 200))
        dense.append(bezier(*parse_path(d)[-1], 1.0))
        pts = [((x + PAD) * SCALE, (y - 36 + PAD) * SCALE) for x, y in dense]
        even, acc = [pts[0]], 0.0
        for a, b in zip(pts, pts[1:]):
            acc += math.dist(a, b)
            if acc >= 0.35:
                even.append(b)
                acc = 0.0
        strokes.append(even)
    return strokes


def render_times(strokes, width, height):
    """Map each inked pixel to (time it is drawn, tone index 1..3)."""
    rng = random.Random(7)
    grain = [[rng.random() for _ in range(width)] for _ in range(height)]
    tone_noise = [[rng.random() for _ in range(width)] for _ in range(height)]
    total = sum(len(s) for s in strokes)
    per_point = WRITE_SECONDS / total
    ink, t, travelled = {}, 0.0, 0
    for s_index, stroke in enumerate(strokes):
        if s_index:
            t += LIFT_SECONDS
        for x, y in stroke:
            # gentle pressure variation along the line
            r = PEN_RADIUS * (0.9 + 0.15 * math.sin(travelled * 0.045))
            travelled += 1
            for py in range(int(y - r - 1), int(y + r + 2)):
                for px in range(int(x - r - 1), int(x + r + 2)):
                    if not (0 <= px < width and 0 <= py < height) or (px, py) in ink:
                        continue
                    dist = math.hypot(px + 0.5 - x, py + 0.5 - y) / r
                    if dist > 1:
                        continue
                    # denser graphite in the middle of the line, speckled at the edges
                    if grain[py][px] > 0.95 - 0.55 * dist * dist:
                        continue
                    n = tone_noise[py][px] + 0.6 * dist
                    tone = 1 if n < 0.55 else 2 if n < 1.05 else 3
                    ink[(px, py)] = (t, tone)
            t += per_point
    return ink, t


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, w):
    return tuple(round(x + (y - x) * w) for x, y in zip(a, b))


def lzw_encode(indices, min_size):
    clear, eoi = 1 << min_size, (1 << min_size) + 1
    out, bit_buf, bit_len = bytearray(), 0, 0

    def emit(code, size):
        nonlocal bit_buf, bit_len
        bit_buf |= code << bit_len
        bit_len += size
        while bit_len >= 8:
            out.append(bit_buf & 0xFF)
            bit_buf >>= 8
            bit_len -= 8

    def reset():
        return {(i,): i for i in range(clear)}, min_size + 1, eoi + 1

    table, size, next_code = reset()
    emit(clear, size)
    w = (indices[0],)
    for k in indices[1:]:
        wk = w + (k,)
        if wk in table:
            w = wk
            continue
        emit(table[w], size)
        table[wk] = next_code
        next_code += 1
        if next_code > (1 << size) and size < 12:
            size += 1
        if next_code == 4096:
            emit(clear, size)
            table, size, next_code = reset()
        w = (k,)
    emit(table[w], size)
    emit(eoi, size)
    if bit_len:
        out.append(bit_buf & 0xFF)
    return bytes(out)


def write_gif(path, width, height, palette, frames, loop=False):
    """frames: list of (x, y, w, h, indices, delay_cs). Index 0 is transparent."""
    data = bytearray(b"GIF89a")
    data += struct.pack("<HHBBB", width, height, 0xF2, 0, 0)  # 8-color global table
    for rgb in palette + [(0, 0, 0)] * (8 - len(palette)):
        data += bytes(rgb)
    if loop:
        data += b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00"
    for x, y, w, h, indices, delay in frames:
        data += struct.pack("<BBBBHBB", 0x21, 0xF9, 4, 0x05, delay, 0, 0)  # keep, transparent idx 0
        data += struct.pack("<BHHHHB", 0x2C, x, y, w, h, 0)
        data += bytes([3])
        encoded = lzw_encode(indices, 3)
        for i in range(0, len(encoded), 255):
            chunk = encoded[i:i + 255]
            data += bytes([len(chunk)]) + chunk
        data += b"\x00"
    data += b";"
    with open(path, "wb") as f:
        f.write(data)


def build(out_dir):
    strokes = sample_strokes()
    width = math.ceil(max(x for s in strokes for x, _ in s) + PAD * SCALE)
    height = math.ceil(max(y for s in strokes for _, y in s) + PAD * SCALE)
    ink, duration = render_times(strokes, width, height)
    frame_s = FRAME_CS / 100
    n_frames = math.ceil(duration / frame_s)

    for name, (accent, surface, contrast) in THEMES.items():
        accent, surface, contrast = hex_rgb(accent), hex_rgb(surface), hex_rgb(contrast)
        palette = [surface, mix(accent, contrast, 0.18), accent, mix(accent, surface, 0.35)]

        frames = [(0, 0, 1, 1, [0], FRAME_CS)]
        for f in range(n_frames):
            lo, hi = f * frame_s, (f + 1) * frame_s
            new = {p: tone for p, (t, tone) in ink.items() if lo <= t < hi or (f == n_frames - 1 and t >= hi)}
            if not new:
                frames.append((0, 0, 1, 1, [0], FRAME_CS))
                continue
            x0 = min(p[0] for p in new); x1 = max(p[0] for p in new)
            y0 = min(p[1] for p in new); y1 = max(p[1] for p in new)
            w, h = x1 - x0 + 1, y1 - y0 + 1
            idx = [new.get((x0 + i, y0 + j), 0) for j in range(h) for i in range(w)]
            frames.append((x0, y0, w, h, idx, FRAME_CS))
        write_gif(os.path.join(out_dir, f"meetally-{name}.gif"), width, height, palette, frames)

        final = [ink[(i, j)][1] if (i, j) in ink else 0 for j in range(height) for i in range(width)]
        write_gif(os.path.join(out_dir, f"meetally-{name}-static.gif"), width, height, palette,
                  [(0, 0, width, height, final, 0)])
    print(f"{width}x{height}px, {n_frames} frames, {duration:.2f}s")


if __name__ == "__main__":
    build(sys.argv[1])
