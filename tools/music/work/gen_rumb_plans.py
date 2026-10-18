"""Generate plan_guitar_rumbling: 16-week x 5-day guitar plan for The Rumbling (4-track ensemble).

Reads tools/music/work/rumb_data.json (extracted from rumb_stand.gp5) and emits:
  plan/plan_guitar_rumbling/{README.md,TARGET.md,GENERATED_WITH.md,
    phase_01..03/{README.md, week_NN/{README.md,TASKS.md, dayNN_DATE/PLAN.md}}}
Each PLAN.md embeds real ASCII tab rendered from the gp5 for that day's measures.
"""
import json
import os
from datetime import date

ROOT = '/Users/infinity/Documents/a_future'
DATA = json.load(open(f'{ROOT}/tools/music/work/rumb_data.json'))
OUT = f'{ROOT}/plan/plan_guitar_rumbling'
META = DATA['meta']
TRACKS = DATA['tracks']
CAL = DATA['calendar']  # 16 weeks x 5 days (Mon-Fri), start 2026-10-19

# ---------------------------------------------------------------- technique lib
TECH = {
    'hold': dict(
        title='持琴与坐姿',
        check=['坐姿端正、琴身三点贴合、左手拇指位置正确，持琴 3 分钟不疲劳'],
        tips=['琴头略抬高，琴身贴胸腹与大腿','左手手腕自然放松，不折腕','拇指放琴颈后中线偏上，不横压'],
        steps=['调好坐姿/站姿，检查琴身三点贴合','左手拇指放到琴颈后中线，其余四指悬在指板上方 1cm','右手自然垂在音孔/拾音器上方，不紧绷'],
        traps=['弯腰驼背看指板导致手型变形','左手拇指横压琴颈导致按弦无力','琴身下滑、持琴不稳'],
        keep='坐姿+手型定型各 3 分钟；找弦与爬格顺延'),
    'pick': dict(
        title='右手拨弦',
        check=['6 根空弦从低音 E 到高音 E 依次拨响，每弦 3 遍无碰弦、音色均匀'],
        tips=['拨片尖端垂直琴弦，向下拨（down）用腕力不用整臂','靠弦点固定，不弹响邻弦','先空弦，再逐弦，慢速均匀'],
        steps=['空弦 6-1-6 逐弦 down-pick，每弦 4 遍','加入 up-pick 交替拨弦（down-up-down-up）','挂节拍器 60bpm 每拍一音，练 4/4 均匀'],
        traps=['整臂发力导致拨片角度乱','拨片入弦太深卡弦','只练 down 不练 up，节奏忽快忽慢'],
        keep='6 弦 down/up 交替各 3 遍 + 节拍器 60bpm 空弦'),
    'fret': dict(
        title='左手按弦与爬格',
        check=['爬格子 1-2-3-4 指在低把位 4 品，节拍器 60bpm 上下行各 3 遍无杂音'],
        tips=['指尖垂直按在品丝正上方偏后，不塌指','按弦发力来自手指，不靠手腕压','每按一个音都弹出干净单音'],
        steps=['低把位 1-2-3-4 指依次按 1-4 品（6 弦→1 弦）','爬格子上下行，60bpm 每拍一音','检查杂音：杂音多就放慢'],
        traps=['按在品丝正上方导致打品','手指离弦太远抬太高','求快导致手型塌'],
        keep='1-2-3-4 爬格上下行各 3 遍，60bpm'),
    'power': dict(
        title='强力和弦（Power Chord）',
        check=['低把位 E5/A5 强力和弦，根音+五度 2 音按稳，拨弦无杂音'],
        tips=['只用根音弦+下一弦（五度），指型=根音食指+五度无名指','其余弦用食指根部或右手闷住不发声','和弦之间快速移动时保持指型不变'],
        steps=['练 E5（6 弦空弦+5 弦 2 品）与 A5（5 弦空弦+4 弦 2 品）','移动 2-3 个把位的 E5/A5 循环','挂节拍器 60bpm 每和弦一换'],
        traps=['多按了不该响的弦','指型松垮导致每次都要重新找','闷音不到位，出来杂音'],
        keep='E5/A5 移动循环 60bpm 各 5 遍'),
    'solo': dict(
        title='主音旋律',
        check=['当日小节每个音按准、节奏对，慢速（60bpm）不断不错'],
        tips=['先右手指法（拨弦）再左手指法（按弦），逐音对齐','遇到连续快音先降速到能跟上的 60%','音色干净，不拖泥带水'],
        steps=['逐音认谱：弦+品 → 指法','慢速单音弹 3 遍，只求对不求快','挂节拍器 60bpm，连起来弹当日小节'],
        traps=['认错弦/品导致音高错','快音处抢拍','不降速硬冲，错误固化'],
        keep='当日小节 60bpm 连续弹 3 遍无错'),
    'rhythm': dict(
        title='强力和弦节奏（含闷音）',
        check=['当日小节和弦切换干净、闷音到位、节奏对齐节拍器'],
        tips=['右手小鱼际轻压琴桥处琴弦做闷音（palm mute）','闷音时拨片继续稳定上下拨','节奏优先：先只扫节奏型，再加左手和弦'],
        steps=['单独练右手闷音节奏型（空弦，不按和弦）','加入左手和弦，先慢速换和弦','挂节拍器 60bpm，对齐每拍'],
        traps=['闷音压太紧变死音、太松变杂音','换和弦时节奏断拍','只关注左手忘记右手节奏'],
        keep='右手闷音节奏型 + 2 个和弦切换各 60bpm 3 遍'),
    'clean': dict(
        title='Clean 分解和弦',
        check=['当日分解和弦每个音清晰、力度均匀、按弦干净'],
        tips=['分解和弦逐音弹，右手用指弹或轻拨','低音先弹根音，再依次高音','保持指型，按满拍不提前松开'],
        steps=['逐和弦认音（根音+和弦内音）','右手分解节奏型空弦练 3 遍','双手合，慢速弹当日小节'],
        traps=['分解时碰响邻弦','和弦内音漏弹/抢拍','按弦松太早声音断掉'],
        keep='当日分解和弦 60bpm 连续弹 3 遍无断音'),
    'assemble': dict(
        title='段落串联',
        check=['当日几段能不停顿串起来，节奏连续、无明显错误'],
        tips=['先逐段各自弹熟，再两段拼接','段与段接缝处单独练 3 遍','串联时保持节拍器，不因换段而变速'],
        steps=['逐段慢速各 2 遍确认','两段接缝处单独 5 遍','整段连续弹，记录卡点'],
        traps=['接缝处断拍/犹豫','前后速度不一致','只练各段不练拼接'],
        keep='最卡的接缝单独练 5 遍 + 整段连续 1 遍'),
    'speed': dict(
        title='提速',
        check=['目标速度下当日小节/段落能完整弹下、节奏稳定'],
        tips=['每次提速 5-8bpm，弹稳了再提','用节拍器锁死节奏，不凭感觉','快音处仍要保持音准与干净'],
        steps=['从上次稳定速度弹 1 遍热身','+5bpm 弹 2 遍，无错再 +5bpm','记下当日最高稳定速度'],
        traps=['一次提太快导致错误','速度快了杂音/抢拍','忘记记录稳定速度'],
        keep='稳定速度 + 一次 +5bpm 尝试'),
    'record': dict(
        title='录音自检',
        check=['完整录音 1 遍，回放听出错点并列出清单'],
        tips=['录音前先完整弹 1 遍热手','回放逐段对照谱面找错音/错节奏','把错误点写进完成记录'],
        steps=['完整弹并录音','回放对照 tab 逐段标记错误','列出明日要补的 2-3 处'],
        traps=['只录不听','录一次不满意就放弃','错误点不记录，下次重犯'],
        keep='完整录音 1 遍 + 错误清单'),
}

