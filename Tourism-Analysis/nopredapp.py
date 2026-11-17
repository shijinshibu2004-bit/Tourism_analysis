import streamlit as st
import pandas as pd
import plotly.express as px
import pdfkit
import os

# Load Data
def fetch_data():
    df = pd.read_csv('data/tourism_data.csv')
    return df

# Save Plotly figures as PNG images (to ensure color in PDF)
def save_plotly_figure(fig, filename):
    fig.write_image(filename, scale=2)  # High-resolution image

# Generate PDF report
def generate_pdf_report(html_content, output_path):
    pdfkit_config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    
    options = {
        'enable-local-file-access': None,  # Allows local image loading
        'dpi': 300,  # High-quality images
        'image-quality': 100,  # Full color
    }
    
    pdfkit.from_string(html_content, output_path, configuration=pdfkit_config, options=options)

st.title("Tourism Analysis Dashboard")
df = fetch_data()

if not df.empty:
    df['year'] = df['year'].astype(int)

    # Sidebar Filters
    st.sidebar.header("Filters")
    selected_countries = st.sidebar.multiselect("Select Countries", options=df['country'].unique(), default=df['country'].unique())
    selected_years = st.sidebar.slider("Select Year Range", min_value=int(df['year'].min()), max_value=int(df['year'].max()), value=(2000, 2024))
    selected_seasons = st.sidebar.multiselect("Select Seasons", options=df['season'].unique(), default=df['season'].unique())

    # Apply filters
    filtered_df = df[(df['country'].isin(selected_countries)) & (df['year'].between(*selected_years)) & (df['season'].isin(selected_seasons))]

    # 📊 Generate Figures (Show in Browser + Save as Images)
    fig1 = px.line(filtered_df, x="year", y="visitors", color="country", markers=True, title="Tourism Trends", color_discrete_sequence=px.colors.qualitative.Set1)
    fig1.update_layout(xaxis=dict(tickmode='linear', dtick=1, tickformat='d', range=[2000, 2027]))
    save_plotly_figure(fig1, "figures/tourism_trends.png")
    st.plotly_chart(fig1)  # Show in browser

    fig2 = px.pie(filtered_df, names="country", values="visitors", title="Visitor Distribution by Country", color_discrete_sequence=px.colors.qualitative.Set1)
    save_plotly_figure(fig2, "figures/visitor_distribution.png")
    st.plotly_chart(fig2)

    fig3 = px.bar(filtered_df, x="season", y="visitors", color="country", title="Peak Travel Seasons", color_discrete_sequence=px.colors.qualitative.Set1)
    save_plotly_figure(fig3, "figures/peak_travel_seasons.png")
    st.plotly_chart(fig3)

    fig4 = px.bar(filtered_df, x="country", y="spending", title="Average Spending per Visitor by Country", color="country", color_discrete_sequence=px.colors.qualitative.Set1)
    save_plotly_figure(fig4, "figures/visitor_spending.png")
    st.plotly_chart(fig4)

    fig5 = px.pie(filtered_df, names="season", values="visitors", title="Visitor Distribution by Season", color_discrete_sequence=px.colors.qualitative.Set1)
    save_plotly_figure(fig5, "figures/visitor_season_distribution.png")
    st.plotly_chart(fig5)

    # ✅ User Chooses Export Format
    export_format = st.radio("Choose Report Format:", ("CSV", "Excel", "PDF"))

    if export_format == "CSV":
        st.download_button("Download CSV", data=filtered_df.to_csv(index=False), file_name="tourism_report.csv", mime="text/csv")
    elif export_format == "Excel":
        excel_file = "tourism_report.xlsx"
        with pd.ExcelWriter(excel_file) as writer:
            filtered_df.to_excel(writer, index=False)
        st.download_button("Download Excel", data=open(excel_file, "rb"), file_name=excel_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif export_format == "PDF":
        # ✅ Modify HTML to Include Images for PDF
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Tourism Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; }}
                h1, h2 {{ color: #333; }}
                img {{ width: 80%; max-width: 800px; margin: 10px auto; display: block; border: 2px solid black; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <h1>Tourism Analysis Report</h1>
            <h2>Tourist Arrivals Over Time</h2>
            <img src="file:///{os.path.abspath('figures/tourism_trends.png')}" />
            
            <h2>Visitor Demographics</h2>
            <img src="file:///{os.path.abspath('figures/visitor_distribution.png')}" />
            
            <h2>Seasonal Travel Trends</h2>
            <img src="file:///{os.path.abspath('figures/peak_travel_seasons.png')}" />
            
            <h2>Visitor Spending by Country</h2>
            <img src="file:///{os.path.abspath('figures/visitor_spending.png')}" />
            
            <h2>Visitor Distribution by Season</h2>
            <img src="file:///{os.path.abspath('figures/visitor_season_distribution.png')}" />
        </body>
        </html>
        """

        pdf_file = "tourism_report.pdf"
        generate_pdf_report(html_content, pdf_file)
        st.download_button("Download PDF", data=open(pdf_file, "rb"), file_name=pdf_file, mime="application/pdf")

else:
    st.warning("No data available. Please upload a valid dataset.")
