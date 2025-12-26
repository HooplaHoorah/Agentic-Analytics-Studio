# Tableau embed failures: what’s actually happening

When the iframe points at the Tableau Cloud root (or a login/home redirect), Tableau returns:
`X-Frame-Options: SAMEORIGIN`

That header blocks framing from `http://localhost:*`, so the viz panel goes blank.

Fix:
- Always embed the view URL:
  `https://<pod>.online.tableau.com/t/<site>/views/<workbook>/<view>?:showVizHome=no&:embed=yes`

And if the browser is not authenticated, the view URL can redirect to login.
For demos: open Tableau Cloud in a tab, sign in, refresh the demo.
