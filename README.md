# Sri Lanka Daily Gold-Price Image — iPhone + WhatsApp Business

Generates a premium Elegance Gem & Jewellers vertical (1080×1920) 22K / 24K gold-price picture using
**Devi Jewellers, Colombo** reference prices, including per-gram and per-8-gram
(pawn) values, a visible source date, and a clear disclaimer. It runs daily on GitHub Actions.

**What it does not do:** automatically post to WhatsApp Status. WhatsApp does
not provide a supported Status-publishing API. Your friend will post from their
iPhone's WhatsApp Business app after the picture is automatically saved to Photos.

## Rate source and safeguards

- Official Devi Jewellers source: https://devijewellers.lk/gold-rate/
- Automated retrieval from **LankaRates.com** public comparison page:
  https://lankarates.com/gold-rates. We use only the rows explicitly attributed
  to Devi Jewellers and pointing at its official page. The direct Devi website
  returned an automated-traffic challenge during setup, so no attempt is made
  to bypass that protection. This is **not** a Devi official API.
- Devi's 24K and 22K displayed prices (e.g. Rs. 366,000 and Rs. 336,700 on
  7 Nov 2026) are **per 8 grams (one pawn)** despite an inconsistent `/g`
  label on parts of the Devi site. We correctly divide each by 8 for per-gram
  prices; this matches LankaRates' units.
- Validate institution, source URL, currency, purity, value and publication
  date; reject rates older than 72 hours. For weekends or holidays, older
  valid reference prices retain their actual source date.
- If the feed is unavailable, inconsistent or too old, **the job fails rather
  than generating an apparently fresh but misleading new image**. The
  previously published image remains unchanged, so review its date before posting.
- The values represent **Devi-published reference rates**, not Elegance's own
  retail selling-price quote. Confirm suitability and data-reuse permission
  with the relevant provider before using at commercial scale.

## Try the design first

```bash
python3 -m pip install -r requirements.txt
python3 generate.py --demo --shop "ELEGANCE"
```

The test file is `docs/sample.png`, prominently watermarked as a demo with
invented prices. Never publish it to customers. To generate from the real API:

```bash
python3 generate.py --shop "ELEGANCE"
```

This produces `docs/today.png` and `docs/today.json`. The source must be
available to your computer. The supplied Elegance mark is at `assets/logo.png`.
To change branding later, use the `--shop`, `--subtitle`, and `--tagline`
arguments or set the corresponding `SHOP_NAME`, `SHOP_SUBTITLE`, and
`SHOP_TAGLINE` environment variables. The text-only fallback works without a logo.

To run the data validation tests:

```bash
python3 -m unittest discover -s tests -v
```

## Set up automated image creation on GitHub

1. This project is uploaded to **naflan222/Goldprice** (public).
2. The workflow already uses **Elegance Gem & Jewellers** branding and the
   matching transparent logo. Change `SHOP_NAME` only if branding changes.
3. Open GitHub repository **Settings → Actions → General**. Allow actions and
   enable workflow read/write permissions if required for the commit step.
4. In the repository's **Actions** tab, run **Generate daily gold-rate Status
   image → Run workflow** once. Check that `docs/today.png` is updated. A
   failure means a data or permission issue; don't silently substitute a price.
5. Use this stable public image URL on the iPhone (no GitHub Pages setup needed):

   `https://raw.githubusercontent.com/naflan222/Goldprice/main/docs/today.png`

6. The scheduled job targets **8:35 AM Sri Lanka time** (`03:05 UTC`). GitHub's schedule may
   occasionally be delayed; if the image hasn't updated, the old timestamp
   remains clearly visible. **Don't post an image if its rate date is too old**.

## Set up automatic saving to Photos on your friend's iPhone

Your friend should do these steps with their own phone:

1. Open **Shortcuts → Automation → + → Time of Day**.
2. Choose **9:00 AM**, **Daily**, and **Run Immediately** (if available).
3. Add a **URL** action, entering the publicly accessible `today.png` URL
   from Step 6 above.
4. Add **Get Contents of URL** (method **GET**).
5. Add **Save to Photo Album**; pass the image result from the previous action.
   Choose the desired album (e.g. create **Daily Gold Rates** in Photos).
6. Add **Show Notification**, with text like "Gold-rate image saved. Open
   WhatsApp Business → Updates → Add Status to post it."
7. Save and run the shortcut manually once to grant Photos and network
   permissions. Verify the correct photo appears in Photos.

If Apple's Actions UI differs on the installed iOS version, search each
action by its name in the Shortcuts action picker. A network failure can
prevent saving; set a clear notification and check the first few runs.

## Final daily step in WhatsApp Business

Your friend opens **WhatsApp Business → Updates → Add Status**, chooses the
latest gold-rate photo from Photos, checks the price/date/audience, and taps
**Send**. This last step cannot be guaranteed unattended by Apple Shortcuts
or the official WhatsApp Business API.

## Security

- Do not share your friend's WhatsApp password, SMS codes or linked-device QR.
- They remain the account owner and approve any permissions themselves.
- Do not install unofficial modified WhatsApp apps for unattended posting.
- Keep your source metadata and source attribution on the image.
