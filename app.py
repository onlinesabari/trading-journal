import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
PASSWORD = "trader123"
CSV_FILE = "trades.csv"

# --- PAGE SETUP ---
st.set_page_config(page_title="My Trading Journal", layout="wide")

# --- AUTHENTICATION ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- MAIN APP ---
st.title("🦅 My Trading Journal")

# 1. Initialize CSV if it doesn't exist
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["Date", "Symbol", "Direction", "Entry", "Exit", "PnL", "Notes"])
    df.to_csv(CSV_FILE, index=False)

# 2. Sidebar - Trade Entry
with st.sidebar:
    st.header("📝 Log a New Trade")
    with st.form("trade_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.today())
        symbol = st.text_input("Symbol (e.g. NIFTY)").upper()
        direction = st.selectbox("Direction", ["LONG", "SHORT"])
        entry_price = st.number_input("Entry Price", min_value=0.0, step=0.05)
        exit_price = st.number_input("Exit Price", min_value=0.0, step=0.05)
        notes = st.text_area("Notes / Strategy")
        
        submitted = st.form_submit_button("💾 Save Trade")
        
        if submitted:
            pnl = exit_price - entry_price if direction == "LONG" else entry_price - exit_price
            
            new_data = pd.DataFrame([{
                "Date": date,
                "Symbol": symbol,
                "Direction": direction,
                "Entry": entry_price,
                "Exit": exit_price,
                "PnL": pnl,
                "Notes": notes
            }])
            
            # Load current CSV, append, and save
            try:
                current_df = pd.read_csv(CSV_FILE)
                updated_df = pd.concat([current_df, new_data], ignore_index=True)
                updated_df.to_csv(CSV_FILE, index=False)
                st.success(f"Trade saved! PnL: {pnl}")
            except Exception as e:
                st.error(f"Error saving data: {e}")

# 3. Main Dashboard
st.subheader("📊 Recent Trades")

if os.path.exists(CSV_FILE):
    try:
        df = pd.read_csv(CSV_FILE)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            total_trades = len(df)
            total_pnl = df["PnL"].sum()
            win_rate = len(df[df["PnL"] > 0]) / total_trades * 100 if total_trades > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total PnL", f"₹{total_pnl:.2f}")
            col2.metric("Total Trades", total_trades)
            col3.metric("Win Rate", f"{win_rate:.1f}%")
        else:
            st.info("No trades logged yet.")
    except Exception as e:
        st.error("Could not read CSV file.")
