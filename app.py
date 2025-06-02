import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import io

st.set_page_config(page_title="🌍 COVID-19 Dashboard", layout="wide")

st.title("🦠 Global COVID-19 Data Analysis")
st.markdown("Explore global COVID-19 trends with rich visualizations")

@st.cache_data(ttl=3600)
def load_data():
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    df = pd.read_csv(url)
    df['date'] = pd.to_datetime(df['date'])
    return df

data = load_data()

# Sidebar
st.sidebar.title("🔧 Filters")
countries = st.sidebar.multiselect(
    "Select countries",
    sorted(data['location'].unique()),
    default=["India", "United States", "Brazil"]
)
start_date, end_date = st.sidebar.date_input(
    "Date Range",
    [data['date'].min(), data['date'].max()]
)

filtered_data = data[
    (data['location'].isin(countries)) &
    (data['date'] >= pd.to_datetime(start_date)) &
    (data['date'] <= pd.to_datetime(end_date))
]

# CSV Download
st.sidebar.download_button(
    "⬇ Download Filtered CSV",
    filtered_data.to_csv(index=False).encode(),
    file_name="covid_filtered_data.csv"
)

# Global summary
st.subheader("📊 Global Summary")
latest = data[data['date'] == data['date'].max()]
st.metric("🌍 Confirmed", f"{int(data['total_cases'].sum()):,}")
st.metric("⚰️ Deaths", f"{int(data['total_deaths'].sum()):,}")
st.metric("💚 Recoveries (est)", f"{int(data['total_cases'].sum() - data['total_deaths'].sum()):,}")

# Tabs
tabs = st.tabs([
    "📈 Plotly Line", "📊 Pie Chart", "🏅 Top 10 Bar", "📉 Seaborn Area",
    "📚 Matplotlib Compare", "☁️ WordCloud", "📊 Streamlit Charts"
])

# 1. Plotly Line
with tabs[0]:
    st.write("### 📈 Total Cases Over Time (Plotly)")
    fig = px.line(filtered_data, x='date', y='total_cases', color='location', title="Cases Over Time")
    st.plotly_chart(fig, use_container_width=True)

# 2. Pie Chart
with tabs[1]:
    st.write("### 📊 Total Case Share by Country")
    pie_data = filtered_data.groupby("location")["total_cases"].max().reset_index()
    fig = px.pie(pie_data, names='location', values='total_cases')
    st.plotly_chart(fig, use_container_width=True)

# 3. Bar Chart of Top 10 Countries
with tabs[2]:
    st.write("### 🏅 Top 10 Countries by Confirmed Cases")
    top_10 = latest.nlargest(10, 'total_cases')[['location', 'total_cases']]
    fig = px.bar(top_10, x='location', y='total_cases', title="Top 10 Countries")
    st.plotly_chart(fig)

# 4. Seaborn Area Plot
with tabs[3]:
    st.write("### 📉 Seaborn Area Plot (Fill)")
    fig, ax = plt.subplots(figsize=(10, 5))
    for country in countries:
        country_data = filtered_data[filtered_data['location'] == country]
        ax.fill_between(country_data['date'], country_data['total_cases'], alpha=0.3, label=country)
    ax.set_title("Area Plot of Cases")
    ax.legend()
    st.pyplot(fig)

# 5. Matplotlib Compare
with tabs[4]:
    st.write("### 📚 Total Case Comparison")
    fig, ax = plt.subplots()
    for country in countries:
        sub = filtered_data[filtered_data['location'] == country]
        ax.plot(sub['date'], sub['total_cases'], label=country)
    ax.set_title("Country Case Comparison")
    ax.legend()
    st.pyplot(fig)

# 6. WordCloud
with tabs[5]:
    st.write("### ☁️ WordCloud: Total Cases by Country Name Size")
    word_data = latest[latest['location'].isin(countries)]
    text_data = {row['location']: row['total_cases'] for _, row in word_data.iterrows()}
    wc = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(text_data)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

# 7. Streamlit Native Charts
with tabs[6]:
    st.write("### 📊 Streamlit Native Charts")
    pivot_data = filtered_data.pivot_table(index='date', columns='location', values='total_cases')
    st.line_chart(pivot_data)
    st.bar_chart(pivot_data.tail(1))
