"""
Synthetic data generator for Atlas Global Logistics, a fictional
mid-size third-party logistics (3PL) operator.

Simulates roughly 3.5 years (January 2023 to August 2026) of shipment
activity across a warehouse network spanning four regions, with
realistic seasonality (a November-December peak, a February lull),
weather-driven delay spikes in winter months for cold-climate lanes,
and carrier-mode cost/speed tradeoffs (air is fast and expensive,
ocean is slow and cheap).

Writes raw CSVs to dbt_project/seeds/, mirroring the pattern used in
the workforce-analytics-meridian sibling project: a Python generator
feeding dbt seeds, rather than hand-written fixtures.

Run:
    python data_generator/generate_logistics_data.py
"""

import os
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd
from faker import Faker

SEED = 2026
random.seed(SEED)
np.random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "dbt_project", "seeds")
os.makedirs(OUT_DIR, exist_ok=True)

START_DATE = date(2023, 1, 1)
END_DATE = date(2026, 8, 31)

# ---------------------------------------------------------------------------
# Warehouses: the origin network
# ---------------------------------------------------------------------------
WAREHOUSES = [
    ("WH-01", "Atlanta DC", "Atlanta", "United States", "North America", 33.7490, -84.3880, 42000),
    ("WH-02", "Dallas DC", "Dallas", "United States", "North America", 32.7767, -96.7970, 38000),
    ("WH-03", "Toronto DC", "Toronto", "Canada", "North America", 43.6532, -79.3832, 26000),
    ("WH-04", "Rotterdam DC", "Rotterdam", "Netherlands", "Europe", 51.9244, 4.4777, 47000),
    ("WH-05", "Hamburg DC", "Hamburg", "Germany", "Europe", 53.5511, 9.9937, 39000),
    ("WH-06", "Lyon DC", "Lyon", "France", "Europe", 45.7640, 4.8357, 24000),
    ("WH-07", "Warsaw DC", "Warsaw", "Poland", "Europe", 52.2297, 21.0122, 21000),
    ("WH-08", "Singapore DC", "Singapore", "Singapore", "Asia Pacific", 1.3521, 103.8198, 45000),
    ("WH-09", "Shanghai DC", "Shanghai", "China", "Asia Pacific", 31.2304, 121.4737, 51000),
    ("WH-10", "Sydney DC", "Sydney", "Australia", "Asia Pacific", -33.8688, 151.2093, 22000),
    ("WH-11", "Dubai DC", "Dubai", "United Arab Emirates", "Middle East", 25.2048, 55.2708, 30000),
    ("WH-12", "Jeddah DC", "Jeddah", "Saudi Arabia", "Middle East", 21.4858, 39.1925, 18000),
]

warehouses_df = pd.DataFrame(
    WAREHOUSES,
    columns=["warehouse_id", "warehouse_name", "city", "country", "region", "lat", "lon", "capacity_units"],
)

# ---------------------------------------------------------------------------
# Destinations: delivery hubs shipments are sent to
# ---------------------------------------------------------------------------
DESTINATIONS = [
    ("DST-01", "New York", "United States", "North America", 40.7128, -74.0060),
    ("DST-02", "Chicago", "United States", "North America", 41.8781, -87.6298),
    ("DST-03", "Los Angeles", "United States", "North America", 34.0522, -118.2437),
    ("DST-04", "Montreal", "Canada", "North America", 45.5019, -73.5674),
    ("DST-05", "Mexico City", "Mexico", "North America", 19.4326, -99.1332),
    ("DST-06", "London", "United Kingdom", "Europe", 51.5074, -0.1278),
    ("DST-07", "Paris", "France", "Europe", 48.8566, 2.3522),
    ("DST-08", "Berlin", "Germany", "Europe", 52.5200, 13.4050),
    ("DST-09", "Madrid", "Spain", "Europe", 40.4168, -3.7038),
    ("DST-10", "Milan", "Italy", "Europe", 45.4642, 9.1900),
    ("DST-11", "Stockholm", "Sweden", "Europe", 59.3293, 18.0686),
    ("DST-12", "Tokyo", "Japan", "Asia Pacific", 35.6762, 139.6503),
    ("DST-13", "Seoul", "South Korea", "Asia Pacific", 37.5665, 126.9780),
    ("DST-14", "Mumbai", "India", "Asia Pacific", 19.0760, 72.8777),
    ("DST-15", "Jakarta", "Indonesia", "Asia Pacific", -6.2088, 106.8456),
    ("DST-16", "Melbourne", "Australia", "Asia Pacific", -37.8136, 144.9631),
    ("DST-17", "Riyadh", "Saudi Arabia", "Middle East", 24.7136, 46.6753),
    ("DST-18", "Abu Dhabi", "United Arab Emirates", "Middle East", 24.4539, 54.3773),
    ("DST-19", "Doha", "Qatar", "Middle East", 25.2854, 51.5310),
    ("DST-20", "Cairo", "Egypt", "Middle East", 30.0444, 31.2357),
]