# ---------------------------------------------------------------- tab renderer
NAMES = {1: 'E', 2: 'B', 3: 'G', 4: 'D', 5: 'A', 6: 'E'}


def render_tab(track_no, m_start, m_end):
    track = TRACKS[str(track_no)]
    lines = []
    for m in range(m_start, m_end + 1):
        key = str(m)
        if key not in track['measures']:
            lines.append(f'm{m}: (rest)')
            continue
        beats = track['measures'][key]['beats']
        grid = {s: ['-' for _ in range(16)] for s in range(1, 7)}
        cum = 0.0
        for b in beats:
            col = min(int(round(cum)), 15)
            for n in b['notes']:
                grid[n['string']][col] = str(n['fret'])
            cum += b['units']
        lines.append(f'm{m}:')
        for s in range(1, 7):
            row = ' '.join(f'{c:>2}' for c in grid[s])
            lines.append(f'  {NAMES[s]}| {row}')
    return '\n'.join(lines)


# ---------------------------------------------------------------- practice detail
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
TUNING = META['tuning']  # [E2 A2 D3 G3 B3 E4]
FX_LABEL = {
    'pm': '闷音', 'hammer': '击弦', 'vibrato': '揉弦', 'letRing': '延音',
    'staccato': '断奏', 'harmonic': '泛音', 'tremolo': '震音拨',
    'bend': '推弦', 'slide': '滑音',
}


