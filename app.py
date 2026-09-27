import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


from database import (
    create_database,
    add_expense,
    get_expenses,
    delete_expense,
    update_expense,
    save_budget,
    get_budget
)

from anomaly_detection import (
    get_anomalies,
    get_anomaly_summary
)

from prediction import (
    forecast_next_month,
    get_forecast_message
)


# =========================================================
# DATABASE
# =========================================================

create_database()


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Personal Expense Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DARK MODERN THEME
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 80% 0%,
                rgba(124, 58, 237, 0.10),
                transparent 30%
            ),
            radial-gradient(
                circle at 0% 100%,
                rgba(37, 99, 235, 0.08),
                transparent 28%
            ),
            #080b12;
        color: #f8fafc;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 4rem;
        padding-bottom: 3rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    h1,
    h2,
    h3,
    h4 {
        color: #f8fafc !important;
    }

    p {
        color: #cbd5e1;
    }

    .stCaption {
        color: #64748b !important;
    }

    /* SIDEBAR */

    section[data-testid="stSidebar"] {
        background: #0b0f17;
        border-right: 1px solid #1e293b;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: #f8fafc !important;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] {
        gap: 5px;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] label {
        color: #cbd5e1 !important;
        border-radius: 10px;
        padding: 8px 10px;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] label:hover {
        background: #151b28;
        color: #ffffff !important;
    }

    /* METRICS */

    div[data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                #111827,
                #0d1320
            );
        border: 1px solid #1f2937;
        border-radius: 17px;
        padding: 18px;
        box-shadow:
            0 8px 28px rgba(0, 0, 0, 0.18);
    }

    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 750;
    }

    div[data-testid="stMetricDelta"] {
        color: #94a3b8 !important;
    }

    /* INPUTS */

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input {
        background: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #263248 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] > div {
        background: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #263248 !important;
        border-radius: 10px !important;
    }

    /* BUTTONS */

    .stButton > button {
        background:
            linear-gradient(
                135deg,
                #7c3aed,
                #4f46e5
            );
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 650;
        min-height: 42px;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
    }

    .stDownloadButton > button {
        background: #111827;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 10px;
        font-weight: 600;
    }

    /* TABS */

    button[data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 600;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #c4b5fd !important;
    }

    /* TABLES */

    div[data-testid="stDataFrame"] {
        border: 1px solid #1e293b;
        border-radius: 13px;
        overflow: hidden;
    }

    /* ALERTS */

    div[data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid #263248;
    }

    /* EXPANDERS */

    div[data-testid="stExpander"] {
        background: #0d1320;
        border: 1px solid #1f2937;
        border-radius: 12px;
    }

    /* PROGRESS */

    div[data-testid="stProgressBar"] {
        background: #111827;
        border-radius: 20px;
    }

    /* DIVIDERS */

    hr {
        border-color: #1e293b !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HELPER FUNCTION
# =========================================================

def create_dataframe(expenses):

    df = pd.DataFrame(
        expenses,
        columns=[
            "ID",
            "Date",
            "Category",
            "Description",
            "Amount",
            "Payment Method"
        ]
    )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df["Amount"] = pd.to_numeric(
        df["Amount"],
        errors="coerce"
    )

    df["Description"] = (
        df["Description"]
        .fillna("")
        .astype(str)
    )

    df = df.dropna(
        subset=[
            "Date",
            "Amount"
        ]
    )

    return df.sort_values(
        "Date"
    )


def get_dashboard_period(
    all_df,
    period_option
):

    today = (
        pd.Timestamp.today()
        .normalize()
    )

    if period_option == "All Time":

        start_date = (
            all_df["Date"]
            .min()
            .normalize()
        )

        end_date = today

    elif period_option == "This Month":

        start_date = (
            today.replace(day=1)
        )

        end_date = today

    elif period_option == "Last Month":

        start_date = (
            today.replace(day=1)
            - pd.DateOffset(months=1)
        )

        end_date = (
            today.replace(day=1)
            - pd.Timedelta(days=1)
        )

    else:

        start_date = (
            today.replace(day=1)
            - pd.DateOffset(months=2)
        )

        end_date = today

    return start_date, end_date


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "💰 Expense Analyzer"
)

st.sidebar.caption(
    "Personal Finance Intelligence"
)

st.sidebar.divider()

