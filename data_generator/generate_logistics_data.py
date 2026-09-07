# ---------------------------------------------------------------------------
# Inventory snapshots: monthly per warehouse per product category
# ---------------------------------------------------------------------------
CATEGORIES = ["Electronics", "Apparel", "Home Goods", "Industrial Parts", "Perishables"]

# Baseline monthly stockout probability per category: perishables turn over
# fast and spoil, so they run out more often; industrial parts are ordered
# in bulk and rarely run dry.
CATEGORY_STOCKOUT_BASE = {
    "Electronics": 0.05,
    "Apparel": 0.07,
    "Home Goods": 0.04,
    "Industrial Parts": 0.03,
    "Perishables": 0.12,
}

inventory_rows = []
months = pd.date_range(START_DATE, END_DATE, freq="MS")
for month in months:
    seasonal_draw = month_seasonality(month.date())  # >1 in peak demand months
    for _, w in warehouses_df.iterrows():
        for category in CATEGORIES:
            base_stock = np.random.randint(500, 5000)
            reorder_point = int(base_stock * 0.25)

            # Demand pressure scales stockout odds up in peak season, down
            # in the seasonal lull.
            stockout_prob = min(0.6, CATEGORY_STOCKOUT_BASE[category] * seasonal_draw)
            stockout_flag = bool(np.random.random() < stockout_prob)

            if stockout_flag:
                stock_units = np.random.randint(0, max(1, int(reorder_point * 0.3)))
            else:
                stock_units = np.random.randint(reorder_point, base_stock)

            inventory_rows.append(
                {
                    "warehouse_id": w.warehouse_id,
                    "month": month.date(),
                    "category": category,
                    "stock_units": int(stock_units),
                    "reorder_point": reorder_point,
                    "stockout_flag": stockout_flag,
                }
            )
inventory_df = pd.DataFrame(inventory_rows)