def midi(s, f):
    return TUNING[6 - s] + f


def note_name(s, f):
    m = midi(s, f)
    return f'{NOTES[m % 12]}{m // 12 - 1}'


def note_label(n):
    return f'{n["string"]}弦{n["fret"]}品{note_name(n["string"], n["fret"])}'


def power_chord(notes):
    """双音间隔纯五度(7 半音) -> 返回 '根音名5'，否则 None。"""
    if len(notes) == 2:
        lo = min(notes, key=lambda n: midi(n['string'], n['fret']))
        hi = max(notes, key=lambda n: midi(n['string'], n['fret']))
        if midi(hi['string'], hi['fret']) - midi(lo['string'], lo['fret']) == 7:
            m = midi(lo['string'], lo['fret'])
            return f'{NOTES[m % 12]}5'
    return None


def beat_label(ns):
    """单拍音符的描述；ns 已按低音弦在前排序。"""
    ns = sorted(ns, key=lambda n: -n['string'])
    fx = []
    for n in ns:
        for k in n.get('fx', {}):
            lbl = FX_LABEL.get(k, k)
            if lbl not in fx:
                fx.append(lbl)
    pc = power_chord(ns)
    if pc:
        body = f'{pc} 强力和弦（' + ' + '.join(note_label(n) for n in ns) + '）'
    elif len(ns) == 1:
        body = note_label(ns[0])
    else:
        body = ' + '.join(note_label(n) for n in ns)
    if fx:
        body += f'〔{"、".join(fx)}〕'
    return body


def describe_measure(track, m):
    key = str(m)
    if key not in track['measures']:
        return None
    beats = track['measures'][key]['beats']
    seq = []
    for b in beats:
        ns = b['notes']
        if not ns:
            continue
        lbl = beat_label(ns)
        if seq and seq[-1][0] == lbl:
            seq[-1][1] += 1
        else:
            seq.append([lbl, 1])
    return '，'.join(lbl if c == 1 else f'{lbl} ×{c}' for lbl, c in seq)


