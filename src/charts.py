"""Compact, class-styled SVG charts. Colours and fonts come from the page CSS, so
light/dark and every theme work with zero inline colour. Every number passed in comes from
the GT3-derived content model; charts only draw it."""
from html import escape as e

W = 560


def _svg(h, label, body, cls="ch", w=W):
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}">'
            f'{body}</svg>')


def hbars(title, rows, maxv=None, note="", label=None, w=W):
    """rows: [(label, value, shown, hot)] on one shared scale."""
    maxv = maxv or max(r[1] for r in rows)
    rh, top = 34, 26
    x0, x1 = (140, w - 96) if w >= W else (150, w - 66)
    h = top + rh * len(rows) + (22 if note else 6)
    out = [f'<text class="t" x="0" y="12">{e(title)}</text>']
    for i, (lab, v, shown, hot) in enumerate(rows):
        y = top + i * rh
        bw = max(3, (x1 - x0) * v / maxv)
        out.append(
            f'<text class="l{" hot" if hot else ""}" x="0" y="{y + 14}">{e(lab)}</text>'
            f'<rect class="tr" x="{x0}" y="{y}" width="{x1 - x0}" height="18" rx="4"/>'
            f'<rect class="bar{" hot" if hot else ""}" x="{x0}" y="{y}" width="{bw:.1f}" '
            f'height="18" rx="4" style="--i:{i}"/>'
            f'<text class="v" x="{x1 + 10}" y="{y + 14}">{e(shown)}</text>')
    if note:
        out.append(f'<text class="n" x="0" y="{h - 6}">{e(note)}</text>')
    return _svg(h, label or title, "".join(out), w=w)


def delta(title, before, after, b_text, a_text, note="", maxv=None, w=W):
    return hbars(title, [("before", before, b_text, False), ("after", after, a_text, True)],
                 maxv=maxv, note=note, label=f"{title}: {b_text} to {a_text}", w=w)


def matrix(rows, cols, hits, title):
    """Evidence heat-grid. rows: concept labels; cols: short entry labels;
    hits[r][c] = number of bullets in that entry mentioning the concept."""
    cw, rh, left, top = 44, 34, 196, 64
    totw = 60
    w = left + cw * len(cols) + totw
    h = top + rh * len(rows) + 8
    mx = max(max(r) for r in hits) or 1
    out = [f'<text class="t" x="0" y="12">{e(title)}</text>']
    for j, c in enumerate(cols):
        x = left + cw * j + cw / 2
        out.append(f'<text class="cl" transform="translate({x:.0f} {top - 10}) rotate(-38)">{e(c)}</text>')
    out.append(f'<text class="cl" x="{left + cw * len(cols) + 6}" y="{top - 10}">total</text>')
    for i, lab in enumerate(rows):
        y = top + i * rh
        out.append(f'<text class="l" x="0" y="{y + 20}">{e(lab)}</text>')
        tot = 0
        for j in range(len(cols)):
            n = hits[i][j]
            tot += n
            op = 0.14 + 0.86 * n / mx if n else 0
            out.append(
                f'<rect class="cell{" on" if n else ""}" x="{left + cw * j + 2}" y="{y + 2}" '
                f'width="{cw - 4}" height="{rh - 4}" rx="5"'
                + (f' style="--o:{op:.2f}"' if n else '') + '/>'
                + (f'<text class="cn" x="{left + cw * j + cw / 2}" y="{y + 21}">{n}</text>' if n else ''))
        out.append(f'<text class="v" x="{left + cw * len(cols) + 10}" y="{y + 21}">{tot}</text>')
    return (f'<svg class="ch mx" viewBox="0 0 {w} {h}" role="img" aria-label="{e(title)}">'
            + "".join(out) + "</svg>")


def timeline(items, y_from=2023.5, y_to=2026.95):
    """Gantt: row labels in a fixed left column, bars on a shared year axis.
    items: [(label, start, end, hot)] in display order, top row first."""
    lh, top, left = 30, 30, 214
    h = top + len(items) * lh + 8
    X = lambda t: left + (W - left) * (t - y_from) / (y_to - y_from)
    out = []
    yr = int(y_from) + 1
    while yr <= y_to:
        x = X(yr)
        out.append(f'<line class="g" x1="{x:.1f}" y1="22" x2="{x:.1f}" y2="{h - 4}"/>'
                   f'<text class="cl" x="{x + 5:.1f}" y="14">{yr}</text>')
        yr += 1
    for i, (lab, a, b, hot) in enumerate(items):
        y = top + i * lh
        out.append(f'<text class="l{" hot" if hot else ""}" x="0" y="{y + 14}">{e(lab)}</text>'
                   f'<rect class="tr" x="{left}" y="{y}" width="{W - left}" height="18" rx="5"/>'
                   f'<rect class="bar{" hot" if hot else " dim"}" x="{X(a):.1f}" y="{y}" '
                   f'width="{max(8, X(b) - X(a)):.1f}" height="18" rx="5" style="--i:{i}"/>')
    return _svg(h, "Career timeline, August 2023 to present", "".join(out), "ch tl")
