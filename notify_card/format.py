# -*- coding: utf-8 -*-
"""Four-line standard notification card. 四行标准通知卡片。

Every card can be read in 3 seconds:

    【类型】名称｜一句话说清是什么事
    数字：最关键的 2–3 个数
    要做：该做的动作 + 截止时间（没有就写「不用动」）
    链接

Five kinds only: 日历 (calendar) / 机会 (opportunity) / 异动 (unusual move) /
故障 (failure) / 观察 (watchlist only, not an entry signal).
A follow-up on the same event uses update=True, which adds 「更新：」 to line one.
Times use Beijing time MM-DD HH:mm (bj_time); money uses 亿 / 万 (money).

Standard library only.
"""
import html as _html
import time

KINDS = ("日历", "机会", "异动", "故障", "观察")
KIND_EN = {"calendar": "日历", "opportunity": "机会", "move": "异动", "failure": "故障", "watch": "观察"}
NO_ACTION = "不用动"
MAX_NUMS = 3
NAME_MAX = 30
WHAT_MAX = 60        # first-line description limit
QUOTE_MAX = 220      # when quoting an official post / announcement
NUM_MAX = 40         # each number fragment
TODO_MAX = 70


def _clean(s):
    """Collapse to one line: drop newlines, repeated whitespace and edge separators."""
    return " ".join(str(s or "").split()).strip(" ｜|，,；;")


def _cut(s, n):
    s = _clean(s)
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def card(kind, name, what, nums=None, todo=None, link=None, update=False, html=False, what_max=WHAT_MAX):
    """Build one standard card and return the text.

    kind      one of KINDS (or an English alias from KIND_EN); anything else raises ValueError —
              better not to send than to send a malformed card.
    name      coin / project / the thing that broke.
    what      one sentence describing the event.
    nums      key numbers, a string or list of strings; at most 3 are kept; omitted -> no 数字 line.
    todo      action + deadline; omitted -> 「不用动」.
    link      one link (must start with http); with html=True an <a ...> tag is also accepted.
    html      escape name / what / nums / todo for Telegram parse_mode=HTML.
    what_max  first-line length limit; use QUOTE_MAX when quoting an announcement.
    """
    kind = KIND_EN.get(kind, kind)
    if kind not in KINDS:
        raise ValueError("kind must be one of %s, got %r" % (" / ".join(KINDS), kind))
    esc = (lambda s: _html.escape(s, quote=False)) if html else (lambda s: s)
    name, what = _cut(name, NAME_MAX), _cut(what, what_max)
    if not name or not what:
        raise ValueError("a card needs both a name and a one-line description")
    lines = ["【%s】%s｜%s%s" % (kind, esc(name), "更新：" if update else "", esc(what))]
    if isinstance(nums, str):
        nums = [nums]
    parts = [_cut(n, NUM_MAX) for n in (nums or []) if _clean(n)][:MAX_NUMS]
    if parts:
        lines.append("数字：" + esc("，".join(parts)))
    lines.append("要做：" + esc(_cut(todo, TODO_MAX) or NO_ACTION))
    link = str(link or "").strip()
    if link.startswith("http") or (html and link.startswith("<a ")):
        lines.append(link)
    return "\n".join(lines)


def bj_time(ts=None):
    """Beijing time MM-DD HH:mm. ts = unix seconds, default now."""
    ts = time.time() if ts is None else float(ts)
    return time.strftime("%m-%d %H:%M", time.gmtime(ts + 8 * 3600))


def money(v, unit="美元"):
    """Amounts in 亿 (1e8) / 万 (1e4): 1.23 亿美元, 253 万美元, 8,500 美元."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    a = abs(v)
    if a >= 1e8:
        s = "%.2f 亿" % (v / 1e8)
    elif a >= 1e4:
        s = ("%.0f 万" if a >= 1e6 else "%.1f 万") % (v / 1e4)
    else:
        s = "{:,.0f}".format(v)
        return s + " " + unit if unit else s
    return s + unit


def pct(v, digits=1):
    """Signed percent: +18.0%."""
    try:
        return "%+.*f%%" % (digits, float(v))
    except (TypeError, ValueError):
        return "—"
