"""Demo cover illustrations for the seeded dataset.

`seed.py` stores filenames such as ``demo-book.svg`` in the ``images`` table, and
``uploads/`` is git-ignored — so the illustrations cannot ship with the repository
and must be *generated* on the machine that runs the seed. This module owns that
artwork so ``python seed.py`` really does rebuild a complete dataset.

Every cover is a hand-written flat SVG in the application's own palette
(``static/css/style.css``) at 800x600 (4:3), which is the aspect ratio of the
listing card thumbnail. ``object-fit: cover`` on the card and
``object-fit: contain`` in the detail gallery both crop these cleanly.

Public API
----------
    write_covers(dest_dir, force=False) -> list[str]
        Write the missing covers into ``dest_dir`` and return their filenames.
    COVERS
        Mapping of filename -> SVG document, for tests and tooling.
"""

import os

# --- palette (mirrors :root in static/css/style.css) -----------------------
BRAND_50 = '#eef2ff'
BRAND_100 = '#e0e7ff'
BRAND_200 = '#c7d2fe'
BRAND_400 = '#818cf8'
BRAND_500 = '#6366f1'
BRAND_600 = '#4f46e5'
BRAND_700 = '#4338ca'
BRAND_800 = '#3730a3'
INK_900 = '#0f172a'
INK_800 = '#1f2937'
INK_700 = '#374151'
INK_600 = '#4b5563'
INK_500 = '#6b7280'
INK_400 = '#9ca3af'
INK_300 = '#cbd5e1'
INK_200 = '#e2e8f0'
LINE = '#e8eaee'
LINE_STRONG = '#d7dae0'
WHITE = '#ffffff'
PRICE = '#e5484d'
SUCCESS = '#15803d'
SUCCESS_DARK = '#0f766e'
SUCCESS_MID = '#0d9488'
SUCCESS_LIGHT = '#14b8a6'
SUCCESS_PALE = '#ccfbf1'
WARNING = '#b45309'
AMBER = '#f59e0b'
AMBER_LIGHT = '#fbbf24'
AMBER_PALE = '#fef3c7'
SLATE = '#64748b'

W, H = 800, 600


