"""Generate per-day sheet files (gp5 + pdf) for plan_guitar_rumbling.

For each music day (track != 0), slice the master gp5 down to that track's
measure range and write:
  <day_dir>/sheet/sheet.gp5   (Guitar Pro 5, single track, sliced measures)
  <day_dir>/sheet/sheet.pdf   (rendered via MuseScore mscore CLI)

Usage (run from tools/music/work):
  uv run --with PyGuitarPro python gen_rumb_sheets.py          # gp5 only
  uv run --with PyGuitarPro python gen_rumb_sheets.py --pdf    # gp5 + pdf
"""
import os
import subprocess
import sys

from guitarpro import parse, write

from gen_rumb_plans import DAYS, META, OUT, PHASE_OF, TRACK_NAME

SRC = '/Users/infinity/Documents/a_future/draft/rumbling/rumb_stand.gp5'
MAKE_PDF = '--pdf' in sys.argv


def slice_song(track_no, a, b):
    s = parse(SRC)
    s.tracks = [s.tracks[track_no - 1]]
    s.measureHeaders = s.measureHeaders[a - 1:b]
    for t in s.tracks:
        t.measures = t.measures[a - 1:b]
        t.number = 1
    for i, mh in enumerate(s.measureHeaders):
        mh.number = i + 1
    return s


def main():
    total = 0
    for day in DAYS:
        if day['track'] == 0:
            continue
        track = day['track']
        a, b = day['a'], day['b']
        daydir = f'{OUT}/phase_{PHASE_OF[day["week"]]:02d}/week_{day["week"]:02d}/day{day["dayno"]:02d}_{day["date"]}'
        os.makedirs(daydir, exist_ok=True)

        s = slice_song(track, a, b)
        trname = TRACK_NAME[track].replace(' (Clean)', '')
        s.title = f'The Rumbling - {trname} m{a}-{b}'
        gp5_path = f'{daydir}/sheet.gp5'
        write(s, gp5_path)
        total += 1

        if MAKE_PDF:
            pdf_path = f'{daydir}/sheet.pdf'
            subprocess.run(['mscore', gp5_path, '-o', pdf_path],
                           check=False, capture_output=True)
    print(f'generated {total} sheet.gp5', '(and pdf)' if MAKE_PDF else '')


if __name__ == '__main__':
    main()