def practice_detail(track_no, a, b):
    """生成「本日精练清单」：逐小节音符 + 把位 + 技巧重点。"""
    track = TRACKS[str(track_no)]
    lines = []
    span = b - a + 1
    show = list(range(a, b + 1))
    if span > 6:
        show = [a, a + 1, a + 2, b]
    for m in show:
        desc = describe_measure(track, m)
        if desc:
            lines.append(f'- m{m}：{desc}')
        else:
            lines.append(f'- m{m}：(休止)')
    if span > 6:
        lines.append(f'- （其余 m{a + 3}-{b - 1} 见第 9 节 tab，逐小节同法认音）')

    frets = []
    fx_set = set()
    for m in range(a, b + 1):
        key = str(m)
        if key not in track['measures']:
            continue
        for b_ in track['measures'][key]['beats']:
            for n in b_['notes']:
                frets.append(n['fret'])
                for k in n.get('fx', {}):
                    fx_set.add(k)
    pos = ''
    if frets:
        lo, hi = min(frets), max(frets)
        if lo == hi:
            pos = f'第 {lo} 品（本日仅此一品附近）'
        else:
            base = lo if lo > 0 else 0
            pos = f'第 {lo}–{hi} 品；食指建议放第 {base} 品，1-2-3-4 指各管一品'

    focus = []
    if 'pm' in fx_set:
        focus.append('闷音：右手小鱼际轻压琴桥处琴弦，音色发闷但不死')
    if 'bend' in fx_set:
        focus.append('推弦：推到目标音高，别推半吊子')
    if 'hammer' in fx_set:
        focus.append('击弦：右手不拨，左手手指敲击发声，力度到位')
    if 'slide' in fx_set:
        focus.append('滑音：按住滑到目标品，过程不断音')
    if 'harmonic' in fx_set:
        focus.append('泛音：手指轻触泛音点，拨响后立即离弦')
    if 'tremolo' in fx_set:
        focus.append('震音拨：快速交替拨弦，节奏均匀')
    if 'vibrato' in fx_set:
        focus.append('揉弦：手腕小幅均匀抖动')
    if 'letRing' in fx_set:
        focus.append('延音：按满时值，不提前松弦')
    if not focus:
        focus.append('音按准、节奏对齐节拍器；和弦换把干净')

    return '\n'.join(lines), pos, focus


# ---------------------------------------------------------------- day mapping
# (track, m_start, m_end, title, tag)  -> one day
def seg(track, a, b, title, tag):
    return dict(track=track, a=a, b=b, title=title, tag=tag)


