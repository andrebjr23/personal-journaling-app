import streamlit as st
import streamlit.components.v1 as components
import sqlite3
from datetime import datetime, date, timedelta
import os
from google import genai
from google.genai import types

DB_PATH = "journal.db"

def get_api_key(key_name):
    try:
        return st.secrets[key_name]
    except Exception:
        return os.environ.get(key_name)

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

def get_entries(entry_types):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    placeholders = ",".join(["?"] * len(entry_types))
    c.execute(f"SELECT * FROM entries WHERE entry_type IN ({placeholders}) ORDER BY created_at DESC", entry_types)
    rows = c.fetchall()
    col_names = [desc[0] for desc in c.description]
    conn.close()
    return rows, col_names

def get_streak():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT created_at FROM entries")
    rows = c.fetchall()
    conn.close()

    entry_dates = set()
    for (created_at,) in rows:
        entry_dates.add(created_at.split(" ")[0])

    today = date.today()
    check_date = today
    if check_date.isoformat() not in entry_dates:
        check_date = today - timedelta(days=1)

    streak = 0
    while check_date.isoformat() in entry_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak

init_db()

st.title("Journal")

streak = get_streak()
if streak > 0:
    fire = "🔥" * min(streak, 5)
    st.markdown(
        f"""
        <div style="text-align:center; padding:14px; background:#A47551; border-radius:10px; margin-bottom:15px;">
            <span style="font-size:26px; font-weight:bold; color:#FFF7EC;">{fire} {streak} Day Streak {fire}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div style="text-align:center; padding:14px; background:#E8D9C5; border-radius:10px; margin-bottom:15px;">
            <span style="font-size:20px; color:#3B2F2F;">Start your streak today!</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

marquee_html = """
<div style="overflow:hidden; white-space:nowrap; background:#E8D9C5; padding:10px 0; border-radius:8px; margin-bottom:20px; width:100%;">
  <div style="display:inline-block; font-family: Georgia, serif; font-size:18px; color:#3B2F2F; animation: scrollLR 45s linear infinite;">
    Ideas don't need to be finished to be worth writing down &nbsp;&nbsp;•&nbsp;&nbsp;
    Every reflection is a takeaway in progress &nbsp;&nbsp;•&nbsp;&nbsp;
    Your own takeaway matters more than anyone else's opinion &nbsp;&nbsp;•&nbsp;&nbsp;
    Small daily notes build a bigger picture &nbsp;&nbsp;•&nbsp;&nbsp;
  </div>
</div>
<style>
@keyframes scrollLR {
  from { transform: translateX(100%); }
  to { transform: translateX(-100%); }
}
</style>
"""
st.markdown(marquee_html, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["New Entry", "Browse Entries", "Focus Timer", "AI Helper"])

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
    entry_types = ["IQR", "START"] if bucket == "IQR / START" else ["Daily", "Longform"]
    rows, col_names = get_entries(entry_types)

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

with tab3:
    st.write("Set a focus timer for your journaling session, with an optional ambient tone.")
    timer_html = """
    <div style="text-align:center; font-family: sans-serif; padding:20px;">
      <div id="display" style="font-size:56px; color:#3B2F2F; font-weight:bold;">20:00</div>
      <div style="margin:15px 0;">
        <button onclick="setDuration(20)" style="margin:5px; padding:8px 16px;">20 min</button>
        <button onclick="setDuration(30)" style="margin:5px; padding:8px 16px;">30 min</button>
      </div>
      <div style="margin:15px 0;">
        <button onclick="startTimer()" style="margin:5px; padding:8px 16px;">Start</button>
        <button onclick="stopTimer()" style="margin:5px; padding:8px 16px;">Reset</button>
      </div>
      <label style="font-size:14px;">
        <input type="checkbox" id="toneToggle" onchange="toggleTone()"> Ambient tone
      </label>
    </div>
    <script>
    let totalSeconds = 20*60;
    let remaining = totalSeconds;
    let timerInterval = null;
    let audioCtx, oscillator1, oscillator2, gainNode;
    function setDuration(mins) {
      totalSeconds = mins*60;
      remaining = totalSeconds;
      updateDisplay();
    }
    function updateDisplay() {
      let m = Math.floor(remaining/60);
      let s = remaining%60;
      document.getElementById('display').innerText =
        String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
    }
    function startTimer() {
      if (timerInterval) return;
      timerInterval = setInterval(() => {
        if (remaining > 0) {
          remaining--;
          updateDisplay();
        } else {
          clearInterval(timerInterval);
          timerInterval = null;
          stopTone();
          document.getElementById('display').innerText = "Done!";
        }
      }, 1000);
    }
    function stopTimer() {
      clearInterval(timerInterval);
      timerInterval = null;
      remaining = totalSeconds;
      updateDisplay();
    }
    function toggleTone() {
      const checked = document.getElementById('toneToggle').checked;
      if (checked) startTone(); else stopTone();
    }
    function startTone() {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      oscillator1 = audioCtx.createOscillator();
      oscillator2 = audioCtx.createOscillator();
      gainNode = audioCtx.createGain();
      oscillator1.type = 'sine';
      oscillator2.type = 'sine';
      oscillator1.frequency.value = 220;
      oscillator2.frequency.value = 224;
      gainNode.gain.value = 0.04;
      oscillator1.connect(gainNode);
      oscillator2.connect(gainNode);
      gainNode.connect(audioCtx.destination);
      oscillator1.start();
      oscillator2.start();
    }
    function stopTone() {
      if (oscillator1) { oscillator1.stop(); oscillator1 = null; }
      if (oscillator2) { oscillator2.stop(); oscillator2 = null; }
      if (audioCtx) { audioCtx.close(); audioCtx = null; }
    }
    updateDisplay();
    </script>
    """
    components.html(timer_html, height=300)

with tab4:
    st.write("Stuck on what to write? Talk it through here.")

    if "gemini_client" not in st.session_state:
        st.session_state.gemini_client = genai.Client(api_key=get_api_key("GEMINI_API_KEY"))

    if "chat" not in st.session_state:
        st.session_state.chat = st.session_state.gemini_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a supportive journaling assistant. Help the user think "
                    "through their IQR (Ideas, Questions, Reflection) or START "
                    "(Situation, Task, Action, Result, Takeaway) entries by asking "
                    "thoughtful follow-up questions, not by giving them answers or "
                    "writing the entry for them. You are not a therapist and do not "
                    "give clinical or medical advice. If the user seems to be in real "
                    "distress, gently encourage them to talk to a real person or "
                    "professional rather than relying on this chat."
                )
            ),
        )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(text)

    user_input = st.chat_input("Ask the journaling helper...")
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user"):
            st.write(user_input)

        response = st.session_state.chat.send_message(user_input)

        st.session_state.chat_history.append(("assistant", response.text))
        with st.chat_message("assistant"):
            st.write(response.text) 
