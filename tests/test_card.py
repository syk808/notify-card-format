import unittest

from notify_card import bj_time, card, is_card, money, parse, parse_all, pct, split


class TestCard(unittest.TestCase):
    def test_basic(self):
        s = card("异动", "ABC", "15 分钟涨 18%", nums=["现价 0.12", "成交额 253 万美元"],
                 todo="不追，等回踩", link="https://example.com/abc")
        self.assertEqual(s.splitlines(), [
            "【异动】ABC｜15 分钟涨 18%",
            "数字：现价 0.12，成交额 253 万美元",
            "要做：不追，等回踩",
            "https://example.com/abc",
        ])

    def test_defaults_and_update(self):
        s = card("日历", "XYZ", "明天 20:00 解锁", update=True)
        self.assertEqual(s, "【日历】XYZ｜更新：明天 20:00 解锁\n要做：不用动")

    def test_english_alias(self):
        self.assertTrue(card("failure", "feed", "no data for 30 min").startswith("【故障】"))

    def test_bad_kind(self):
        with self.assertRaises(ValueError):
            card("news", "A", "b")

    def test_missing_name(self):
        with self.assertRaises(ValueError):
            card("机会", "  ", "b")

    def test_truncate_and_max_nums(self):
        s = card("机会", "A", "x" * 100, nums=["1", "2", "3", "4"])
        head, nums = s.splitlines()[:2]
        self.assertTrue(head.endswith("…"))
        self.assertEqual(nums, "数字：1，2，3")

    def test_non_http_link_dropped(self):
        self.assertNotIn("ftp", card("机会", "A", "b", link="ftp://x"))

    def test_html_escape(self):
        self.assertIn("&lt;b&gt;", card("机会", "<b>", "x", html=True))


class TestHelpers(unittest.TestCase):
    def test_money(self):
        self.assertEqual(money(123_000_000), "1.23 亿美元")
        self.assertEqual(money(2_530_000), "253 万美元")
        self.assertEqual(money(15_000), "1.5 万美元")
        self.assertEqual(money(8500), "8,500 美元")
        self.assertEqual(money("x"), "—")

    def test_pct(self):
        self.assertEqual(pct(18), "+18.0%")
        self.assertEqual(pct(-3.456, 2), "-3.46%")

    def test_bj_time(self):
        self.assertEqual(bj_time(0), "01-01 08:00")


class TestParse(unittest.TestCase):
    def test_roundtrip(self):
        s = card("机会", "ABC", "白名单开放", nums=["名额 5000", "截止 10-25"],
                 todo="去官网登记（风险：可能要 KYC）", link="https://example.com", update=True)
        c = parse(s)
        self.assertEqual(c["kind"], "机会")
        self.assertEqual(c["name"], "ABC")
        self.assertTrue(c["update"])
        self.assertEqual(c["what"], "白名单开放")
        self.assertEqual(c["nums"], ["名额 5000", "截止 10-25"])
        self.assertEqual(c["todo"], "去官网登记")
        self.assertEqual(c["risk"], "可能要 KYC")
        self.assertEqual(c["link"], "https://example.com")

    def test_multiple_and_plain_lines(self):
        body = "早报\n" + card("异动", "A", "x") + "\n\n" + card("故障", "B", "y")
        items = split(body)
        self.assertEqual(items[0], "早报")
        self.assertEqual([c["name"] for c in parse_all(body)], ["A", "B"])

    def test_not_a_card(self):
        self.assertFalse(is_card("hello\nworld"))
        self.assertIsNone(parse(""))


if __name__ == "__main__":
    unittest.main()
