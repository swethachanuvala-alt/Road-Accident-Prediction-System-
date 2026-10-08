"""Road signs and a traffic light drawn as inline SVG."""
from __future__ import annotations

import math

YELLOW, RED, GREEN, BLUE, WHITE, BLACK = "#FFC400", "#E5322D", "#0B7A4B", "#1E66D0", "#FFFFFF", "#111111"
FONT = "Barlow Condensed, Arial Narrow, Arial, sans-serif"
NS = 'xmlns="http://www.w3.org/2000/svg"'


def warning_sign(symbol="!", size=90):
    return (f'<svg viewBox="0 0 100 100" width="{size}" {NS} role="img" aria-label="Warning sign">'
            f'<rect x="15" y="15" width="70" height="70" rx="9" transform="rotate(45 50 50)" fill="{YELLOW}" stroke="{BLACK}" stroke-width="5"/>'
            f'<rect x="23" y="23" width="54" height="54" rx="5" transform="rotate(45 50 50)" fill="none" stroke="{BLACK}" stroke-width="2"/>'
            f'<text x="50" y="65" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="44" fill="{BLACK}">{symbol}</text></svg>')


def speed_sign(value, size=90):
    text = str(value)
    fs = 44 if len(text) <= 2 else 32 if len(text) == 3 else 26
    return (f'<svg viewBox="0 0 100 100" width="{size}" {NS} role="img" aria-label="Speed limit {text}">'
            f'<circle cx="50" cy="50" r="46" fill="{WHITE}" stroke="{RED}" stroke-width="10"/>'
            f'<text x="50" y="{50 + fs * 0.34:.0f}" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="{fs}" fill="{BLACK}">{text}</text></svg>')


def stop_sign(size=90):
    def poly(r):
        return " ".join(f"{50 + r * math.cos(math.radians(22.5 + 45 * k)):.1f},{50 + r * math.sin(math.radians(22.5 + 45 * k)):.1f}"
                        for k in range(8))
    return (f'<svg viewBox="0 0 100 100" width="{size}" {NS} role="img" aria-label="Stop sign">'
            f'<polygon points="{poly(49)}" fill="{RED}"/><polygon points="{poly(43)}" fill="none" stroke="{WHITE}" stroke-width="2.5"/>'
            f'<text x="50" y="60" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="30" fill="{WHITE}">STOP</text></svg>')


def info_sign(text, size=90):
    fs = 34 if len(text) <= 2 else 24
    return (f'<svg viewBox="0 0 100 100" width="{size}" {NS} role="img" aria-label="Information sign">'
            f'<circle cx="50" cy="50" r="47" fill="{BLUE}" stroke="{WHITE}" stroke-width="4"/>'
            f'<text x="50" y="{50 + fs * 0.34:.0f}" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="{fs}" fill="{WHITE}">{text}</text></svg>')


def prohibition_sign(text, size=90):
    return (f'<svg viewBox="0 0 100 100" width="{size}" {NS} role="img" aria-label="Prohibition sign">'
            f'<circle cx="50" cy="50" r="46" fill="{WHITE}" stroke="{RED}" stroke-width="10"/>'
            f'<text x="50" y="60" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="30" fill="{BLACK}">{text}</text>'
            f'<line x1="22" y1="78" x2="78" y2="22" stroke="{RED}" stroke-width="8"/></svg>')


def guide_sign(text, sub="", width=300):
    h = 84
    sub_svg = (f'<text x="150" y="68" text-anchor="middle" font-family="{FONT}" font-size="17" fill="{WHITE}" fill-opacity=".85">{sub}</text>'
               if sub else "")
    ty = 46 if sub else 52
    return (f'<svg viewBox="0 0 300 {h}" width="{width}" {NS} role="img" aria-label="{text}">'
            f'<rect x="2" y="2" width="296" height="{h - 4}" rx="10" fill="{GREEN}" stroke="{WHITE}" stroke-width="3"/>'
            f'<rect x="9" y="9" width="282" height="{h - 18}" rx="6" fill="none" stroke="{WHITE}" stroke-width="1.5" stroke-opacity=".7"/>'
            f'<text x="150" y="{ty}" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="30" fill="{WHITE}">{text}</text>{sub_svg}</svg>')


def traffic_light(level, size=96):
    """level 0 = green, 1 = amber, 2 = red (the lit lamp)."""
    lamps = [(2, "#FF4D3D", "#3A1A1A", 38), (1, "#FFC400", "#3A3015", 100), (0, "#2ED47A", "#12301F", 162)]
    out = [f'<svg viewBox="0 0 80 200" width="{size}" {NS} role="img" aria-label="Traffic light">',
           '<rect x="4" y="4" width="72" height="192" rx="16" fill="#0C0D10" stroke="#4A5160" stroke-width="3"/>']
    for lvl, lit, dim, cy in lamps:
        if lvl == level:
            out.append(f'<circle cx="40" cy="{cy}" r="34" fill="{lit}" fill-opacity=".22"/>')
            out.append(f'<circle cx="40" cy="{cy}" r="25" fill="{lit}"/><circle cx="33" cy="{cy - 8}" r="6" fill="#fff" fill-opacity=".45"/>')
        else:
            out.append(f'<circle cx="40" cy="{cy}" r="25" fill="{dim}"/>')
    out.append("</svg>")
    return "".join(out)


def signpost(sign_svg, pole=46):
    return (f'<div class="post">{sign_svg}<div class="pole" style="height:{pole}px"></div></div>')
