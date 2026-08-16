import sqlite3
from datetime import date
from flask import Flask, request, redirect

app = Flask(__name__)
DB = "/tmp/clinic.db"

def init_db():
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, date TEXT, status TEXT, fee INTEGER)""")
    conn.commit()
    conn.close()

def get_data():
    init_db()
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    today = str(date.today())
    cur.execute("SELECT COUNT(*) FROM tokens WHERE date=? AND status='Done'", (today,))
    current = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tokens WHERE date=? AND status='Waiting'", (today,))
    waiting = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*), COALESCE(SUM(fee),0) FROM tokens WHERE date=?", (today,))
    total, earning = cur.fetchone()
    cur.execute("SELECT * FROM tokens WHERE date=? ORDER BY id DESC", (today,))
    all_tokens = cur.fetchall()
    conn.close()
    return current, waiting, total, earning, all_tokens

@app.route("/", methods=["GET"])
def home():
    current, waiting, total, earning, tokens = get_data()
    rows = "".join([f"<tr><td>{t[0]}</td><td>{t[1]}</td><td>{t[3]}</td><td>Rs {t[4]}</td></tr>" for t in tokens])
    html = f"""
    <html><head><meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>body{{font-family:Arial;padding:20px;background:#f5f5f5}} .card{{background:white;padding:15px;border-radius:10px;margin:10px;display:inline-block;min-width:120px;text-align:center;box-shadow:0 2px 5px #ccc}} .btn{{padding:10px 15px;border:none;border-radius:8px;cursor:pointer;margin:5px}} .primary{{background:#000;color:white}} table{{width:100%;background:white;border-radius:10px;border-collapse:collapse}} td,th{{padding:10px;border-bottom:1px solid #eee}}</style>
    </head><body>
    <h1>🏥 Dadu Clinic Token System</h1><p>Date: {date.today()}</p>
    <div class='card'><h3>NOW SERVING</h3><h1>{current}</h1></div>
    <div class='card'><h3>WAITING</h3><h1>{waiting}</h1></div>
    <div class='card'><h3>TOTAL</h3><h1>{total}</h1></div>
    <div class='card'><h3>EARNING</h3><h1>Rs {earning}</h1></div>
    <hr>
    <h3>Add Patient</h3>
    <form action='/add' method='post'>
    <input name='name' placeholder='Patient Name' required style='padding:10px;width:200px;border-radius:8px;border:1px solid #ccc'>
    <input name='fee' type='number' value='500' style='padding:10px;width:100px;border-radius:8px;border:1px solid #ccc'>
    <button class='btn primary' type='submit'>➕ Add Token</button>
    </form>
    <form action='/next' method='post' style='display:inline'><button class='btn' style='background:#28a745;color:white'>✅ Next Patient</button></form>
    <form action='/reset' method='post' style='display:inline'><button class='btn' style='background:#dc3545;color:white'>🔄 Reset</button></form>
    <hr><h3>Today's Patients</h3>
    <table><tr><th>ID</th><th>Name</th><th>Status</th><th>Fee</th></tr>{rows}</table>
    </body></html>
    """
    return html

@app.route("/add", methods=["POST"])
def add():
    init_db()
    name = request.form.get("name","").strip()
    fee = int(request.form.get("fee",500))
    if name:
        conn = sqlite3.connect(DB, check_same_thread=False)
        cur = conn.cursor()
        cur.execute("INSERT INTO tokens (name,date,status,fee) VALUES (?,?,?,?)",(name,str(date.today()),"Waiting",fee))
        conn.commit(); conn.close()
    return redirect("/")

@app.route("/next", methods=["POST"])
def next_p():
    init_db()
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("SELECT id FROM tokens WHERE date=? AND status='Waiting' ORDER BY id ASC LIMIT 1",(str(date.today()),))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE tokens SET status='Done' WHERE id=?",(row[0],))
        conn.commit()
    conn.close()
    return redirect("/")

@app.route("/reset", methods=["POST"])
def reset():
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS tokens")
    conn.commit(); conn.close()
    init_db()
    return redirect("/")

# For Vercel
app = app