DAYMAP = {
    1: [  # W1 基础入门
        seg(0, 0, 0, '持琴姿势 + 认识吉他各部分', 'hold'),
        seg(0, 0, 0, '右手拨弦（空弦）', 'pick'),
        seg(0, 0, 0, '左手按弦 + 1-2-3-4 爬格', 'fret'),
        seg(0, 0, 0, '强力和弦入门 E5/A5', 'power'),
        seg(1, 1, 2, '读六线谱 + Solo A 开头认音（m1-2）', 'solo'),
    ],
    2: [  # W2
        seg(1, 1, 2, 'Solo A m1-2 慢速', 'solo'),
        seg(1, 3, 4, 'Solo A m3-4 慢速', 'solo'),
        seg(1, 5, 6, 'Solo A m5-6 慢速', 'solo'),
        seg(1, 1, 6, 'Solo A m1-6 串联', 'assemble'),
        seg(2, 13, 13, 'Verse A 强力和弦认音（m13）', 'rhythm'),
    ],
    3: [  # W3
        seg(1, 7, 8, 'Solo A m7-8 慢速', 'solo'),
        seg(1, 9, 10, 'Solo A m9-10 慢速', 'solo'),
        seg(1, 11, 12, 'Solo A m11-12 慢速', 'solo'),
        seg(1, 7, 12, 'Solo A m7-12 串联', 'assemble'),
        seg(1, 1, 12, 'Solo A 全段（m1-12）完整', 'assemble'),
    ],
    4: [  # W4
        seg(2, 13, 16, 'Verse A Rhythm1 m13-16', 'rhythm'),
        seg(2, 17, 20, 'Verse A Rhythm1 m17-20', 'rhythm'),
        seg(2, 21, 24, 'Verse A Rhythm1 m21-24', 'rhythm'),
        seg(2, 13, 24, 'Verse A Rhythm1 m13-24 串联', 'assemble'),
        seg(1, 1, 12, 'Solo A 复练 + 录音自检', 'record'),
    ],
    5: [  # W5 -> M1 验收
        seg(2, 25, 28, 'Verse A Rhythm1 m25-28', 'rhythm'),
        seg(2, 29, 32, 'Verse A Rhythm1 m29-32', 'rhythm'),
        seg(2, 33, 34, 'Verse A Rhythm1 m33-34 收尾', 'rhythm'),
        seg(2, 13, 34, 'Verse A Rhythm1 全段（m13-34）', 'assemble'),
        seg(1, 1, 12, 'M1 验收：Solo A 完整不断不错', 'record'),
    ],
    6: [  # W6
        seg(1, 50, 52, 'Solo B m50-52 慢速', 'solo'),
        seg(1, 53, 55, 'Solo B m53-55 慢速', 'solo'),
        seg(1, 56, 58, 'Solo B m56-58 慢速', 'solo'),
        seg(1, 50, 58, 'Solo B 全段（m50-58）串联', 'assemble'),
        seg(2, 35, 38, 'Chorus Rhythm1 m35-38', 'rhythm'),
    ],
    7: [  # W7
        seg(2, 39, 42, 'Chorus Rhythm1 m39-42', 'rhythm'),
        seg(2, 43, 46, 'Chorus Rhythm1 m43-46', 'rhythm'),
        seg(2, 47, 50, 'Chorus Rhythm1 m47-50', 'rhythm'),
        seg(2, 35, 50, 'Chorus Rhythm1 全段（m35-50）', 'assemble'),
        seg(1, 50, 58, 'Solo B 复练 + 录音自检', 'record'),
    ],
    8: [  # W8 -> M2 验收（Solo 轨全曲旋律）
        seg(1, 76, 80, 'Solo C m76-80 慢速（含弱起）', 'solo'),
        seg(1, 81, 84, 'Solo C m81-84 慢速', 'solo'),
        seg(1, 85, 89, 'Solo C m85-89 慢速', 'solo'),
        seg(1, 90, 93, 'Solo C m90-93 慢速', 'solo'),
        seg(1, 76, 93, 'M2 验收：Solo C 全段 + Solo 轨旋律完整', 'record'),
    ],
    9: [  # W9
        seg(2, 59, 62, 'Verse B Rhythm1 m59-62', 'rhythm'),
        seg(2, 63, 66, 'Verse B Rhythm1 m63-66', 'rhythm'),
        seg(2, 67, 70, 'Verse B Rhythm1 m67-70', 'rhythm'),
        seg(2, 71, 74, 'Verse B Rhythm1 m71-74 收尾', 'rhythm'),
        seg(2, 59, 74, 'Verse B Rhythm1 全段（m59-74）', 'assemble'),
    ],
    10: [  # W10
        seg(3, 105, 108, 'Chorus Rhythm2 m105-108', 'rhythm'),
        seg(3, 109, 112, 'Chorus Rhythm2 m109-112', 'rhythm'),
        seg(3, 113, 116, 'Chorus Rhythm2 m113-116', 'rhythm'),
        seg(3, 117, 120, 'Chorus Rhythm2 m117-120', 'rhythm'),
        seg(3, 121, 124, 'Chorus Rhythm2 m121-124 收尾', 'rhythm'),
    ],
    11: [  # W11 -> M3 验收（Rhythm1+Rhythm2 全曲）
        seg(3, 105, 124, 'Chorus Rhythm2 全段（m105-124）', 'assemble'),
        seg(2, 13, 50, 'Rhythm1 Verse A + Chorus 复练', 'assemble'),
        seg(2, 59, 74, 'Rhythm1 Verse B 复练', 'assemble'),
        seg(3, 105, 124, 'Rhythm2 复练 + 闷音打磨', 'rhythm'),
        seg(2, 13, 50, 'M3 验收：Rhythm1 全曲节奏不断不错', 'record'),
    ],
    12: [  # W12 -> M4（Guitar3 clean）
        seg(4, 97, 99, 'Guitar3 clean m97-99', 'clean'),
        seg(4, 100, 102, 'Guitar3 clean m100-102', 'clean'),
        seg(4, 103, 105, 'Guitar3 clean m103-105', 'clean'),
        seg(4, 106, 108, 'Guitar3 clean m106-108', 'clean'),
        seg(4, 97, 108, 'M4 验收：Guitar3 全段（m97-108）', 'record'),
    ],
    13: [  # W13
        seg(1, 124, 126, 'Solo D m125-126 慢速', 'solo'),
        seg(1, 127, 129, 'Solo D m127-129 慢速', 'solo'),
        seg(1, 130, 132, 'Solo D m130-132 收尾', 'solo'),
        seg(1, 124, 132, 'Solo D 全段（m125-132）串联', 'assemble'),
        seg(1, 1, 132, 'Solo 轨全曲结构串联（分段过一遍）', 'assemble'),
    ],
    14: [  # W14 提速
        seg(1, 1, 12, 'Solo A 提速', 'speed'),
        seg(1, 50, 58, 'Solo B 提速', 'speed'),
        seg(1, 76, 93, 'Solo C 提速', 'speed'),
        seg(2, 13, 50, 'Rhythm1 提速到目标', 'speed'),
        seg(3, 105, 124, 'Rhythm2 提速到目标', 'speed'),
    ],
    15: [  # W15 合奏 + 表现力
        seg(2, 13, 74, 'Rhythm1 全曲跟伴奏/节拍器 145bpm', 'assemble'),
        seg(1, 1, 93, 'Solo 轨全曲跟伴奏/节拍器', 'assemble'),
        seg(4, 97, 108, 'Guitar3 全段跟伴奏', 'assemble'),
        seg(3, 105, 124, 'Rhythm2 全段跟伴奏', 'assemble'),
        seg(1, 1, 132, '全曲四轨结构完整过一遍（自选主轨）', 'assemble'),
    ],
    16: [  # W16 录制 -> M5
        seg(1, 1, 132, '选定主轨完整录音（Solo）', 'record'),
        seg(2, 13, 74, 'Rhythm1 完整录音', 'record'),
        seg(3, 105, 124, 'Rhythm2 完整录音', 'record'),
        seg(4, 97, 108, 'Guitar3 完整录音', 'record'),
        seg(1, 1, 132, 'M5 验收：四轨均可完整弹 + 成品录制', 'record'),
    ],
}

