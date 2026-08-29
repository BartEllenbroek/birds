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

`data/sightings.json` starts empty. To see the app with something in it before you add your own,
copy `data/sightings.example.json` over it — six records across New Zealand, the Netherlands
and the Ross Sea, enough to light up the map and the stats.

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
checklist and the full image in the detail panel.

## Photo sizes

GitHub Pages serves whatever you commit, but a repository over about 1 GB gets unwieldy and
full-resolution files make the checklist slow to scroll. Resizing the long edge to ~1600 px
is plenty:

```bash
# macOS / Linux, with ImageMagick
mogrify -resize '1600x1600>' -quality 82 photos/*.jpg
```

## Credits

Taxonomy, English names, ranges and Red List categories: **AviList v2025**
([avilist.org](https://www.avilist.org/), [doi:10.2173/avilist.v2025](https://doi.org/10.2173/avilist.v2025)),
used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Map tiles © OpenStreetMap contributors. Map rendering by [Leaflet](https://leafletjs.com/).
