"""Extract structured tab data from The Rumbling gp5 -> JSON for plan generation."""
import json
from datetime import date, timedelta
from guitarpro import parse

SRC = '/Users/infinity/Documents/a_future/draft/rumbling/rumb_stand.gp5'
OUT = '/Users/infinity/Documents/a_future/tools/music/work/rumb_data.json'


def dur_units(b) -> float:
    d = b.duration
    base = {1: 16, 2: 8, 4: 4, 8: 2, 16: 1, 32: 0.5, 64: 0.25}.get(d.value, 1)
    if d.isDotted:
        base *= 1.5
    if d.tuplet and d.tuplet.times and d.tuplet.times > d.tuplet.enters:
        base = base * d.tuplet.enters / d.tuplet.times
    return base


def note_effect(n) -> dict:
    e = n.effect
    out = {}
    if getattr(e, 'palmMute', False):
        out['pm'] = True
    if getattr(e, 'hammer', False):
        out['hammer'] = True
    if getattr(e, 'vibrato', False):
        out['vibrato'] = True
    if getattr(e, 'letRing', False):
        out['letRing'] = True
    if getattr(e, 'staccato', False):
        out['staccato'] = True
    if getattr(e, 'isHarmonic', False):
        out['harmonic'] = True
    if getattr(e, 'isTremoloPicking', False):
        out['tremolo'] = True
    b = getattr(e, 'bend', None)
    if isinstance(b, int) and b > 0:
        out['bend'] = b
    sl = getattr(e, 'slides', None)
    if sl:
        vals = [s.value if hasattr(s, 'value') else str(s) for s in sl]
        if vals:
            out['slide'] = vals
    return out


def main():
    s = parse(SRC)
    data = {
        'meta': {
            'title': s.title,
            'subtitle': s.subtitle,
            'artist': s.artist,
            'bpm': s.tempo,
            'measures': len(s.measureHeaders),
            'tuning': [40, 45, 50, 55, 59, 64],  # E2 A2 D3 G3 B3 E4
        },
        'markers': [],
        'tracks': {},
    }
    for i, mh in enumerate(s.measureHeaders, 1):
        if mh.marker:
            data['markers'].append({'measure': i, 'title': mh.marker.title})

    for t in s.tracks:
        measures = {}
        for i, meas in enumerate(t.measures, 1):
            beats = []
            for v in meas.voices:
                for b in v.beats:
                    notes = []
                    for n in b.notes:
                        nn = {'string': n.string, 'fret': n.value}
                        fx = note_effect(n)
                        if fx:
                            nn['fx'] = fx
                        notes.append(nn)
                    beats.append({'notes': notes, 'units': dur_units(b)})
            note_count = sum(1 for b in beats for _ in b['notes'])
            measures[str(i)] = {'beats': beats, 'note_count': note_count}
        data['tracks'][str(t.number)] = {'name': t.name, 'measures': measures}

    # calendar: 16 weeks x 5 days (Mon-Fri), starting 2026-10-19
    start = date(2026, 10, 19)
    cal = []
    d = start
    for week in range(1, 17):
        days = []
        for _ in range(5):
            days.append(d.isoformat())
            d += timedelta(days=1)
        # skip to next Monday
        while d.weekday() != 0:
            d += timedelta(days=1)
        cal.append({'week': week, 'days': days})
    data['calendar'] = cal

    with open(OUT, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print('wrote', OUT)
    print('weeks:', len(cal), 'first:', cal[0]['days'], 'last:', cal[-1]['days'])


if __name__ == '__main__':
    main()
