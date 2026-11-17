import pandas as pd
import numpy as np
import sqlite3

def load_data(csv_file):
    df = pd.read_csv(csv_file)
    df.fillna(0, inplace=True)  # Handle missing values
    return df

def store_data(df):
    conn = sqlite3.connect("tourism.db")
    df.to_sql("tourism_data", conn, if_exists="append", index=False)
    conn.close()

if __name__ == "__main__":
    df = load_data("data/tourism_data.csv")
    store_data(df)
    print("Data successfully stored in SQLite database.")
