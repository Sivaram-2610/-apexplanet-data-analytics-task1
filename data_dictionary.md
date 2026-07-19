# Data Dictionary — ApexPlanet Sales Dataset

**Source file:** `ApexPlanet_DataAnalytics_Dataset.xlsx` (sheet: `Sales_Dataset`)
**Grain:** one row = one order line item
**Raw row count:** 1,000
**Raw column count:** 12

## Raw Columns

| # | Column Name | Data Type (raw) | Description | Example | Business Relevance |
|---|---|---|---|---|---|
| 1 | `Order_ID` | Text (string) | Unique identifier for a sales order, format `ORD1000xx` | `ORD100002` | Primary key for joining order-level facts; used to track individual transactions and detect duplicate/rebilled orders |
| 2 | `Order_Date` | Date (stored as text `YYYY-MM-DD`) | Date the order was placed | `2025-02-25` | Enables trend analysis, seasonality, monthly/quarterly revenue reporting |
| 3 | `Customer_ID` | Text (string) | Unique identifier for the customer, format `CUSTxxxx` | `CUST5529` | Primary key for customer-level analysis (repeat purchase rate, CLV, segmentation) |
| 4 | `Customer_Name` | Text (string) | Display name of the customer, format `Customer_xxx` | `Customer_227` | Human-readable label only; **not unique** — must not be used as a join key (see Data Quality Notes) |
| 5 | `Age` | Numeric (float) | Customer's age in years at time of order | `30.0` | Enables demographic segmentation and age-based marketing/targeting |
| 6 | `Gender` | Text (categorical) | Customer's gender | `Female` / `Male` | Demographic segmentation |
| 7 | `City` | Text (categorical) | City where the order/customer is based | `Bengaluru` | Geographic/regional sales analysis |
| 8 | `Product` | Text (categorical) | Product purchased | `Rice`, `Book`, `Mobile`, `Laptop`, `Shoes`, `Chair` | Product-level performance analysis |
| 9 | `Category` | Text (categorical) | Product category (1:1 with Product) | `Grocery`, `Education`, `Electronics`, `Fashion`, `Furniture` | Category-level performance analysis, merchandising decisions |
| 10 | `Quantity` | Numeric (integer) | Number of units purchased in the order | `7` | Volume analysis, demand planning |
| 11 | `Unit_Price` | Numeric (float, currency) | Price per unit (₹, implied local currency) | `2829.77` | Pricing analysis, margin/revenue modeling |
| 12 | `Total_Sales` | Numeric (float, currency) | Order line revenue = `Quantity × Unit_Price` | `19808.39` | Core revenue KPI; primary measure for all sales reporting |

## Engineered Columns (added during cleaning — see `cleaning_script.py`)

| Column Name | Type | Description | Business Relevance |
|---|---|---|---|
| `Order_Date` (converted) | Datetime | `Order_Date` cast from text to a true datetime type | Required for any date-based grouping/filtering in BI tools |
| `Order_Year` | Integer | Calendar year extracted from `Order_Date` | Year-over-year comparisons |
| `Order_Month` | Integer (1–12) | Calendar month extracted from `Order_Date` | Monthly trend reporting |
| `Order_Month_Name` | Text | Month name, e.g. `February` | Readable labels for dashboards |
| `Order_Quarter` | Text, e.g. `Q1` | Calendar quarter | Quarterly business reviews |
| `Order_Day_Of_Week` | Text, e.g. `Monday` | Day of week the order was placed | Weekday vs weekend demand patterns |
| `Age_Group` | Text (categorical) | Binned age range: `18-25`, `26-35`, `36-45`, `46-55`, `56-65` | Simplifies demographic segmentation for reporting/visuals |
| `Age_Was_Imputed` | Boolean | `True` if `Age` was missing in the raw data and filled with the overall median | Transparency flag so imputed records can be excluded from age-sensitive analysis if needed |
| `City_Was_Imputed` | Boolean | `True` if `City` was missing in the raw data and filled with `"Unknown"` | Transparency flag; lets analysts exclude/handle unknown-location rows separately |
| `Order_ID_Was_Reassigned` | Boolean | `True` if the original `Order_ID` was a duplicate and this row received a newly generated unique ID | Data-integrity audit trail |
| `Sales_Value_Tier` | Text (categorical) | `Low` / `Medium` / `High` tier based on `Total_Sales` terciles | Quick segmentation of order value for reporting/visuals |

## Data Quality Notes (found during profiling)

1. **Duplicate `Order_ID`:** the value `ORD100050` was used for 9 different, otherwise-valid transactions (different customers, products, dates). This is a synthetic-ID collision, not a duplicate transaction — all 9 rows have distinct data in every other field. Fixed by reassigning new sequential IDs from the gaps already present in the ID number sequence.
2. **Missing values:** `Age` missing in 20 rows (2.0%); `City` missing in 13 rows (1.3%). No row is missing more than these two fields.
3. **`Customer_Name` is not a unique key:** 294 of 425 distinct names are shared by more than one `Customer_ID`, and 52 `Customer_ID`s have more than one associated name. Always join/group on `Customer_ID`, never on `Customer_Name`.
4. **No full-row duplicates** were found.
5. **`Total_Sales` recomputation check:** `Quantity × Unit_Price` matches the stored `Total_Sales` for all 1,000 rows (no arithmetic errors).
6. **No invalid ranges:** `Quantity` and `Unit_Price` are always positive; `Age` falls within a plausible 18–65 range; `Order_Date` falls within Jan 2025–Jan 2026.
7. **High-value orders:** 19 rows sit above the upper IQR fence for `Total_Sales`. These are legitimate combinations of high quantity × high unit price (e.g., bulk electronics orders), not data errors, so they were **flagged**, not removed or capped.
8. **Text fields** (`Gender`, `City`, `Product`, `Category`) were already consistently cased with no leading/trailing whitespace, but the cleaning script defensively trims and title-cases them in case future data loads are messier.
