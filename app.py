import streamlit as st
import pandas as pd
from classifier import classify_transactions
from io import BytesIO
from openpyxl import load_workbook
from copy import copy
import tempfile
import json

from streamlit_local_storage import LocalStorage

st.set_page_config(page_title="Transaction Classifier", layout="centered")
st.title("💼 Transaction Classifier – Business Expense Categorizer")

# --- LocalStorage for categories ---
localS = LocalStorage()
categories_json = localS.getItem("categories")
if categories_json:
    categories = json.loads(categories_json)
else:
    categories = {
        "Software": ["naimish.dg"],
        "Travel": ["cab"],
        "Office Supplies": ["Google"],
        "Client Entertainment": ["madhurimamukher"],
        "Employee Relaxation": ["vamsi0597"],
    }



uploaded_file = st.file_uploader("Upload your bank statement (.xlsx)", type=["xlsx"])

if uploaded_file:
    st.subheader("Business Categories & Keywords")
    st.write("Add/edit categories and keywords. These will be saved in your browser.")

    if "category_inputs" not in st.session_state:
        st.session_state.category_inputs = categories.copy()
    
    def save_categories():
        localS.setItem("categories", json.dumps(st.session_state.category_inputs))

    for cat in list(st.session_state.category_inputs.keys()):
        with st.expander(f"Category: {cat}", expanded=False):
            keywords = st.text_area(
                f"Keywords for '{cat}' (comma separated)",
                value=", ".join(st.session_state.category_inputs[cat]),
                key=f"kw_{cat}_text_area"
            )
            st.session_state.category_inputs[cat] = [k.strip() for k in keywords.split(",") if k.strip()]

            if st.button(f"Delete Category '{cat}'", key=f"del_{cat}_button"):
                del st.session_state.category_inputs[cat]
                st.rerun()


    # Add new category
    new_cat = st.text_input("Add new category", key="new_cat")
    if st.button("Add Category"):
        if new_cat and new_cat not in st.session_state.category_inputs:
            st.session_state.category_inputs[new_cat] = []
            st.rerun()


    # Save to localStorage
    if st.button("Save Categories"):
        localS.setItem("categories", json.dumps(st.session_state.category_inputs))
        st.success("Categories saved to your browser!")

    # Use the latest categories for classification
    categories_for_classifier = st.session_state.category_inputs
    header_row = st.number_input("Which row contains headers?", min_value=1, step=1, value=17)

    try:
        # Save uploaded file to temp file for openpyxl
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        # Read all rows as raw data to get pre-header rows
        df_raw = pd.read_excel(tmp_path, header=None, dtype=str)
        pre_header = df_raw.iloc[:header_row-1, :]

        # Read data with header for processing
        df = pd.read_excel(tmp_path, header=header_row - 1, dtype=str)
        st.success("Headers loaded successfully. Map columns below.")

        # Column selection
        col_options = df.columns.tolist()
        col_serial = st.selectbox("🔢 Serial Number column", col_options, index=col_options.index("S.N.") if "S.N." in col_options else 0)
        col_remarks = st.selectbox("📝 Transaction Remarks column", col_options, index=col_options.index("Transaction Remarks") if "Transaction Remarks" in col_options else 0)
        col_withdrawal = st.selectbox("💸 Withdrawal Amount column", col_options, index=col_options.index("Withdrawal Amt (INR)") if "Withdrawal Amt (INR)" in col_options else 0)
        col_deposit = st.selectbox("💰 Deposit Amount column", col_options, index=col_options.index("Deposit Amt (INR)") if "Deposit Amt (INR)" in col_options else 0)

        if st.button("🔍 Process Transactions"):
            processed_df = classify_transactions(
                df.copy(),
                col_remarks,
                col_withdrawal,
                col_deposit,
                col_serial,
                categories_for_classifier
            )
            st.success("✅ File processed successfully!")
            st.dataframe(processed_df)

            # Load workbook for formatting
            wb = load_workbook(tmp_path)
            ws = wb.active

            # Find where to add new columns (right after the last column)
            start_col = ws.max_column + 1
            header_row_idx = header_row

            # Write new headers
            ws.cell(row=header_row_idx, column=start_col, value='Expense Type')
            ws.cell(row=header_row_idx, column=start_col+1, value='Business Category')

            # --- Copy header style from last header cell ---
            last_header_col = start_col - 1
            ref_header_cell = ws.cell(row=header_row_idx, column=last_header_col)
            header_font = copy(ref_header_cell.font)
            header_border = copy(ref_header_cell.border)
            header_fill = copy(ref_header_cell.fill)
            header_alignment = copy(ref_header_cell.alignment)

            for col in [start_col, start_col+1]:
                cell = ws.cell(row=header_row_idx, column=col)
                cell.font = header_font
                cell.border = header_border
                cell.fill = header_fill
                cell.alignment = header_alignment

            # --- Copy data row style from last data column and write values ---
            for i, (etype, bcat) in enumerate(zip(processed_df["Expense Type"], processed_df["Business Category"]), start=header_row_idx+1):
                ref_data_cell = ws.cell(row=i, column=last_header_col)
                data_font = copy(ref_data_cell.font)
                data_border = copy(ref_data_cell.border)
                data_fill = copy(ref_data_cell.fill)
                data_alignment = copy(ref_data_cell.alignment)

                cell1 = ws.cell(row=i, column=start_col, value=etype)
                cell1.font = data_font
                cell1.border = data_border
                cell1.fill = data_fill
                cell1.alignment = data_alignment

                cell2 = ws.cell(row=i, column=start_col+1, value=bcat)
                cell2.font = data_font
                cell2.border = data_border
                cell2.fill = data_fill
                cell2.alignment = data_alignment

            # Save to BytesIO for download
            output = BytesIO()
            wb.save(output)
            output.seek(0)

            st.download_button(
                label="📥 Download Processed File (with formatting)",
                data=output,
                file_name="Processed_Transactions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"⚠️ Error while reading or processing: {e}")
