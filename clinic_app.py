import streamlit as st
import sqlite3
from datetime import datetime
import time

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tokens
                 (id INTEGER PRIMARY KEY, token_no INTEGER, name TEXT, time TEXT, date TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def add_token(name):
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()
    # Get last token number today
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT MAX(token_no) FROM tokens WHERE date=?", (today,))
    last = c.fetchone()[0]
    new_no = 1 if last is None else last + 1

    now_time = datetime.now().strftime("%H:%M")
    c.execute("INSERT INTO tokens (token_no, name, time, date, status) VALUES (?,?,?,?,?)",
              (new_no, name, now_time, today, "Waiting"))
    conn.commit()
    conn.close()
    return new_no

def get_current_and_waiting():
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM tokens WHERE date=? AND status='Waiting'", (today,))
    waiting = c.fetchone()[0]
    c.execute("SELECT MAX(token_no) FROM tokens WHERE date=? AND status='Done'", (today,))
    done = c.fetchone()[0]
    current = 0 if done is None else done
    conn.close()
    return current, waiting
current, waiting = get_current_and_waiting()
total, earning = today_hisab()
col1, col2, col3 = st.columns(3)
col1.metric("NOW", current)
col2.metric("WAITING", waiting)
col3.metric("TOTAL", total)


def next_token():
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    # Mark smallest waiting token as Done
    c.execute("SELECT id, token_no FROM tokens WHERE date=? AND status='Waiting' ORDER BY token_no ASC LIMIT 1", (today,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE tokens SET status='Done' WHERE id=?", (row[0],))
        conn.commit()
        conn.close()
        return row[1]
    conn.close()
    return None

def today_hisab():
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM tokens WHERE date=?", (today,))
    total = c.fetchone()[0]
    conn.close()
    return total, total*500 # assuming Rs.500 fees

# --- APP UI ---
st.set_page_config(page_title="Dadu Clinic Token", page_icon="🏥")
init_db()

st.title("🏥 Dadu Clinic Token - Dr. Sahab")
st.write("For Compounder Use Only - 1 Mobile Model")

current, waiting = get_current_and_waiting()

# BIG DISPLAY FOR PATIENTS TO SEE FROM FAR
st.markdown(f"""
<div style="background-color:#e8f5e9; padding:20px; border-radius:10px; text-align:center;">
    <h1 style="font-size:60px; margin:0;">NOW: {current}</h1>
    <h2 style="margin:0;">Waiting: {waiting} patients</h2>
</div>
""", unsafe_allow_html=True)

st.write("---")

# --- FUNCTION 1: NEW TOKEN ---
st.subheader("1. New Patient Aaye?")
name_input = st.text_input("Name likho (optional, Amma ka naam nahi to khali chhor do):", placeholder="Ali / Mai Jee")
if st.button("🟢 NEW TOKEN - Naya Token Do", use_container_width=True):
    token_no = add_token(name_input if name_input else "Patient")
    st.balloons()
    st.success(f"Token {token_no} diya gaya! Chit pe {token_no} likh ke de do.")
    # Voice Announcement Text
    st.info(f"🔊 Speaker bolega: 'Token number {token_no}, thoda intezar karo'")
    time.sleep(1)
    st.rerun()

# --- FUNCTION 2: NEXT TOKEN ---
st.write("---")
st.subheader("2. Doctor ne patient dekha?")
if st.button("🔵 NEXT - Agla Mareez Bulao", use_container_width=True):
    called = next_token()
    if called:
        st.warning(f"🔊 BULAO: Token {called} andar aao! (Token {called} called inside)")
        # For real speaker, you will use this line later with Bluetooth speaker
        # import pyttsx3; engine.say(f"Token number {called} andar aao")
    else:
        st.error("Koi waiting patient nahi hai")
    time.sleep(1)
    st.rerun()

# --- FUNCTION 3: HISAB ---
st.write("---")
if st.button("📊 AAJ KA HISAB DEKHO"):
    total, earning = today_hisab()
    st.metric("Total Patients Today", total)
    st.metric("Total Kamai (Rs.500 x patient)", f"Rs. {earning}")

# --- FUNCTION 4: LIST ---
with st.expander("📋 Aaj ki List Dekho"):
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT token_no, name, time, status FROM tokens WHERE date=? ORDER BY token_no", (today,))
    rows = c.fetchall()
    for r in rows:
        st.write(f"Token {r[0]} - {r[1]} - {r[2]} - {r[3]}")
    conn.close()

st.caption("Made for Dadu Clinics | Works Offline | No Patient App Needed")
