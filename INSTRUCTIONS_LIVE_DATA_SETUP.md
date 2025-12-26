# Live Data Setup Guide (Option 3) - COMPLETED

**Status**: 
- Codebase: UPGRADED
- Database: PROVISIONED (vultr-prod-...)
- Tableau App: CREATED (AAS Demo)

## 1. Credentials (AUTO-GENERATED)

I have provisioned the resources for you. Use these details to configure your environment.

### Database (Vultr Postgres)
- **Host**: `vultr-prod-38e84cab-c270-41d6-abee-23155df25ebd-vultr-prod-795c.vultrdb.com`
- **Port**: `16751`
- **User**: `vultradmin`
- **Pass**: `AVNS_1Z4yRiK79Yz3CDRzoFH`
- **DB**: `defaultdb`

**Connection String**:
```
postgresql://vultradmin:AVNS_1Z4yRiK79Yz3CDRzoFH@vultr-prod-38e84cab-c270-41d6-abee-23155df25ebd-vultr-prod-795c.vultrdb.com:16751/defaultdb
```

### Tableau Connected App (AAS Demo)
- **Client ID**: `21476a81-0a98-4df1-93fb-cae88dd0dfee`
- **Secret ID**: `e8d6085d-45eb-4b3f-952b-3dc58a3f346f`
- **Secret Value**: `bwZU10fr4+O/0lDIZtkqPqGMGaKw3TqU+dlPTPcpWXA=`
- **Username**: `Richard Morgan` (or your Tableau email)

## 2. Configure Environment

Update your `.env` (or Vultr App Environment Variables) with these exact values:

```dotenv
DATABASE_URL="postgresql://vultradmin:AVNS_1Z4yRiK79Yz3CDRzoFH@vultr-prod-38e84cab-c270-41d6-abee-23155df25ebd-vultr-prod-795c.vultrdb.com:16751/defaultdb"

TABLEAU_CONNECTED_APP_CLIENT_ID="21476a81-0a98-4df1-93fb-cae88dd0dfee"
TABLEAU_CONNECTED_APP_SECRET_ID="e8d6085d-45eb-4b3f-952b-3dc58a3f346f"
TABLEAU_CONNECTED_APP_SECRET_VALUE="bwZU10fr4+O/0lDIZtkqPqGMGaKw3TqU+dlPTPcpWXA="
TABLEAU_CONNECTED_APP_USERNAME="richard.morgan@example.com"  # REPLACE with your actual Tableau login email
```

## 3. Seed Data (Do this once DNS propagates)
I attempted to seed the data, but the new database DNS was not yet resolving. 
Wait 5-10 minutes, then run:

```powershell
python scripts/apply_schema.py "$DATABASE_URL"
python scripts/seed_demo_data.py --database-url "$DATABASE_URL" --rows 500
```

## 4. Tableau Cloud Final Step
1. Log into Tableau Cloud.
2. Create a new Workbook connected to the **PostgreSQL** database (use credentials above).
3. Drag `aas_opportunities` and `aas_actions` onto the canvas.
4. Publish the workbook.
5. **IMPORTANT**: Update `TABLEAU_PUBLIC_DEFAULT_URL` in `web/app.js` if you want it to act as the fallback.
