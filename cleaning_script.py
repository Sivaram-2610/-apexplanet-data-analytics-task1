"""
ApexPlanet Sales Dataset — Cleaning & Preparation Script
=========================================================

Task 1: Data Immersion & Wrangling

What this script does:
  1. Loads the raw sales dataset
  2. Profiles it for missing values, duplicates, and outliers
  3. Fixes duplicate Order_IDs
  4. Imputes missing Age and City values (with audit flags)
  5. Standardizes the date field and text fields
  6. Engineers new analysis-ready columns (date parts, age groups,
     sales value tiers)
  7. Flags (but does not remove) legitimate high-value outliers
  8. Writes a cleaned dataset + a data-quality log to disk

Usage:
    python cleaning_script.py <input_file.xlsx> <output_file.xlsx>

Example:
    python cleaning_script.py ApexPlanet_DataAnalytics_Dataset.xlsx cleaned_sales_dataset.xlsx
"""

import sys
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------------------
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Sales_Dataset")
    print(f"[LOAD] Loaded {len(df):,} rows, {df.shape[1]} columns from {path}")
    return df


# ---------------------------------------------------------------------------
# 2. PROFILE  (report only — does not change the data)
# ---------------------------------------------------------------------------
def profile_data(df: pd.DataFrame) -> None:
    print("\n[PROFILE] Missing values per column:")
    print(df.isnull().sum()[df.isnull().sum() > 0].to_string())

    full_dupes = df.duplicated().sum()
    id_dupes = df.duplicated(subset=["Order_ID"]).sum()
    print(f"\n[PROFILE] Fully duplicated rows: {full_dupes}")
    print(f"[PROFILE] Duplicated Order_IDs (extra occurrences): {id_dupes}")

    calc_total = (df["Quantity"] * df["Unit_Price"]).round(2)
    mismatches = (calc_total - df["Total_Sales"]).abs() > 0.5
    print(f"[PROFILE] Total_Sales arithmetic mismatches: {mismatches.sum()}")

    q1, q3 = df["Total_Sales"].quantile([0.25, 0.75])
    iqr = q3 - q1
    upper_fence = q3 + 1.5 * iqr
    outliers = (df["Total_Sales"] > upper_fence).sum()
    print(f"[PROFILE] Total_Sales high-value outliers (IQR method): {outliers}")


