import streamlit as st
from datetime import date
import calendar
import pandas as pd

# --- 1. PAGE CONFIG & UI ---
st.set_page_config(page_title="Personal Budget", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    /* HIDE STREAMLIT DEPLOY BUTTON AND OTHER EXTRAS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000;
        font-family: 'Inter', sans-serif;
        color: #E6E6FA;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(15, 15, 15, 0.95);
        border-right: 1px solid rgba(230, 230, 250, 0.1);
    }
    div[data-testid="stMetric"] {
        background: rgba(230, 230, 250, 0.03);
        border: 1px solid rgba(230, 230, 250, 0.2);
        padding: 25px;
        border-radius: 20px;
        backdrop-filter: blur(8px);
    }
    [data-testid="stMetricValue"] { color: #E6E6FA !important; }
    [data-testid="stMetricLabel"] { color: #9370DB !important; }
    
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #9370DB 0%, #E6E6FA 100%);
        color: #000000;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
    }
    .stProgress > div > div > div > div { background-color: #9370DB; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. STATE ---
if 'expenses' not in st.session_state:
    st.session_state.expenses = []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #E6E6FA;'>Control Center</h2>", unsafe_allow_html=True)
    monthly_budget = st.number_input("Monthly Budget (£)", min_value=0.0, value=1500.0)
    fixed_costs = st.number_input("Fixed Bills (£)", min_value=0.0, value=500.0)
    
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("➕ ADD NEW EXPENSE", expanded=True):
        name = st.text_input("Item Name")
        amt = st.number_input("Amount (£)", min_value=0.0, step=1.0)
        cat = st.selectbox("Category", ["Food", "Transport", "Rent", "Study", "Fun", "Health"])
        if st.button("Add to Tracker"):
            if name and amt > 0:
                st.session_state.expenses.append({"Item": name, "Amount": amt, "Category": cat, "Date": date.today()})
                st.toast(f"✅ Added {name}", icon='💜')
                st.rerun()

# --- 4. CALCULATIONS ---
total_var = sum(item['Amount'] for item in st.session_state.expenses)
total_spent = total_var + fixed_costs
remaining = monthly_budget - total_spent

# --- 5. MAIN DASHBOARD ---
st.markdown("<h1 style='text-align: center; color: #E6E6FA; letter-spacing: -2px;'>Your BUDGET for this month</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #9370DB;'>{date.today().strftime('%A, %d %B %Y')}</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Centered Metrics (Only 2 now for maximum focus)
col_spacer1, m1, m2, col_spacer2 = st.columns([1, 2, 2, 1])
m1.metric("Available Balance", f"£{remaining:,.2f}")
m2.metric("Total Monthly Spend", f"£{total_spent:,.2f}")

st.divider()

# --- 6. HISTORY & PROGRESS ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📋 Activity History")
    if st.session_state.expenses:
        df = pd.DataFrame(st.session_state.expenses)
        
        # Search filter for better interaction
        search = st.text_input("🔍 Search expenses...")
        if search:
            df = df[df['Item'].str.contains(search, case=False) | df['Category'].str.contains(search, case=False)]
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export History (CSV)", data=csv, file_name='expenses.csv', mime='text/csv')
    else:
        st.info("No variable expenses logged yet.")

with col_right:
    st.markdown("### 📊 Budget Progress")
    usage_perc = min(1.0, total_spent / monthly_budget) if monthly_budget > 0 else 0
    st.progress(usage_perc)
    st.write(f"**{usage_perc*100:.1f}%** of your total £{monthly_budget} budget has been used.")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Reset Tracker"):
        st.session_state.expenses = []
        st.rerun()