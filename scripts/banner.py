#!/usr/bin/env python3
"""Build assets/banner.svg and the section headers (assets/h-0X.svg).

Edit the constants below, then run:  python3 scripts/banner.py
The avatar is embedded as base64 because GitHub blocks external images inside SVGs.
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# --- edit me ----------------------------------------------------------------
NAME = "OverCapi"
COMMAND = "$ xxd -g1 ./overcapi | head -3"
PAYLOAD = b"OverCapi@42 fr\n\x00low-lvl\x00"  # 8 bytes per hexdump line
AVATAR = ASSETS / "avatar.jpg"
AVATAR_LABEL = "avatar.bin · 0x6b50"
SECTIONS = ["whoami", "objdump -h stack", "readelf -S projects", "contributions", 'grep -r "one piece" /']

# code panels: [a]amber[/] [c]cyan[/] [d]dim[/] [r]keyword[/] [_] blinking cursor
WHOAMI_LEFT = """[d](gdb)[/] p *overcapi
[d]$1 =[/] {
  alias    = [a]"OverCapi"[/],
  school   = [a]"42"[/],
  location = [a]"France"[/],
  langs    = {[a]"fr"[/], [a]"en"[/]},
  building = [a]"kyara-extension"[/],
  learning = [a]"Rust"[/],
  status   = [c]PROMPTING_CLAUDE[/]
}"""
WHOAMI_RIGHT = """[d](gdb)[/] info registers
rip  [c]0x00000042[/]    <school+0>
rsp  [c]0x7ffd0c0ffee[/] <coffee>
rax  [c]0x0[/]           leaks
rbx  [c]0xdeadbeef[/]    segfaults
rcx  [c]0x1[/]           more emulator
eflags [ [a]ZF CURIOUS[/] ]

[d](gdb)[/] continue[_]"""
ONEPIECE = """[d]00000420[/]  4f 4e 45 50 49 45 43 45  [a]|ONEPIECE|[/]
[d]00000428[/]  69 73 20 72 65 61 6c 21  [a]|is real!|[/]

[r]while[/] (!found([c]ONE_PIECE[/]))
    sail([a]GRAND_LINE[/]);   [d]// next stop: Laugh Tale[/]

