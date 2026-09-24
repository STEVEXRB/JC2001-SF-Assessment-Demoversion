# charts.py - quantitative figures for the testing and evaluation chapter
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE = os.path.dirname(os.path.abspath(__file__))
LANG = os.environ.get("CHART_LANG", "en")
OUT = os.path.join(HERE, "figures" if LANG == "en" else "figures_" + LANG)
os.makedirs(OUT, exist_ok=True)

ZH = {
    "In-process response time by operation": "各操作的进程内响应时间",
    "Flask test client, %d repeats per operation (%d for the write paths), "
    "Python %s. Network and browser time excluded.":
        "Flask test client，每个操作重复 %d 次（写路径 %d 次），Python %s。不含网络与浏览器耗时。",
    "milliseconds per request": "每次请求毫秒数",
    "median": "中位数", "95th percentile": "95 分位",
    "Browse the catalogue (page 1 of 42)": "浏览商品目录",
    "Keyword search across title and description": "关键词搜索",
    "Keyword search with no match": "无匹配的关键词搜索",
    "Filter by category and sort by price": "分类筛选并按价格排序",
    "Open a listing detail page": "打开商品详情页",
    "Open the busiest listing (5 comments)": "打开留言最多的商品",
    "Read the comment thread": "读取留言区",
    "Load the personal centre listing grid": "加载个人中心商品网格",
    "Conversation list (60 threads)": "会话列表（60 个会话）",
    "Open a 40-message thread": "打开 40 条消息的会话",
    "Publish a listing": "发布商品",
    "Add and remove a favourite": "收藏并取消收藏",
    "Toggle a listing offline and back": "下架再重新上架",

    "How the catalogue reads scale with the size of the table": "目录读取成本随数据量增长的变化",
    "A 20-fold increase in rows costs about 0.3 ms. Both the keyword search and the "
    "filtered catalogue still scan the table, but at this scale the scan is not the "
    "dominant cost.":
        "数据行数增长二十倍，成本仅增加约 0.3 毫秒。关键词搜索与带筛选的目录仍会扫描全表，"
        "但在这一规模下扫描并非主要成本。",
    "listings stored in the items table": "items 表中的商品数",
    "median milliseconds": "中位毫秒数",
    "Catalogue page 1": "目录第 1 页",
    "Keyword search (LIKE on two columns)": "关键词搜索（两列 LIKE）",
    "Category filter + sort by price": "分类筛选并按价格排序",

    "Automated test suite: 80 cases, all passing": "自动化测试套件：80 个用例全部通过",
    "Grouped by the component under test, so a failure names the module that regressed. "
    "Every case ran against a throwaway database and upload directory.":
        "按被测组件分组，因此一旦失败即可指出发生回归的模块。每个用例都在一次性的数据库与上传目录上运行。",
    "automated test cases": "自动化用例数",
    "TC-A  Accounts": "TC-A  账号", "TC-C  Catalogue": "TC-C  目录",
    "TC-L  Listings": "TC-L  商品", "TC-U  Upload": "TC-U  上传",
    "TC-T  Transitions": "TC-T  状态迁移", "TC-S  Social": "TC-S  社交",
    "TC-P  Personal centre": "TC-P  个人中心",
    "registration, login, session, profile": "注册、登录、会话、资料",
    "listing, search, filter, sort, paging, detail": "目录、搜索、筛选、排序、分页、详情",
    "create, update, soft delete, ownership": "创建、编辑、软删除、归属",
    "extension allow-list, size cap, stored names": "扩展名白名单、大小上限、存储命名",
    "the item status state machine": "商品状态机",
    "favourites, comments, private messages": "收藏、留言、私信",
    "my listings and sold items": "我的发布与已售出",

    "Requirements realised and independently verified": "已实现并已独立验证的需求",
    "Each requirement below is traced to the design element that implements it and to at "
    "least one automated case that exercises it (Appendix B of the report).":
        "以下每条需求都追溯到实现它的设计要素，以及至少一个行使它的自动化用例（见报告附录 B）。",
    "Functional requirements": "功能需求",
    "Non-functional requirements": "非功能需求",
    "Status transition guards": "状态迁移守卫",
    "Authorisation rules": "权限规则",
    "Input validation rules": "输入校验规则",
    "realised in the PoC": "已在 PoC 中实现",
    "%d / %d verified": "%d / %d 已验证",
    "number of requirements": "需求条数",
}