st.sidebar.markdown(
    "**Navigation**"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Expense",
        "Expense History",
        "Edit Expense",
        "Delete Expense",
        "Budget"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()

st.sidebar.caption(
    "Python • Streamlit • Pandas • SQLite"
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    expenses = get_expenses()

    if not expenses:

        st.title(
            "Welcome 👋"
        )

        st.info(
            "You don't have any expenses yet. "
            "Go to **Add Expense** to get started."
        )

        st.stop()


    # =====================================================
    # DATA
    # =====================================================

    all_df = create_dataframe(
        expenses
    )


    # =====================================================
    # HEADER
    # =====================================================

    title_col, filter_col = st.columns(
        [4, 1]
    )

    with title_col:

        st.title(
            "📊 Dashboard"
        )

        st.caption(
            "Your spending, visualized."
        )

    with filter_col:

        period_option = st.selectbox(
            "Period",
            [
                "All Time",
                "This Month",
                "Last Month",
                "Last 3 Months"
            ]
        )


    # =====================================================
    # FILTER PERIOD
    # =====================================================

    start_date, end_date = get_dashboard_period(
        all_df,
        period_option
    )


    df = all_df[
        (
            all_df["Date"]
            >= start_date
        )
        &
        (
            all_df["Date"]
            <= end_date
        )
    ].copy()


    if df.empty:

        st.warning(
            f"No expenses found for **{period_option}**."
        )

        st.stop()


    st.caption(
        f"{start_date.strftime('%d %b %Y')} "
        f"→ "
        f"{end_date.strftime('%d %b %Y')}"
    )


    # =====================================================
    # KPI
    # =====================================================

    total_spending = (
        df["Amount"].sum()
    )

    transaction_count = (
        len(df)
    )

    average_expense = (
        df["Amount"].mean()
    )


    today = (
        pd.Timestamp.today()
        .normalize()
    )


    current_month = (
        today.strftime("%Y-%m")
    )


    current_budget = get_budget(
        current_month
    )


    current_month_spending = (
        all_df[
            all_df["Date"]
            .dt.strftime("%Y-%m")
            == current_month
        ]["Amount"]
        .sum()
    )


    budget_remaining = (
        current_budget
        - current_month_spending
    )


    st.subheader(
        "Overview"
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "💸 Total Spending",
            f"₹{total_spending:,.0f}"
        )


    with col2:

        st.metric(
            "🧾 Transactions",
            transaction_count
        )


    with col3:

        st.metric(
            "📊 Average Expense",
            f"₹{average_expense:,.0f}"
        )


    with col4:

        st.metric(
            "💰 Budget Left",
            f"₹{budget_remaining:,.0f}"
        )


    st.divider()


    # =====================================================
    # TABS
    # =====================================================

    overview_tab, analytics_tab = st.tabs(
        [
            "🏠 Overview",
            "📊 Advanced Analytics"
        ]
    )


    # =====================================================
    # OVERVIEW
    # =====================================================

    with overview_tab:

        # -------------------------------------------------
        # CALCULATIONS
        # -------------------------------------------------

        category_spending = (
            df.groupby(
                "Category"
            )["Amount"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        payment_spending = (
            df.groupby(
                "Payment Method"
            )["Amount"]
            .sum()
            .sort_values(
                ascending=False
            )
        )


        daily_spending = (
            df.groupby(
                "Date"
            )["Amount"]
            .sum()
        )


        top_category = (
            category_spending.index[0]
        )


        top_category_amount = (
            category_spending.iloc[0]
        )


        top_category_percentage = (
            top_category_amount
            / total_spending
            * 100
        )


        biggest_expense = (
            df.loc[
                df["Amount"].idxmax()
            ]
        )


        most_used_payment = (
            df["Payment Method"]
            .value_counts()
            .index[0]
        )


        # -------------------------------------------------
        # SPENDING TREND
        # -------------------------------------------------

        st.subheader(
            "📈 Spending Trend"
        )


        if PLOTLY_AVAILABLE:

            trend_df = (
                daily_spending
                .reset_index()
            )


            fig = px.area(
                trend_df,
                x="Date",
                y="Amount"
            )


            fig.update_traces(
                line_color="#8b5cf6",
                fillcolor="rgba(139,92,246,0.12)"
            )


            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                xaxis_title=None,
                yaxis_title=None,
                margin=dict(
                    l=10,
                    r=10,
                    t=10,
                    b=10
                ),
                height=330
            )


            fig.update_xaxes(
                showgrid=False
            )


            fig.update_yaxes(
                gridcolor="#1e293b"
            )


            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )

        else:

            st.line_chart(
                daily_spending
            )


        st.divider()


        # -------------------------------------------------
        # CATEGORY + INSIGHTS
        # -------------------------------------------------

        col1, col2 = st.columns(
            [2, 1]
        )


        with col1:

            st.subheader(
                "🍩 Where Your Money Goes"
            )


            if PLOTLY_AVAILABLE:

                pie_df = (
                    category_spending
                    .reset_index()
                )


                fig = px.pie(
                    pie_df,
                    names="Category",
                    values="Amount",
                    hole=0.62
                )


                fig.update_traces(
                    textposition="inside",
                    textinfo="percent"
                )


                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#cbd5e1",
                    margin=dict(
                        l=10,
                        r=10,
                        t=10,
                        b=10
                    ),
                    height=350
                )


                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "displayModeBar": False
                    }
                )

            else:

                st.bar_chart(
                    category_spending
                )


        with col2:

            st.subheader(
                "🧠 Key Insights"
            )


            st.info(
                f"🏆 **Top Category**\n\n"
                f"{top_category}\n\n"
                f"₹{top_category_amount:,.0f} "
                f"({top_category_percentage:.1f}%)"
            )


            st.info(
                f"💸 **Largest Expense**\n\n"
                f"₹{biggest_expense['Amount']:,.0f}\n\n"
                f"{biggest_expense['Description'] or 'No description'}"
            )


            st.info(
                f"💳 **Most Used Payment**\n\n"
                f"{most_used_payment}"
            )


        st.divider()


        # -------------------------------------------------
        # ANOMALY + FORECAST
        # -------------------------------------------------

        col1, col2 = st.columns(2)


        with col1:

            st.subheader(
                "🚨 Unusual Spending"
            )


            anomaly_summary = (
                get_anomaly_summary(df)
            )


            anomalies = (
                get_anomalies(df)
            )


            a1, a2 = st.columns(2)


            with a1:

                st.metric(
                    "Unusual Expenses",
                    anomaly_summary[
                        "anomaly_count"
                    ]
                )


            with a2:

                st.metric(
                    "Anomaly %",
                    f'{anomaly_summary["anomaly_percentage"]:.1f}%'
                )


            if len(df) < 4:

                st.caption(
                    "Add at least 4 expenses in this period "
                    "for anomaly detection."
                )


            elif not anomalies.empty:

                st.warning(
                    f"{len(anomalies)} unusual expense(s) detected."
                )


                with st.expander(
                    "View detected expenses"
                ):

                    anomaly_display = anomalies[
                        [
                            "Date",
                            "Category",
                            "Description",
                            "Amount",
                            "Anomaly Score"
                        ]
                    ].copy()


                    anomaly_display["Date"] = (
                        anomaly_display["Date"]
                        .dt.strftime("%Y-%m-%d")
                    )


                    st.dataframe(
                        anomaly_display,
                        use_container_width=True,
                        hide_index=True
                    )


            else:

                st.success(
                    "No unusually high expenses detected."
                )


        with col2:

            st.subheader(
                "🔮 Next Month Forecast"
            )


            forecast_data = (
                forecast_next_month(
                    all_df
                )
            )


            if forecast_data is None:

                st.info(
                    "Not enough historical data "
                    "for a forecast."
                )


            else:

                forecast_amount = (
                    forecast_data["forecast"]
                )


                forecast_month = (
                    forecast_data["next_month"]
                )


                historical_average = (
                    forecast_data[
                        "monthly_data"
                    ].mean()
                )


                f1, f2 = st.columns(2)


                with f1:

                    st.metric(
                        "Estimated",
                        f"₹{forecast_amount:,.0f}"
                    )


                with f2:

                    st.metric(
                        "Historical Average",
                        f"₹{historical_average:,.0f}"
                    )


                st.info(
                    get_forecast_message(
                        forecast_data
                    )
                )


                with st.expander(
                    "View forecast trend"
                ):

                    forecast_chart = (
                        forecast_data[
                            "monthly_data"
                        ].copy()
                    )


                    next_period = pd.Period(
                        forecast_month,
                        freq="M"
                    )


                    forecast_chart.loc[
                        next_period
                    ] = forecast_amount


                    forecast_chart.index = (
                        forecast_chart.index
                        .astype(str)
                    )


                    st.line_chart(
                        forecast_chart
                    )


        st.divider()


        # =================================================
        # CURRENT MONTH BUDGET
        # =================================================

        st.subheader(
            "💰 Current Month Budget"
        )


        budget_percentage = (
            current_month_spending
            / current_budget
            * 100
            if current_budget > 0
            else 0
        )


        b1, b2, b3 = st.columns(3)


        with b1:

            st.metric(
                "Budget",
                f"₹{current_budget:,.0f}"
            )


        with b2:

            st.metric(
                "Spent",
                f"₹{current_month_spending:,.0f}"
            )


        with b3:

            st.metric(
                "Remaining",
                f"₹{budget_remaining:,.0f}"
            )


        st.progress(
            min(
                max(
                    budget_percentage / 100,
                    0
                ),
                1
            )
        )


        st.caption(
            f"{budget_percentage:.1f}% of your current "
            f"monthly budget has been used."
        )


    # =====================================================
    # ADVANCED ANALYTICS
    # =====================================================

    with analytics_tab:

        st.subheader(
            "📊 Advanced Analytics"
        )


        st.caption(
            "Detailed analysis of the selected period."
        )


        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        st.write(
            "### 🥧 Category Contribution"
        )


        category_percentage = (
            category_spending
            / total_spending
            * 100
        )


        category_table = pd.DataFrame(
            {
                "Category": category_spending.index,
                "Total Spending": category_spending.values,
                "Percentage": category_percentage.values
            }
        )


        category_table[
            "Total Spending"
        ] = (
            category_table[
                "Total Spending"
            ].round(2)
        )


        category_table[
            "Percentage"
        ] = (
            category_table[
                "Percentage"
            ].round(1)
        )


        st.dataframe(
            category_table,
            use_container_width=True,
            hide_index=True
        )


        if PLOTLY_AVAILABLE:

            category_chart = (
                category_table
                .copy()
            )


            fig = px.bar(
                category_chart,
                x="Category",
                y="Total Spending",
                text="Percentage"
            )


            fig.update_traces(
                marker_color="#8b5cf6"
            )


            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                xaxis_title=None,
                yaxis_title="₹"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


        st.divider()


        # -------------------------------------------------
        # DAY OF WEEK
        # -------------------------------------------------

        st.write(
            "### 📅 Spending by Day of Week"
        )


        df["Day of Week"] = (
            df["Date"]
            .dt.day_name()
        )


        weekday_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]


        weekday_spending = (
            df.groupby(
                "Day of Week"
            )["Amount"]
            .sum()
            .reindex(
                weekday_order
            )
            .fillna(0)
        )


        if PLOTLY_AVAILABLE:

            weekday_df = (
                weekday_spending
                .reset_index()
            )


            fig = px.bar(
                weekday_df,
                x="Day of Week",
                y="Amount"
            )


            fig.update_traces(
                marker_color="#2563eb"
            )


            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                xaxis_title=None,
                yaxis_title="₹"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.bar_chart(
                weekday_spending
            )


        highest_weekday = (
            weekday_spending
            .idxmax()
        )


        st.info(
            f"Highest spending weekday: "
            f"**{highest_weekday}** — "
            f"₹{weekday_spending.max():,.0f}"
        )


        st.divider()


        # -------------------------------------------------
        # MONTHLY
        # -------------------------------------------------

        st.write(
            "### 📆 Monthly Spending"
        )


        monthly_spending = (
            df.groupby(
                df["Date"]
                .dt.to_period("M")
            )["Amount"]
            .sum()
        )


        monthly_chart = (
            monthly_spending
            .copy()
        )


        monthly_chart.index = (
            monthly_chart.index
            .astype(str)
        )


        if PLOTLY_AVAILABLE:

            monthly_df = (
                monthly_chart
                .reset_index()
            )


            monthly_df.columns = [
                "Month",
                "Amount"
            ]


            fig = px.line(
                monthly_df,
                x="Month",
                y="Amount",
                markers=True
            )


            fig.update_traces(
                line_color="#22c55e"
            )


            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                xaxis_title=None,
                yaxis_title="₹"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.line_chart(
                monthly_chart
            )


        st.divider()


        # -------------------------------------------------
        # PAYMENT METHOD
        # -------------------------------------------------

        st.write(
            "### 💳 Payment Method Analysis"
        )


        if PLOTLY_AVAILABLE:

            payment_df = (
                payment_spending
                .reset_index()
            )


            fig = px.bar(
                payment_df,
                x="Payment Method",
                y="Amount"
            )


            fig.update_traces(
                marker_color="#f59e0b"
            )


            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                xaxis_title=None,
                yaxis_title="₹"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.bar_chart(
                payment_spending
            )


        st.divider()


        # -------------------------------------------------
        # BUDGET VS ACTUAL
        # -------------------------------------------------

        st.write(
            "### 💰 Budget vs Actual"
        )


        all_months = (
            all_df["Date"]
            .dt.to_period("M")
            .astype(str)
            .unique()
            .tolist()
        )


        current_month_for_budget = (
            date.today()
            .strftime("%Y-%m")
        )


        if current_month_for_budget not in all_months:

            all_months.append(
                current_month_for_budget
            )


        all_months = sorted(
            all_months,
            reverse=True
        )


        selected_budget_month = st.selectbox(
            "Select Month",
            all_months,
            key="analytics_budget_month"
        )


        selected_budget = get_budget(
            selected_budget_month
        )


        selected_actual = all_df[
            all_df["Date"]
            .dt.strftime("%Y-%m")
            == selected_budget_month
        ]["Amount"].sum()


        selected_remaining = (
            selected_budget
            - selected_actual
        )


        selected_percentage = (
            selected_actual
            / selected_budget
            * 100
            if selected_budget > 0
            else 0
        )


        c1, c2, c3 = st.columns(3)


        with c1:

            st.metric(
                "Budget",
                f"₹{selected_budget:,.0f}"
            )


        with c2:

            st.metric(
                "Actual Spending",
                f"₹{selected_actual:,.0f}"
            )


        with c3:

            st.metric(
                "Remaining",
                f"₹{selected_remaining:,.0f}"
            )


        st.progress(
            min(
                max(
                    selected_percentage / 100,
                    0
                ),
                1
            )
        )


        st.caption(
            f"{selected_percentage:.1f}% of budget used."
        )


        if selected_remaining < 0:

            st.error(
                f"Over budget by "
                f"₹{abs(selected_remaining):,.0f}"
            )

        else:

            st.success(
                f"₹{selected_remaining:,.0f} remaining."
            )


        st.divider()


        # -------------------------------------------------
        # TOP 5
        # -------------------------------------------------

        st.write(
            "### 💸 Top 5 Largest Expenses"
        )


        top_expenses = (
            df.sort_values(
                "Amount",
                ascending=False
            )
            .head(5)
        )


        top_display = (
            top_expenses[
                [
                    "Date",
                    "Category",
                    "Description",
                    "Amount",
                    "Payment Method"
                ]
            ].copy()
        )


        top_display["Date"] = (
            top_display["Date"]
            .dt.strftime("%Y-%m-%d")
        )


        st.dataframe(
            top_display,
            use_container_width=True,
            hide_index=True
        )


    # =====================================================
    # EXPORT
    # =====================================================

    st.divider()


    st.subheader(
        "📥 Export Data"
    )


    export_df = df.copy()


    if "Day of Week" in export_df.columns:

        export_df = export_df.drop(
            columns=["Day of Week"]
        )


    export_df["Date"] = (
        export_df["Date"]
        .dt.strftime("%Y-%m-%d")
    )


    csv_data = (
        export_df.to_csv(
            index=False
        )
    )


    excel_buffer = BytesIO()


    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        export_df.to_excel(
            writer,
            sheet_name="Expenses",
            index=False
        )


        category_export = (
            df.groupby(
                "Category"
            )["Amount"]
            .sum()
            .reset_index()
            .sort_values(
                "Amount",
                ascending=False
            )
        )


        category_export.columns = [
            "Category",
            "Total Spending"
        ]


        category_export.to_excel(
            writer,
            sheet_name="Category Summary",
            index=False
        )


        monthly_export = (
            monthly_spending
            .reset_index()
        )


        monthly_export.columns = [
            "Month",
            "Total Spending"
        ]


        monthly_export["Month"] = (
            monthly_export[
                "Month"
            ].astype(str)
        )


        monthly_export.to_excel(
            writer,
            sheet_name="Monthly Summary",
            index=False
        )


    excel_buffer.seek(0)


    e1, e2 = st.columns(2)


    with e1:

        st.download_button(
            "📄 Download CSV",
            csv_data,
            "expense_data.csv",
            "text/csv"
        )


    with e2:

        st.download_button(
            "📊 Download Excel",
            excel_buffer,
            "expense_analysis.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# =========================================================
# ADD EXPENSE
# =========================================================

elif page == "Add Expense":

    st.title(
        "➕ Add Expense"
    )

    st.caption(
        "Record a transaction and keep your spending organised."
    )


    with st.form(
        "add_expense_form"
    ):

        col1, col2 = st.columns(2)


        with col1:

            expense_date = st.date_input(
                "Date",
                value=date.today(),
                max_value=date.today()
            )


            category = st.selectbox(
                "Category",
                [
                    "Food",
                    "Transport",
                    "Shopping",
                    "Education",
                    "Entertainment",
                    "Bills",
                    "Health",
                    "Other"
                ]
            )


        with col2:

            description = st.text_input(
                "Description",
                placeholder="e.g. Lunch at college"
            )


            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                step=10.0
            )


        payment_method = st.selectbox(
            "Payment Method",
            [
                "UPI",
                "Cash",
                "Debit Card",
                "Credit Card"
            ]
        )


        submitted = st.form_submit_button(
            "➕ Save Expense"
        )


    if submitted:

        if not description.strip():

            st.error(
                "Please enter a description."
            )

        elif amount <= 0:

            st.error(
                "Amount must be greater than ₹0."
            )

        elif expense_date > date.today():

            st.error(
                "Expense date cannot be in the future."
            )

        else:

            add_expense(
                str(expense_date),
                category,
                description.strip(),
                amount,
                payment_method
            )


            st.success(
                "Expense saved successfully! 💰"
            )


            st.rerun()