[d]/* crew:   nakama[] = { claude, gdb, valgrind };  */[/]
[d]/* bounty: 0x00000000 berries (for now)           */[/]
[d]/* hat:    straw, sizeof(dream) > SIZE_MAX        */[/]"""
# ----------------------------------------------------------------------------

AMBER, CYAN, DIM, FG, WHITE = "#f0b429", "#56d4dd", "#8b949e", "#c9d1d9", "#f0f3f6"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def hexdump(data):
    lines = []
    for off in range(0, len(data), 8):
        chunk = data[off:off + 8].ljust(8, b"\x00")
        hexs = " ".join(f"{b:02x}" for b in chunk)
        ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append((f"{off:08x}", hexs, ascii_))
    return lines


def typing_values(width, steps=45, slots=250):
    # discrete SMIL values: type in `steps` frames, then hold for the rest of the loop
    vals = [round(width * i / steps) for i in range(steps + 1)]
    return ";".join(map(str, vals + [width] * (slots - len(vals))))


def banner():
    img = base64.b64encode(AVATAR.read_bytes()).decode()
    mime = "image/png" if AVATAR.suffix == ".png" else "image/jpeg"
    rows, clips = [], []
    for i, (off, hexs, ascii_) in enumerate(hexdump(PAYLOAD)):
        y = 108 + i * 24
        clips.append(
            f'<clipPath id="t{i}"><rect x="252" y="{y - 17}" height="24" width="0">'
            f'<animate attributeName="width" values="{typing_values(560)}" calcMode="discrete" '
            f'dur="9s" begin="{i * 0.25}s" repeatCount="indefinite"/></rect></clipPath>'
        )
        rows.append(
            f'<text x="252" y="{y}" clip-path="url(#t{i})" font-size="14" fill="{FG}" xml:space="preserve">'
            f'<tspan fill="{DIM}">{off}</tspan>  {hexs}  <tspan fill="{AMBER}">|{esc(ascii_)}|</tspan></text>'
        )
    name_y = 108 + len(rows) * 24 + 52
    name = esc(NAME)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 300" width="880" height="300" role="img" aria-label="{name}">
<style>
text{{font-family:{FONT}}}
.blink{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.g1,.g2{{opacity:0;animation:glitch 5s steps(1) infinite}}
@keyframes glitch{{89%{{opacity:.9;transform:translate(-3px,0)}}91%{{opacity:.9;transform:translate(3px,0)}}93%{{opacity:0}}}}
.name{{animation:shake 5s steps(1) infinite}}
@keyframes shake{{89%{{transform:translate(-2px,0)}}91%{{transform:translate(2px,0)}}93%{{transform:none}}}}
</style>
<defs>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#ffffff" opacity=".03"/></pattern>
<clipPath id="av"><rect x="42" y="66" width="168" height="168"/></clipPath>
{"".join(clips)}
</defs>
<rect x=".5" y=".5" width="879" height="299" rx="10" fill="#0a0d12" stroke="#30363d"/>
<rect x="1" y="1" width="878" height="298" rx="10" fill="url(#scan)"/>
<rect x="36.5" y="60.5" width="179" height="179" fill="none" stroke="{AMBER}" stroke-opacity=".4"/>
<image href="data:{mime};base64,{img}" x="42" y="66" width="168" height="168" preserveAspectRatio="xMidYMid slice" clip-path="url(#av)"/>
<text x="36" y="262" font-size="10" fill="{DIM}">{esc(AVATAR_LABEL)}</text>
<text x="252" y="80" font-size="12" fill="{DIM}">{esc(COMMAND)}</text>
{"".join(rows)}
<text class="g1" x="252" y="{name_y}" font-size="54" font-weight="800" fill="{CYAN}">{name}</text>
<text class="g2" x="252" y="{name_y}" font-size="54" font-weight="800" fill="{AMBER}" style="animation-delay:.04s">{name}</text>
<text class="name" x="252" y="{name_y}" font-size="54" font-weight="800" fill="{WHITE}">{name}<tspan class="blink" fill="{AMBER}">_</tspan></text>
</svg>
'''


def header(i, label):
    tag = f"0x{i:02d}"
    line_x = 16 + (len(tag) + len(label) + 2) * 8.6
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 28" width="880" height="28" role="img" aria-label="{esc(label)}">
<style>text{{font-family:{FONT}}}</style>
<text x="0" y="19" font-size="14" fill="{DIM}" xml:space="preserve"><tspan fill="{AMBER}">{tag}</tspan> {esc(label)}</text>
<rect x="{line_x:.0f}" y="13" width="{880 - line_x:.0f}" height="1" fill="#30363d"/>
</svg>
'''


COLORS = {"a": AMBER, "c": CYAN, "d": DIM, "r": "#ff7b72"}


def code_line(src):
    """'[a]x[/] y' -> tspans; '[_]' -> blinking cursor."""
    out = []
    for tok in re.split(r"(\[[a-z_]\]|\[/\])", src):
        if tok == "[_]":
            out.append(f'<tspan class="blink" fill="{AMBER}">█</tspan>')
        elif tok == "[/]":
            out.append("</tspan>")
        elif re.fullmatch(r"\[[a-z]\]", tok):
            out.append(f'<tspan fill="{COLORS[tok[1]]}">')
        else:
            out.append(esc(tok))
    return "".join(out)


def panels(blocks, width=880, pad=22, lh=22, gap=16):
    """Side-by-side code panels without GitHub's table/code-block chrome."""
    h = max(len(b.splitlines()) for b in blocks) * lh + pad * 2 - 6
    w = (width - gap * (len(blocks) - 1)) / len(blocks)
    parts = []
    for i, block in enumerate(blocks):
        x = i * (w + gap)
        parts.append(f'<rect x="{x + .5:.1f}" y=".5" width="{w - 1:.1f}" height="{h - 1}" rx="8" fill="#161b22" stroke="#30363d"/>')
        for j, line in enumerate(block.splitlines()):
            parts.append(f'<text x="{x + pad:.1f}" y="{pad + 10 + j * lh}" font-size="13" fill="{FG}" xml:space="preserve">{code_line(line)}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" width="{width}" height="{h}">
<style>text{{font-family:{FONT}}}.blink{{animation:blink 1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}</style>
{"".join(parts)}
</svg>
'''


if __name__ == "__main__":
    assert hexdump(b"OverCapi")[0] == ("00000000", "4f 76 65 72 43 61 70 69", "OverCapi")
    assert code_line("[a]x[/] <y>") == f'<tspan fill="{AMBER}">x</tspan> &lt;y&gt;'
    (ASSETS / "banner.svg").write_text(banner())
    (ASSETS / "whoami.svg").write_text(panels([WHOAMI_LEFT, WHOAMI_RIGHT]))
    (ASSETS / "onepiece.svg").write_text(panels([ONEPIECE]))
    for i, label in enumerate(SECTIONS, 1):
        (ASSETS / f"h-{i:02d}.svg").write_text(header(i, label))
    print("wrote banner.svg +", len(SECTIONS), "headers")
