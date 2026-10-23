# notify-card-format

A tiny, dependency-free Python helper that turns any alert into the same
**four-line card** that can be read in three seconds, and parses those cards back
into fields.

一个零依赖的小工具：把各种通知（行情异动、日历提醒、机会、故障）统一成**四行标准卡片**，
任何一条 3 秒能看完；也能把卡片解析回字段，方便下游程序处理。

```
【类型】名称｜一句话说清是什么事
数字：最关键的 2–3 个数
要做：该做的动作 + 截止时间（没有就写「不用动」）
链接
```

```
【异动】ABC｜15 分钟涨 +18.2%
数字：现价 0.1234，成交额 253 万美元，持仓量 4100 万美元
要做：不追，回踩 0.11 附近再看
https://example.com/abc
```

## Card kinds / 五种类型

| kind | alias | meaning |
| --- | --- | --- |
| 日历 | `calendar` | scheduled event: unlock, sale, earnings / 日程 |
| 机会 | `opportunity` | something you can act on / 可参与 |
| 异动 | `move` | unusual price / volume move / 行情异动 |
| 故障 | `failure` | a data source or job broke / 系统故障 |
| 观察 | `watch` | watchlist only, not an entry signal / 只进观察名单 |

Rules enforced by `card()`:

- unknown kind -> `ValueError` (better not to send than to send a malformed card)
- name max 30 chars, description max 60 (use `what_max=QUOTE_MAX` for quotes), at most 3 numbers
- empty `todo` becomes 「不用动」 (no action needed)
- only `http(s)` links are kept; `html=True` escapes text for Telegram `parse_mode=HTML`
- `update=True` marks a follow-up on the same event with 「更新：」

Helpers: `money()` formats amounts in 亿 / 万, `pct()` gives a signed percent,
`bj_time()` gives Beijing time `MM-DD HH:mm`.

## Install / 安装

Standard library only, Python 3.8+.

```bash
git clone https://github.com/syk808/notify-card-format.git
cd notify-card-format
python examples/demo.py
```

Or just copy the `notify_card/` folder into your project.

## Usage / 用法

```python
from notify_card import card, parse, money, pct

text = card("异动", "ABC", "15 分钟涨 " + pct(18.2),
            nums=["现价 0.1234", "成交额 " + money(2_530_000)],
            todo="不追，回踩再看", link="https://example.com/abc")

c = parse(text)
# {'kind': '异动', 'name': 'ABC', 'update': False, 'what': '15 分钟涨 +18.2%',
#  'nums': ['现价 0.1234', '成交额 253 万美元'], 'todo': '不追，回踩再看', 'risk': '', 'link': 'https://...'}
```

`parse_all(body)` returns every card in a message; `split(body)` keeps non-card
lines too, in order. A trailing 「（风险：…）」 in the 要做 line is split into `risk`.

Sending is up to you (Telegram, Slack, email ...). This library only formats text,
it has no network code and stores no credentials.

## Tests / 测试

```bash
python -m unittest -v
```

## Disclaimer / 免责声明

The examples use made-up tickers and numbers. Nothing here is investment advice.

示例中的币名和数字均为虚构，不构成任何投资建议。

## License

MIT
