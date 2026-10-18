from guitarpro import *

s = parse('/Users/infinity/Documents/a_future/draft/rumbling/rumb_stand.gp5')

def dump(track, measures):
    for mi in measures:
        meas = track.measures[mi - 1]
        out = []
        for v in meas.voices:
            for b in v.beats:
                if b.notes:
                    ns = ','.join(f's{n.string}f{n.value}' for n in b.notes)
                    out.append(ns)
        print(f'  m{mi}: ' + ' ; '.join(out) if out else f'  m{mi}: (rest)')

for t in s.tracks:
    print(f'\n#### track {t.number} {t.name} ####')
    if t.number == 1:
        dump(t, [1, 2, 3, 4, 5, 49, 50, 51, 52, 77, 78, 79, 80, 85, 90, 125, 126, 127])
    if t.number == 2:
        dump(t, [13, 14, 15, 35, 36, 37, 45, 46, 59, 60, 61, 109, 110, 111])
    if t.number == 3:
        dump(t, [35, 36, 37, 38, 97, 98, 99, 100, 109, 110, 111])
    if t.number == 4:
        dump(t, [97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108])