# milestone label per week
MILESTONE = {
    1: ('M1', '第 5 周末：Solo A 主音（m1-12）慢速完整不断不错'),
    2: ('M1', '第 5 周末：Solo A 主音（m1-12）慢速完整不断不错'),
    3: ('M1', '第 5 周末：Solo A 主音（m1-12）慢速完整不断不错'),
    4: ('M1', '第 5 周末：Solo A 主音（m1-12）慢速完整不断不错'),
    5: ('M1', '第 5 周末：Solo A 主音（m1-12）慢速完整不断不错'),
    6: ('M2', '第 8 周末：Solo 轨全曲旋律（m1-93 / m124-132）完整弹下'),
    7: ('M2', '第 8 周末：Solo 轨全曲旋律完整弹下'),
    8: ('M2', '第 8 周末：Solo 轨全曲旋律完整弹下'),
    9: ('M3', '第 11 周末：Rhythm1+Rhythm2 全曲强力和弦节奏完整弹下'),
    10: ('M3', '第 11 周末：Rhythm1+Rhythm2 全曲节奏完整弹下'),
    11: ('M3', '第 11 周末：Rhythm1+Rhythm2 全曲节奏完整弹下'),
    12: ('M4', '第 12 周末：Guitar3 Clean 分解全段（m97-108）完整弹下'),
    13: ('M5', '第 16 周末：四轨均可完整弹 + 成品录制'),
    14: ('M5', '第 16 周末：四轨均可完整弹 + 成品录制'),
    15: ('M5', '第 16 周末：四轨均可完整弹 + 成品录制'),
    16: ('M5', '第 16 周末：四轨均可完整弹 + 成品录制'),
}

