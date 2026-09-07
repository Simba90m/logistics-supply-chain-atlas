# Supply Chain Analytics: Atlas Global Logistics

An end to end logistics and supply chain analytics project built for
a fictional mid-size 3PL operator, Atlas Global Logistics. It covers
the full pipeline from raw data generation through transformation to
a published dashboard with a real warehouse map, plus a lightweight
app for exploring the data without opening Tableau.

Live dashboard: **[link added once published to Tableau Public]**
Live app: **[link added once deployed to Streamlit Community Cloud]**

## Why this project

Before data analytics, I spent time as an onsite recruitment
supervisor staffing a high-volume logistics operation in Bremen:
watching trucks leave on schedule or not, hearing which carriers
customers complained about, seeing a warehouse scramble when a
shipment landed late during peak season. This project rebuilds that
world from the data side: a warehouse network, a carrier mix with
real cost and reliability tradeoffs, and the questions a supply chain
manager actually asks, which lanes are slow, which carriers are worth
the premium, where is inventory running thin, mapped and charted the
way I wish I'd had access to back then.

## Architecture

```
generate_logistics_data.py (Python + Faker/NumPy)
        |
        v
dbt seeds (raw CSVs -> DuckDB "raw" schema)
        |
        v
dbt staging models (clean, type, derive one row per grain)
        |
        v
dbt mart models (shipment volume, carrier performance, warehouse
                  geography, on-time rate, inventory health)
        |
        +--> Streamlit app (quick exploration, in this repo)
        |
        +--> Tableau Public dashboard (the polished, shareable version,
             including a live map of the warehouse network)
```

## The dataset

Fully synthetic, generated with [Faker](https://faker.readthedocs.io/)
and NumPy, seeded for reproducibility. It simulates roughly 18,600
shipments over a 3.5 year window (January 2023 to August 2026) moving
from 12 distribution centers across four regions (North America,
Europe, Asia Pacific, Middle East) to 20 destination cities worldwide,
carried by 7 carriers across four transport modes (Truck, Rail, Air,
Ocean). Seasonality (a November-December peak, a February lull),
winter-weather delay spikes on truck and ocean lanes, and a realistic
cost/speed/reliability tradeoff per mode (air is fast, reliable, and
expensive, ocean is slow, less reliable, and cheap) are built into the
simulation logic rather than randomly scattered.

Raw tables (`data_generator/generate_logistics_data.py` writes these
to `dbt_project/seeds/`):

| Table | Grain | What it captures |
|---|---|---|
| `raw_warehouses` | one row per distribution center | location (with lat/lon), region, capacity |
| `raw_destinations` | one row per delivery hub | location (with lat/lon), region |
| `raw_carriers` | one row per carrier | transport mode, cost per km, speed, base reliability |
| `raw_shipments` | one row per shipment | origin, destination, carrier, planned vs actual ship/delivery dates, cost, weight, status |
| `raw_returns` | one row per returned shipment | reason, refund amount |
| `raw_inventory_snapshots` | one row per warehouse/category/month | stock level, reorder point, stockout flag |

## The dbt project

`dbt_project/` follows the same staging-to-marts pattern as my
[workforce-analytics-meridian](https://github.com/Simba90m/workforce-analytics-meridian)
repo: a thin staging layer that cleans and types the raw sources one
to one, then mart models that do the actual joining and aggregation.

Staging models (`models/staging/`): one model per raw source, each
adding light cleanup (normalized boolean flags, derived transit days
and delay days) without changing the grain.

Mart models (`models/marts/`):

- `mart_shipment_volume_monthly`: monthly shipment count, weight,
  freight cost, and on-time rate by warehouse and region.
- `mart_carrier_performance`: on-time rate, average cost per km, and
  planned vs. actual transit days by carrier and year.
- `mart_warehouse_geo`: one row per warehouse with lat/lon, shipment
  volume, average cost, and on-time rate, built for a real map.
- `mart_ontime_by_warehouse_year`: on-time rate by warehouse and year,
  for a heatmap view.
- `mart_inventory_health`: average stock level and stockout rate by
  warehouse, category, and month.

Data quality: 34 dbt tests (`not_null`, `unique`, `relationships`,
`accepted_values`) across the staging and mart layers, plus a source
freshness check, all passing (`dbt test`).

DuckDB is the warehouse here instead of a hosted Postgres, so the
whole project runs locally with no cloud account needed to reproduce
it.

## The apps

**Streamlit** (`app/dashboard_app.py`): a quick, code-first look at
the marts, a warehouse map colored by on-time rate, shipment volume
trend by region, a carrier cost-vs-reliability scatter, an on-time
heatmap by warehouse and year, and inventory stockout rates by
category. Useful for reviewing the data without opening Tableau. Live
at **[link added once deployed]**.

**Tableau Public**: the polished, presentation-ready version of the
same marts, built for a non-technical audience, a real geographic map
of the warehouse network, carrier performance, and inventory health.
Link goes here once published.

## Running it locally

```bash
git clone https://github.com/Simba90m/logistics-supply-chain-atlas.git
cd logistics-supply-chain-atlas
pip install -r requirements.txt

# 1. generate the raw data
python data_generator/generate_logistics_data.py

# 2. build the warehouse
cd dbt_project
dbt seed
dbt run
dbt test

# 3. explore it
cd ..
streamlit run app/dashboard_app.py
```

To refresh the parquet snapshots the deployed Streamlit app reads from
(after regenerating data or rebuilding the marts):

```bash
python -c "
import duckdb
con = duckdb.connect('dbt_project/logistics_supply_chain.duckdb', read_only=True)
tables = {
    'shipment_volume': 'marts.mart_shipment_volume_monthly',
    'carrier_performance': 'marts.mart_carrier_performance',
    'warehouse_geo': 'marts.mart_warehouse_geo',
    'ontime_by_warehouse_year': 'marts.mart_ontime_by_warehouse_year',
    'inventory_health': 'marts.mart_inventory_health',
}
for name, tbl in tables.items():
    con.execute(f'select * from {tbl}').df().to_parquet(f'app/data/{name}.parquet', index=False)
con.close()
"
```

## Tech stack

Python (Faker and NumPy for data generation, pandas/Streamlit/Plotly
for the exploration app), SQL, dbt (staging/marts modeling, testing,
source freshness), DuckDB, Tableau Public.

## Repo structure

```
data_generator/
    generate_logistics_data.py   # writes raw CSVs to dbt_project/seeds/
dbt_project/
    dbt_project.yml
    macros/generate_schema_name.sql
    seeds/                        # raw_*.csv (generated, not hand-written)
    models/
        staging/                  # stg_*.sql + sources.yml + schema.yml
        marts/                    # mart_*.sql + schema.yml
app/
    dashboard_app.py              # Streamlit companion app
    data/                         # parquet snapshots the app reads from
requirements.txt
README.md
```
