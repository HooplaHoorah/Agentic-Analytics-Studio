# Tableau Workbook / Sheet Info Needed (for v22)

To finalize the “Public-by-default” demo, we need the **Tableau Public** embed URL(s) for your AAS dashboard(s).

## 1) Primary (minimum required)
Provide **one** Tableau Public embed URL that shows the AAS “Overview” dashboard:

- Tableau Public “Share” URL (copy from Share dialog):
  - [PASTE HERE]
- Workbook name:
  - [PASTE HERE]
- Sheet / Dashboard name shown in the URL path:
  - [PASTE HERE]

**Preferred format (embed URL):**
- `https://public.tableau.com/views/<WORKBOOK>/<SHEET>?:showVizHome=no&:embed=true`

If you only give the Share URL, we can usually derive the embed URL.

## 2) Optional (recommended): multiple sheets mapped to AAS context
AAS may call `loadTableauView(preferredName)` with names like:
- `overview`
- `pipeline`
- `risk`
- other view names returned by your API (`data.visual_context.view_name`, action metadata, etc.)

If you have multiple Public sheets, list them like this:

| AAS preferredName key | Workbook | Sheet/Dashboard | Tableau Public embed URL |
|---|---|---|---|
| overview |  |  |  |
| pipeline |  |  |  |
| risk |  |  |  |

These will populate `TABLEAU_PUBLIC_VIEWS = { ... }`.

## 3) Optional: Cloud mode support (dev only)
If you want `?tableau=cloud` to work for **your** environment too, share:
- Tableau Cloud site/pod (e.g., `10ax.online.tableau.com`)
- Whether you expect iframe embedding (usually blocked) or prefer **open-in-new-tab**
- The view names returned by `GET /tableau/views` (names + embed_url domains)

## How to get the Tableau Public URL quickly
1. Open the workbook on Tableau Public
2. Click **Share**
3. Copy the link
4. Paste it above

That’s it — once we have these, we’ll swap out the Superstore placeholder with your AAS workbook/sheet.