TRACK_NAME = {1: 'Solo', 2: 'Rhythm Guitar 1', 3: 'Rhythm Guitar 2', 4: 'Guitar 3 (Clean)'}
NOTOUCH = {
    'hold': '右手拨弦、按弦、曲目内容（明天开始）',
    'pick': '左手按弦、强力和弦、曲目内容',
    'fret': '强力和弦、曲目内容',
    'power': '曲目内容、Solo 旋律',
    'solo': '强力和弦节奏、闷音、提速（Phase 3）',
    'rhythm': 'Solo 旋律、Clean 分解、提速',
    'clean': 'Solo 旋律、强力和弦节奏、提速',
    'assemble': '提速、表现力（Phase 3）',
    'speed': '新增段落（只提速已学内容）',
    'record': '新增段落（只录音复习已学内容）',
}
TRACK_LINK = {
    1: '主音旋律线（全曲 Solo 声部），是最终合奏里最显耳、决定成品完成度的声部',
    2: '节奏吉他的主要和声骨架（Verse+Chorus），是合奏的节奏/和声底子',
    3: '节奏吉他的加厚层（Chorus 部分），让合奏在高潮段更饱满有力',
    4: 'Clean 分解和弦过门段（m97-108），是情绪转折的过渡声部',
}


def fmt_date(s):
    y, m, d = s.split('-')
    return f'{y}-{m}-{d}'


def plan_path(dayno, datestr):
    return f'{OUT}/phase_%02d/week_%02d/day%02d_{datestr}' % (
        PHASE_OF[week_of(dayno)], week_of(dayno), dayno, datestr)


def week_of(dayno):
    return (dayno - 1) // 5 + 1


PHASE_OF = {w: (1 if w <= 5 else (2 if w <= 11 else 3)) for w in range(1, 17)}
PHASE_TITLE = {
    1: 'Phase 1 · 基础入门 + Solo A 主音（W1-5）',
    2: 'Phase 2 · 分轨攻克全曲（W6-11）',
    3: 'Phase 3 · 合奏 + 提速 + 打磨成型（W12-16）',
}

# flatten into ordered days
DAYS = []
for w in range(1, 17):
    for i, d in enumerate(DAYMAP[w]):
        dayno = (w - 1) * 5 + i + 1
        datestr = CAL[w - 1]['days'][i]
        DAYS.append(dict(dayno=dayno, week=w, date=datestr, **d))


