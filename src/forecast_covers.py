"""
forecast_orders.py

Forecast daily covers for 2026 based on historical data:


Output:
    data/processed/forecast_2026.csv.

Run:
    python src/forecast_covers.py

Next Steps:
- Use the outputted data to generate ingredient level
- demand for orders
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor


# --- Load historical data ---
df = pd.read_csv("data/raw/covers_history.csv",
                     parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)


# --- Feature Engineering ---
df['lag_7'] = df['covers'].shift(7)
df['lag_14'] = df['covers'].shift(14)

# Drop NaNs
df = df.dropna().reset_index(drop=True)

df['day_of_week'] = df['date'].dt.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5,6]).astype(int)
df['day_of_year'] = df['date'].dt.dayofyear


# Summer seasonality
summer_peak_day = 200
summer_width = 40

df['summer_seasonality'] = 35 * np.exp(
    -((df['day_of_year'] - summer_peak_day) ** 2) /
    (2 * summer_width ** 2)
)


# Define the key holiday dates for Spain / restaurant
# spikes
holiday_dates = pd.to_datetime([
    "2025-01-01",  # New Year's Day
    "2025-01-06",  # Dia de Reyes
    "2025-12-20",  # Christmas week start
    "2025-12-21", "2025-12-22", "2025-12-23", "2025-12-24",
    "2025-12-25", "2025-12-26", "2025-12-27", "2025-12-28",
    "2025-12-29", "2025-12-30", "2025-12-31",  # NYE
])


# Christmas Spike
df['christmas_spike'] = 0
df.loc[
    (df['date'].dt.month == 12) &
    (df['date'].dt.day >= 16),
'christmas_spike'
] = 30


# --- Define features set ---
features = [
    'lag_7', 'lag_14',
    'day_of_week', 'is_weekend', 'day_of_year', 
    'summer_seasonality',
    'trend', 
    'christmas_spike', 'is_holiday_period'
]


# --- Train Model ---
rf_model = RandomForestRegressor(
    n_estimators=500,
    max_depth=None,
    random_state=42
)
rf_model.fit(df[features], df['covers'])


# ----------------------------------
# --- Forecast Covers for 1 year ---
# ----------------------------------

forecast_df = df.copy()

# --- Generate Future Dates and Append ---
future_dates = pd.date_range(
    start=df['date'].max() + pd.Timedelta(days=1),
    periods=365
)

future = pd.DataFrame({'date': future_dates})
forecast_df = pd.concat([forecast_df, future], ignore_index=True)


# --- Recreate deterministic features for entire dataset ---

# Day features
forecast_df['day_of_week'] = forecast_df['date'].dt.dayofweek
forecast_df['is_weekend'] = forecast_df['day_of_week'].isin([5,6]).astype(int)
forecast_df['day_of_year'] = forecast_df['date'].dt.dayofyear

# Summer seasonality 
forecast_df['summer_seasonality'] = 35 * np.exp(
    -((forecast_df['day_of_year'] - summer_peak_day) ** 2) /
    (2 * summer_width ** 2)
)

# Christmas spike
forecast_df['christmas_spike'] = 0

forecast_df.loc[
    (forecast_df['date'].dt.month == 12) &
    (forecast_df['date'].dt.day >= 20),
    'christmas_spike'
] = 60

# Known holiday flag
holiday_dates_2026 = pd.to_datetime([
    "2026-01-01", "2026-01-06", "2026-12-20", "2026-12-21",
    "2026-12-22", "2026-12-23", "2026-12-24", "2026-12-25",
    "2026-12-26", "2026-12-27", "2026-12-28", "2026-12-29",
    "2026-12-30", "2026-12-31"
])
forecast_df['is_holiday_period'] = forecast_df['date'].isin(holiday_dates_2026).astype(int)

# Continued business growth trend
daily_increment = 10 / 365
forecast_df['trend'] = np.arange(len(forecast_df)) * daily_increment


# Initialize future covers as NaN
forecast_df.loc[len(df):, 'covers'] = np.nan


# --- Recursive Forecasting ---

for i in range(len(df), len(forecast_df)):

    forecast_df.loc[i, 'lag_7']  = forecast_df.loc[i-7, 'covers']  if i-7 >= 0 else historical_mean
    forecast_df.loc[i, 'lag_14'] = forecast_df.loc[i-14, 'covers'] if i-14 >= 0 else historical_mean

    row = forecast_df.loc[i, features].to_frame().T
    prediction = rf_model.predict(row)[0]
    forecast_df.loc[i, 'covers'] = prediction


# Extract 2026 forecast
forecast_2026 = forecast_df[forecast_df['date'].dt.year == 2026]

# Sanity check
print(forecast_2026['covers'].describe())
print("Total:", forecast_2026['covers'].sum())

# Save output CSV
forecast_2026.to_csv("data/processed/forecast_2026.csv", index=False)

print("Forecast saved.")