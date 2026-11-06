import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from generate import validate_rate


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


if __name__ == "__main__":
    unittest.main()
