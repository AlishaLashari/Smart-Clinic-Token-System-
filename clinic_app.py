import streamlit as st
import sqlite3
from datetime import date

DB = "clinic.db"

def init_db():
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS tokens")
    cur.execute("""
        CREATE TABLE tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            status TEXT,
            fee INTEGER
        )
    """)
    conn.commit()
    conn.close()

def get_current_and_waiting():
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    today = str(date.today())
    cur.execute("SELECT COUNT(*) FROM tokens WHERE date=? AND status='Done'", (today,))
    current = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tokens WHERE date=? AND status='Waiting'", (today,))
    waiting = cur.fetchone()[0]
    conn.close()
    return current, waiting

def today_hisab():
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    today = str(date.today())
    cur.execute("SELECT COUNT(*), COALESCE(SUM(fee),0) FROM tokens WHERE date=?", (today,))
    total, earning = cur.fetchone()
    conn.close()
    return total, earning

def add_token(name, fee):
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("INSERT INTO tokens (name, date, status, fee) VALUES (?,?,?,?)",
                (name, str(date.today()), "Waiting", fee))
    conn.commit()
    conn.close()

def mark_done():
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    today = str(date.today())
    cur.execute("SELECT id FROM tokens WHERE date=? AND status='Waiting' ORDER BY id ASC LIMIT 1", (today,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE tokens SET status='Done' WHERE id=?", (row[0],))
        conn.commit()
    conn.close()
    return row is not None

# ---- MAIN APP ----
init_db()
# Note: For demo we keep DROP TABLE, for real clinic remove DROP line after first run

current, waiting = get_current_and_waiting()
total, earning = today_hisab()

st.set_page_config(page_title="Dadu Clinic Token", page_icon="🏥")
st.title("🏥 Dadu Clinic Token System")
st.caption(f"Date: {date.today()}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("NOW SERVING", current)
c2.metric("WAITING", waiting)
c3.metric("TOTAL", total)
c4.metric("EARNING", f"Rs {earning}")

st.divider()

st.subheader("Add Patient")
p_name = st.text_input("Patient Name")
p_fee = st.number_input("Fee Rs.", value=500, min_value=0, step=50)

col_a, col_b = st.columns(2)
with col_a:
    if st.button("➕ Add Token", use_container_width=True, type="primary"):
        if p_name.strip() == "":
            st.error("Enter name")
        else:
            add_token(p_name.strip(), p_fee)
            st.success(f"Added: {p_name}")
            st.rerun()
with col_b:
    if st.button("✅ Next Patient (Done)", use_container_width=True):
        if mark_done():
            st.success("Next patient called")
            st.rerun()
        else:
            st.warning("No waiting patients")

st.divider()
if st.button("🔄 Reset Today's Data"):
    init_db()
    st.rerun()