def render_plan(day, prev_day, next_day):
    tech = TECH[day['tag']]
    mk_id, mk_text = MILESTONE[day['week']]
    mk = f'{mk_id} — {mk_text}'
    track = day['track']
    detail_block = ''
    sheet_note = ''
    if track == 0:
        tab = '(基本功日，无谱面小节)'
        measure_label = '基本功'
        trname = '基本功'
        link = '为后续弹奏做准备的地基：姿势/拨弦/按弦/强力和弦是弹任何声部的前提'
    else:
        tab = render_tab(track, day['a'], day['b'])
        measure_label = f'第 {day["a"]}-{day["b"]} 小节' if day['a'] != day['b'] else f'第 {day["a"]} 小节'
        trname = TRACK_NAME[track]
        link = TRACK_LINK[track]
        sheet_note = (f'\n> 本日分谱文件（与 PLAN.md 同级）：`sheet.gp5`（Guitar Pro 5，可用 Guitar Pro / TuxGuitar / MuseScore 打开）· '
                      f'`sheet.pdf`（五线谱+六线谱成品）\n')
        detail, pos, focus = practice_detail(track, day['a'], day['b'])
        focus_lines = '\n'.join(f'- {f}' for f in focus)
        detail_block = f'''### 本日精练清单（具体到音）

{detail}

- 把位建议：{pos}
- 本段技巧重点：
{focus_lines}

'''

    prev_line = f'- 已有：前一天的完成项（{prev_day["title"]}）' if prev_day else '- 已有：计划开始日，无前置'
    next_line = f'- 明日重点：{next_day["title"]}' if next_day else '- 明日重点：复盘收尾'

    checks = '\n'.join(f'- [ ] {c}' for c in tech['check'])
    tips = '\n'.join(f'- {c}' for c in tech['tips'])
    steps = '\n'.join(f'- {c}' for c in tech['steps'])
    traps = '\n'.join(f'- {c}' for c in tech['traps'])

    # extra measure-specific step for non-fundamental days
    measure_step = ''
    if track != 0:
        measure_step = (f'\n### Step 4 · 对照谱面精练（15 min）\n'
                        f'打开本日 tab，逐音认「弦+品」，对照下方谱面把 {measure_label} 弹熟，'
                        f'挂节拍器 60bpm 连起来。')
    if day['tag'] in ('assemble', 'speed', 'record'):
        measure_step = ''

    return f'''# Day {day['dayno']:02d} · {day['date']} · Week {day['week']:02d} · {day['title']}

## 0. 今天只做一件事

聚焦「{day['title']}」：练 {measure_label}，达成下面的验收勾选项。

不碰：{NOTOUCH[day['tag']]}。

## 1. 资产锚点（今天与最终目标的关系）

- 里程碑：{mk}
- 今天练完，「最终目标（四轨合奏完整演奏 The Rumbling）」多了什么：{trname} 的 {measure_label} 这一块被拿下，离该阶段里程碑更近一步。
- 练的东西 → 最终目标的关系：{link}。今天练的是这 {measure_label}，是全曲合奏里必须现在就啃下的一块，不解决它后面合奏会在这里卡壳。

## 2. 起点（前置确认）

{prev_line}
{next_line}
- 需确认：昨天的难点是否解决；今日 {measure_label} 的音名/指法是否已在谱上标好。

## 3. 验收对齐（今天做完要能勾掉）

{checks}

## 4. 时间块（≤ 60 分钟）

| 时间 | 优先级 | 内容 |
| --- | --- | --- |
| 0–5 min | P0 | 热身：手腕/手指放松 + 空弦慢拨 |
| 5–40 min | P0 | 主练：{day['title']}（{measure_label}） |
| 40–50 min | P0 | 复习：前一天/上一段已学内容，保持手感 |
| 50–60 min | P1 | 总结：写完成记录 + 标注明日重点 |

时间不足时最低保留：{tech['keep']}。

## 5. 今日练习要点（只练完成今天目标必须的）

{tips}

{detail_block}## 6. 执行步骤

### Step 1 · 热身（5 min）
{tech['steps'][0]}

### Step 2 · 主练（35 min）
{tech['steps'][1]}；{tech['steps'][2]}

### Step 3 · 复习 + 总结（20 min）
复习前一天/上一段已学内容各 1 遍，写完成记录。
{measure_step}

## 7. 易错点 / 常见坑

{traps}

## 8. 时间不够时（最小保留）

{tech['keep']}。

## 9. 今日谱面（{measure_label}）
{sheet_note}
```
{tab}
```

## 10. 完成记录

- 实际用时：___ min
- 完成度：___%
- 最高稳定速度：___ bpm（提速期填写）
- 难点记录：
- 明日重点：
'''


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)


def main():
    os.makedirs(OUT, exist_ok=True)
    for i, day in enumerate(DAYS):
        prev = DAYS[i - 1] if i > 0 else None
        nxt = DAYS[i + 1] if i < len(DAYS) - 1 else None
        p = f'{OUT}/phase_{PHASE_OF[day["week"]]:02d}/week_{day["week"]:02d}/day{day["dayno"]:02d}_{day["date"]}/PLAN.md'
        write(p, render_plan(day, prev, nxt))
    print(f'generated {len(DAYS)} PLAN.md files -> {OUT}')


if __name__ == '__main__':
    main()

