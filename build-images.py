#!/usr/bin/env python3
"""Deduplicate, downscale and convert the site images to WebP.

Run from the repository root:  python3 build-images.py

The source JPEGs in assets/src were extracted from the original single file
version of the site, which carried every image inline as base64. That file was
11.4 MB, of which 4.4 MB was the same seven photographs repeated on three
pages. Images here are written once, named by content, and referenced by every
page that uses them, so the browser downloads each one at most once.
"""
import hashlib, json, os, re, subprocess, sys

SRC = 'assets/src'
OUT = 'assets/img'
QUALITY = 80

# Long edge in pixels, by how large the image is actually displayed.
# A photograph served larger than its slot costs the visitor data and buys
# nothing. Most of this site is read on a phone over mobile data in Ghana.
# The cap is on the LONG edge, not the width. Several of these photographs are
# portrait and sit in a card about 340 px tall, so capping width alone left them
# four times larger than they are ever drawn.
CAPS = {'logo': 500, 'hero': 1600, 'card': 900, 'default': 1200}


def jpeg_dimensions(data):
    import struct
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = struct.unpack('>H', data[i + 2:i + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack('>HH', data[i + 5:i + 9])
            return width, height
        i += 2 + length
    raise ValueError('no SOF marker')


def resize_args(data, role):
    """cwebp takes a width and a height, 0 meaning "scale to match the other".
    Pass the cap on whichever edge is longer so the aspect ratio is kept."""
    cap = CAPS.get(role, CAPS['default'])
    width, height = jpeg_dimensions(data)
    if max(width, height) <= cap:
        return []
    return ['-resize', str(cap), '0'] if width >= height else ['-resize', '0', str(cap)]


def main():
    os.makedirs(OUT, exist_ok=True)
    usage = json.load(open('assets/usage.json'))
    seen, mapping = {}, {}
    for src in sorted(os.listdir(SRC)):
        if not re.search(r'\.(jpg|png)$', src):
            continue
        data = open(os.path.join(SRC, src), 'rb').read()
        digest = hashlib.sha256(data).hexdigest()[:10]
        role = usage.get(src, 'default')
        out_name = '%s.webp' % digest
        dest = os.path.join(OUT, out_name)
        if digest not in seen:
            cmd = (['cwebp', '-quiet', '-q', str(QUALITY), '-metadata', 'none']
                   + resize_args(data, role)
                   + [os.path.join(SRC, src), '-o', dest])
            subprocess.run(cmd, check=True)
            seen[digest] = out_name
        mapping[src] = out_name
    json.dump(mapping, open('assets/img-map.json', 'w'), indent=1, sort_keys=True)
    total = sum(os.path.getsize(os.path.join(OUT, n)) for n in set(seen.values()))
    print('%d source files -> %d unique WebP, %.2f MB total'
          % (len(mapping), len(seen), total / 1024 / 1024))


if __name__ == '__main__':
    main()
