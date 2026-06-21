# Personal Journal App

A journaling app built around two original frameworks: IQR (Ideas, Questions, Reflection) for processing ideas, and START (Situation, Task, Action, Result, Takeaway) — adapted from the STAR interview method, with an added personal Takeaway step — for processing experiences. Includes a focus timer, a generated ambient tone, and an AI assistant that asks reflective questions instead of writing entries for you.

## Live demo
https://personal-journaling-app-6dgrpn4ad7shcl54tmnu5f.streamlit.app/

## Features
- Four entry types: IQR, START, Daily Notes, Long-form
- Persistent storage with separate browsing for structured (IQR/START) vs. freeform entries
- 20/30 minute focus timer with a synthesized ambient tone (Web Audio API, no licensed audio)
- Scrolling affirmation bar
- AI journaling assistant (Gemini API) designed to ask questions, not give answers — it won't write your entry for you, and it's not a substitute for a real person if you're going through something serious

## Built with
- Python, Streamlit
- SQLite for storage
- Gemini API for the AI assistant

## Run it locally
\`\`\`bash
pip install -r requirements.txt
streamlit run app.py
\`\`\`
You'll need a Gemini API key set as an environment variable: `GEMINI_API_KEY`.

---
Built by Andre, incoming UMass CS '30 

