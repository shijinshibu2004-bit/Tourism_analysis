import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from sklearn.linear_model import LinearRegression
import numpy as np
import pdfkit
import os

# Ensure the directory for saving images exists
if not os.path.exists("figures"):
    os.makedirs("figures")

def fetch_data():
    """Load the dataset from CSV."""
    return pd.read_csv('data/tourism_data.csv')

def save_plot_as_image(fig, filename):
    """Save a Plotly figure as an image."""
    pio.write_image(fig, filename, format='png')

def generate_pdf_report(html_content, output_path):
    pdfkit_config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    
    # Save HTML to a temp file
    with open("temp_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # Convert to PDF from file instead of string
    pdfkit.from_file("temp_report.html", output_path, configuration=pdfkit_config, options={'enable-local-file-access': None})


# Streamlit UI
st.title("Tourism Analysis Dashboard")

df = fetch_data()

if not df.empty:
    df['year'] = df['year'].astype(int)  # Ensure 'year' is integer

    # Sidebar Filters
    st.sidebar.header("Filters")
    selected_countries = st.sidebar.multiselect("Select Countries", options=df['country'].unique(), default=df['country'].unique())
    selected_years = st.sidebar.slider("Select Year Range", min_value=int(df['year'].min()), max_value=int(df['year'].max()), value=(2000, 2024))
    selected_seasons = st.sidebar.multiselect("Select Seasons", options=df['season'].unique(), default=df['season'].unique())

    # Apply filters
    filtered_df = df[(df['country'].isin(selected_countries)) & 
                     (df['year'].between(*selected_years)) & 
                     (df['season'].isin(selected_seasons))]

    st.subheader("Tourist Arrivals Over Time")
    fig = px.line(filtered_df, x="year", y="visitors", color="country", markers=True, title="Tourism Trends")
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=2000, dtick=1, tickformat='d', range=[2000, 2027]))
    st.plotly_chart(fig)
    save_plot_as_image(fig, "figures/tourism_trends.png")

    st.subheader("Visitor Demographics")
    fig_pie = px.pie(filtered_df, names="country", values="visitors", title="Visitor Distribution by Country")
    st.plotly_chart(fig_pie)
    save_plot_as_image(fig_pie, "figures/visitor_distribution.png")

    st.subheader("Seasonal Travel Trends")
    fig_bar = px.bar(filtered_df, x="season", y="visitors", color="country", title="Peak Travel Seasons")
    st.plotly_chart(fig_bar)
    save_plot_as_image(fig_bar, "figures/seasonal_travel.png")

    st.subheader("Visitor Spending by Country")
    fig_spending = px.bar(filtered_df, x="country", y="spending", title="Average Spending per Visitor by Country")
    st.plotly_chart(fig_spending)
    save_plot_as_image(fig_spending, "figures/spending.png")

    st.subheader("Visitor Distribution by Season")
    fig_season_pie = px.pie(filtered_df, names="season", values="visitors", title="Visitor Distribution by Season")
    st.plotly_chart(fig_season_pie)
    save_plot_as_image(fig_season_pie, "figures/season_distribution.png")

    # Prediction for future years
    st.subheader("Predicted Tourist Arrivals for 2025, 2026, and 2027")
    predictions = []

    for country in filtered_df['country'].unique():
        country_df = df[df['country'] == country]
        X = country_df[['year']]
        y = country_df['visitors']
        model = LinearRegression()
        model.fit(X, y)
        future_years = np.array([[2025], [2026], [2027]])
        future_visitors = model.predict(future_years)
        for year, visitors in zip(future_years.flatten(), future_visitors):
            predictions.append({'year': year, 'country': country, 'visitors': visitors})

    prediction_df = pd.DataFrame(predictions)
    combined_df = pd.concat([filtered_df, prediction_df])

    fig_prediction = px.line(combined_df, x="year", y="visitors", color="country", markers=True, title="Tourism Trends with Predictions")
    fig_prediction.update_layout(xaxis=dict(tickmode='linear', tick0=2000, dtick=1, tickformat='d', range=[2000, 2027]))
    st.plotly_chart(fig_prediction)
    save_plot_as_image(fig_prediction, "figures/future_predictions.png")

    # Export options
    st.sidebar.header("Export Options")
    export_format = st.sidebar.selectbox("Select Export Format", ["CSV", "Excel", "PDF"])

    if st.sidebar.button("Export Report"):
        if export_format == "CSV":
            filtered_df.to_csv("tourism_report.csv", index=False)
            st.success("Report exported as CSV.")
        elif export_format == "Excel":
            filtered_df.to_excel("tourism_report.xlsx", index=False)
            st.success("Report exported as Excel.")
        elif export_format == "PDF":
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Tourism Analysis Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    h1, h2 {{ color: #333; }}
                    .chart-container {{ margin-bottom: 20px; text-align: center; }}
                </style>
            </head>
            <body>
                <h1>Tourism Analysis Report</h1>
                <div class="chart-container">
                    <h2>Tourist Arrivals Over Time</h2>
                    <img src="figures/tourism_trends.png" width="600">
                </div>
                <div class="chart-container">
                    <h2>Visitor Demographics</h2>
                    <img src="figures/visitor_distribution.png" width="600">
                </div>
                <div class="chart-container">
                    <h2>Seasonal Travel Trends</h2>
                    <img src="figures/seasonal_travel.png" width="600">
                </div>
                <div class="chart-container">
                    <h2>Visitor Spending by Country</h2>
                    <img src="figures/spending.png" width="600">
                </div>
                <div class="chart-container">
                    <h2>Visitor Distribution by Season</h2>
                    <img src="figures/season_distribution.png" width="600">
                </div>
                <div class="chart-container">
                    <h2>Predicted Tourist Arrivals for 2025, 2026, and 2027</h2>
                    <img src="figures/future_predictions.png" width="600">
                </div>
            </body>
            </html>
            """
            generate_pdf_report(html_content, "tourism_report.pdf")
            st.success("Report exported as PDF.")

else:
    st.warning("No data available. Please upload a valid dataset.")
