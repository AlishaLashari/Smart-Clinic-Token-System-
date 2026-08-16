import streamlit as st
import sqlite3
from datetime import date

DB = "clinic.db"

def init_db():
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            status TEXT,
            fee INTEGER
        )
    """)
    conn.commit()
    conn.close()

def get_counts():
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    today = str(date.today())
    cur.execute("SELECT COUNT(*) FROM tokens WHERE date=? AND status='Done'", (today,))
    done = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tokens WHERE date=? AND status='Waiting'", (today,))
    waiting = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*), COALESCE(SUM(fee),0) FROM tokens WHERE date=?", (today,))
    total, earning = cur.fetchone()
    conn.close()
    return done, waiting, total, earning

# Init
init_db()
done, waiting, total, earning = get_counts()

# UI
st.set_page_config(page_title="Dadu Clinic", page_icon="🏥")
st.title("🏥 Dadu Clinic - Token System")

c1, c2, c3, c4 = st.columns(4)
c1.metric("DONE", done)
c2.metric("WAITING", waiting)
c3.metric("TOTAL", total)
c4.metric("EARNING", f"Rs {earning}")

st.divider()
name = st.text_input("Patient Name")
fee = st.number_input("Fee", value=500, min_value=0, step=100)

col1, col2 = st.columns(2)
if col1.button("Add Token", type="primary", use_container_width=True):
    if name.strip():
        conn = sqlite3.connect(DB, check_same_thread=False)
        conn.execute("INSERT INTO tokens (name,date,status,fee) VALUES (?,?,?,?)",
                     (name.strip(), str(date.today()), "Waiting", fee))
        conn.commit()
        conn.close()
        st.rerun()

if col2.button("Next Patient Done", use_container_width=True):
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("SELECT id FROM tokens WHERE date=? AND status='Waiting' ORDER BY id LIMIT 1", (str(date.today()),))
    r = cur.fetchone()
    if r:
        cur.execute("UPDATE tokens SET status='Done' WHERE id=?", (r[0],))
        conn.commit()
    conn.close()
    st.rerun()