# =========================================================
# EXPENSE HISTORY
# =========================================================

elif page == "Expense History":

    st.title(
        "📋 Expense History"
    )


    st.caption(
        "Search and filter your transactions."
    )


    expenses = get_expenses()


    if not expenses:

        st.info(
            "No expenses added yet."
        )

        st.stop()


    df = create_dataframe(
        expenses
    )


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search_text = st.text_input(
        "🔎 Search Description",
        placeholder="lunch, shopping, transport..."
    )


    # -----------------------------------------------------
    # CATEGORY + PAYMENT
    # -----------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        categories = [
            "All"
        ] + sorted(
            df["Category"]
            .unique()
            .tolist()
        )


        selected_category = st.selectbox(
            "Category",
            categories
        )


    with col2:

        payment_methods = [
            "All"
        ] + sorted(
            df["Payment Method"]
            .unique()
            .tolist()
        )


        selected_payment = st.selectbox(
            "Payment Method",
            payment_methods
        )


    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    selected_dates = st.date_input(
        "Date Range",
        value=(
            df["Date"].min().date(),
            df["Date"].max().date()
        )
    )


    # -----------------------------------------------------
    # AMOUNT
    # -----------------------------------------------------

    minimum_amount = float(
        df["Amount"].min()
    )


    maximum_amount = float(
        df["Amount"].max()
    )


    col1, col2 = st.columns(2)


    with col1:

        min_amount = st.number_input(
            "Minimum Amount (₹)",
            min_value=0.0,
            value=minimum_amount,
            step=50.0
        )


    with col2:

        max_amount = st.number_input(
            "Maximum Amount (₹)",
            min_value=0.0,
            value=maximum_amount,
            step=50.0
        )


    # =====================================================
    # APPLY FILTERS
    # =====================================================

    filtered_df = df.copy()


    if search_text.strip():

        filtered_df = filtered_df[
            filtered_df[
                "Description"
            ].str.contains(
                search_text.strip(),
                case=False,
                na=False
            )
        ]


    if selected_category != "All":

        filtered_df = filtered_df[
            filtered_df[
                "Category"
            ]
            == selected_category
        ]


    if selected_payment != "All":

        filtered_df = filtered_df[
            filtered_df[
                "Payment Method"
            ]
            == selected_payment
        ]


    if len(selected_dates) == 2:

        start = pd.Timestamp(
            selected_dates[0]
        )


        end = (
            pd.Timestamp(
                selected_dates[1]
            )
            + pd.Timedelta(days=1)
            - pd.Timedelta(seconds=1)
        )


        filtered_df = filtered_df[
            (
                filtered_df["Date"]
                >= start
            )
            &
            (
                filtered_df["Date"]
                <= end
            )
        ]


    if min_amount <= max_amount:

        filtered_df = filtered_df[
            (
                filtered_df["Amount"]
                >= min_amount
            )
            &
            (
                filtered_df["Amount"]
                <= max_amount
            )
        ]

    else:

        st.error(
            "Minimum amount cannot be greater than maximum amount."
        )


    st.divider()


    # =====================================================
    # FILTER METRICS
    # =====================================================

    filtered_total = (
        filtered_df["Amount"]
        .sum()
    )


    filtered_count = (
        len(filtered_df)
    )


    filtered_average = (
        filtered_df["Amount"].mean()
        if not filtered_df.empty
        else 0
    )


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "💰 Filtered Spending",
            f"₹{filtered_total:,.0f}"
        )


    with c2:

        st.metric(
            "🧾 Transactions",
            filtered_count
        )


    with c3:

        st.metric(
            "📊 Average",
            f"₹{filtered_average:,.0f}"
        )


    st.divider()


    if filtered_df.empty:

        st.warning(
            "No expenses match your filters."
        )

    else:

        display_df = (
            filtered_df.copy()
        )


        display_df["Date"] = (
            display_df["Date"]
            .dt.strftime("%Y-%m-%d")
        )


        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


        filtered_csv = (
            filtered_df.copy()
        )


        filtered_csv["Date"] = (
            filtered_csv["Date"]
            .dt.strftime("%Y-%m-%d")
        )


        st.download_button(
            "📥 Download Filtered CSV",
            filtered_csv.to_csv(
                index=False
            ),
            "filtered_expenses.csv",
            "text/csv"
        )


