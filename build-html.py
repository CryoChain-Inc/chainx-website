#!/usr/bin/env python3
"""Turn index.src.html into the index.html that gets published.

Run build-images.py first, then this.  It does three things to every <img>:
points it at the deduplicated WebP, states the real pixel size so the browser
can reserve the space before the file arrives, and marks everything below the
first screen as lazy. The hero and the two logos load eagerly because they are
the first screen.
"""
import json, os, re, struct, sys

# Where the site is served from. Open Graph needs absolute URLs, so a link
# shared on WhatsApp shows no preview card at all if this is wrong. Change it
# here, in this one place, if the site moves to its own domain, and rebuild.
SITE = 'https://chainx.cryochain.co/'

EAGER = {'img-01.jpg', 'img-02.jpg', 'img-53.jpg', 'img-03.jpg'}
HERO = 'img-03.jpg'


def webp_dimensions(path):
    head = open(path, 'rb').read(32)
    if head[:4] != b'RIFF' or head[8:12] != b'WEBP':
        raise ValueError('not a webp: %s' % path)
    kind = head[12:16]
    if kind == b'VP8 ':
        w, h = struct.unpack('<HH', head[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if kind == b'VP8L':
        bits = int.from_bytes(head[21:25], 'little')
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if kind == b'VP8X':
        return (int.from_bytes(head[24:27], 'little') + 1,
                int.from_bytes(head[27:30], 'little') + 1)
    raise ValueError('unknown webp chunk %r' % kind)


def main():
    mapping = json.load(open('assets/img-map.json'))
    dims = {}
    html = open('index.src.html', encoding='utf-8').read()
    used = set()

    def rewrite(match):
        tag, src = match.group(0), match.group(1)
        name = os.path.basename(src)
        if name not in mapping:
            print('no mapping for %s' % name)
            sys.exit(1)
        out = mapping[name]
        used.add(name)
        if out not in dims:
            dims[out] = webp_dimensions('assets/img/' + out)
        width, height = dims[out]
        tag = tag.replace(src, 'assets/img/' + out)
        extra = ' width="%d" height="%d" decoding="async"' % (width, height)
        if name in EAGER:
            extra += ' fetchpriority="high"' if name == HERO else ''
        else:
            extra += ' loading="lazy"'
        return tag[:-1].rstrip() + extra + '>'

    html = re.sub(r'<img\b[^>]*?\bsrc="(assets/img/img-\d+\.(?:jpg|png))"[^>]*>', rewrite, html)
    html = html.replace('{{SITE}}', SITE)

    missing = set(mapping) - used
    if missing:
        print('mapped but never referenced: %s' % sorted(missing))
        sys.exit(1)
    if 'data:image/jpeg' in html:
        print('a jpeg is still inline'); sys.exit(1)
    if '{{SITE}}' in html:
        print('a site URL was left unresolved'); sys.exit(1)

    open('index.html', 'w').write(html)
    print('index.html written, %.0f KB, %d <img> rewritten, %d unique files'
          % (len(html.encode()) / 1024, len(used), len(dims)))


if __name__ == '__main__':
    main()