def _doc(label, top, bottom, blob, body):
    """Wrap one illustration in the shared 4:3 canvas."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" '
        'width="800" height="600" role="img" aria-label="%s">\n'
        '  <defs>\n'
        '    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">\n'
        '      <stop offset="0" stop-color="%s"/>\n'
        '      <stop offset="1" stop-color="%s"/>\n'
        '    </linearGradient>\n'
        '  </defs>\n'
        '  <rect width="800" height="600" fill="url(#bg)"/>\n'
        '  <circle cx="648" cy="118" r="146" fill="%s" opacity=".55"/>\n'
        '  <circle cx="146" cy="496" r="108" fill="%s" opacity=".45"/>\n'
        '%s\n'
        '</svg>\n' % (label, top, bottom, blob, blob, body)
    )


# --------------------------------------------------------------- 1. textbook
_BOOK = _doc(
    'Textbook cover illustration',
    BRAND_50, WHITE, BRAND_100,
    '''  <g transform="rotate(-6 400 300)">
    <rect x="516" y="150" width="34" height="300" rx="6" fill="''' + WHITE + '''" stroke="''' + LINE_STRONG + '''" stroke-width="2"/>
    <g stroke="''' + LINE + '''" stroke-width="3">
      <path d="M528 160v280"/>
      <path d="M538 160v280"/>
    </g>
    <rect x="212" y="140" width="318" height="320" rx="14" fill="''' + BRAND_700 + '''"/>
    <rect x="196" y="134" width="318" height="320" rx="14" fill="''' + BRAND_600 + '''"/>
    <path d="M196 148a14 14 0 0 1 14-14h20v320h-20a14 14 0 0 1-14-14z" fill="''' + BRAND_800 + '''"/>
    <rect x="266" y="204" width="188" height="16" rx="8" fill="''' + BRAND_200 + '''"/>
    <rect x="266" y="236" width="132" height="16" rx="8" fill="#a5b4fc"/>
    <rect x="266" y="326" width="76" height="76" rx="12" fill="''' + BRAND_500 + '''"/>
    <rect x="360" y="336" width="118" height="12" rx="6" fill="#a5b4fc"/>
    <rect x="360" y="360" width="90" height="12" rx="6" fill="''' + BRAND_400 + '''"/>
    <rect x="360" y="384" width="104" height="12" rx="6" fill="''' + BRAND_400 + '''"/>
    <path d="M436 116h30v130l-15-20-15 20z" fill="''' + AMBER + '''"/>
  </g>''')

# ---------------------------------------------------------------- 2. laptop
_LAPTOP = _doc(
    'Laptop cover illustration',
    BRAND_50, WHITE, BRAND_100,
    '''  <rect x="188" y="126" width="424" height="282" rx="16" fill="''' + INK_800 + '''"/>
  <rect x="206" y="144" width="388" height="242" rx="8" fill="''' + BRAND_600 + '''"/>
  <rect x="228" y="166" width="344" height="54" rx="10" fill="''' + BRAND_500 + '''"/>
  <rect x="246" y="186" width="120" height="14" rx="7" fill="''' + BRAND_100 + '''"/>
  <rect x="386" y="186" width="60" height="14" rx="7" fill="''' + BRAND_400 + '''"/>
  <rect x="228" y="238" width="104" height="124" rx="10" fill="''' + BRAND_400 + '''"/>
  <rect x="348" y="238" width="104" height="124" rx="10" fill="#a5b4fc"/>
  <rect x="468" y="238" width="104" height="124" rx="10" fill="''' + BRAND_400 + '''"/>
  <rect x="348" y="290" width="104" height="12" rx="6" fill="''' + WHITE + '''" opacity=".55"/>
  <path d="M164 406h472l34 34a8 8 0 0 1-6 12H136a8 8 0 0 1-6-12z" fill="''' + INK_300 + '''"/>
  <path d="M164 406h472l10 10H154z" fill="''' + INK_400 + '''"/>
  <rect x="352" y="418" width="96" height="10" rx="5" fill="''' + INK_400 + '''"/>''')

# ------------------------------------------------------------ 3. headphones
_HEADPHONES = _doc(
    'Headphones cover illustration',
    BRAND_50, WHITE, BRAND_100,
    '''  <path d="M208 344v-58a192 192 0 0 1 384 0v58" fill="none" stroke="''' + BRAND_600 + '''" stroke-width="28" stroke-linecap="round"/>
  <path d="M232 340v-54a168 168 0 0 1 336 0v54" fill="none" stroke="''' + BRAND_400 + '''" stroke-width="8" stroke-linecap="round"/>
  <rect x="176" y="316" width="86" height="150" rx="40" fill="''' + BRAND_600 + '''"/>
  <rect x="196" y="338" width="46" height="106" rx="23" fill="''' + INK_900 + '''"/>
  <rect x="538" y="316" width="86" height="150" rx="40" fill="''' + BRAND_600 + '''"/>
  <rect x="558" y="338" width="46" height="106" rx="23" fill="''' + INK_900 + '''"/>
  <rect x="196" y="356" width="14" height="70" rx="7" fill="''' + INK_500 + '''" opacity=".45"/>
  <rect x="590" y="356" width="14" height="70" rx="7" fill="''' + INK_500 + '''" opacity=".45"/>''')

# ----------------------------------------------------------------- 4. mouse
_MOUSE = _doc(
    'Computer mouse cover illustration',
    BRAND_50, WHITE, BRAND_100,
    '''  <path d="M400 168c72 0 118 62 118 150v72c0 88-52 148-118 148s-118-60-118-148v-72c0-88 46-150 118-150z" fill="''' + INK_800 + '''"/>
  <path d="M322 250c8-40 30-66 58-74" fill="none" stroke="''' + INK_600 + '''" stroke-width="12" stroke-linecap="round"/>
  <path d="M400 174v92" stroke="''' + INK_600 + '''" stroke-width="4"/>
  <rect x="386" y="196" width="28" height="58" rx="14" fill="''' + BRAND_500 + '''"/>
  <rect x="496" y="326" width="18" height="56" rx="9" fill="''' + INK_600 + '''"/>
  <rect x="286" y="330" width="18" height="56" rx="9" fill="''' + INK_600 + '''"/>
  <circle cx="400" cy="486" r="10" fill="''' + INK_600 + '''" opacity=".6"/>''')

# ------------------------------------------------------------------ 5. lamp
_LAMP = _doc(
    'Desk lamp cover illustration',
    '#fffbeb', WHITE, AMBER_PALE,
    '''  <path d="M528 262L292 522h342z" fill="''' + AMBER_LIGHT + '''" opacity=".22"/>
  <rect x="286" y="512" width="228" height="16" rx="8" fill="''' + INK_400 + '''"/>
  <rect x="330" y="460" width="140" height="54" rx="16" fill="''' + INK_800 + '''"/>
  <rect x="352" y="476" width="96" height="10" rx="5" fill="''' + INK_600 + '''"/>
  <path d="M400 464V336l120-82" fill="none" stroke="''' + SLATE + '''" stroke-width="18" stroke-linecap="round"/>
  <circle cx="400" cy="336" r="16" fill="''' + INK_600 + '''"/>
  <g transform="rotate(-30 500 262)">
    <rect x="458" y="226" width="132" height="66" rx="18" fill="''' + AMBER + '''"/>
    <rect x="480" y="246" width="88" height="26" rx="13" fill="''' + AMBER_PALE + '''"/>
  </g>
  <circle cx="536" cy="238" r="9" fill="''' + AMBER_PALE + '''" opacity=".9"/>''')

# -------------------------------------------------------------- 6. backpack
_BACKPACK = _doc(
    'Backpack cover illustration',
    '#f0fdfa', WHITE, SUCCESS_PALE,
    '''  <path d="M340 178v-24a60 60 0 0 1 120 0v24" fill="none" stroke="''' + SUCCESS_DARK + '''" stroke-width="16" stroke-linecap="round"/>
  <rect x="272" y="176" width="256" height="286" rx="52" fill="''' + SUCCESS_MID + '''"/>
  <path d="M272 228v-16a92 92 0 0 1 92-92h72a92 92 0 0 1 92 92v16z" fill="''' + SUCCESS_DARK + '''"/>
  <path d="M272 228v-16a92 92 0 0 1 92-92h72a92 92 0 0 1 92 92v16z" fill="''' + INK_900 + '''" opacity=".14"/>
  <rect x="304" y="310" width="192" height="120" rx="34" fill="''' + SUCCESS_LIGHT + '''"/>
  <rect x="304" y="310" width="192" height="12" rx="6" fill="''' + INK_900 + '''" opacity=".28"/>
  <rect x="392" y="352" width="16" height="38" rx="8" fill="''' + AMBER_LIGHT + '''"/>
  <rect x="378" y="204" width="44" height="30" rx="12" fill="''' + AMBER_LIGHT + '''"/>
  <rect x="318" y="272" width="164" height="14" rx="7" fill="''' + INK_900 + '''" opacity=".16"/>''')

# --------------------------------------------------------------- 7. bicycle
_BICYCLE = _doc(
    'Bicycle cover illustration',
    BRAND_50, WHITE, BRAND_100,
    '''  <rect x="120" y="510" width="560" height="8" rx="4" fill="''' + INK_200 + '''"/>
  <g fill="none" stroke="''' + INK_800 + '''" stroke-width="14">
    <circle cx="246" cy="404" r="98"/>
    <circle cx="554" cy="404" r="98"/>
  </g>
  <g stroke="''' + INK_300 + '''" stroke-width="5">
    <path d="M246 308v192M150 404h192M177 335l138 138M315 335L177 473"/>
    <path d="M554 308v192M458 404h192M485 335l138 138M623 335L485 473"/>
  </g>
  <circle cx="246" cy="404" r="13" fill="''' + INK_800 + '''"/>
  <circle cx="554" cy="404" r="13" fill="''' + INK_800 + '''"/>
  <g fill="none" stroke="''' + BRAND_600 + '''" stroke-width="15" stroke-linecap="round">
    <path d="M246 404h150"/>
    <path d="M396 404l-64-142"/>
    <path d="M332 262l-86 142"/>
    <path d="M332 262h150"/>
    <path d="M396 404l86-142"/>
    <path d="M482 262l72 142"/>
  </g>
  <circle cx="396" cy="404" r="26" fill="none" stroke="''' + INK_600 + '''" stroke-width="8"/>
  <circle cx="396" cy="404" r="8" fill="''' + INK_600 + '''"/>
  <path d="M482 262v-16" stroke="''' + INK_800 + '''" stroke-width="12" stroke-linecap="round"/>
  <path d="M462 238h48" stroke="''' + INK_800 + '''" stroke-width="16" stroke-linecap="round"/>
  <path d="M302 252h74a15 15 0 0 1 0 30h-74a15 15 0 0 1 0-30z" fill="''' + INK_800 + '''"/>''')

# --------------------------------------------------------------- 8. racket
_RACKET = _doc(
    'Badminton racket cover illustration',
    '#f0fdf4', WHITE, '#dcfce7',
    '''  <defs>
    <clipPath id="racket-head">
      <ellipse cx="452" cy="238" rx="104" ry="122"/>
    </clipPath>
  </defs>
  <g transform="rotate(-16 452 356)">
    <rect x="430" y="340" width="44" height="186" rx="22" fill="''' + INK_800 + '''"/>
    <g stroke="''' + INK_600 + '''" stroke-width="5" stroke-linecap="round">
      <path d="M437 372h30M437 398h30M437 424h30M437 450h30M437 476h30"/>
    </g>
    <rect x="416" y="498" width="72" height="24" rx="12" fill="''' + INK_600 + '''"/>
  </g>
  <ellipse cx="452" cy="238" rx="104" ry="122" fill="''' + WHITE + '''"/>
  <g clip-path="url(#racket-head)" stroke="''' + BRAND_200 + '''" stroke-width="3">
    <path d="M362 112v252M380 112v252M398 112v252M416 112v252M434 112v252M452 112v252M470 112v252M488 112v252M506 112v252M524 112v252M542 112v252"/>
    <path d="M344 130h216M344 148h216M344 166h216M344 184h216M344 202h216M344 220h216M344 238h216M344 256h216M344 274h216M344 292h216M344 310h216M344 328h216M344 346h216"/>
  </g>
  <ellipse cx="452" cy="238" rx="104" ry="122" fill="none" stroke="''' + BRAND_600 + '''" stroke-width="15"/>
  <g>
    <path d="M612 452h56l-11 42h-34z" fill="''' + WHITE + '''" stroke="''' + INK_300 + '''" stroke-width="3"/>
    <path d="M626 454v40M640 454v40M654 454v40" stroke="''' + INK_300 + '''" stroke-width="2.5"/>
    <path d="M621 494h38l-5 16h-28z" fill="''' + INK_200 + '''"/>
    <circle cx="640" cy="514" r="17" fill="''' + BRAND_600 + '''"/>
  </g>''')

# ----------------------------------------------------------- 9. calculator
_CALCULATOR = _doc(
    'Scientific calculator cover illustration',
    BRAND_50, WHITE, BRAND_100,
    '''  <rect x="288" y="116" width="224" height="368" rx="26" fill="''' + INK_800 + '''"/>
  <rect x="288" y="116" width="224" height="368" rx="26" fill="''' + INK_900 + '''" opacity=".22"/>
  <rect x="312" y="142" width="176" height="88" rx="12" fill="''' + INK_900 + '''"/>
  <rect x="322" y="152" width="156" height="68" rx="8" fill="''' + BRAND_200 + '''"/>
  <rect x="404" y="176" width="62" height="14" rx="7" fill="''' + BRAND_700 + '''"/>
  <rect x="444" y="196" width="24" height="12" rx="6" fill="''' + BRAND_500 + '''"/>
  <rect x="322" y="246" width="88" height="10" rx="5" fill="''' + INK_600 + '''"/>
  <g fill="''' + INK_600 + '''">
    <rect x="318" y="288" width="36" height="30" rx="8"/>
    <rect x="362" y="288" width="36" height="30" rx="8"/>
    <rect x="406" y="288" width="36" height="30" rx="8"/>
    <rect x="318" y="326" width="36" height="30" rx="8"/>
    <rect x="362" y="326" width="36" height="30" rx="8"/>
    <rect x="406" y="326" width="36" height="30" rx="8"/>
    <rect x="318" y="364" width="36" height="30" rx="8"/>
    <rect x="362" y="364" width="36" height="30" rx="8"/>
    <rect x="406" y="364" width="36" height="30" rx="8"/>
    <rect x="318" y="402" width="36" height="30" rx="8"/>
    <rect x="362" y="402" width="36" height="30" rx="8"/>
  </g>
  <rect x="450" y="288" width="36" height="30" rx="8" fill="''' + PRICE + '''"/>
  <rect x="450" y="326" width="36" height="30" rx="8" fill="''' + INK_600 + '''"/>
  <rect x="450" y="364" width="36" height="30" rx="8" fill="''' + INK_600 + '''"/>
  <rect x="406" y="402" width="80" height="30" rx="8" fill="''' + BRAND_500 + '''"/>
  <rect x="318" y="440" width="168" height="24" rx="12" fill="''' + INK_600 + '''"/>''')

# ------------------------------------------------------------ 10. lecture notes
_NOTES = _doc(
    'Lecture notes cover illustration',
    BRAND_50, WHITE, BRAND_100,
    '''  <g transform="rotate(-2 400 310)">
    <rect x="240" y="180" width="330" height="258" rx="10" fill="''' + WHITE + '''" stroke="''' + LINE_STRONG + '''" stroke-width="2"/>
    <rect x="232" y="172" width="330" height="258" rx="10" fill="''' + WHITE + '''" stroke="''' + LINE_STRONG + '''" stroke-width="2"/>
    <rect x="224" y="164" width="330" height="258" rx="10" fill="''' + WHITE + '''" stroke="''' + BRAND_200 + '''" stroke-width="2.5"/>
    <path d="M282 176v234" stroke="''' + PRICE + '''" stroke-width="3" opacity=".4"/>
    <g fill="#a5b4fc">
      <rect x="300" y="196" width="150" height="11" rx="5.5"/>
      <rect x="300" y="220" width="196" height="11" rx="5.5"/>
      <rect x="300" y="244" width="120" height="11" rx="5.5"/>
    </g>
    <rect x="296" y="270" width="184" height="22" rx="7" fill="''' + AMBER_LIGHT + '''" opacity=".38"/>
    <rect x="300" y="276" width="150" height="11" rx="5.5" fill="''' + BRAND_400 + '''"/>
    <rect x="300" y="312" width="92" height="72" rx="8" fill="''' + BRAND_50 + '''" stroke="''' + BRAND_200 + '''" stroke-width="2.5"/>
    <path d="M312 366l24-26 18 14 24-30" fill="none" stroke="''' + BRAND_500 + '''" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
    <g fill="#a5b4fc">
      <rect x="410" y="322" width="110" height="11" rx="5.5"/>
      <rect x="410" y="346" width="86" height="11" rx="5.5"/>
      <rect x="410" y="370" width="98" height="11" rx="5.5"/>
    </g>
    <g fill="''' + BRAND_50 + '''" stroke="''' + LINE_STRONG + '''" stroke-width="2">
      <circle cx="252" cy="222" r="6"/>
      <circle cx="252" cy="292" r="6"/>
      <circle cx="252" cy="362" r="6"/>
    </g>
  </g>
  <g transform="rotate(12 450 409)">
    <rect x="350" y="398" width="190" height="22" rx="11" fill="''' + BRAND_600 + '''"/>
    <rect x="350" y="398" width="62" height="22" rx="11" fill="''' + BRAND_800 + '''"/>
    <path d="M540 403l24 6-24 6z" fill="''' + INK_400 + '''"/>
    <circle cx="348" cy="409" r="7" fill="''' + BRAND_800 + '''"/>
  </g>''')

COVERS = {
    'demo-book.svg': _BOOK,
    'demo-laptop.svg': _LAPTOP,
    'demo-headphones.svg': _HEADPHONES,
    'demo-mouse.svg': _MOUSE,
    'demo-lamp.svg': _LAMP,
    'demo-backpack.svg': _BACKPACK,
    'demo-bicycle.svg': _BICYCLE,
    'demo-racket.svg': _RACKET,
    'demo-calculator.svg': _CALCULATOR,
    'demo-notes.svg': _NOTES,
}


def write_covers(dest_dir, force=False):
    """Write the demo covers into `dest_dir`.

    Existing files are left alone unless `force` is set, so a human who replaced a
    placeholder with a real photo keeps it. Returns the filenames written, in the
    order of `COVERS`; an empty list means everything was already in place.
    """
    os.makedirs(dest_dir, exist_ok=True)
    written = []
    for filename, svg in COVERS.items():
        path = os.path.join(dest_dir, filename)
        if not force and os.path.exists(path):
            continue
        with open(path, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(svg)
        written.append(filename)
    return written


if __name__ == '__main__':
    names = write_covers('uploads', force='--force' in os.sys.argv)
    if names:
        print('Wrote %d demo cover illustration(s) into uploads/:' % len(names))
        for name in names:
            print('  ' + name)
    else:
        print('All demo cover illustrations are already present in uploads/.')
