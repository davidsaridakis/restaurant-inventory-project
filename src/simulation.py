import pandas as pd
import numpy as np
from pathlib import Path

"""
simulation.py

Generates 12 months of simulated daily restaurant 
cover data for a medium sized restaurant.

Features included:
- Weekdays vs weekend demand difference
- Linear upward business trend
- Bell-shaped summer seasonality
- Christmas spike in demand
- Random noise for realistic data

Ouput:
    data/raw/covers_history.csv

Run:
    python src/simulation.py
"""

# Create seed for reproducibility
np.random.seed(42)


# --- 1. Create date range ---
start_date = "2025-01-01"
end_date = "2025-12-31"

dates = pd.date_range(start=start_date, end=end_date, freq='D')
df = pd.DataFrame({"date": dates})
df


# --- 2. Basic time features ---
df['day_of_week'] = df['date'].dt.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
df['day_of_year'] = df['date'].dt.dayofyear


# --- 3. Base demand ---
weekday_base = 60
weekend_base = 95

df['base_covers'] = np.where(
    df['is_weekend'] == 1,
    weekend_base,
    weekday_base
)


# --- 4. Upward trend (business growth) ---
df['trend'] = np.linspace(0, 10, len(df))


# --- 5. Summer season demand (peak mid July) ---
summer_peak_day = 200
summer_width = 40

df['summer_seasonality'] = 35 * np.exp(
    -((df['day_of_year'] - summer_peak_day) ** 2) / 
    (2 * summer_width ** 2)
)


# --- 6. Xmas spike (last 2 weeks od December)---
df['christmas_spike'] = 0

# Define last 16 days of December
last_two_weeks = (
    (df['date'].dt.month == 12) &
    (df['date'].dt.day >= 16)
)

# Add spike for those days
df.loc[last_two_weeks, "christmas_spike"] = 30


# --- 7. Random noise ---
noise = np.random.normal(0, 8, len(df))


# ---8. Final covers calculation ---
df['covers'] = (
    df['base_covers'] + df['trend']
    + df['summer_seasonality']
    + df['christmas_spike']
    + noise
)

# Close Christmas Day
df.loc[
    (df['date'].dt.month == 12) &
    (df['date'].dt.day == 25),
    'covers'
] = 0

# Round to whole numbers and avoid negative covers
df['covers'] = df['covers'].round().clip(lower=0)

# --- 9. Save ---
output_path = Path("data/raw/covers_history.csv")
df.to_csv(output_path, index=False)

print(f"Dataset saved to {output_path}")