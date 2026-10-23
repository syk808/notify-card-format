# -*- coding: utf-8 -*-
"""Parse standard cards back into fields. 把标准卡片解析回字段。

A message body may contain several cards mixed with other text; ``parse_all``
returns every card it finds, ``split`` also keeps the non-card lines.
Pure text processing, no I/O.
"""
import re

_HEAD = re.compile(r"^【(日历|机会|异动|故障|观察)】\s*([^｜\n]+?)\s*｜\s*(更新：)?(.+?)\s*$")
_URL = re.compile(r"^(?:https?://\S+|<a\s.+</a>)$")
_RISK = re.compile(r"（风险：(.+)）\s*$")


def split_todo(todo):
    """'动作（风险：xxx）' -> ('动作', 'xxx')."""
    risk = ""
    m = _RISK.search(todo or "")
    if m:
        risk, todo = m.group(1).strip(), todo[:m.start()].rstrip()
    return (todo or "").strip(), risk


def _parse_at(src, i):
    """Try to read one card starting at line i. Returns (card_dict, next_index) or (None, i)."""
    m = _HEAD.match(src[i].strip())
    if not m:
        return None, i
    c = {"kind": m.group(1), "name": m.group(2).strip(), "update": bool(m.group(3)),
         "what": m.group(4).strip(), "nums": [], "todo": "", "risk": "", "link": ""}
    i += 1
    seen_nums = seen_todo = False
    while i < len(src):
        t = src[i].strip()
        if t.startswith("数字：") and not seen_nums:
            c["nums"] = [x.strip() for x in t[3:].split("，") if x.strip()]
            seen_nums = True
        elif t.startswith("要做：") and not seen_todo:
            c["todo"], c["risk"] = split_todo(t[3:].strip())
            seen_todo = True
        elif _URL.match(t) and not c["link"]:
            c["link"] = t
        else:
            break
        i += 1
    return c, i


def split(body):
    """Return a list of items: card dicts, or plain strings for non-card lines (kept in order)."""
    src = (body or "").splitlines()
    out, i = [], 0
    while i < len(src):
        c, j = _parse_at(src, i)
        if c is None:
            out.append(src[i])
            i += 1
        else:
            out.append(c)
            i = j
    return out


def parse_all(body):
    """Every standard card in ``body``."""
    return [x for x in split(body) if isinstance(x, dict)]


def parse(body):
    """First card in ``body`` or None."""
    cards = parse_all(body)
    return cards[0] if cards else None


def is_card(body):
    return parse(body) is not None
