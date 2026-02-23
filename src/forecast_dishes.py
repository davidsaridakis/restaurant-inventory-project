"""
forecast_dishes.py

Generate dish-level daily orders for 2026 based on:
    - 2026 forecasted covers
    - 2025 dish orders


Output:
    data/processed/forecasted_dishes_2026.csv.

Run:
    python src/forecast_dishes.py

Next Steps:
- Use the outputted data to generate ingredient level
- demand for orders
"""

import pandas as pd
from pathlib import Path


def main():

    # --- 1. Load data ---

    # Load historical dish data (2025)
    dishes_path = Path("data/raw/daily_dishes.csv")
    df_dishes_2025 = pd.read_csv(dishes_path, parse_dates=['date']) 

    # Load historical covers data (2025)
    covers_2025_path = Path("data/raw/covers_history.csv")
    df_covers_2025 = pd.read_csv(covers_2025_path, parse_dates=['date'])

    # Load forecasted covers data (20226)
    covers_2026_path = Path("data/processed/forecast_2026.csv")
    df_covers_2026 = pd.read_csv(covers_2026_path, parse_dates=['date'])


    # --- 2. Merge 2025 covers and dishes ---
    df_2025 = df_dishes_2025.merge(
        df_covers_2025[['date', 'covers']],
        on='date',
        how='inner'
    )


    # --- 3. Define dish columns ---
    dish_columns = [
        'garlic_prawns',
        'spanish_tortilla',
        'tabbouleh_salad',
        'grilled_lamb_cutlets',
        'spanakopita',
        'chicken_pesto_skewers',
        'ropa_vieja',
        'cheesecake'
    ]


    # --- 4. Compute per-cover dish ratios ---
    total_covers_2025 = df_2025['covers'].sum()
    dish_totals = df_2025[dish_columns].sum()

    dish_ratios = dish_totals / total_covers_2025


    # --- 5. Generate 2026 dish forecast ---
    df_dishes_2026 = pd.DataFrame()
    df_dishes_2026['date'] = df_covers_2026['date']

    for dish in dish_columns:
        df_dishes_2026[dish] = df_covers_2026['covers'] * dish_ratios[dish]

    df_dishes_2026['covers'] = df_covers_2026['covers']


    # --- 6. Save 2026 forecasted dishes ---
    output_path = Path("data/processed/forecasted_dishes_2026.csv")
    df_dishes_2026.to_csv(output_path, index=False)

    print(f"Forecasted dishes saved to {output_path}")


if __name__ == "__main__":
    main()