# =========================================================
# EDIT EXPENSE
# =========================================================

elif page == "Edit Expense":

    st.title(
        "✏️ Edit Expense"
    )


    st.caption(
        "Select an expense and update its details."
    )


    expenses = get_expenses()


    if not expenses:

        st.info(
            "No expenses available to edit."
        )

        st.stop()


    df = create_dataframe(
        expenses
    )


    # -----------------------------------------------------
    # SELECT ID
    # -----------------------------------------------------

    selected_id = st.selectbox(
        "Select Expense ID",
        df["ID"].tolist()
    )


    # -----------------------------------------------------
    # GET SELECTED EXPENSE
    # -----------------------------------------------------

    selected_expense = df[
        df["ID"] == selected_id
    ].iloc[0]


    # -----------------------------------------------------
    # OPTIONS
    # -----------------------------------------------------

    categories = [
        "Food",
        "Transport",
        "Shopping",
        "Education",
        "Entertainment",
        "Bills",
        "Health",
        "Other"
    ]


    payment_methods = [
        "UPI",
        "Cash",
        "Debit Card",
        "Credit Card"
    ]


    current_category = (
        selected_expense["Category"]
    )


    current_payment = (
        selected_expense["Payment Method"]
    )


    category_index = (
        categories.index(
            current_category
        )
        if current_category in categories
        else 0
    )


    payment_index = (
        payment_methods.index(
            current_payment
        )
        if current_payment in payment_methods
        else 0
    )


    # =====================================================
    # IMPORTANT FIX
    # Each widget gets a unique key for each expense ID.
    # =====================================================

    col1, col2 = st.columns(2)


    with col1:

        edit_date = st.date_input(
            "Date",
            value=pd.to_datetime(
                selected_expense["Date"]
            ).date(),
            max_value=date.today(),
            key=f"edit_date_{selected_id}"
        )


        edit_category = st.selectbox(
            "Category",
            categories,
            index=category_index,
            key=f"edit_category_{selected_id}"
        )


    with col2:

        edit_description = st.text_input(
            "Description",
            value=str(
                selected_expense["Description"]
            ),
            key=f"edit_description_{selected_id}"
        )


        edit_amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            value=float(
                selected_expense["Amount"]
            ),
            step=10.0,
            key=f"edit_amount_{selected_id}"
        )


    edit_payment = st.selectbox(
        "Payment Method",
        payment_methods,
        index=payment_index,
        key=f"edit_payment_{selected_id}"
    )


    # =====================================================
    # UPDATE
    # =====================================================

    if st.button(
        "💾 Update Expense"
    ):

        if not edit_description.strip():

            st.error(
                "Please enter a description."
            )

        elif edit_amount <= 0:

            st.error(
                "Amount must be greater than ₹0."
            )

        elif edit_date > date.today():

            st.error(
                "Expense date cannot be in the future."
            )

        else:

            update_expense(
                selected_id,
                str(edit_date),
                edit_category,
                edit_description.strip(),
                edit_amount,
                edit_payment
            )


            st.success(
                "Expense updated successfully! ✅"
            )


            st.rerun()