destinations_df = pd.DataFrame(
    DESTINATIONS, columns=["destination_id", "city", "country", "region", "lat", "lon"]
)

# ---------------------------------------------------------------------------
# Carriers: mode determines the cost/speed/reliability tradeoff
# ---------------------------------------------------------------------------
CARRIERS = [
    # carrier_id, name, mode, cost_per_km, speed_kmph, base_on_time_rate
    ("CAR-01", "Meridian Freight Lines", "Truck", 0.85, 70, 0.90),
    ("CAR-02", "Continental Trucking Co.", "Truck", 0.78, 65, 0.87),
    ("CAR-03", "Ironrail Cargo", "Rail", 0.35, 55, 0.83),
    ("CAR-04", "SkyBridge Air Cargo", "Air", 3.20, 780, 0.94),
    ("CAR-05", "Polaris Airfreight", "Air", 3.55, 800, 0.92),
    ("CAR-06", "Blue Horizon Ocean Lines", "Ocean", 0.09, 32, 0.78),
    ("CAR-07", "Pacific Rim Shipping", "Ocean", 0.10, 30, 0.75),
]

carriers_df = pd.DataFrame(
    CARRIERS, columns=["carrier_id", "carrier_name", "mode", "cost_per_km", "speed_kmph", "base_on_time_rate"]
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return r * 2 * np.arcsin(np.sqrt(a))


def month_seasonality(d: date) -> float:
    """Relative shipment volume multiplier by month: Nov/Dec peak, Feb lull."""
    return {
        1: 0.85, 2: 0.75, 3: 0.90, 4: 0.95, 5: 1.00, 6: 1.00,
        7: 0.95, 8: 0.90, 9: 1.00, 10: 1.10, 11: 1.35, 12: 1.45,
    }[d.month]


def is_winter_northern(d: date) -> bool:
    return d.month in (12, 1, 2)


# reasonable per-mode plausible carriers, so an ocean carrier isn't hauling
# a same-region short-haul lane and a truck isn't crossing an ocean
MODE_MAX_DISTANCE_KM = {"Truck": 4500, "Rail": 6000, "Air": 20000, "Ocean": 20000}
MODE_MIN_DISTANCE_KM = {"Truck": 0, "Rail": 0, "Air": 0, "Ocean": 3000}

# ---------------------------------------------------------------------------
# Shipments
# ---------------------------------------------------------------------------
shipment_rows = []
shipment_id_counter = 1

# precompute distance for every warehouse/destination pair once
dist_lookup = {}
for _, w in warehouses_df.iterrows():
    for _, d in destinations_df.iterrows():
        dist_lookup[(w.warehouse_id, d.destination_id)] = haversine_km(w.lat, w.lon, d.lat, d.lon)

all_days = pd.date_range(START_DATE, END_DATE, freq="D")

for day in all_days:
    d = day.date()
    seasonal_mult = month_seasonality(d)
    base_daily_shipments = 14  # roughly ~18k shipments over the full window
    n_shipments_today = np.random.poisson(base_daily_shipments * seasonal_mult)

    for _ in range(n_shipments_today):
        warehouse = warehouses_df.sample(1, weights=warehouses_df["capacity_units"]).iloc[0]

        # prefer destinations in the same or a neighboring region (more realistic
        # freight lanes) but allow some long-haul intercontinental shipments
        if random.random() < 0.65:
            same_region_dest = destinations_df[destinations_df["region"] == warehouse.region]
            dest_pool = same_region_dest if len(same_region_dest) else destinations_df
        else:
            dest_pool = destinations_df
        destination = dest_pool.sample(1).iloc[0]

        distance_km = dist_lookup[(warehouse.warehouse_id, destination.destination_id)]

        eligible_carriers = carriers_df[
            (carriers_df["mode"].map(MODE_MIN_DISTANCE_KM) <= distance_km)
            & (distance_km <= carriers_df["mode"].map(MODE_MAX_DISTANCE_KM))
        ]
        if eligible_carriers.empty:
            eligible_carriers = carriers_df
        carrier = eligible_carriers.sample(1).iloc[0]

        weight_kg = round(np.random.lognormal(mean=6.0, sigma=1.0), 1)  # skewed, mostly small-mid parcels/pallets
        freight_cost = round(distance_km * carrier.cost_per_km * (weight_kg / 500 + 0.4), 2)

        order_date = d
        handling_days = random.choice([0, 0, 1, 1, 2])
        planned_ship_date = order_date + timedelta(days=handling_days)
        transit_days_planned = max(1, round(distance_km / carrier.speed_kmph / 24) + random.choice([0, 1]))
        planned_delivery_date = planned_ship_date + timedelta(days=transit_days_planned)

        # delay model: base carrier reliability, worse in winter for ocean/truck,
        # worse in peak season across the board (congestion)
        on_time_prob = carrier.base_on_time_rate
        if seasonal_mult > 1.2:
            on_time_prob -= 0.08
        if is_winter_northern(d) and carrier.mode in ("Truck", "Ocean") and warehouse.region in (
            "North America", "Europe",
        ):
            on_time_prob -= 0.10
        on_time_prob = max(0.45, min(0.98, on_time_prob))

        roll = random.random()
        if roll < 0.01:
            status = "Cancelled"
            actual_ship_date = pd.NaT
            actual_delivery_date = pd.NaT
            on_time_flag = None
        elif roll < 0.015:
            status = "In Transit"
            actual_ship_date = planned_ship_date
            actual_delivery_date = pd.NaT
            on_time_flag = None
        else:
            status = "Delivered"
            actual_ship_date = planned_ship_date + timedelta(days=random.choice([0, 0, 0, 1]))
            if random.random() < on_time_prob:
                delay_days = 0
            else:
                delay_days = int(np.random.gamma(shape=2.0, scale=2.0)) + 1
            actual_delivery_date = planned_delivery_date + timedelta(days=delay_days)
            on_time_flag = delay_days == 0

        shipment_rows.append(
            {
                "shipment_id": f"SHP-{shipment_id_counter:06d}",
                "warehouse_id": warehouse.warehouse_id,
                "destination_id": destination.destination_id,
                "carrier_id": carrier.carrier_id,
                "order_date": order_date,
                "planned_ship_date": planned_ship_date,
                "actual_ship_date": actual_ship_date,
                "planned_delivery_date": planned_delivery_date,
                "actual_delivery_date": actual_delivery_date,
                "distance_km": round(distance_km, 1),
                "weight_kg": weight_kg,
                "freight_cost": freight_cost,
                "status": status,
                "on_time_flag": on_time_flag,
            }
        )
        shipment_id_counter += 1

shipments_df = pd.DataFrame(shipment_rows)

# ---------------------------------------------------------------------------
# Returns: a subset of delivered shipments
# ---------------------------------------------------------------------------
RETURN_REASONS = ["Damaged in transit", "Wrong item", "Customer changed mind", "Late delivery refusal", "Quality issue"]
delivered = shipments_df[shipments_df["status"] == "Delivered"].copy()
n_returns = int(len(delivered) * 0.045)
returned_shipments = delivered.sample(n=n_returns, random_state=SEED)

return_rows = []
for _, s in returned_shipments.iterrows():
    return_date = pd.to_datetime(s.actual_delivery_date) + timedelta(days=random.randint(1, 14))
    return_rows.append(
        {
            "return_id": f"RET-{len(return_rows) + 1:05d}",
            "shipment_id": s.shipment_id,
            "return_date": return_date.date(),
            "return_reason": random.choice(RETURN_REASONS),
            "refund_amount": round(s.freight_cost * random.uniform(0.8, 1.3), 2),
        }
    )
returns_df = pd.DataFrame(return_rows)

# ---------------------------------------------------------------------------
# Inventory snapshots: monthly per warehouse per product category
# ---------------------------------------------------------------------------
CATEGORIES = ["Electronics", "Apparel", "Home Goods", "Industrial Parts", "Perishables"]
inventory_rows = []
months = pd.date_range(START_DATE, END_DATE, freq="MS")
for month in months:
    for _, w in warehouses_df.iterrows():
        for category in CATEGORIES:
            base_stock = np.random.randint(500, 5000)
            seasonal_draw = month_seasonality(month.date())
            stock_units = max(0, int(base_stock / seasonal_draw + np.random.normal(0, 150)))
            reorder_point = int(base_stock * 0.25)
            stockout_flag = stock_units < reorder_point * 0.3
            inventory_rows.append(
                {
                    "warehouse_id": w.warehouse_id,
                    "month": month.date(),
                    "category": category,
                    "stock_units": stock_units,
                    "reorder_point": reorder_point,
                    "stockout_flag": stockout_flag,
                }
            )
inventory_df = pd.DataFrame(inventory_rows)

# ---------------------------------------------------------------------------
# Write seeds
# ---------------------------------------------------------------------------
warehouses_df.to_csv(os.path.join(OUT_DIR, "raw_warehouses.csv"), index=False)
destinations_df.to_csv(os.path.join(OUT_DIR, "raw_destinations.csv"), index=False)
carriers_df.to_csv(os.path.join(OUT_DIR, "raw_carriers.csv"), index=False)
shipments_df.to_csv(os.path.join(OUT_DIR, "raw_shipments.csv"), index=False)
returns_df.to_csv(os.path.join(OUT_DIR, "raw_returns.csv"), index=False)
inventory_df.to_csv(os.path.join(OUT_DIR, "raw_inventory_snapshots.csv"), index=False)

print(f"warehouses: {len(warehouses_df)}")
print(f"destinations: {len(destinations_df)}")
print(f"carriers: {len(carriers_df)}")
print(f"shipments: {len(shipments_df)}")
print(f"returns: {len(returns_df)}")
print(f"inventory snapshots: {len(inventory_df)}")
