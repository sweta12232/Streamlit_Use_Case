import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Advanced Retail Dashboard",
    page_icon="...",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. Data Loading & Caching
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(num_rows=50000):
    np.random.seed(42)
    dates = pd.date_range(start="2025-01-01", periods=365)
    random_dates = np.random.choice(dates, num_rows)
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports"]
    regions = ["North America", "Europe", "Asia", "South America"]
    
    data = {
        "Date": random_dates,
        "Category": np.random.choice(categories, num_rows),
        "Region": np.random.choice(regions, num_rows),
        "Sales": np.random.uniform(10, 500, num_rows),
        "Profit": np.random.uniform(-10, 200, num_rows) # Note: some profits are negative
    }
    
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

# -----------------------------------------------------------------------------
# 3. Sidebar Filters
# -----------------------------------------------------------------------------
st.sidebar.title(" Filter Options")

all_regions = df['Region'].unique().tolist()
selected_regions = st.sidebar.multiselect("Select Region(s):", all_regions, all_regions)

all_categories = ["All"] + df['Category'].unique().tolist()
selected_category = st.sidebar.selectbox("Select Category:", all_categories)

filtered_df = df[df['Region'].isin(selected_regions)]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

# Prevent errors if all filters are cleared
if filtered_df.empty:
    st.warning("Please select at least one region and category.")
    st.stop()

# -----------------------------------------------------------------------------
# 4. Main Dashboard & KPIs
# -----------------------------------------------------------------------------
st.title("Advanced Retail Analytics")
st.markdown("Explore regional performance, categorical market share, and profitability metrics.")

# Calculate KPIs
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
avg_transaction = filtered_df['Sales'].mean()
profit_margin = (total_profit / total_sales) * 100

# Display KPIs in 4 columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales Revenue", f"${total_sales:,.0f}")
col2.metric("Total Profit", f"${total_profit:,.0f}")
col3.metric("Profit Margin", f"{profit_margin:.1f}%")
col4.metric("Avg Transaction", f"${avg_transaction:,.2f}")

st.divider()

# -----------------------------------------------------------------------------
# 5. Automated Data Insights
# -----------------------------------------------------------------------------
# Find the best performing category and month dynamically
best_category = filtered_df.groupby('Category')['Sales'].sum().idxmax()
best_month = filtered_df.groupby('Month')['Sales'].sum().idxmax()

st.info(f" **Quick Insight:** Based on your current filters, **{best_category}** generates the most revenue, and **{best_month}** was the highest-performing month.")

# -----------------------------------------------------------------------------
# 6. Advanced Visualizations
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([" Trends", " Region", " Category", " Correlation"])

with tab1:
    st.subheader("Monthly Revenue Trends")
    monthly_sales = filtered_df.groupby('Month')['Sales'].sum().reset_index()
    fig_trend = px.line(monthly_sales, x='Month', y='Sales', markers=True, 
                        title="Sales Over Time", template="plotly_white")
    st.plotly_chart(fig_trend, use_container_width=True)

with tab2:
    st.subheader("Profitability by Region")
    fig_region = px.bar(
        filtered_df, 
        x='Region', 
        y='Profit', 
        color='Category', 
        barmode='group', 
        title="Profit Distribution",
        color_discrete_sequence=px.colors.qualitative.Pastel # Or Bold, Vivid, etc.
    )
    
    # ADD theme=None HERE to stop Streamlit from making it dark/dull
    st.plotly_chart(fig_region, use_container_width=True, theme=None)
    
with tab3:
    st.subheader("Market Share by Category")
    # Added a Donut Chart for proportional viewing
    cat_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
    fig_pie = px.pie(cat_sales, values='Sales', names='Category', hole=0.4, 
                     title="Sales Distribution (%)", template="plotly_white")
    st.plotly_chart(fig_pie, use_container_width=True)

with tab4:
    st.subheader("Sales vs. Profit Analysis")
    st.markdown("Use this scatter plot to identify high-revenue, low-profit outlier transactions.")
    # Added a Scatter plot to show correlation; taking a sample so the browser doesn't freeze
    sample_df = filtered_df.sample(n=min(2000, len(filtered_df)), random_state=42)
    fig_scatter = px.scatter(sample_df, x='Sales', y='Profit', color='Category', 
                             hover_data=['Region', 'Date'], opacity=0.7,
                             title="Sales vs Profit (Sampled 2000 records)", template="plotly_white")
    st.plotly_chart(fig_scatter, use_container_width=True)

# -----------------------------------------------------------------------------
# 7. Raw Data
# -----------------------------------------------------------------------------
with st.expander("🔎 View Raw Data"):
    st.dataframe(filtered_df.head(100), use_container_width=True)