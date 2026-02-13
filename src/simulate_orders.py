"""
simulate_orders.py

Simulate daily dish-level orders based on the following:
- Daily covers (from covers_history.csv)
- Table size
- Dish category probabilities
- Table-level starter plate ordering behaviour

Output:
    data/raw/daily_dish_orders.csv

Run:
    python src/simulate_orders.py

Next Steps:
- Use the outputted data to make business decisions about
quantities of ingredients needed in weekly orders.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# For reproducibility
np.random.seed(42)


# --- Load cover data ---
input_path = Path("data/raw/covers_history.csv")
df_covers = pd.read_csv(input_path, parse_dates=['date'])


# --- Define menu ---
small_plates = {
    "garlic_prawns": 0.4,
    "spanish_tortilla": 0.35,
    "tabbouleh_salad": 0.25
}

mains = {
    "grilled_lamb_cutlets": 0.2,
    "spanakopita": 0.15,
    "chicken_pesto_skewers": 0.4,
    "ropa_vieja":0.25
}

desserts = {
    "cheesecake": 1.0
}


# --- Table size distribution and simulation ---
table_sizes = [2, 3, 4, 5, 6]
table_probs = [0.45, 0.15, 0.3, 0.05, 0.05]

def simulate_day(covers):

    # Initialise dish counter
    dish_counts = {dish: 0 for dish in
                   list(small_plates.keys())
                   + list(mains.keys())
                   + list(desserts.keys())}
    
    remaining_covers = covers

    while remaining_covers > 0:
        # Generate table size
        table_size = np.random.choice(table_sizes, p=table_probs)

        # Prevent over shooting remaining covers
        table_size = min(table_size, remaining_covers)
        remaining_covers -= table_size

        # Small plate orders (95% chance per table)
        if np.random.rand() < 0.95:
            n_small = np.random.randint(1, 4) # 1-3 starters ordered
            chosen_small = np.random.choice(
                list(small_plates.keys()),
                size=n_small,
                p=list(small_plates.values())
            )

            # Update dish count
            for dish in chosen_small:
                dish_counts[dish] += 1
        
        # Mains orders (1 per diner)
        chosen_main = np.random.choice(
            list(mains.keys()),
            size=table_size,
            p=list(mains.values())
        )

        # Update dish count
        for dish in chosen_main:
            dish_counts[dish] += 1
        
        # Dessert orders (35% per diner)
        for _ in range(table_size):
            if np.random.rand() < 0.35:
                dish_counts['cheesecake'] += 1

    return dish_counts


# --- Simulate for all days ---
all_results = []

for _, row in df_covers.iterrows():
    daily_counts = simulate_day(int(row['covers']))
    daily_counts['date'] = row['date']
    all_results.append(daily_counts)

df_orders = pd.DataFrame(all_results)


# --- Save output ---
output_path = Path("data/raw/daily_dishes.csv")
df_orders.to_csv(output_path, index=False)

print(f"Daily dish-level dataset saved to {output_path}")