# =========================================================
# DELETE EXPENSE
# =========================================================

elif page == "Delete Expense":

    st.title(
        "🗑️ Delete Expense"
    )


    st.caption(
        "Select a transaction to remove it."
    )


    expenses = get_expenses()


    if not expenses:

        st.info(
            "No expenses available to delete."
        )

        st.stop()


    selected_id = st.selectbox(
        "Select Expense ID",
        [
            expense[0]
            for expense in expenses
        ]
    )


    selected_expense = next(
        expense
        for expense in expenses
        if expense[0] == selected_id
    )


    st.write(
        f"**Date:** {selected_expense[1]}"
    )


    st.write(
        f"**Category:** {selected_expense[2]}"
    )


    st.write(
        f"**Description:** {selected_expense[3]}"
    )


    st.write(
        f"**Amount:** ₹{selected_expense[4]:,.2f}"
    )


    st.write(
        f"**Payment Method:** {selected_expense[5]}"
    )


    st.warning(
        "⚠️ This action cannot be undone."
    )


    if st.button(
        "🗑️ Delete Expense"
    ):

        delete_expense(
            selected_id
        )


        st.success(
            "Expense deleted successfully! ✅"
        )


        st.rerun()


# =========================================================
# BUDGET
# =========================================================

elif page == "Budget":

    st.title(
        "💰 Monthly Budget"
    )


    st.caption(
        "Set a monthly spending limit and monitor your progress."
    )


    selected_month = st.date_input(
        "Select Month",
        value=date.today(),
        key="budget_month"
    )


    current_month = (
        selected_month.strftime("%Y-%m")
    )


    current_budget = get_budget(
        current_month
    )


    budget = st.number_input(
        "Monthly Budget (₹)",
        min_value=0.0,
        value=float(
            current_budget
        ),
        step=500.0
    )


    if st.button(
        "💾 Save Budget"
    ):

        if budget > 0:

            save_budget(
                current_month,
                budget
            )


            st.success(
                f"Budget saved for {current_month}."
            )


            st.rerun()


        else:

            st.error(
                "Budget must be greater than ₹0."
            )


    expenses = get_expenses()


    if expenses:

        df = create_dataframe(
            expenses
        )


        monthly_expenses = df[
            df["Date"]
            .dt.strftime("%Y-%m")
            == current_month
        ]


        total_spent = (
            monthly_expenses[
                "Amount"
            ].sum()
        )

    else:

        total_spent = 0


    if current_budget > 0:

        remaining = (
            current_budget
            - total_spent
        )


        percentage_used = (
            total_spent
            / current_budget
            * 100
        )


        st.divider()


        c1, c2, c3 = st.columns(3)


        with c1:

            st.metric(
                "💰 Budget",
                f"₹{current_budget:,.0f}"
            )


        with c2:

            st.metric(
                "💸 Spent",
                f"₹{total_spent:,.0f}"
            )


        with c3:

            st.metric(
                "💵 Remaining",
                f"₹{remaining:,.0f}"
            )


        st.progress(
            min(
                max(
                    percentage_used / 100,
                    0
                ),
                1
            )
        )


        st.caption(
            f"{percentage_used:.1f}% of budget used."
        )


        if remaining > 0:

            st.success(
                f"🎉 ₹{remaining:,.0f} remaining this month."
            )


        elif remaining == 0:

            st.warning(
                "⚠️ You have reached your budget."
            )


        else:

            st.error(
                f"🚨 You are ₹{abs(remaining):,.0f} over budget."
            )


    else:

        st.info(
            "Set a monthly budget to start tracking."
        )