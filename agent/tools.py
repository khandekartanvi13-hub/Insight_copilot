
import pandas as pd
import plotly.express as px
from langchain_core.tools import tool

# Load and clean the dataset
DATA_PATH = "data/Sales_Dataset_2024.xlsx"

clean_df = pd.read_excel(DATA_PATH)

text_cols = ["Region", "Product", "Salesperson", "Category"]

for col in text_cols:
    clean_df[col] = clean_df[col].astype("string").str.strip()

clean_df["Region"] = (
    clean_df["Region"]
    .str.lower()
    .replace({
        "westt": "west",
        "easst": "east"
    })
    .str.title()
)

clean_df["Date"] = pd.to_datetime(
    clean_df["Date"], errors="coerce"
)

latest_chart = None


@tool
def sales_data_query(
    metric: str,
    group_by: str,
    category: str = "All",
    top_n: int = 5
) -> str:
    """Query and rank sales data by region, product, category or salesperson."""

    metric_map = {
        "revenue": "Revenue",
        "profit": "Profit",
        "cost": "Cost",
        "units_sold": "Units_Sold"
    }

    group_map = {
        "region": "Region",
        "product": "Product",
        "category": "Category",
        "salesperson": "Salesperson"
    }

    metric = metric_map.get(metric.lower(), metric)
    group_by = group_map.get(group_by.lower(), group_by)

    if metric not in ["Revenue", "Profit", "Cost", "Units_Sold"]:
        return "Invalid metric."

    if group_by not in ["Region", "Product", "Category", "Salesperson"]:
        return "Invalid grouping column."

    data = clean_df.copy()

    if category.lower() != "all":
        data = data[data["Category"].str.lower() == category.lower()]

    result = (
        data.dropna(subset=[metric, group_by])
        .groupby(group_by)[metric]
        .sum()
        .reset_index()
        .sort_values(metric, ascending=False)
        .head(top_n)
    )

    return result.to_string(index=False)


@tool
def calculate_sales_metric(
    metric: str,
    category: str = "All"
) -> str:
    """Calculate total, average, minimum and maximum for a sales metric."""

    metric_map = {
        "revenue": "Revenue",
        "profit": "Profit",
        "cost": "Cost",
        "units_sold": "Units_Sold"
    }

    metric = metric_map.get(metric.lower(), metric)

    if metric not in ["Revenue", "Profit", "Cost", "Units_Sold"]:
        return "Invalid metric."

    data = clean_df.copy()

    if category.lower() != "all":
        data = data[data["Category"].str.lower() == category.lower()]

    values = data[metric].dropna()

    return (
        f"Total {metric}: {values.sum():,.2f}\n"
        f"Average {metric}: {values.mean():,.2f}\n"
        f"Maximum {metric}: {values.max():,.2f}\n"
        f"Minimum {metric}: {values.min():,.2f}"
    )


@tool
def create_sales_chart(
    metric: str,
    group_by: str,
    category: str = "All"
) -> str:
    """Create a bar chart for a sales metric grouped by a selected column."""

    global latest_chart

    metric_map = {
        "revenue": "Revenue",
        "profit": "Profit",
        "cost": "Cost",
        "units_sold": "Units_Sold"
    }

    group_map = {
        "region": "Region",
        "product": "Product",
        "category": "Category",
        "salesperson": "Salesperson"
    }

    metric = metric_map.get(metric.lower(), metric)
    group_by = group_map.get(group_by.lower(), group_by)

    data = clean_df.copy()

    if category.lower() != "all":
        data = data[data["Category"].str.lower() == category.lower()]

    result = (
        data.dropna(subset=[metric, group_by])
        .groupby(group_by)[metric]
        .sum()
        .reset_index()
        .sort_values(metric, ascending=False)
    )

    latest_chart = px.bar(
        result,
        x=group_by,
        y=metric,
        title=f"{metric} by {group_by}",
        text_auto=True
    )

    return f"Chart created successfully: {metric} by {group_by}."
