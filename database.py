import sqlite3


# --------------------------------------------------
# CREATE DATABASE
# --------------------------------------------------

def create_database():

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL
        )
    """)

    # Budget table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            month TEXT PRIMARY KEY,
            budget REAL NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# ADD EXPENSE
# --------------------------------------------------

def add_expense(
    date,
    category,
    description,
    amount,
    payment_method
):

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO expenses
        (date, category, description, amount, payment_method)
        VALUES (?, ?, ?, ?, ?)
    """, (
        date,
        category,
        description,
        amount,
        payment_method
    ))

    connection.commit()
    connection.close()


# --------------------------------------------------
# GET ALL EXPENSES
# --------------------------------------------------

def get_expenses():

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            date,
            category,
            description,
            amount,
            payment_method
        FROM expenses
        ORDER BY date DESC
    """)

    expenses = cursor.fetchall()

    connection.close()

    return expenses


# --------------------------------------------------
# DELETE EXPENSE
# --------------------------------------------------

def delete_expense(expense_id):

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM expenses
        WHERE id = ?
    """, (expense_id,))

    connection.commit()
    connection.close()


# --------------------------------------------------
# UPDATE EXPENSE
# --------------------------------------------------

def update_expense(
    expense_id,
    date,
    category,
    description,
    amount,
    payment_method
):

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE expenses
        SET
            date = ?,
            category = ?,
            description = ?,
            amount = ?,
            payment_method = ?
        WHERE id = ?
    """, (
        date,
        category,
        description,
        amount,
        payment_method,
        expense_id
    ))

    connection.commit()
    connection.close()


# --------------------------------------------------
# SAVE MONTHLY BUDGET
# --------------------------------------------------

def save_budget(month, budget):

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO budgets
        (month, budget)
        VALUES (?, ?)
    """, (
        month,
        budget
    ))

    connection.commit()
    connection.close()


# --------------------------------------------------
# GET MONTHLY BUDGET
# --------------------------------------------------

def get_budget(month):

    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT budget
        FROM budgets
        WHERE month = ?
    """, (month,))

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]

    return 0
def delete_expense(expense_id):

    connection = sqlite3.connect("expenses.db")

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    connection.commit()

    connection.close()