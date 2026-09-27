import pandas as pd


def prepare_monthly_spending(df):
    """
    Convert expense data into monthly spending totals.
    """

    data = df.copy()

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce"
    )

    data["Amount"] = pd.to_numeric(
        data["Amount"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["Date", "Amount"]
    )

    monthly_spending = (
        data.groupby(
            data["Date"].dt.to_period("M")
        )["Amount"]
        .sum()
        .sort_index()
    )

    return monthly_spending


def forecast_next_month(df):
    """
    Estimate next month's spending using
    previous monthly spending.
    """

    monthly_spending = prepare_monthly_spending(df)

    if len(monthly_spending) == 0:
        return None

    if len(monthly_spending) == 1:
        forecast = monthly_spending.iloc[-1]

    elif len(monthly_spending) < 3:
        forecast = monthly_spending.mean()

    else:
        recent_months = monthly_spending.tail(3)
        forecast = recent_months.mean()

    next_month = (
        monthly_spending.index[-1] + 1
    )

    return {
        "next_month": str(next_month),
        "forecast": round(float(forecast), 2),
        "monthly_data": monthly_spending
    }


def get_forecast_message(forecast_data):
    """
    Generate a simple explanation for the forecast.
    """

    if forecast_data is None:
        return "Not enough data to generate a forecast."

    amount = forecast_data["forecast"]
    month = forecast_data["next_month"]

    return (
        f"Based on your previous spending pattern, "
        f"your estimated spending for {month} is "
        f"₹{amount:,.2f}."
    )