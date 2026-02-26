# Restaurant Demand Forecasting & Procurement Analytics Pipeline

## Overview

This project demonstrates an end-to-end analytics pipeline for restaurant demand forecasting and operational procurement planning.

The system simulates historical customer demand, applies machine learning to forecast future restaurant covers, translates projected demand into dish-level orders, and generates weekly ingredient procurement recommendations. Final outputs are exported into a structured database layer for integration with reporting systems.

The goal is to showcase practical data analytics and machine learning skills in a business-oriented context.

---

## Business Problem

Restaurants must anticipate customer demand while minimizing inventory waste and stock shortages.

This project addresses:

- Forecasting daily customer covers
- Translating customer demand into dish-level projections
- Estimating ingredient procurement quantities
- Structuring outputs for operational decision-making

---

## Pipeline Architecture

The analytical workflow follows this structure:

Simulation → Feature Engineering → Forecast Model → Dish Demand Projection → Ingredient Planning → Database Export

Each stage is modular and reproducible.

---

## 1. Demand Simulation

Synthetic historical data was generated to replicate realistic restaurant behavior, including:

- Weekday vs weekend variation
- Seasonal summer demand
- Holiday demand spikes
- Business growth trend
- Controlled stochastic noise

In addition to cover simulation, dish-level ordering behavior was modeled using:

- Realistic table-size distributions based on probability assumptions
- Dish category demand patterns (starters, mains, desserts)
- Per-cover dish ordering ratios

This ensures that downstream forecasts reflect plausible restaurant ordering behavior.

Script:
- `simulate_covers.py`

Output:
- `data/raw/covers_history.csv`

---

## 2. Cover Forecasting (Machine Learning)

Daily covers were forecasted using supervised regression models.

Feature engineering included:

- Lag features
- Weekly seasonality
- Trend approximation
- Holiday indicators
- Seasonal demand curves

Models evaluated:

- Linear Regression
- Random Forest Regressor (selected model)

Evaluation Metrics:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R² Score
- Residual Standard Deviation

Notebook:
- `forecasting_model.ipynb`

---

## 3. Dish-Level Demand Projection

Dish-level order quantities were estimated using per-cover ordering ratios derived from historical data.

Assumption:
- Menu preference distribution remains stable over forecast horizon.

Script:
- `forecast_dishes.py`

Output:
- `data/processed/forecasted_dishes_2026.csv`

---

## 4. Ingredient Procurement Planning

Dish forecasts were mapped to ingredient requirements using a structured recipe matrix.

Features include:

- Ingredient quantity per dish
- Buffer rate application
- Unit-aware rounding rules
- Weekly aggregation

Script:
- `forecast_ingredients.py`

Output:
- `outputs/tables/weekly_procurement_plan_2026.csv`

---

## 5. Database Integration Layer

Final procurement outputs are exported into a SQLite database to demonstrate pipeline operationalization and integration readiness.

Script:
- `export_procurement_to_sql.py`

Database:
- `analytics.db` (generated locally, not tracked in repository)

---

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn
- SQLAlchemy
- SQLite

---

## Key Skills Demonstrated

- Time series feature engineering
- Machine learning regression modeling
- Model evaluation and comparison
- Data transformation and aggregation
- Pipeline modularization
- Business-oriented analytics translation
- Database export integration

---

## Project Structure

- `data/`
  - `raw/` → Raw CSV files from simulation    scripts.  
    -`recipe_matrix.xlsx` 
  - `processed/` → Generate csv files of forecasts. 
- `notebooks/` → Jupyter notebooks  
  - `data_simulation_validation.ipynb` → Check simulated data and plot. Inpect forecasted covers for 2026.
   - `forecsting_model.ipynb` → Train, test, and validate models. 
  - `dish_forecasting.ipynb` → Forecast dish-level orders for 2026.
  - `ingredients_forecast_check.ipynb` → Inspect ingredient procurement output.
- `src/` → Python scripts  
  - `simulate covers.py` → Generate 12 months of historical data for restaurant covers.
  - `simulate_dishes.py` → Generate 12 months of dish-level orders based on covers.
  - `forecast_covers.py` → Forecast 12 months of covers.
  - `forecast_dishes.py` → Forecast 12 months of dish-level orders.
  - `forecast_ingredients.py` → Forecast 12 months of ingredients by week.
  - `export_procurement_to_sql.py` → Export weekly procurement plan to SQL database
- `.gitignore`  
- `requirements.txt`  
- `README.md`

---

## Future Enhancements

- Incorporation of external variables (weather, events)
- Advanced gradient boosting models
- Automated pipeline orchestration
- Cost optimization modeling

---

## Purpose

This project was developed as part of a data analytics portfolio to demonstrate applied machine learning and operational forecasting capabilities suitable for data analytics or business intelligence roles.
