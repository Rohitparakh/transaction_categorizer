import pandas as pd

CATEGORY_KEYWORDS = {
    "Software": ["naimish.dg"],
    "Travel": ["cab"],
    "Office Supplies": ["Google"],
    "Client Entertainment": ["madhurimamukher"],
    "Employee Relaxation": ["vamsi0597"],
}

def classify_transactions(df: pd.DataFrame, col_remarks: str, col_withdrawal: str, col_deposit: str, col_serial: str) -> pd.DataFrame:
    # Initialize columns with empty values first
    df["Expense Type"] = ""
    df["Business Category"] = ""

    def is_valid_serial(val):
        if pd.isna(val):
            return False
        # Accept only numeric serial numbers (int or float)
        try:
            float_val = float(val)
            return True
        except:
            return False

    # Find start index where serial number is valid
    start_idx = None
    for idx, val in df[col_serial].items():
        if is_valid_serial(val):
            start_idx = idx
            break

    if start_idx is None:
        # No valid serial numbers found, return original df
        return df

    # Process rows from start_idx onward until serial number invalid or empty
    for idx in range(start_idx, len(df)):
        val = df.at[idx, col_serial]
        if not is_valid_serial(val):
            break  # stop processing further rows

        remark = str(df.at[idx, col_remarks]).lower()

        # Safe numeric conversion
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
            for category, keywords in CATEGORY_KEYWORDS.items():
                if any(keyword.lower() in remark for keyword in keywords):
                    df.at[idx, "Expense Type"] = "Business"
                    df.at[idx, "Business Category"] = category
                    matched = True
                    break
            if not matched:
                df.at[idx, "Expense Type"] = "Uncategorised"
                df.at[idx, "Business Category"] = ""
        else:
            df.at[idx, "Expense Type"] = ""
            df.at[idx, "Business Category"] = ""

    return df
