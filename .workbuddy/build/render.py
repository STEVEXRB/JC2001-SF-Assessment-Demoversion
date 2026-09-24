# render.py - render every Canvas returned by a figure module into a PNG via headless Edge.
# Usage:  python render.py                # renders all figures
#         python render.py fig_arch_layers fig_usecase
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LANG = os.environ.get("FIGURE_LANG", "en")
OUT = os.path.join(HERE, "figures" if LANG == "en" else "figures_" + LANG)

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_edge():
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    raise SystemExit("Microsoft Edge not found")


def render(canvas, path, scale=2, wait_ms=1200):
    edge = find_edge()
    html_path = path + ".tmp.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(canvas.html(scale=scale))
    tmp_profile = tempfile.mkdtemp(prefix="edgeprof-")
    cmd = [
        edge,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--force-device-scale-factor=%d" % scale,
        "--default-background-color=FFFFFFFF",
        "--window-size=%d,%d" % (canvas.w, canvas.h),
        "--virtual-time-budget=%d" % wait_ms,
        "--user-data-dir=" + tmp_profile,
        "--screenshot=" + os.path.abspath(path),
        "file:///" + os.path.abspath(html_path).replace("\\", "/"),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        os.remove(html_path)
    except OSError:
        pass
    if not os.path.exists(path):
        raise SystemExit("render failed for %s\n%s\n%s" % (path, res.stdout, res.stderr))
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    mod_name = os.environ.get("FIGMOD", "figures")
    sys.path.insert(0, HERE)
    if LANG != "en":
        import importlib
        importlib.import_module("i18n_figures").install()
        print("label language:", LANG)
    mod = __import__(mod_name)
    wanted = set(sys.argv[1:])
    figs = getattr(mod, "FIGS")
    order = getattr(mod, "ORDER", list(figs.keys()))
    n = 0
    for name in order:
        if wanted and name not in wanted:
            continue
        canvas = figs[name]() if callable(figs[name]) else figs[name]
        if canvas is None:
            continue
        path = os.path.join(OUT, name + ".png")
        render(canvas, path)
        size = os.path.getsize(path)
        print("ok  %-34s %5dx%-5d %6.1f KB" % (name, canvas.w * 2, canvas.h * 2, size / 1024))
        n += 1
    print("rendered %d figure(s) -> %s" % (n, OUT))


if __name__ == "__main__":
    main()
