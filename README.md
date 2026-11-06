# Sri Lanka Daily Gold-Price Image — iPhone + WhatsApp Business

Generates a premium Elegance Gem & Jewellers vertical (1080×1920) 22K / 24K gold-price picture, including
per-gram and per-8-gram (pawn) values, a visible source timestamp, and a clear
"indicative market reference" warning. It can run daily on GitHub Actions.

**What it does not do:** automatically post to WhatsApp Status. WhatsApp does
not provide a supported Status-publishing API. Your friend will post from their
iPhone's WhatsApp Business app after the picture is automatically saved to Photos.

## Rate source and safeguards

- JSON API: https://www.goldpricetoday.lk/api/v1/gold-price
- Commercial-use API terms: https://www.goldpricetoday.lk/terms
- API is a third-party *indicative* market reference, **not a retail jewellery quote**.
- Validate currency, values and source timestamps; reject readings older than
  72 hours. In weekends and holidays, an older valid observation is labelled
  "latest" and carries the exact underlying timestamp.
- If the feed is unavailable, invalid or too old, **the job fails rather than
  generating a misleading new image**. The previously published file remains.
- It is your responsibility to check that this source is suitable for the shop.

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

1. Create a repository on your GitHub account; for example `daily-gold-rates`.
   Upload all project files *including* `.github/workflows/daily-gold.yml`.
2. The workflow already uses **Elegance Gem & Jewellers** branding and the
   matching logo. Change `SHOP_NAME` only if the branding changes.
3. Open the repo **Settings → Actions → General**. Allow actions and enable
   workflow read/write permissions if required for the commit step.
4. In **Actions**, run **Generate daily gold-rate Status image → Run workflow**.
   Check that `docs/today.png` appears. A failure means a data or permission
   issue; don't silently substitute another price.
5. In **Settings → Pages**, set **Build and deployment → Deploy from a branch**;
   select your default branch, folder **/docs**, and Save.
6. Your latest image URL is normally:

   `https://YOUR_GITHUB_USERNAME.github.io/YOUR_REPOSITORY/today.png`

   For `naflan222/daily-gold-rates`, it would be
   `https://naflan222.github.io/daily-gold-rates/today.png`
   **only after you create and enable that repo and Pages**.

7. The scheduled job runs at **8:35 AM Sri Lanka time**. GitHub's schedule may
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
