import unittest
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from generate import validate_rate, parse_devi_rates


TZ = ZoneInfo("Asia/Colombo")


def payload(when):
    return {
        "status": "ok", "currency": "LKR", "as_of": when.isoformat(),
        "prices": {
            "24k": {"per_gram": 45000, "per_8g": 360000},
            "22k": {"per_gram": 41250, "per_8g": 330000},
        },
    }


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 6, 9, 0, tzinfo=TZ)

    def test_recent_valid_price(self):
        validated = validate_rate(payload(self.now - timedelta(hours=2)), self.now)
        self.assertEqual(validated["prices"]["24k"]["per_gram"], 45000)

    def test_outdated_source_fails(self):
        with self.assertRaises(ValueError):
            validate_rate(payload(self.now - timedelta(days=5)), self.now)

    def test_future_source_fails(self):
        with self.assertRaises(ValueError):
            validate_rate(payload(self.now + timedelta(days=1)), self.now)

    def test_22k_must_be_less_than_24k(self):
        bad = payload(self.now)
        bad["prices"]["22k"] = {"per_gram": 46000, "per_8g": 368000}
        with self.assertRaises(ValueError):
            validate_rate(bad, self.now)

    def test_pawn_value_is_consistent(self):
        bad = payload(self.now)
        bad["prices"]["24k"]["per_8g"] = 1
        with self.assertRaises(ValueError):
            validate_rate(bad, self.now)


def wrap(value):
    if isinstance(value, dict):
        return [0, {key: wrap(part) for key, part in value.items()}]
    if isinstance(value, list):
        return [1, [wrap(part) for part in value]]
    return [0, value]


def devi_page(day="2026-11-07", rates=None):
    if rates is None:
        rates = {"24ct": 366000, "22ct": 336700}
    rows = []
    for carat, pawn in rates.items():
        rows.append({
            "institution": {"code": "devi-jewellers"},
            "commodity": {"karat": carat, "unit": "pawn_8g"},
            "rate": {"priceLkr": pawn},
            "rateDate": day,
            "source": {"url": "https://devijewellers.lk/gold-rate", "effectiveDate": day},
        })
    return "<astro-island props='" + json.dumps({"rates": wrap(rows)}) + "'></astro-island>"


class DeviSourceTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 7, 9, 0, tzinfo=TZ)

    def test_pawn_is_converted_to_per_gram(self):
        result = parse_devi_rates(devi_page(), self.now)
        self.assertEqual(result["prices"]["24k"]["per_gram"], 45750)
        self.assertEqual(result["prices"]["22k"]["per_gram"], 42087.5)
        self.assertEqual(result["prices"]["22k"]["per_8g"], 336700)

    def test_missing_devi_karat_fails(self):
        with self.assertRaises(ValueError):
            parse_devi_rates(devi_page(rates={"24ct": 366000}), self.now)

    def test_stale_devi_date_fails(self):
        with self.assertRaises(ValueError):
            parse_devi_rates(devi_page(day="2026-11-01"), self.now)

    def test_conflicting_devi_rates_fail(self):
        with self.assertRaises(ValueError):
            parse_devi_rates(devi_page() + devi_page(rates={"24ct": 367000, "22ct": 336700}), self.now)


if __name__ == "__main__":
    unittest.main()