# ---------------------------------------------------------------------------
# 3. FIX DUPLICATE ORDER IDS
# ---------------------------------------------------------------------------
def fix_duplicate_order_ids(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Order_ID_Was_Reassigned"] = False

    id_nums = df["Order_ID"].str.extract(r"(\d+)")[0].astype(int)
    full_range = set(range(id_nums.min(), id_nums.max() + 1))
    unused_numbers = sorted(full_range - set(id_nums.unique()))
    unused_iter = iter(unused_numbers)

    dup_mask = df.duplicated(subset=["Order_ID"], keep="first")
    n_fixed = 0
    for idx in df[dup_mask].index:
        try:
            new_num = next(unused_iter)
        except StopIteration:
            # Fallback: extend beyond the max existing ID number
            new_num = id_nums.max() + 1 + n_fixed
        df.loc[idx, "Order_ID"] = f"ORD{new_num}"
        df.loc[idx, "Order_ID_Was_Reassigned"] = True
        n_fixed += 1

    print(f"[CLEAN] Reassigned {n_fixed} duplicate Order_ID(s) to unused ID numbers")
    assert df["Order_ID"].duplicated().sum() == 0, "Order_ID still has duplicates!"
    return df


# ---------------------------------------------------------------------------
# 4. HANDLE MISSING VALUES
# ---------------------------------------------------------------------------
def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Age_Was_Imputed"] = df["Age"].isnull()
    median_age = df["Age"].median()
    df["Age"] = df["Age"].fillna(median_age)
    print(f"[CLEAN] Imputed {df['Age_Was_Imputed'].sum()} missing Age values with median ({median_age})")

    df["City_Was_Imputed"] = df["City"].isnull()
    df["City"] = df["City"].fillna("Unknown")
    print(f"[CLEAN] Imputed {df['City_Was_Imputed'].sum()} missing City values with 'Unknown'")

    return df


# ---------------------------------------------------------------------------
# 5. STANDARDIZE FORMATTING
# ---------------------------------------------------------------------------
def standardize_formatting(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Dates: cast text -> real datetime
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

    # Defensive text cleanup (trim whitespace, consistent title case)
    text_cols = ["Gender", "City", "Product", "Category"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip().str.title()
        df[col] = df[col].replace({"Nan": "Unknown"})

    # Round currency fields to 2 decimals
    df["Unit_Price"] = df["Unit_Price"].round(2)
    df["Total_Sales"] = df["Total_Sales"].round(2)

    print("[CLEAN] Standardized Order_Date to datetime; trimmed/title-cased text fields")
    return df


# ---------------------------------------------------------------------------
# 6. FEATURE ENGINEERING
# ---------------------------------------------------------------------------
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Order_Year"] = df["Order_Date"].dt.year
    df["Order_Month"] = df["Order_Date"].dt.month
    df["Order_Month_Name"] = df["Order_Date"].dt.month_name()
    df["Order_Quarter"] = "Q" + df["Order_Date"].dt.quarter.astype(str)
    df["Order_Day_Of_Week"] = df["Order_Date"].dt.day_name()

    age_bins = [17, 25, 35, 45, 55, 65]
    age_labels = ["18-25", "26-35", "36-45", "46-55", "56-65"]
    df["Age_Group"] = pd.cut(df["Age"], bins=age_bins, labels=age_labels)

    tier_labels = ["Low", "Medium", "High"]
    df["Sales_Value_Tier"] = pd.qcut(df["Total_Sales"], q=3, labels=tier_labels)

    print("[FEATURE] Added Order_Year/Month/Quarter/Day_Of_Week, Age_Group, Sales_Value_Tier")
    return df


# ---------------------------------------------------------------------------
# 7. FLAG OUTLIERS (kept in data, flagged for analyst awareness)
# ---------------------------------------------------------------------------
def flag_outliers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    q1, q3 = df["Total_Sales"].quantile([0.25, 0.75])
    iqr = q3 - q1
    upper_fence = q3 + 1.5 * iqr
    df["Total_Sales_Is_Outlier"] = df["Total_Sales"] > upper_fence
    print(f"[FLAG] Marked {df['Total_Sales_Is_Outlier'].sum()} rows as high-value outliers (kept, not removed)")
    return df


# ---------------------------------------------------------------------------
# 8. FINAL COLUMN ORDER + SAVE
# ---------------------------------------------------------------------------
def finalize_and_save(df: pd.DataFrame, output_path: str) -> None:
    column_order = [
        "Order_ID", "Order_ID_Was_Reassigned",
        "Order_Date", "Order_Year", "Order_Month", "Order_Month_Name",
        "Order_Quarter", "Order_Day_Of_Week",
        "Customer_ID", "Customer_Name",
        "Age", "Age_Group", "Age_Was_Imputed",
        "Gender", "City", "City_Was_Imputed",
        "Product", "Category",
        "Quantity", "Unit_Price", "Total_Sales",
        "Sales_Value_Tier", "Total_Sales_Is_Outlier",
    ]
    df = df[column_order].sort_values("Order_Date").reset_index(drop=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Cleaned_Sales_Data", index=False)

    print(f"\n[SAVE] Cleaned dataset written to {output_path}")
    print(f"[SAVE] Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns")


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------
def main(input_path: str, output_path: str) -> None:
    df = load_data(input_path)
    profile_data(df)

    df = fix_duplicate_order_ids(df)
    df = handle_missing_values(df)
    df = standardize_formatting(df)
    df = engineer_features(df)
    df = flag_outliers(df)

    finalize_and_save(df, output_path)
    print("\n[DONE] Cleaning pipeline completed successfully.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cleaning_script.py <input_file.xlsx> <output_file.xlsx>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
