import streamlit as st
import pandas as pd
import numpy as np

# 1. PAGE SETUP
st.set_page_config(page_title="State Logistics Sim", layout="wide")
st.title("🏛️ State Govt. PPP Logistics Simulator (₹)")

# 2. INTERACTIVE CONTROLS (Main Page)
st.markdown("### 🎛️ Network Inputs")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.subheader("📊 Demand")
    avg_daily_orders = st.slider("Total Daily Orders", 500, 5000, 2000)
    avg_pkg_wt = st.number_input("Avg Weight (kg)", value=5.0)
    avg_pkg_vol = st.number_input("Avg Volume (ft³)", value=1.2)

with col_b:
    st.subheader("🚌 Fleet")
    num_buses = st.slider("Active Buses/Day", 50, 500, 150)
    # Reducing this creates the 'Bottleneck' you need to see the graph
    avg_free_space_vol = st.slider("Unused Vol/Bus (ft³)", 5, 50, 15)
    avg_free_space_wt = st.slider("Unused Wt/Bus (kg)", 20, 200, 50)

with col_c:
    st.subheader("💰 PPP Financials")
    license_fee = st.number_input("Quarterly Fee (₹)", value=500000.0)
    revenue_per_pkg = st.number_input("Revenue (₹/pkg)", value=150.0)
    sim_days = 90

# 3. ENGINE WITH STOCHASTIC NOISE
data = []
inventory_pkgs = 0
total_rev = 0

for d in range(1, sim_days + 1):
    # Introduce 'Demand Spikes' (e.g., weekends or festivals)
    spike = 1.5 if d % 7 == 0 else 1.0
    new_orders = np.random.poisson(avg_daily_orders * spike)
    inventory_pkgs += new_orders
    
    # Capacity fluctuates (Sometimes buses are full of people, leaving less cargo space)
    daily_wt_cap = num_buses * np.random.uniform(avg_free_space_wt * 0.3, avg_free_space_wt)
    daily_vol_cap = num_buses * np.random.uniform(avg_free_space_vol * 0.3, avg_free_space_vol)
    
    can_ship_wt = daily_wt_cap // avg_pkg_wt
    can_ship_vol = daily_vol_cap // avg_pkg_vol
    shipped_today = int(min(inventory_pkgs, can_ship_wt, can_ship_vol))
    
    total_rev += (shipped_today * revenue_per_pkg)
    inventory_pkgs -= shipped_today
    
    data.append({
        "Day": d,
        "Network Inventory (Waiting)": inventory_pkgs,
        "Capacity Utilization %": (shipped_today / max(1, (daily_vol_cap/avg_pkg_vol))) * 100,
        "Daily Revenue": shipped_today * revenue_per_pkg
    })

df = pd.DataFrame(data)

# 4. DASHBOARD
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Quarterly Profit", f"₹{(total_rev - license_fee):,.0f}")
m2.metric("Max Station Backlog", f"{df['Network Inventory (Waiting)'].max():,.0f} units")
m3.metric("Fleet Efficiency", f"{round(df['Capacity Utilization %'].mean(), 1)}%")

st.subheader("📦 Network Inventory (Packages at Bus Stands)")
st.area_chart(df.set_index("Day")["Network Inventory (Waiting)"])

st.subheader("🚛 Capacity vs Usage")
st.line_chart(df.set_index("Day")["Capacity Utilization %"])
