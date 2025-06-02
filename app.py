import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="🌍 COVID-19 Dashboard", layout="wide")

st.title("🦠 Global COVID-19 Data Analysis")
st.markdown("Explore trends using Plotly, Seaborn, and Matplotlib")

@st.cache_data(ttl=3600)
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

# CSV Download
st.sidebar.download_button(
    label="⬇️ Download Filtered CSV",
    data=filtered_data.to_csv(index=False).encode('utf-8'),
    file_name='filtered_covid_data.csv',
    mime='text/csv'
)

# Summary
st.subheader("📌 Global Summary")
latest = data[data['date'] == data['date'].max()]
st.metric("🌍 Total Confirmed", f"{int(data['total_cases'].sum()):,}")
st.metric("⚰️ Total Deaths", f"{int(data['total_deaths'].sum()):,}")
st.metric("💚 Estimated Recoveries", f"{int(data['total_cases'].sum() - data['total_deaths'].sum()):,}")

# Top countries
st.subheader("🏆 Top 10 Countries by Confirmed Cases")
top_10 = latest.nlargest(10, 'total_cases')[['location', 'total_cases']]
st.dataframe(top_10)

# Tabs for visualizations
st.subheader("📊 Visualizations")
tabs = st.tabs(["📈 Plotly", "📊 Seaborn", "🖼️ Matplotlib", "🔥 Heatmap"])

# Plotly
with tabs[0]:
    st.write("### Plotly: Total Cases Over Time")
    fig = px.line(
        filtered_data, 
        x='date', y='total_cases', 
        color='location', 
        title="Total Cases Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)

# Seaborn 
with tabs[1]:
    st.write("### Seaborn: Total Cases Over Time")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=filtered_data, x='date', y='total_cases', hue='location', ax=ax)
    ax.set_title("Total Cases Over Time (Seaborn)")
    st.pyplot(fig)

# Matplotlib
with tabs[2]:
    st.write("### Matplotlib: Total Cases Over Time")
    fig, ax = plt.subplots(figsize=(10, 5))
    for country in countries:
        country_data = filtered_data[filtered_data['location'] == country]
        ax.plot(country_data['date'], country_data['total_cases'], label=country)
    ax.set_title("Total Cases Over Time (Matplotlib)")
    ax.legend()
    st.pyplot(fig)
