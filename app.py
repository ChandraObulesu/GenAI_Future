import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

ROOT = Path(__file__).resolve().parent
HISTORY_PATH = ROOT / "chat_history.json"

SYSTEM_PROMPT = """
You are Cricket Guru, a friendly cricket expert.

You know the laws of cricket, formats (Test, ODI, T20, and others), tactics, fielding positions, gear, tournaments, history, and players.

Follow these rules on every reply:
1. Talk about cricket only.
2. If a question is not about cricket but you can honestly connect it to cricket, answer through that cricket link. Example: a question about the weather becomes an answer about the pitch, swing, and match conditions.
3. If you cannot connect the question to cricket, reply with exactly this text and nothing else: out of the context
4. Language: reply in English. If the user writes in Tinglish (Telugu mixed with English, written in English letters), reply in Tinglish.
5. Length: keep a short answer short. If the answer would be long, start with one short summary line, then use bullet points. Do not write long paragraphs.
6. Do not invent live scores. If you are unsure of a fact or statistic, say you are not sure.
""".strip()

def save_history(messages):
    """Overwrite the JSON file with the current chat only."""
    HISTORY_PATH.write_text(json.dumps(messages, indent=2), encoding="utf-8")

def ask_gemini(messages):
    client =  genai.Client(api_key =  os.getenv("GEMINI_API_Key"))
    model = os.getenv("genai_model","gemini-3.8-flash")
    response = client.models.generate_content(
        model = model,
        contents = "SYSTEM_PROMPT",
        config = types.GenerateContentConfig(
            temperature = 0.8
        )
    )
    return response.text or "out of context"

st.set_page_config(page_title="Cricket Guru", page_icon="🏏")
st.title("Cricket Guru")
st.caption("Cricket only. Ask about rules, players, tactics, or matches.")

if not os.getenv("GEMINI_API_Key"):
    st.error("Add your OpenAI key to the .env file as GEMINI_API_Key, then restart the app.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
    save_history([])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask a cricket question")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history(st.session_state.messages)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            reply = ask_gemini(st.session_state.messages)
        except Exception as exc:
            # Do not show the raw error. It can include part of the API key. simply print the error
            print(exc)
            reply = "Could not reach OpenAI. Check your internet connection and try again."
        
    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_history(st.session_state.messages)
    st.markdown(reply)