import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="🌍 COVID-19 Dashboard", layout="wide")

st.title("🦠 Global COVID-19 Data Analysis")
st.markdown("Analyze worldwide COVID-19 trends with real-time visual insights.")

# Caching the data loading
@st.cache_data(ttl=3600)  # cache for 1 hour
def load_data():
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    df = pd.read_csv(url)
    df['date'] = pd.to_datetime(df['date'])
    return df

data = load_data()

# Sidebar filters
countries = st.sidebar.multiselect(
    "🌍 Select countries", 
    options=sorted(data['location'].unique()), 
    default=["India", "United States", "Brazil"]
)

date_range = st.sidebar.date_input(
    "📅 Select date range", 
    [data['date'].min(), data['date'].max()]
)

start_date, end_date = date_range

# Filter data
filtered_data = data[
    (data['location'].isin(countries)) &
    (data['date'] >= pd.to_datetime(start_date)) &
    (data['date'] <= pd.to_datetime(end_date))
]

# Download CSV
st.sidebar.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=filtered_data.to_csv(index=False).encode('utf-8'),
    file_name='filtered_covid_data.csv',
    mime='text/csv'
)

# Summary metrics
st.subheader("🌐 Global Summary")
latest = data[data['date'] == data['date'].max()]

st.write(f"📅 Data last updated: `{data['date'].max().date()}`")
st.metric("🌍 Total Confirmed Cases", f"{int(data['total_cases'].sum()):,}")
st.metric("💚 Estimated Recovered", f"{int(data['total_cases'].sum() - data['total_deaths'].sum()):,}")
st.metric("⚰️ Total Deaths", f"{int(data['total_deaths'].sum()):,}")

# Top 10 countries by confirmed cases
st.subheader("🏆 Top 10 Countries by Confirmed Cases")
top_10 = latest.nlargest(10, 'total_cases')[['location', 'total_cases']]
st.dataframe(top_10)

# Visualizations
st.subheader("📈 Case Trends Over Time")

tab1, tab2, tab3 = st.tabs(["🦠 Total Cases", "☠️ Total Deaths", "💚 Recovered"])

with tab1:
    fig = px.line(
        filtered_data,
        x='date',
        y='total_cases',
        color='location',
        title="Total Cases Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = px.line(
        filtered_data,
        x='date',
        y='total_deaths',
        color='location',
        title="Total Deaths Over Time"
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    # Estimate recovered cases as total - deaths
    filtered_data['estimated_recovered'] = filtered_data['total_cases'] - filtered_data['total_deaths']
    fig3 = px.line(
        filtered_data,
        x='date',
        y='estimated_recovered',
        color='location',
        title="Estimated Recoveries Over Time"
    )
    st.plotly_chart(fig3, use_container_width=True)
