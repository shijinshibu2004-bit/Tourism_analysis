import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

def fetch_data():
    # Read the CSV file directly
    df = pd.read_csv('data/tourism_data.csv')
    return df

def generate_pdf_report(html_content, output_path):
    import pdfkit
    # Set the path to wkhtmltopdf if it's not in your PATH
    pdfkit_config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    pdfkit.from_string(html_content, output_path, configuration=pdfkit_config)

st.title("Tourism Analysis Dashboard")

df = fetch_data()

if not df.empty:
    # Convert the 'year' column to integer type
    df['year'] = df['year'].astype(int)

    # Filters
    st.sidebar.header("Filters")
    selected_countries = st.sidebar.multiselect("Select Countries", options=df['country'].unique(), default=df['country'].unique())
    selected_years = st.sidebar.slider("Select Year Range", min_value=int(df['year'].min()), max_value=int(df['year'].max()), value=(2000, 2024))
    selected_seasons = st.sidebar.multiselect("Select Seasons", options=df['season'].unique(), default=df['season'].unique())

    # Apply filters
    filtered_df = df[(df['country'].isin(selected_countries)) & (df['year'].between(*selected_years)) & (df['season'].isin(selected_seasons))]

    st.subheader("Tourist Arrivals Over Time")
    fig = px.line(filtered_df, x="year", y="visitors", color="country", markers=True, title="Tourism Trends")
    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=2000,
            dtick=1,
            tickformat='d',  # Ensure the tick format is integer
            range=[2000, 2027]  # Set the range of the x-axis
        )
    )
    st.plotly_chart(fig)

    st.subheader("Visitor Demographics")
    fig_pie = px.pie(filtered_df, names="country", values="visitors", title="Visitor Distribution by Country")
    st.plotly_chart(fig_pie)

    st.subheader("Seasonal Travel Trends")
    fig_bar = px.bar(filtered_df, x="season", y="visitors", color="country", title="Peak Travel Seasons")
    st.plotly_chart(fig_bar)

    # New section for visitor demographics by nationality
    st.subheader("Visitor Spending by Country")
    fig_spending = px.bar(filtered_df, x="country", y="spending", title="Average Spending per Visitor by Country")
    st.plotly_chart(fig_spending)

    # New section for visitor demographics by season
    st.subheader("Visitor Distribution by Season")
    fig_season_pie = px.pie(filtered_df, names="season", values="visitors", title="Visitor Distribution by Season")
    st.plotly_chart(fig_season_pie)

    # Prediction for future years
    st.subheader("Predicted Tourist Arrivals for 2025, 2026, and 2027")
    countries = filtered_df['country'].unique()
    predictions = []

    for country in countries:
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
    fig_prediction.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=2000,
            dtick=1,
            tickformat='d',  # Ensure the tick format is integer
            range=[2000, 2027]  # Set the range of the x-axis
        )
    )
    st.plotly_chart(fig_prediction)

    # Display detailed analytics for a single country
    if len(selected_countries) == 1:
        country = selected_countries[0]
        st.subheader(f"Detailed Analytics for {country}")
        country_df = filtered_df[filtered_df['country'] == country]

        st.write(f"Total Visitors: {country_df['visitors'].sum()}")
        st.write(f"Average Spending: {country_df['spending'].mean()}")

        fig_country_trend = px.line(country_df, x="year", y="visitors", title=f"Tourist Arrivals Over Time for {country}")
        st.plotly_chart(fig_country_trend)

        fig_country_season = px.bar(country_df, x="season", y="visitors", title=f"Seasonal Travel Trends for {country}")
        st.plotly_chart(fig_country_season)

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
                    .chart-container {{ margin-bottom: 20px; }}
                </style>
            </head>
            <body>
                <h1>Tourism Analysis Report</h1>
                <div class="chart-container">
                    <h2>Tourist Arrivals Over Time</h2>
                    {fig.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>
                <div class="chart-container">
                    <h2>Visitor Demographics</h2>
                    {fig_pie.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>
                <div class="chart-container">
                    <h2>Seasonal Travel Trends</h2>
                    {fig_bar.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>
                <div class="chart-container">
                    <h2>Visitor Spending by Country</h2>
                    {fig_spending.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>
                <div class="chart-container">
                    <h2>Visitor Distribution by Season</h2>
                    {fig_season_pie.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>
                <div class="chart-container">
                    <h2>Predicted Tourist Arrivals for 2025, 2026, and 2027</h2>
                    {fig_prediction.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>
            </body>
            </html>
            """
            generate_pdf_report(html_content, "tourism_report.pdf")
            st.success("Report exported as PDF.")

else:
    st.warning("No data available. Please upload a valid dataset.")