# The rcParams.update() below is authoritative for font.family, so the CJK face is
# chosen there rather than here.
FAMILIES = (["Microsoft YaHei", "SimHei", "DejaVu Sans"] if LANG != "en"
            else ["Arial", "DejaVu Sans"])
plt.rcParams["axes.unicode_minus"] = False


def T(s):
    return ZH.get(s, s) if LANG != "en" else s

INK = "#14181f"
MUTED = "#5b6472"
GRID = "#dde3ea"
PRIMARY = "#2f5d8c"
TEAL = "#0f766e"
AMBER = "#a8610a"
GREY = "#8b95a3"
RED = "#b3261e"
GREEN = "#2f7d4f"

plt.rcParams.update({
    "font.family": FAMILIES,
    "font.size": 8.2,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.7,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def clean(ax, xgrid=False, ygrid=True):
    ax.set_axisbelow(True)
    ax.grid(axis="x", visible=xgrid)
    ax.grid(axis="y", visible=ygrid)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)


def _wrap(text, n):
    out, line = [], ""
    for w in str(text).split():
        if len(line) + 1 + len(w) <= n:
            line = (line + " " + w).strip()
        else:
            out.append(line)
            line = w
    if line:
        out.append(line)
    return out


def title(fig, main, sub=None, y=0.985):
    fig.text(0.012, y, main, fontsize=10.5, fontweight="bold", color=INK, va="top")
    if sub:
        for i, line in enumerate(_wrap(sub, 112)):
            fig.text(0.012, y - 0.052 - i * 0.045, line, fontsize=7.4, color=MUTED, va="top")


# ------------------------------------------------------------------ perf chart
def chart_perf():
    data = json.load(open(os.path.join(HERE, "perf.json"), encoding="utf-8"))
    rows = list(data["results"].items())
    labels = [T(k) for k, _ in rows][::-1]
    med = [v["median"] for _, v in rows][::-1]
    p95 = [v["p95"] for _, v in rows][::-1]

    fig, ax = plt.subplots(figsize=(6.25, 4.05), dpi=300)
    y = range(len(labels))
    h = 0.36
    ax.barh([i + h / 2 for i in y], med, height=h, color=PRIMARY, label=T("median"),
            edgecolor="white", linewidth=0.6)
    ax.barh([i - h / 2 for i in y], p95, height=h, color="#9dc0e0", label=T("95th percentile"),
            edgecolor="white", linewidth=0.6)
    for i, (m, p) in enumerate(zip(med, p95)):
        ax.text(p + 0.16, i - h / 2, "%.1f" % p, va="center", fontsize=6.2, color=MUTED)
        ax.text(m + 0.16, i + h / 2, "%.1f" % m, va="center", fontsize=6.2, color=PRIMARY)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=7.2)
    ax.set_xlabel(T("milliseconds per request"))
    ax.set_xlim(0, max(p95) * 1.30)
    ax.legend(frameon=False, loc="upper right", fontsize=7.4)
    clean(ax, xgrid=True, ygrid=False)
    title(fig, T("In-process response time by operation"),
          T("Flask test client, %d repeats per operation (%d for the write paths), "
            "Python %s. Network and browser time excluded.")
          % (data["meta"]["repeats"], 100, data["meta"]["runtime"]))
    fig.subplots_adjust(left=0.325, right=0.985, top=0.845, bottom=0.10)
    fig.savefig(os.path.join(OUT, "chart_perf.png"))
    plt.close(fig)


# ----------------------------------------------------------------- scale chart
def chart_scale():
    rows = json.load(open(os.path.join(HERE, "scale.json"), encoding="utf-8"))
    xs = [r["_rows"] for r in rows]
    keys = [k for k in rows[0] if not k.startswith("_")]
    colors = [PRIMARY, AMBER, TEAL]

    fig, ax = plt.subplots(figsize=(6.25, 3.1), dpi=300)
    for key, col in zip(keys, colors):
        ys = [r[key] for r in rows]
        ax.plot(xs, ys, marker="o", color=col, linewidth=1.9, markersize=6, label=T(key))
        for x, yv in zip(xs, ys):
            ax.annotate("%.2f" % yv, (x, yv), textcoords="offset points", xytext=(0, 7),
                        ha="center", fontsize=6.4, color=col)
    ax.set_xscale("log")
    ax.set_xticks(xs)
    ax.set_xticklabels([str(x) for x in xs])
    ax.set_xlabel(T("listings stored in the items table"))
    ax.set_ylabel(T("median milliseconds"))
    ax.set_ylim(2.0, max(3.1, max(r[k] for r in rows for k in keys) + 0.35))
    ax.legend(frameon=False, fontsize=7.4, loc="upper left")
    clean(ax)
    title(fig, T("How the catalogue reads scale with the size of the table"),
          T("A 20-fold increase in rows costs about 0.3 ms. Both the keyword search and the "
            "filtered catalogue still scan the table, but at this scale the scan is not the "
            "dominant cost."))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.79, bottom=0.155)
    fig.savefig(os.path.join(OUT, "chart_scale.png"))
    plt.close(fig)


