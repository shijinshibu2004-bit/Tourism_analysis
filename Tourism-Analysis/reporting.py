import pandas as pd
import sqlite3

def generate_report():
    conn = sqlite3.connect("tourism.db")
    df = pd.read_sql_query("SELECT * FROM tourism_data", conn)
    conn.close()

    report_summary = df.groupby(["country", "year"]).agg({"visitors": "sum", "spending": "mean"}).reset_index()
    report_summary.to_csv("reports/tourism_report.csv", index=False)
    print("Report successfully generated!")

if __name__ == "__main__":
    generate_report()
