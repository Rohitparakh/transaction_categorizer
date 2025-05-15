import streamlit as st
import pandas as pd
from classifier import classify_transactions
from io import BytesIO

st.set_page_config(page_title="Transaction Classifier", layout="centered")
st.title("💼 Transaction Classifier – Business Expense Categorizer")

uploaded_file = st.file_uploader("Upload your bank statement (.xlsx)", type=["xlsx"])

if uploaded_file:
    header_row = st.number_input("Which row contains headers?", min_value=1, step=1, value=1)

    try:
        df = pd.read_excel(uploaded_file, header=header_row - 1)  # pandas uses 0-index
        st.success("Headers loaded successfully. Map columns below.")

        # Column selection
        col_options = df.columns.tolist()
        col_serial = st.selectbox("🔢 Serial Number column", col_options, index=col_options.index("S.N.") if "S.N." in col_options else 0)
        col_remarks = st.selectbox("📝 Transaction Remarks column", col_options, index=col_options.index("Transaction Remarks") if "Transaction Remarks" in col_options else 0)
        col_withdrawal = st.selectbox("💸 Withdrawal Amount column", col_options, index=col_options.index("Withdrawal Amt (INR)") if "Withdrawal Amt (INR)" in col_options else 0)
        col_deposit = st.selectbox("💰 Deposit Amount column", col_options, index=col_options.index("Deposit Amt (INR)") if "Deposit Amt (INR)" in col_options else 0)

        if st.button("🔍 Process Transactions"):
            processed_df = classify_transactions(df.copy(), col_remarks, col_withdrawal, col_deposit, col_serial)

            st.success("✅ File processed successfully!")
            st.dataframe(processed_df)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                processed_df.to_excel(writer, index=False, sheet_name='Processed Transactions')
            output.seek(0)

            st.download_button(
                label="📥 Download Processed File",
                data=output,
                file_name="Processed_Transactions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"⚠️ Error while reading or processing: {e}")
