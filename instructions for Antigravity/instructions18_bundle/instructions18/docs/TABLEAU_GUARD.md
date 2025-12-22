# How the Tableau Guard works (v18)

Because Tableau is cross-origin, the demo cannot inspect iframe contents.
So the guard uses time-based detection:

- When the iframe `src` changes, we assume a new load started.
- We wait up to 8 seconds for the iframe `load` event.
- If `load` fires: hide banner.
- If the timer expires: show banner with a recovery path.

Additionally, if the iframe `src` contains login indicators:
- `/signin`
- `/login`
- `auth`
- `sso`
the banner shows immediately.
