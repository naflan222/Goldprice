#!/usr/bin/env python3
"""Create a daily, clearly labelled Sri Lankan gold-rate Status image.

The input is an indicative market-reference API, NOT a jewellery retail quote.
Fail closed when the source is malformed or too old. `--demo` never uses live data.
"""

import argparse
import json
import math
import os
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "docs"
SOURCE_API = "https://www.goldpricetoday.lk/api/v1/gold-price"
SOURCE_NAME = "GoldPriceToday.lk"
COLOMBO = ZoneInfo("Asia/Colombo")
WIDTH, HEIGHT = 1080, 1920
GOLD = (222, 185, 111)
PALE = (245, 227, 183)
MUTED = (151, 165, 153)
WHITE = (248, 248, 238)


def font(size: int, bold: bool = False, serif: bool = False):
    paths = (["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"] if serif else
             ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
             ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def validate_rate(payload: dict, now: datetime) -> dict:
    if payload.get("status") != "ok" or payload.get("currency") != "LKR":
        raise ValueError("Expected a successful LKR price response")
    when = datetime.fromisoformat(payload["as_of"].replace("Z", "+00:00"))
    if when.tzinfo is None:
        raise ValueError("Price timestamp has no timezone")
    when = when.astimezone(COLOMBO)
    age = now - when
    if age < -timedelta(minutes=15) or age > timedelta(hours=72):
        raise ValueError(f"Price is future-dated or stale: {age}")

    prices = {}
    for purity in ("24k", "22k"):
        row = payload["prices"][purity]
        gram, pawn = float(row["per_gram"]), float(row["per_8g"])
        if not (math.isfinite(gram) and math.isfinite(pawn)):
            raise ValueError(f"Non-finite {purity} price")
        if not (1000 <= gram <= 1_000_000 and abs(pawn - gram * 8) <= max(2, gram * .03)):
            raise ValueError(f"Suspicious {purity} prices")
        prices[purity] = {"per_gram": gram, "per_8g": pawn}
    if prices["22k"]["per_gram"] >= prices["24k"]["per_gram"]:
        raise ValueError("22K price cannot be greater than or equal to 24K")
    return {"as_of": when, "prices": prices}


def get_rates(demo=False):
    now = datetime.now(COLOMBO)
    if demo:
        payload = {
            "status": "ok", "currency": "LKR", "as_of": now.isoformat(),
            "prices": {
                "24k": {"per_gram": 45000, "per_8g": 360000},
                "22k": {"per_gram": 41250, "per_8g": 330000},
            },
        }
    else:
        request = Request(SOURCE_API, headers={
            "User-Agent": "GoldRateStatusImage/1.0 (+daily reference image)",
            "Accept": "application/json",
        })
        with urlopen(request, timeout=25) as response:
            payload = json.load(response)
    result = validate_rate(payload, now)
    return now, result


def centered(draw, xy, value, fill, face, **kwargs):
    draw.text(xy, value, anchor="mm", fill=fill, font=face, **kwargs)


def gradient_background():
    image = Image.new("RGB", (WIDTH, HEIGHT), "#071612")
    pixels = image.load()
    for y in range(HEIGHT):
        t = y / HEIGHT
        for x in range(WIDTH):
            dx = (x - 550) / 800
            glow = max(0, 1 - math.hypot(dx, (y - 700) / 1500)) * .13
            pixels[x, y] = (int(8 + t * 2 + glow * 110),
                            int(29 - t * 13 + glow * 60),
                            int(22 - t * 10 + glow * 36))
    return image


def fit_logo(image, draw, logo_path):
    if logo_path and Path(logo_path).is_file():
        with Image.open(logo_path) as logo_file:
            logo = logo_file.convert("RGBA")
            logo.thumbnail((260, 245), Image.Resampling.LANCZOS)
            image.paste(logo, ((WIDTH-logo.width)//2, 55), logo)
    else:
        draw.ellipse((491, 110, 589, 208), outline=GOLD, width=3)
        draw.polygon([(540, 119), (551, 150), (581, 159), (551, 170),
                      (540, 200), (529, 170), (499, 159), (529, 150)],
                     fill=GOLD)


def card(draw, top, purity, data):
    bottom = top + 376
    draw.rounded_rectangle((72, top + 11, 1008, bottom + 12), radius=40,
                           fill=(4, 18, 14))
    draw.rounded_rectangle((65, top, 1015, bottom), radius=40,
                           fill=(15, 36, 29), outline=(122, 98, 62), width=2)
    draw.line((111, top+108, 969, top+108), fill=(76, 84, 65), width=2)
    draw.rounded_rectangle((114, top+34, 236, top+90), radius=21,
                           fill=(74, 64, 39), outline=GOLD, width=1)
    centered(draw, (175, top+63), purity, PALE, font(34, bold=True))
    draw.text((267, top+52), "GOLD REFERENCE RATE", font=font(27), fill=MUTED)

    draw.text((118, top+133), "PER GRAM", font=font(27, bold=True), fill=GOLD)
    draw.text((112, top+177), f"Rs. {data['per_gram']:,.2f}",
              font=font(67, bold=True), fill=WHITE)
    draw.line((117, top+278, 965, top+278), fill=(62, 79, 62), width=2)
    draw.text((118, top+302), "PER 8 GRAMS (PAWN)", font=font(25), fill=MUTED)
    draw.text((560, top+296), f"Rs. {data['per_8g']:,.2f}",
              font=font(40, bold=True), fill=PALE)


def render(now, data, demo, shop_name, shop_subtitle, shop_tagline, logo_path):
    image = gradient_background()
    d = ImageDraw.Draw(image)
    # Ornamental border and header.
    d.rounded_rectangle((34, 30, 1046, 1890), radius=30,
                        outline=(97, 82, 49), width=3)
    fit_logo(image, d, logo_path)
    centered(d, (540, 322), shop_name[:35].upper(), PALE, font(72, serif=True))
    centered(d, (540, 382), shop_subtitle[:44].upper(), GOLD, font(27, bold=True))
    centered(d, (540, 421), shop_tagline[:65], MUTED, font(24, serif=True))
    d.line((297, 462, 783, 462), fill=GOLD, width=2)
    centered(d, (540, 515), "DAILY GOLD RATES", WHITE, font(61, serif=True))
    centered(d, (540, 592), now.strftime("%A, %d %B %Y"), PALE, font(32))

    reference_day = data["as_of"].date() == now.date()
    label = "LATEST MARKET REFERENCE" if not reference_day else "TODAY'S MARKET REFERENCE"
    centered(d, (540, 663), label, GOLD, font(26, bold=True))
    card(d, 716, "24K", data["prices"]["24k"])
    card(d, 1111, "22K", data["prices"]["22k"])

    timestamp = data["as_of"].strftime("%d %b %Y · %I:%M %p")
    centered(d, (540, 1543), f"Rate last updated: {timestamp} (SL time)", PALE,
             font(27))
    d.line((132, 1601, 948, 1601), fill=(98, 83, 52), width=2)
    centered(d, (540, 1661), "INDICATIVE MARKET PRICES ONLY", GOLD,
             font(30, bold=True))
    centered(d, (540, 1715), "Not a jewellery shop's selling-price quote.",
             WHITE, font(27))
    centered(d, (540, 1754), "Making charges, taxes and margins may apply.",
             MUTED, font(24))
    centered(d, (540, 1837), f"Source: {SOURCE_NAME}", MUTED, font(24))

    if demo:
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        layer = ImageDraw.Draw(overlay)
        layer.rounded_rectangle((150, 870, 930, 963), radius=12,
                                fill=(152, 0, 0, 228))
        centered(layer, (540, 917), "DEMO ONLY — NOT LIVE PRICES", (255,255,255,255),
                 font(33, bold=True))
        layer.rounded_rectangle((150, 1264, 930, 1357), radius=12,
                                fill=(152, 0, 0, 228))
        centered(layer, (540, 1310), "DEMO ONLY — NOT LIVE PRICES", (255,255,255,255),
                 font(33, bold=True))
        image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Render clearly labelled sample values; never publish as live")
    parser.add_argument("--shop", default=os.getenv("SHOP_NAME", "ELEGANCE"))
    parser.add_argument("--subtitle", default=os.getenv("SHOP_SUBTITLE", "GEM & JEWELLERS"))
    parser.add_argument("--tagline", default=os.getenv("SHOP_TAGLINE", "Timeless Beauty, enduring Gold"))
    parser.add_argument("--logo", default=os.getenv("SHOP_LOGO", "assets/logo.png"))
    args = parser.parse_args()
    now, data = get_rates(args.demo)
    logo_file = ROOT / args.logo if not Path(args.logo).is_absolute() else Path(args.logo)
    image = render(now, data, args.demo, args.shop, args.subtitle, args.tagline, logo_file)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT / ("sample.png" if args.demo else "today.png"), optimize=True)
    if not args.demo:
        metadata = {
            "generated_at": now.isoformat(),
            "source": SOURCE_NAME,
            "source_url": SOURCE_API,
            "price_as_of": data["as_of"].isoformat(),
            "currency": "LKR",
            "type": "indicative_market_reference_not_retail_quote",
            "prices": data["prices"],
        }
        (OUTPUT / "today.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {'demo' if args.demo else 'live'} image to {OUTPUT}")


if __name__ == "__main__":
    main()
