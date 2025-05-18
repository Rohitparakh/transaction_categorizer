import pandas as pd

def classify_transactions(df: pd.DataFrame, col_remarks: str, col_withdrawal: str, col_deposit: str, col_serial: str, category_data: dict) -> pd.DataFrame:
    if "Expense Type" not in df.columns:
        df["Expense Type"] = ""
    if "Expense Category" not in df.columns:
        df["Expense Category"] = ""
    if "Expense Subcategory" not in df.columns:
        df["Expense Subcategory"] = ""
    if "Remarks" not in df.columns:
        df["Remarks"] = ""

    def is_valid_serial(val):
        if pd.isna(val):
            return False
        try:
            float(val)
            return True
        except:
            return False

    start_idx = None
    for idx, val in df[col_serial].items():
        if is_valid_serial(val):
            start_idx = idx
            break

    if start_idx is None:
        return df

    for idx in range(start_idx, len(df)):
        val = df.at[idx, col_serial]
        if not is_valid_serial(val):
            break

        remark = str(df.at[idx, col_remarks]).lower()
        try:
            withdrawal = float(str(df.at[idx, col_withdrawal]).replace(",", "").strip() or 0)
        except:
            withdrawal = 0
        try:
            deposit = float(str(df.at[idx, col_deposit]).replace(",", "").strip() or 0)
        except:
            deposit = 0

        if withdrawal > 0:
            matched = False
            for category, subcats in category_data.items():
                for subcat, keywords in subcats.items():
                    if any(keyword.lower() in remark for keyword in keywords):
                        df.at[idx, "Expense Type"] = "Business"
                        df.at[idx, "Expense Category"] = category
                        df.at[idx, "Expense Subcategory"] = subcat
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                df.at[idx, "Expense Type"] = "Uncategorised"
                df.at[idx, "Expense Category"] = ""
                df.at[idx, "Expense Subcategory"] = ""
        else:
            df.at[idx, "Expense Type"] = ""
            df.at[idx, "Expense Category"] = ""
            df.at[idx, "Expense Subcategory"] = ""

        df.at[idx, "Remarks"] = ""  # Always empty

    return df
