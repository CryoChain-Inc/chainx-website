# ChainX website

The public site for ChainX: BYD T5DM and T5EV electric box trucks, charger
installation and service, sold from Tema.

Published at <https://cryochain-inc.github.io/chainx-website/>.

## What to edit

| To change | Edit |
|---|---|
| Any page content, copy, prices, specifications | `index.src.html` |
| The WhatsApp number, analytics ID, company details | the `window.CX` block near the top of `index.src.html` |
| The address the site is served from | `SITE` in `build-html.py` |
| The photographs | `assets/src/`, then rebuild |

**Never edit `index.html` directly.** It is generated, and the next build
overwrites it.

## Building

```
python3 build-images.py     # assets/src/*.jpg  ->  assets/img/*.webp
python3 build-html.py       # index.src.html    ->  index.html
```

`build-images.py` deduplicates by content hash, caps each photograph at the
size it is actually drawn, and converts to WebP. `build-html.py` points every
`<img>` at the deduplicated file, writes in the real pixel dimensions so the
browser can reserve the space before the file arrives, and marks everything
below the first screen as lazy.

The original single file version of this site carried every photograph inline
as base64 and came to 11.4 MB, of which 4.4 MB was the same seven pictures
repeated on three pages. It is now 106 KB of HTML and 1.5 MB of images, almost
none of which is fetched before the visitor scrolls. That matters because this
is read on a phone, on mobile data, in Ghana.

## Configuration still outstanding

These live in the `window.CX` block. Each one is optional: leave it empty and
every sentence that would have needed it is left out, so no page ever shows a
blank or a placeholder.

| Key | What it is | Needed for |
|---|---|---|
| `gaId` | Google Analytics measurement ID | Knowing whether the market test worked |
| `company` | Registered company name | The terms and privacy pages |
| `address` | Registered address | The terms and privacy pages |
| `email` | Contact and privacy email | A second contact route besides WhatsApp |
| `dpc` | Data Protection Commission registration | Act 843 compliance on the privacy page |

## Checks

`.shots/` holds the render and functional checks used while building. They
need a local server and a copy of puppeteer-core:

```
python3 -m http.server 8777 --bind 127.0.0.1 &
node .shots/functional.js
```

---

CryoChain Inc. Confidential. Prices and specifications on this site are
planning figures from the factory quotation, not commitments.
