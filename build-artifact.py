#!/usr/bin/env python3
"""Emit a preview build for a host that supplies its own document skeleton.

Some hosts wrap the page they are given in their own <!doctype>, <head> and
<body>, so a complete document cannot be handed over as is. This takes the
built index.html and returns just its contents, in order, with the head
elements kept at the top where they still apply.

The published site in index.html is the real artefact. This is for review.
"""
import os, re, shutil, sys

src = open('index.html', encoding='utf-8').read()

head = re.search(r'<head>(.*?)</head>', src, re.S)
body = re.search(r'<body>(.*?)</body>', src, re.S)
if not head or not body:
    print('could not find head and body'); sys.exit(1)

keep = head.group(1)
# charset and viewport come from the host; a second copy of either is ignored
# at best and overrides the host's at worst.
for pattern in (r'\s*<meta charset="[^"]*">', r'\s*<meta name="viewport"[^>]*>'):
    keep = re.sub(pattern, '', keep)
# canonical and og:url name the production address, which this preview is not.
keep = re.sub(r'\s*<link rel="canonical"[^>]*>', '', keep)
keep = re.sub(r'\s*<meta property="og:[^"]*"[^>]*>', '', keep)
keep = re.sub(r'\s*<meta name="twitter:[^"]*"[^>]*>', '', keep)

os.makedirs('artifact', exist_ok=True)
out = keep.strip() + '\n' + body.group(1)
open('artifact/page.html', 'w').write(out)
print('artifact/page.html written, %.0f KB' % (len(out.encode()) / 1024))

for name in ('<!DOCTYPE', '<html', '<head>', '<body>'):
    if name.lower() in out.lower():
        print('skeleton tag %s survived' % name); sys.exit(1)
if '<title>' not in out:
    print('no title'); sys.exit(1)
print('no skeleton tags, title present')
