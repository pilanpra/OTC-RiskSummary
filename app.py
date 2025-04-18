# app.py
import streamlit as st
import pandas as pd
import json
import altair as alt

# --- Load data ---
@st.cache_data
def load_data():
    df = pd.read_csv("simulated_otc_trades_with_pse.csv")
    with open("scenarios.json", "r") as f:
        scenarios = json.load(f)["scenarios"]
    return df, scenarios

df, scenarios = load_data()

# --- Sidebar: Scenario Selection ---
st.sidebar.title("Market Scenario")
scenario_name = st.sidebar.selectbox("Select a scenario", list(scenarios.keys()))
scenario_col = f"pse_{scenario_name.replace(' ', '_').lower()}"

# --- Title ---
st.title("🧮 OTC Derivatives Risk Summary Tool")
st.markdown(f"**Scenario Selected:** {scenario_name}")

# --- KPIs ---
st.subheader("📊 Key Exposure Metrics")
total_exposure = df[scenario_col].sum()
max_exposure = df[scenario_col].max()
top_counterparty = df.loc[df[scenario_col].idxmax(), "counterparty"]

st.metric("Total PSE", f"${total_exposure:,.0f}")
st.metric("Max Trade PSE", f"${max_exposure:,.0f}")
st.metric("Most Exposed Counterparty", top_counterparty)

# --- Bar Chart: Exposure by Counterparty ---
st.subheader("🏦 Exposure by Counterparty")
exposure_by_cp = df.groupby("counterparty")[scenario_col].sum().reset_index().sort_values(by=scenario_col, ascending=False)

chart_cp = alt.Chart(exposure_by_cp).mark_bar().encode(
    x=alt.X(scenario_col, title="Total Exposure"),
    y=alt.Y("counterparty", sort='-x'),
    tooltip=["counterparty", scenario_col]
).properties(height=400)

st.altair_chart(chart_cp, use_container_width=True)

# --- Maturity Buckets ---
st.subheader("📅 Exposure by Maturity Bucket")
def maturity_bucket(days):
    if days < 90:
        return "Short (<90d)"
    elif days <= 365:
        return "Medium (90-365d)"
    else:
        return "Long (>365d)"

df["maturity_bucket"] = df["maturity_days"].apply(maturity_bucket)
exposure_by_bucket = df.groupby("maturity_bucket")[scenario_col].sum().reset_index()

chart_bucket = alt.Chart(exposure_by_bucket).mark_bar().encode(
    x=alt.X("maturity_bucket", sort=["Short (<90d)", "Medium (90-365d)", "Long (>365d)"]),
    y=alt.Y(scenario_col, title="Total Exposure"),
    tooltip=["maturity_bucket", scenario_col]
).properties(height=350)

st.altair_chart(chart_bucket, use_container_width=True)

# --- Show Full Table ---
st.subheader("📋 Full Trade Table")
st.dataframe(df[['trade_id', 'counterparty', 'trade_type', 'notional', 'rate', 'volatility', 'maturity_days', scenario_col]])