# ----------------------------------------------------------------- tests chart
def chart_tests():
    groups = [
        ("TC-A  Accounts", 10, "registration, login, session, profile"),
        ("TC-C  Catalogue", 14, "listing, search, filter, sort, paging, detail"),
        ("TC-L  Listings", 12, "create, update, soft delete, ownership"),
        ("TC-U  Upload", 8, "extension allow-list, size cap, stored names"),
        ("TC-T  Transitions", 15, "the item status state machine"),
        ("TC-S  Social", 16, "favourites, comments, private messages"),
        ("TC-P  Personal centre", 5, "my listings and sold items"),
    ]
    labels = [T(g[0]) for g in groups][::-1]
    counts = [g[1] for g in groups][::-1]
    notes = [T(g[2]) for g in groups][::-1]

    fig, ax = plt.subplots(figsize=(6.25, 3.35), dpi=300)
    y = list(range(len(labels)))
    ax.barh(y, counts, height=0.58, color=[PRIMARY if c >= 10 else "#7fa8cd" for c in counts],
            edgecolor="white", linewidth=0.6)
    for i, (c, n) in enumerate(zip(counts, notes)):
        ax.text(c + 0.18, i + 0.13, str(c), va="center", fontsize=7.6,
                color=PRIMARY, fontweight="bold")
        ax.text(c + 0.68, i + 0.13, n, va="center", fontsize=6.4, color=MUTED)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.4)
    ax.set_xlabel(T("automated test cases"))
    ax.set_xlim(0, 35)
    ax.set_xticks([0, 5, 10, 15, 20])
    clean(ax, xgrid=True, ygrid=False)
    title(fig, T("Automated test suite: 80 cases, all passing"),
          T("Grouped by the component under test, so a failure names the module that regressed. "
            "Every case ran against a throwaway database and upload directory."))
    fig.subplots_adjust(left=0.245, right=0.985, top=0.835, bottom=0.115)
    fig.savefig(os.path.join(OUT, "chart_tests.png"))
    plt.close(fig)


# --------------------------------------------------------------- coverage chart
def chart_coverage():
    rows = [
        ("Functional requirements", 28, 28, 0),
        ("Non-functional requirements", 12, 12, 0),
        ("Status transition guards", 15, 15, 0),
        ("Authorisation rules", 9, 9, 0),
        ("Input validation rules", 11, 11, 0),
    ]
    labels = [T(r[0]) for r in rows][::-1]
    covered = [r[1] for r in rows][::-1]
    verified = [r[2] for r in rows][::-1]

    fig, ax = plt.subplots(figsize=(6.25, 2.85), dpi=300)
    y = list(range(len(labels)))
    ax.barh(y, covered, height=0.5, color=TEAL, label=T("realised in the PoC"),
            edgecolor="white", linewidth=0.6)
    for i, (c, v) in enumerate(zip(covered, verified)):
        ax.text(c + 0.35, i, T("%d / %d verified") % (v, c), va="center", fontsize=6.6, color=MUTED)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.4)
    ax.set_xlabel(T("number of requirements"))
    ax.set_xlim(0, 40)
    clean(ax, xgrid=True, ygrid=False)
    title(fig, T("Requirements realised and independently verified"),
          T("Each requirement below is traced to the design element that implements it and to at "
            "least one automated case that exercises it (Appendix B of the report)."))
    fig.subplots_adjust(left=0.275, right=0.985, top=0.80, bottom=0.145)
    fig.savefig(os.path.join(OUT, "chart_coverage.png"))
    plt.close(fig)


if __name__ == "__main__":
    chart_perf()
    chart_scale()
    chart_tests()
    chart_coverage()
    for name in ("chart_perf", "chart_scale", "chart_tests", "chart_coverage"):
        p = os.path.join(OUT, name + ".png")
        print("ok  %-16s %6.1f KB" % (name, os.path.getsize(p) / 1024))
