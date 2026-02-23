"""
simulate_covers.py

Generates 12 months of simulated daily restaurant 
cover data for a medium sized restaurant.

Features included:
- Weekdays vs weekend demand difference
- Linear upward business trend
- Bell-shaped summer seasonality
- Christmas spike in demand
- Random noise for realistic data

Output:
    data/raw/covers_history.csv

Run:
    python src/simulate_covers.py
"""

import pandas as pd
import numpy as np
from pathlib import Path


def main():
    # Create seed for reproducibility
    np.random.seed(42)


    # --- 1. Create date range ---
    start_date = "2025-01-01"
    end_date = "2025-12-31"

    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    df = pd.DataFrame({"date": dates})


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


    # --- 6. Define the key holiday dates for Spain / 
    # restaurant spikes
    holiday_dates = pd.to_datetime([
        "2025-01-01",  # New Year's Day
        "2025-01-06",  # Dia de Reyes
        "2025-12-20",  # Christmas week start
        "2025-12-21", "2025-12-22", "2025-12-23", "2025-12-24",
        "2025-12-25", "2025-12-26", "2025-12-27", "2025-12-28",
        "2025-12-29", "2025-12-30", "2025-12-31",  # NYE
    ])

    # Add a binary column to indicate if the day is a known holiday spike
    df['is_holiday_period'] = df['date'].isin(holiday_dates).astype(int)


    # --- 7. Xmas spike (last 2 weeks of December)---
    df['christmas_spike'] = 0

    # Define last 16 days of December
    last_two_weeks = (
        (df['date'].dt.month == 12) &
        (df['date'].dt.day >= 16)
    )

    # Add spike for those days
    df.loc[last_two_weeks, "christmas_spike"] = 30


    # --- 8. Random noise ---
    noise = np.random.normal(0, 8, len(df))


    # --- 9. Final covers calculation ---
    df['covers'] = (df['base_covers'] 
        + df['trend']
        + df['summer_seasonality']
        + df['christmas_spike']
        + noise
    )


    # --- 10. Close Christmas Day ---
    df.loc[
        (df['date'].dt.month == 12) &
        (df['date'].dt.day == 25),
        'covers'
    ] = 0

    # --- 11. Round to whole numbers and avoid negative covers ---
    df['covers'] = df['covers'].round().clip(lower=0)


    # --- 12. Save ---
    output_path = Path("data/raw/covers_history.csv")
    df.to_csv(output_path, index=False)

    print(f"Dataset saved to {output_path}")


if __name__ == "__main__":
    main()