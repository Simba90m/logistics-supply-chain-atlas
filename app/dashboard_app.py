"""
Streamlit companion app for the Atlas Global Logistics supply chain
dataset. This is a lightweight, code-first preview of the marts that
also power the Tableau Public dashboard: useful for exploring the data
quickly, or for anyone reviewing the repo without opening Tableau.

Run locally:
    streamlit run app/dashboard_app.py

Reads the mart tables from the parquet snapshots in app/data/, so the
app needs no local dbt build to run, deployable as-is on Streamlit
Community Cloud. Those snapshots are regenerated from the dbt-built
DuckDB file, see README for the export step.
"""

import os

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

st.set_page_config(page_title="Atlas Global Logistics", layout="wide")


@st.cache_data
def load_data():
    shipment_volume = pd.read_parquet(os.path.join(DATA_DIR, "shipment_volume.parquet"))
    carrier_performance = pd.read_parquet(os.path.join(DATA_DIR, "carrier_performance.parquet"))
    warehouse_geo = pd.read_parquet(os.path.join(DATA_DIR, "warehouse_geo.parquet"))
    ontime_by_warehouse_year = pd.read_parquet(os.path.join(DATA_DIR, "ontime_by_warehouse_year.parquet"))
    inventory_health = pd.read_parquet(os.path.join(DATA_DIR, "inventory_health.parquet"))
    return shipment_volume, carrier_performance, warehouse_geo, ontime_by_warehouse_year, inventory_health


shipment_volume, carrier_performance, warehouse_geo, ontime_by_warehouse_year, inventory_health = load_data()

st.title("Atlas Global Logistics: Supply Chain Overview")
st.caption(
    "Synthetic logistics dataset, transformed with dbt, explored here in Streamlit and "
    "presented as a full dashboard with a live warehouse map on Tableau Public."
)

total_shipments = shipment_volume["shipment_count"].sum()
avg_on_time = (shipment_volume["on_time_count"].sum() / shipment_volume["delivered_count"].sum())
total_cost = shipment_volume["total_freight_cost"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total shipments", f"{total_shipments:,.0f}")
col2.metric("Overall on-time rate", f"{avg_on_time:.1%}")
col3.metric("Total freight cost", f"€{total_cost:,.0f}")

st.subheader("Warehouse network, by on-time delivery rate")
fig_map = px.scatter_geo(
    warehouse_geo,
    lat="lat",
    lon="lon",
    size="shipment_count",
    color="on_time_rate",
    color_continuous_scale="RdYlGn",
    hover_name="warehouse_name",
    hover_data={"city": True, "country": True, "shipment_count": True, "on_time_rate": ":.1%", "lat": False, "lon": False},
    projection="natural earth",
)
fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Shipment volume over time, by region")
volume_by_region = shipment_volume.groupby(["month_start", "region"], as_index=False)["shipment_count"].sum()
fig_volume = px.area(
    volume_by_region,
    x="month_start",
    y="shipment_count",
    color="region",
    title="Monthly shipment volume, seeded January 2023",
)
st.plotly_chart(fig_volume, use_container_width=True)

col4, col5 = st.columns(2)

with col4:
    st.subheader("Carrier performance: cost vs. reliability")
    carrier_avg = carrier_performance.groupby(["carrier_name", "mode"], as_index=False).agg(
        avg_cost_per_km=("avg_cost_per_km", "mean"),
        on_time_rate=("on_time_rate", "mean"),
        shipment_count=("shipment_count", "sum"),
    )
    fig_carrier = px.scatter(
        carrier_avg,
        x="avg_cost_per_km",
        y="on_time_rate",
        color="mode",
        size="shipment_count",
        hover_name="carrier_name",
        labels={"avg_cost_per_km": "Avg cost per km (EUR)", "on_time_rate": "On-time rate"},
    )
    fig_carrier.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_carrier, use_container_width=True)

with col5:
    st.subheader("On-time rate by warehouse and year")
    pivot = ontime_by_warehouse_year.pivot(index="warehouse_name", columns="year", values="on_time_rate")
    fig_heat = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn",
        aspect="auto",
        labels=dict(color="On-time rate"),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

st.subheader("Inventory stockout rate by category")
stockout_by_category = inventory_health.groupby("category", as_index=False)["stockout_rate"].mean()
fig_stockout = px.bar(
    stockout_by_category.sort_values("stockout_rate"),
    x="category",
    y="stockout_rate",
    labels={"stockout_rate": "Avg. stockout rate", "category": "Product category"},
)
fig_stockout.update_yaxes(tickformat=".0%")
st.plotly_chart(fig_stockout, use_container_width=True)

st.caption(
    "Data is fully synthetic, generated for portfolio purposes. "
    "See data_generator/generate_logistics_data.py for the generation logic and "
    "dbt_project/ for the staging and mart models."
)
