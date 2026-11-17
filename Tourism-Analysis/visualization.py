import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pandas as pd
import sqlite3

def fetch_data():
    conn = sqlite3.connect("tourism.db")
    df = pd.read_sql_query("SELECT * FROM tourism_data", conn)
    conn.close()
    return df

def plot_trend_chart():
    df = fetch_data()
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x="year", y="visitors", hue="country", marker="o")
    plt.title("Tourist Arrival Trends Over Time")
    plt.xlabel("Year")
    plt.ylabel("Number of Visitors")
    plt.show()

def plot_heatmap():
    df = fetch_data()
    pivot_table = df.pivot_table(index="season", columns="country", values="visitors", aggfunc="sum")
    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot_table, cmap="coolwarm", annot=True, fmt="g")
    plt.title("Most Visited Locations Heatmap")
    plt.show()

if __name__ == "__main__":
    plot_trend_chart()
    plot_heatmap()
