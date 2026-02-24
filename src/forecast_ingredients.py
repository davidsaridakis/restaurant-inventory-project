"""
forecast_ingredients.py

Generate weekly required ingredients for 2026 based on:

Inputs:
    data/processed/forecasted_dishes_2026.csv
    data/raw/recipe_matrix.xlsx


Output:
    data/processed/forecasted_ingredients_2026.csv.

Run:
    python src/forecast_ingredients.py

"""

import pandas as pd
from pathlib import Path


def main():
    
    # --- 1. Load Data ---
    # Load dish forecast
    dish_path = Path("data/processed/forecasted_dishes_2026.csv")
    df_dishes = pd.read_csv(dish_path, parse_dates=['date'])

    # Load recipe matrix
    recipe_path = Path("data/raw/recipe_matrix.xlsx")
    df_recipe = pd.read_excel(recipe_path)

    # Force numeric values
    df_recipe["qty_per_dish"] = pd.to_numeric(
        df_recipe["qty_per_dish"],
        errors="coerce"
    )

    df_recipe["buffer_rate"] = pd.to_numeric(
        df_recipe["buffer_rate"],
        errors="coerce"
    )

    print("Files loaded successfully.")

    # --- 2. Add 'year' and 'week' for weekly aggregation ---
    df_dishes['year'] = df_dishes['date'].dt.isocalendar().year
    df_dishes['week'] = df_dishes['date'].dt.isocalendar().week

    # Exclude non dish columns
    non_dish_cols = ['date', 'covers', 'month', 'year', 'week']
    dish_columns = [col for col in df_dishes.columns if col not in non_dish_cols]
    
    # Aggregate weekly
    df_weekly_dishes = (
        df_dishes
        .groupby(['year', 'week'])[dish_columns]
        .sum()
        .reset_index()
    )


    # --- 3. Convert weekly dishes to long format ---
    df_weekly_long = df_weekly_dishes.melt(
        id_vars=['year', 'week'],
        var_name='dish',
        value_name='dish_qty'
    )


    # --- 4. Merge with recipe matrix ---
    df_merged = df_weekly_long.merge(
        df_recipe,
        on='dish',
        how='left'
    )
    # Drop na's
    df_merged = df_merged.dropna(subset=["ingredient"])

    # --- 5. Calculate ingredient quantities ---

    # Ensure numeric types
    numeric_cols = ['dish_qty', 'qty_per_dish', 'buffer_rate']

    for col in numeric_cols:
        df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')


    # Calculate ingredient quantities
    df_merged['ingredient_qty'] = (
        df_merged['dish_qty'] *
        df_merged['qty_per_dish']
    )
    
    df_merged['ingredient_qty_buffered'] = (
        df_merged['ingredient_qty'] *
        (1 + df_merged['buffer_rate'])
    )


    # --- 6. Weekly ordering summary output ---
    
    # Aggregate ingredient demand
    df_procurement = (
        df_merged
        .groupby(['year', 'week', 'ingredient', 'unit'], as_index=False)
        ['ingredient_qty_buffered']
        .sum()
        .rename(columns={
            'ingredient_qty_buffered': 'order_quantity'
        })
    )

    # Round quantities accordint to business rules
    def round_order_quantity(qty, unit):
        """
        Procurement rounding rules
        """
        if unit == 'kg':
            return round(qty * 2) / 2 # nearest 0.5 kg
        elif unit == 'litre':
            return round(qty * 2) / 2 # nearest 0.5 litre
        elif unit == 'piece':
            return round(qty)
        else:
            return round(qty, 2)
        
    # Apply rounding
    df_procurement['order_quantity'] = df_procurement.apply(
        lambda row: round_order_quantity(
            row['order_quantity'],
            row['unit']
        ),
        axis=1
    )


    # --- Save output ---
    output_path = Path("outputs/tables/weekly_procurement_plan_2026.csv")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    df_procurement.to_csv(output_path, index=False)

    print(f"Procurement summary saved to {output_path}")



if __name__ == "__main__":
    main()