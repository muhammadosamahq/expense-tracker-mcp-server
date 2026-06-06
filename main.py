# from fastmcp import FastMCP
# import os
# import json
# import pandas as pd
# from typing import Optional

# BASE_DIR = os.path.dirname(__file__)
# EXCEL_PATH = os.path.join(BASE_DIR, "expenses.xlsx")

# mcp = FastMCP("ExpenseTracker")

# COLUMNS = [
#     "id",
#     "date",
#     "amount",
#     "category",
#     "note"
# ]


# def init_excel():
#     if not os.path.exists(EXCEL_PATH):
#         df = pd.DataFrame(columns=COLUMNS)
#         df.to_excel(EXCEL_PATH, index=False)


# def load_expenses():
#     init_excel()
#     return pd.read_excel(EXCEL_PATH)


# def save_expenses(df):
#     df.to_excel(EXCEL_PATH, index=False)


# init_excel()


# @mcp.tool()
# def add_expense(date: str, amount: float, category: str, note: str = ""):
#     """Add a new expense entry to the Excel sheet."""

#     df = load_expenses()
#     next_id = 1 if df.empty else int(df["id"].max()) + 1
#     new_row = {
#         "id": next_id,
#         "date": date,
#         "amount": amount,
#         "category": category,
#         "note": note
#     }

#     df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
#     save_expenses(df)
#     return {
#         "status": "ok",
#         "id": next_id
#     }


# @mcp.tool()
# def list_expenses(start_date: str, end_date: str):
#     """List expense entries within an inclusive date range."""

#     df = load_expenses()

#     if df.empty:
#         return []

#     filtered = df[
#         (df["date"] >= start_date) &
#         (df["date"] <= end_date)
#     ]

#     return filtered.to_dict(orient="records")


# @mcp.tool()
# def summarize(start_date: str, end_date: str, category: Optional[str]  = None):
#     """Summarize expenses by category."""

#     df = load_expenses()
#     if df.empty:
#         return []

#     filtered = df[
#         (df["date"] >= start_date) &
#         (df["date"] <= end_date)
#     ]
#     if category:
#         filtered = filtered[
#             filtered["category"] == category
#         ]

#     if filtered.empty:
#         return []
#     summary = (
#         filtered.groupby("category")["amount"]
#         .sum()
#         .reset_index(name="total_amount")
#         .sort_values("category")
#     )
#     return summary.to_dict(orient="records")


# if __name__ == "__main__":
#     mcp.run(transport="http", host="0.0.0.0", port=8000)
#     # mcp.run()




















from fastmcp import FastMCP
import os
import pandas as pd
from typing import Optional
import asyncio

BASE_DIR = os.path.dirname(__file__)
EXCEL_FILE = os.getenv("EXCEL_FILE_PATH", "/tmp/expenses.xlsx")

mcp = FastMCP("ExpenseTracker")

COLUMNS = ["id", "date", "amount", "category", "note"]


def init_excel():
    if not os.path.exists(EXCEL_PATH):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_excel(EXCEL_PATH, index=False)


def load_expenses():
    init_excel()
    return pd.read_excel(EXCEL_PATH)


def save_expenses(df):
    df.to_excel(EXCEL_PATH, index=False)


init_excel()


# ---------- TOOL: ADD EXPENSE ----------
@mcp.tool()
async def add_expense(date: str, amount: float, category: str, note: str = ""):
    df = await asyncio.to_thread(load_expenses)

    next_id = 1 if df.empty else int(df["id"].max()) + 1

    new_row = {
        "id": next_id,
        "date": date,
        "amount": amount,
        "category": category,
        "note": note
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    await asyncio.to_thread(save_expenses, df)

    return {"status": "ok", "id": next_id}


# ---------- TOOL: LIST EXPENSES ----------
@mcp.tool()
async def list_expenses(start_date: str, end_date: str):
    df = await asyncio.to_thread(load_expenses)

    if df.empty:
        return []

    filtered = df[
        (df["date"] >= start_date) &
        (df["date"] <= end_date)
    ]

    return filtered.to_dict(orient="records")


# ---------- TOOL: SUMMARY ----------
@mcp.tool()
async def summarize(
    start_date: str,
    end_date: str,
    category: Optional[str] = None
):
    df = await asyncio.to_thread(load_expenses)

    if df.empty:
        return []

    filtered = df[
        (df["date"] >= start_date) &
        (df["date"] <= end_date)
    ]

    if category:
        filtered = filtered[filtered["category"] == category]

    if filtered.empty:
        return []

    summary = (
        filtered.groupby("category")["amount"]
        .sum()
        .reset_index(name="total_amount")
        .sort_values("category")
    )

    return summary.to_dict(orient="records")


# ---------- RUN SERVER ----------
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )