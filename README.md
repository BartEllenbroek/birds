# Life List

A personal world bird checklist. All 11,131 species of [AviList v2025](https://www.avilist.org/)
in taxonomic sequence, with your own sightings — date, place, coordinates and a photo —
layered on top. Runs as a static site on GitHub Pages; no server, no build step, no dependencies
to install.

## Putting it online

1. Create a new repository on GitHub (public is simplest; private works on a paid plan).
2. Copy everything in this folder into it and push.
3. In the repo, go to **Settings → Pages**, set **Source** to *Deploy from a branch*,
   branch `main`, folder `/ (root)`, and save.
4. A minute later the site is at `https://<your-username>.github.io/<repo-name>/`.

Uploading through the browser takes three passes, because GitHub accepts at most 100 files at a
time and `photos/` holds 263. Send everything except `photos/` first (35 files), then the images
in two or three batches. GitHub Desktop does it in one commit if you would rather install it.

`data/sightings.json` is pre-loaded with 270 records covering 264 species, and `photos/` already
holds all 263 images, resized for the web. 109 records carry coordinates and appear on the map;
the rest have none, because the photographs hold no GPS or capture metadata — those have to be
filled in by hand, on the Add tab or by editing the file. Dates are blank throughout.

To try it locally first, run `python3 -m http.server` in this folder and open
`http://localhost:8000`. Opening `index.html` by double-clicking will *not* work —
browsers block a local page from reading its sibling data files.

## What goes where

```
index.html                  the app — a single self-contained file
data/species.json           AviList v2025, 11,131 species (do not edit)
data/sightings.json         your records — this is the file you grow
data/sightings.example.json six worked examples, for reference
photos/                     your images
tools/import_photos.py      bulk-import photos into sightings.json
```

## Adding sightings

**One at a time, in the browser.** Open the **Add** tab, drop the photo in — if it carries
GPS and a capture date those fields fill themselves — pick the species, add a place name,
and click *Add to list*. Records accumulate in the browser until you press
**Download sightings.json**; replace `data/sightings.json` with that file, copy the photos
into `photos/`, and commit. That commit is what makes them permanent.

**In bulk, from a folder of photos.** Name each file after the bird
(`north-island-robin-01.jpg`, `Petroica_longipes_2.jpg`, `2026-01-14 tui zealandia.jpg` all
work), drop them in `photos/`, then:

```bash
pip install Pillow
python3 tools/import_photos.py                          # preview the matches
python3 tools/import_photos.py --write                  # merge them in
python3 tools/import_photos.py --write --place "Zealandia, Wellington"
```

It reads date and coordinates from each photo's EXIF and prints anything it could not name,
so nothing is silently guessed.

## The record format

`data/sightings.json` is a flat array. Only `sci` is required, and repeating a species is fine —
each encounter is its own record.

```json
{
  "sci": "Petroica longipes",
  "date": "2026-01-14",
  "place": "Zealandia, Wellington",
  "lat": -41.2967,
  "lon": 174.7449,
  "photo": "photos/north-island-robin-01.jpg"
}
```

`sci` must match an AviList scientific name exactly — that is the key the app joins on.
Records with `lat`/`lon` appear on the map; records with a `photo` show a thumbnail in the
checklist and the full image in the detail panel. A species can hold several records — one per
encounter — and a record needs neither a photo nor a coordinate.

## Filtering the checklist

Search matches English and scientific names and eBird codes. The Order and Family dropdowns are
linked: choosing an order narrows Family to that order's families, and choosing a family fills in
the order it belongs to. "Range mentions" searches the AviList distribution text, so typing
*New Zealand* finds everything recorded from there.

## Photo sizes

The images in `photos/` are already web-sized: anything over 1600 px on the long edge was
resized, and anything already smaller was left untouched rather than re-compressed. The folder
is about 29 MB. For photos you add later:

```bash
# macOS / Linux, with ImageMagick
mogrify -resize '1600x1600>' -quality 86 photos/*.jpg
```

## Credits

Taxonomy, English names, ranges and Red List categories: **AviList v2025**
([avilist.org](https://www.avilist.org/), [doi:10.2173/avilist.v2025](https://doi.org/10.2173/avilist.v2025)),
used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Map tiles © OpenStreetMap contributors. Map rendering by [Leaflet](https://leafletjs.com/).
