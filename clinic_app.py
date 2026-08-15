import streamlit as st
import sqlite3
from datetime import date

def init_db():
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tokens
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, date TEXT, status TEXT, fee INTEGER)''')
    conn.commit()
    conn.close()

def get_current_and_waiting():
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()
    today = str(date.today())
    c.execute("SELECT COUNT(*) FROM tokens WHERE date=? AND status='Done'", (today,))
    current = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tokens WHERE date=? AND status='Waiting'", (today,))
    waiting = c.fetchone()[0]
    conn.close()
    return current, waiting

def today_hisab():
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()
    today = str(date.today())
    c.execute("SELECT COUNT(*), COALESCE(SUM(fee),0) FROM tokens WHERE date=?", (today,))
    total, earning = c.fetchone()
    conn.close()
    return total, earning

# IMPORTANT ORDER
init_db()
current, waiting = get_current_and_waiting()
total, earning = today_hisab()

st.title("Dadu Clinic Token System")

col1, col2, col3 = st.columns(3)
col1.metric("NOW", current)
col2.metric("WAITING", waiting)
col3.metric("TOTAL TODAY", total)

st.write(f"Earning Today: Rs. {earning}")

# Add token
name = st.text_input("Patient Name")
fee = st.number_input("Fee", min_value=0, value=500)
if st.button("Add Token"):
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()
    c.execute("INSERT INTO tokens (name, date, status, fee) VALUES (?,?,?,?)",
              (name, str(date.today()), 'Waiting', fee))
    conn.commit()
    conn.close()
    st.success(f"Token for {name} added!")
    st.rerun()
