from prophet import Prophet
import pandas as pd

def train_demand_model(df):
    df = df.groupby("BookingDate").size().reset_index(name="y")
    df.rename(columns={"BookingDate": "ds"}, inplace=True)

    model = Prophet()
    model.fit(df)
    return model

def forecast_demand(model, periods=30):
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

def calculate_dynamic_price(base_price, forecasted_demand):
    if forecasted_demand > 50:  # threshold
        return round(base_price * 1.2, 2)  # 20% increase
    elif forecasted_demand < 20:
        return round(base_price * 0.9, 2)  # 10% discount
    return base_price