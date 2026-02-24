from sqlalchemy import create_engine
import pandas as pd

def main():

    # Load procurement forecast
    df_procurement = pd.read_csv(
        "outputs/tables/weekly_procurement_plan_2026.csv"
    )

    # Database connection example
    engine = create_engine("sqlite:///analytics.db")

    df_procurement.to_sql(
        "weekly_procurement_plan",
        engine,
        if_exists="replace",
        index=False
    )

    print("Data exported to SQL database.")

if __name__ == "__main__":
    main()