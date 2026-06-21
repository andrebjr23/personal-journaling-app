import streamlit as st
import sqlite3
from datetime import datetime

DB_PATH = "journal.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            ideas TEXT,
            questions TEXT,
            reflection TEXT,
            situation TEXT,
            task TEXT,
            action TEXT,
            result TEXT,
            takeaway TEXT,
            daily_note TEXT,
            longform_content TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_entry(entry_type, fields):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    columns = ["entry_type", "created_at"] + list(fields.keys())
    values = [entry_type, created_at] + list(fields.values())
    placeholders = ",".join(["?"] * len(values))
    col_str = ",".join(columns)
    c.execute(f"INSERT INTO entries ({col_str}) VALUES ({placeholders})", values)
    conn.commit()
    conn.close()

def get_entries(types):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    placeholders = ",".join(["?"] * len(types))
    c.execute(f"SELECT * FROM entries WHERE entry_type IN ({placeholders}) ORDER BY created_at DESC", types)
    rows = c.fetchall()
    col_names = [desc[0] for desc in c.description]
    conn.close()
    return rows, col_names

init_db()

st.title("Journal")

tab1, tab2 = st.tabs(["New Entry", "Browse Entries"])

with tab1:
    entry_type = st.selectbox("Entry type", ["IQR", "START", "Daily Note", "Long-form"])

    if entry_type == "IQR":
        ideas = st.text_area("Ideas")
        questions = st.text_area("Questions")
        reflection = st.text_area("Reflection")
        if st.button("Save Entry"):
            save_entry("IQR", {"ideas": ideas, "questions": questions, "reflection": reflection})
            st.success("Saved.")

    elif entry_type == "START":
        situation = st.text_area("Situation")
        task = st.text_area("Task")
        action = st.text_area("Action")
        result = st.text_area("Result")
        takeaway = st.text_area("Takeaway (your own, not external)")
        if st.button("Save Entry"):
            save_entry("START", {"situation": situation, "task": task, "action": action, "result": result, "takeaway": takeaway})
            st.success("Saved.")

    elif entry_type == "Daily Note":
        note = st.text_area("What's on your mind today?")
        if st.button("Save Entry"):
            save_entry("Daily", {"daily_note": note})
            st.success("Saved.")

    elif entry_type == "Long-form":
        content = st.text_area("Write freely", height=300)
        if st.button("Save Entry"):
            save_entry("Longform", {"longform_content": content})
            st.success("Saved.")

with tab2:
    bucket = st.radio("View", ["IQR / START", "Daily Notes / Long-form"])
    types = ["IQR", "START"] if bucket == "IQR / START" else ["Daily", "Longform"]
    rows, col_names = get_entries(types)

    if not rows:
        st.write("No entries yet.")
    else:
        for row in rows:
            entry = dict(zip(col_names, row))
            st.markdown(f"**{entry['entry_type']}** — {entry['created_at']}")
            if entry["entry_type"] == "IQR":
                st.write(f"Ideas: {entry['ideas']}")
                st.write(f"Questions: {entry['questions']}")
                st.write(f"Reflection: {entry['reflection']}")
            elif entry["entry_type"] == "START":
                st.write(f"Situation: {entry['situation']}")
                st.write(f"Task: {entry['task']}")
                st.write(f"Action: {entry['action']}")
                st.write(f"Result: {entry['result']}")
                st.write(f"Takeaway: {entry['takeaway']}")
            elif entry["entry_type"] == "Daily":
                st.write(entry["daily_note"])
            elif entry["entry_type"] == "Longform":
                st.write(entry["longform_content"])
            st.divider()
