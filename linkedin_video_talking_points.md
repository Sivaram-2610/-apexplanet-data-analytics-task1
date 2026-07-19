# LinkedIn Video Walkthrough — Talking Points (Target: 3-5 minutes)

## 0:00-0:30 — Intro
"Hi everyone, I'm [Name], a Data Analytics Intern at ApexPlanet. For my first task, I was
given a 1,000-row sales transactions dataset and asked to take it from raw to
analysis-ready. In this video I'll walk through the data issues I found and how I
cleaned them."

## 0:30-1:30 — The dataset & profiling
- "The dataset had 12 columns covering orders, customers, demographics, product, and
  sales figures — one row per order line."
- "Before touching anything, I profiled it: checked missing values, duplicates,
  formatting consistency, and outliers."
- Show/mention findings:
  - 20 missing `Age` values (2%), 13 missing `City` values (1.3%)
  - 8 duplicate `Order_ID`s all sharing the value `ORD100050`
  - No fully duplicated rows
  - `Total_Sales` matched `Quantity x Unit_Price` for every row — no arithmetic errors
  - 19 legitimately high-value orders flagged by the IQR method

## 1:30-2:30 — The trickiest issue: duplicate Order_IDs
- "The most interesting issue was 9 completely different transactions all sharing
  the ID `ORD100050` — different customers, products, and dates, so these weren't
  duplicate rows, just an ID collision bug."
- "I noticed the ID numbers ran from 100002 to 101001 — exactly 1,000 possible values
  — and found 8 numbers in that range were never used. That confirmed the pattern:
  8 IDs got reassigned instead of using the missing numbers. I fixed it by giving
  each duplicate row one of those unused numbers, keeping the original ID format
  and preserving uniqueness."
- "I also learned `Customer_Name` isn't a safe unique key — the same name is reused
  across hundreds of different customer IDs, so all analysis should join on
  `Customer_ID` instead."

## 2:30-3:30 — Cleaning & transformations
- "For missing values, I imputed `Age` with the dataset median and filled missing
  `City` with 'Unknown' — and added `Age_Was_Imputed` / `City_Was_Imputed` flag
  columns so nothing is hidden; analysts can filter these out if needed."
- "I converted `Order_Date` from text to a real datetime type, which unlocked
  feature engineering: `Order_Year`, `Order_Month`, `Order_Quarter`, and
  `Order_Day_Of_Week`."
- "I also binned `Age` into `Age_Group` buckets, and split `Total_Sales` into
  Low/Medium/High value tiers for quick segmentation."
- "The 19 high-value outliers were legitimate large orders, not errors, so I flagged
  them with a boolean column instead of deleting or capping them."

## 3:30-4:15 — The deliverables
- "The final output is a clean, 23-column, zero-null dataset ready for analysis or
  dashboarding."
- "I documented everything in a data dictionary covering every original and
  engineered column, wrote a reusable Python/Pandas cleaning script so this
  pipeline can run again on future data pulls, and pushed all three — data
  dictionary, script, and cleaned dataset — to GitHub."

## 4:15-4:45 — Wrap-up
- "This task really drove home that data cleaning isn't just about deleting bad
  rows — it's about understanding *why* something looks wrong, documenting your
  decisions, and keeping an audit trail so nothing gets silently changed."
- "Thanks for watching — link to the GitHub repo is in the post. Excited for the
  next task in this internship!"

---
**Recording tips:**
- Screen-record your Jupyter/VS Code running `cleaning_script.py` output alongside
  a quick scroll through the cleaned Excel file — visuals make this much more
  engaging than talking to camera the whole time.
- Keep total runtime under 5 minutes; the sections above are paced to roughly 4:45.
