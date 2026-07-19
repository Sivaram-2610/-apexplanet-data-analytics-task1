# ApexPlanet Data Analytics Internship — Task 1: Data Immersion & Wrangling

Goal: take a raw sales transactions dataset from messy/raw to a clean,
analysis-ready dataset — documenting every decision along the way.

## Repository Structure

```
├── data/
│   ├── raw_sales_dataset.xlsx        # Original, untouched raw dataset (1,000 rows x 12 cols)
│   └── cleaned_sales_dataset.xlsx    # Final cleaned & feature-engineered dataset (1,000 rows x 23 cols)
├── scripts/
│   └── cleaning_script.py            # Reproducible Python/Pandas cleaning pipeline
├── docs/
│   ├── data_dictionary.md            # Column-by-column documentation + data quality notes
│   └── linkedin_video_talking_points.md  # Script for the 3-5 min walkthrough video
└── README.md
```

## What was done

1. **Profiled** the raw data for missing values, duplicates, formatting issues, and outliers.
2. **Fixed** 8 duplicate `Order_ID`s caused by an ID-generation collision.
3. **Imputed** missing `Age` (median) and `City` (`"Unknown"`) values, with audit flag
   columns (`Age_Was_Imputed`, `City_Was_Imputed`) so nothing is hidden.
4. **Standardized** `Order_Date` into a real datetime type and cleaned text fields.
5. **Engineered** new columns: `Order_Year`, `Order_Month`, `Order_Quarter`,
   `Order_Day_Of_Week`, `Age_Group`, `Sales_Value_Tier`.
6. **Flagged** (not removed) 19 legitimate high-value orders using the IQR method.

Full details on every issue found and every decision made are in
[`docs/data_dictionary.md`](docs/data_dictionary.md).

## How to reproduce

```bash
pip install pandas openpyxl
python scripts/cleaning_script.py data/raw_sales_dataset.xlsx data/cleaned_sales_dataset.xlsx
```

## Author

[Your Name] — Data Analytics Intern, ApexPlanet
