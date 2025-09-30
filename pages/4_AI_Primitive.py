import streamlit as st
import pandas as pd  # ✅ Needed for date handling
import DatabaseManager
from ai_models import train_demand_model, forecast_demand, calculate_dynamic_price

# Ensure user is logged in as admin
if "role" not in st.session_state or st.session_state.role != "admin":
    st.warning("⚠️ Access denied. Only admins can view the Management Page.")
    st.stop()

st.title("🧠 AI Features - Demand Prediction & Dynamic Pricing")

# SECTION 1 — Train Model
with st.expander('📊 Train Demand Prediction Model'):
    if st.button('Train Model'):
        df = DatabaseManager.getBookingHistory()
        result = train_demand_model(df)  # ✅ Pass df as argument
        st.success(result)

# SECTION 2 — Forecast Demand
with st.expander('📈 View Demand Forecast'):
    df = DatabaseManager.getBookingHistory()
    model = train_demand_model(df)
    
    days = st.slider('Select number of days to forecast', min_value=1, max_value=30, value=7)
    if st.button('Show Forecast'):
        forecast = forecast_demand(model, periods=days)  # ✅ Use correct parameter name
        if forecast is not None and not forecast.empty:
            st.line_chart(forecast.set_index("ds")[["yhat"]])
        else:
            st.warning("No forecast available. Train the model first or ensure enough data.")

# SECTION 3 — Dynamic Pricing
with st.expander("💸 Dynamic Room Pricing"):
    base_price = st.number_input("Enter Base Price (Rs.)", value=500.0)
    forecast_days = st.slider("Forecast Days", min_value=1, max_value=30, value=7)

    if st.button("Calculate Dynamic Price"):
        price = calculate_dynamic_price(base_price, forecast_days)
        st.success(f"Suggested Dynamic Price: Rs. {price:.2f}")

# SECTION 4 — Forecast Graph (30 Days)
with st.expander("📈 Demand Forecast for Next 30 Days"):
    df = DatabaseManager.getBookingHistory()
    model = train_demand_model(df)
    forecast = forecast_demand(model, periods=30)
    st.line_chart(forecast.set_index("ds")[["yhat"]])

# SECTION 5 — Dynamic Price by Date
with st.expander("💰 Check Dynamic Room Price"):
    roomtype_id = int(st.number_input("Enter Room Type ID", step=1,min_value=0, max_value=5))
    date = st.date_input("Select Booking Date")

    if st.button("Get Dynamic Price"):
        base_rate = DatabaseManager.getRoomBaseRate(roomtype_id)
        
        df = DatabaseManager.getBookingHistory()
        model = train_demand_model(df)
        forecast = forecast_demand(model, periods=60)

        demand_on_date = forecast[forecast["ds"] == pd.to_datetime(date)]  # ✅ pd now imported

        if not demand_on_date.empty:
            predicted_demand = demand_on_date.iloc[0]["yhat"]
            dynamic_price = calculate_dynamic_price(base_rate, predicted_demand)
            st.info(f"Base Rate: {base_rate} | Predicted Demand: {int(predicted_demand)}")
            st.success(f"💸 Dynamic Price: Rs. {dynamic_price:.2f}")
        else:
            st.warning("No forecast available for the selected date.")