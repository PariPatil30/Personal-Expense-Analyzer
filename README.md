# 💰 Personal Expense Analyzer

A smart and interactive personal expense management application built with **Python, Streamlit, Pandas, and SQLite**.

The application allows users to record expenses, manage transactions, analyze spending patterns, track monthly budgets, detect unusually high expenses, and generate a simple monthly spending forecast through an easy-to-use dashboard.

---

## 📌 Project Overview

Managing personal expenses manually can make it difficult to understand where money is being spent.

The **Personal Expense Analyzer** provides a centralized platform to:

- Record daily expenses
- View and manage transaction history
- Analyze spending patterns
- Monitor category-wise spending
- Track payment methods
- Set monthly budgets
- Detect unusually high expenses
- Estimate future monthly spending
- Export expense data for further analysis

The project combines **database management, data analysis, statistical analysis, and interactive visualization** into a single application.

---

## ✨ Features

### 💸 Expense Management

Users can:

- Add new expenses
- View existing expenses
- Edit expenses
- Delete expenses
- Store expense information in SQLite

Each transaction contains:

- Date
- Category
- Description
- Amount
- Payment Method

---

### 📊 Interactive Dashboard

The dashboard provides:

- Total spending
- Number of transactions
- Average expense
- Top spending category
- Biggest individual expense
- Most frequently used payment method
- Highest spending day
- Highest spending month

---

### 🧠 Smart Spending Insights

The application automatically analyzes expense patterns and provides simple insights such as:

- Highest spending category
- Category contribution to total expenses
- Large individual expenses
- Frequently used payment methods
- Transaction activity

---

### 💡 Personalized Recommendations

The system generates rule-based recommendations based on the user's spending behavior.

Examples include:

- High spending concentration in a category
- Individual expenses significantly above the average
- Large numbers of transactions
- Payment-method based observations

---

### 🚨 Unusual Spending Detection

The application includes statistical anomaly detection using the **Interquartile Range (IQR)** method.

The system identifies expenses that are unusually high compared with the user's spending distribution.

The dashboard displays:

- Total analyzed expenses
- Number of unusual expenses
- Anomaly percentage
- Anomaly score
- Reason for the detected anomaly

> Note: This is statistical anomaly detection, not a machine-learning model.

---

### 🔮 Monthly Spending Forecast

The application provides a simple forecast for the next month.

The forecast is calculated using recent historical monthly spending.

The dashboard displays:

- Estimated next-month spending
- Historical monthly average
- Historical spending trend
- Forecast explanation

> Note: This is a simple statistical forecasting approach rather than a machine-learning prediction model.

---

### 🗓️ Dashboard Time Filters

Users can analyze expenses for different periods:

- All Time
- This Month
- Last Month
- Last 3 Months

The selected period updates the dashboard analysis and visualizations.

---

### 📊 Advanced Analytics

The dashboard includes:

#### Category Spending Distribution

Shows how much each category contributes to total spending.

#### Spending by Day of Week

Analyzes spending across:

- Monday
- Tuesday
- Wednesday
- Thursday
- Friday
- Saturday
- Sunday

#### Budget vs Actual Spending

Compares:

- Monthly budget
- Actual spending
- Remaining amount
- Percentage of budget used

---

### 🔎 Advanced Expense Search

Expense History includes:

- Description search
- Category filter
- Payment method filter
- Date range filter
- Minimum amount
- Maximum amount

The filtered results also display:

- Filtered spending
- Number of matching transactions
- Average filtered expense

---

### 💰 Monthly Budget Tracking

Users can set a monthly budget and monitor:

- Total budget
- Amount spent
- Remaining amount
- Budget utilization
- Over-budget status

---

### 📥 Data Export

Expense data can be exported as:

- CSV
- Excel

The Excel file contains:

- Expenses
- Category Summary
- Monthly Summary

Filtered expenses can also be downloaded as CSV.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application interface |
| Pandas | Data analysis and manipulation |
| NumPy | Statistical calculations |
| SQLite | Database management |
| OpenPyXL | Excel export |

---

## 🏗️ Project Structure

```text
Personal Expense Tracker/
│
├── app.py
│       Main Streamlit application
│
├── database.py
│       SQLite database operations
│
├── anomaly_detection.py
│       Statistical anomaly detection
│
├── prediction.py
│       Monthly spending forecasting
│
├── requirements.txt
│       Python dependencies
│
├── README.md
│       Project documentation
│
└── expenses.db
        SQLite database