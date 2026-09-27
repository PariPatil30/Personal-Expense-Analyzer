import pandas as pd
import numpy as np


def detect_anomalies(df):
    """
    Detect unusually high expenses using the
    Interquartile Range (IQR) method.

    Returns:
        DataFrame containing the original expenses
        plus anomaly information.
    """

    # Make a copy so the original DataFrame
    # is not modified
    data = df.copy()

    # Make sure Amount is numeric
    data["Amount"] = pd.to_numeric(
        data["Amount"],
        errors="coerce"
    )

    # Remove invalid amounts
    data = data.dropna(
        subset=["Amount"]
    )

    # Need enough data points for meaningful
    # statistical analysis
    if len(data) < 4:

        data["Is Anomaly"] = False
        data["Anomaly Score"] = 0.0
        data["Anomaly Reason"] = (
            "Not enough data for anomaly detection"
        )

        return data


    # =====================================================
    # IQR CALCULATION
    # =====================================================

    q1 = data["Amount"].quantile(0.25)

    q3 = data["Amount"].quantile(0.75)

    iqr = q3 - q1


    # Calculate upper statistical boundary
    upper_limit = q3 + (1.5 * iqr)


    # =====================================================
    # ANOMALY DETECTION
    # =====================================================

    data["Is Anomaly"] = (
        data["Amount"] > upper_limit
    )


    # =====================================================
    # ANOMALY SCORE
    # =====================================================

    if iqr > 0:

        data["Anomaly Score"] = (
            (data["Amount"] - q3) / iqr
        )

    else:

        data["Anomaly Score"] = 0.0


    # Make scores easier to understand

    data["Anomaly Score"] = (
        data["Anomaly Score"]
        .clip(lower=0)
        .round(2)
    )


    # =====================================================
    # EXPLANATION
    # =====================================================

    data["Anomaly Reason"] = np.where(
        data["Is Anomaly"],
        "This expense is unusually high compared with your normal spending pattern.",
        "Expense is within the normal spending range."
    )


    return data


# =========================================================
# GET ONLY ANOMALOUS EXPENSES
# =========================================================

def get_anomalies(df):

    analyzed_data = detect_anomalies(
        df
    )

    anomalies = analyzed_data[
        analyzed_data["Is Anomaly"]
    ].copy()


    return anomalies


# =========================================================
# SUMMARY
# =========================================================

def get_anomaly_summary(df):

    analyzed_data = detect_anomalies(
        df
    )


    total_expenses = len(
        analyzed_data
    )


    anomaly_count = int(
        analyzed_data["Is Anomaly"].sum()
    )


    if total_expenses > 0:

        anomaly_percentage = (
            anomaly_count
            / total_expenses
        ) * 100

    else:

        anomaly_percentage = 0


    return {
        "total_expenses": total_expenses,
        "anomaly_count": anomaly_count,
        "anomaly_percentage": round(
            anomaly_percentage,
            2
        )
    }