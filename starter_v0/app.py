import streamlit as st
import json
from pathlib import Path
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import (
    run_model_tool_loop,
    now_iso,
    trim_history,
    write_transcript,
    safe_slug,
    build_artifact_version,
    artifact_version_dict,
)

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

st.set_page_config(page_title="AI2026 Research Agent", layout="wide")

st.title("Research Agent")

# Sidebar setup
with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
    model_name = st.text_input("Model (để trống để dùng default)", "")
    version_label = st.text_input("Version Label", "v0")
    max_rounds = st.number_input("Max Tool Rounds", min_value=1, max_value=10, value=4)
    history_window = st.number_input("History Window", min_value=1, max_value=20, value=5)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "transcript" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"{safe_slug(version_label)}_{safe_slug(provider_name)}_{timestamp}"
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        "provider": provider_name,
        "model": model_name or "default",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

# Load resources
@st.cache_resource
def get_system_prompt():
    return (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")

@st.cache_resource
def get_tools():
    tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    return to_openai_tools(tool_declarations)

system_prompt = get_system_prompt()
openai_tools = get_tools()

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# User Input
user_text = st.chat_input("Nhập tin nhắn...")

if user_text:
    st.chat_message("user").write(user_text)
    
    provider = make_provider(provider_name)
    model = model_name if model_name else getattr(provider, "default_model", None)
    
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]
    
    turn_record = {
        "turn_index": len(st.session_state.transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
    }
    
    with st.spinner("Agent đang xử lý..."):
        try:
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=model,
                max_tool_rounds=max_rounds,
            )
            
            turn_record.update(result)
            assistant_text = result.get("assistant_text", "")
            if assistant_text:
                st.chat_message("assistant").write(assistant_text)
                
            # Cập nhật lịch sử
            st.session_state.messages.append({"role": "user", "content": user_text})
            st.session_state.messages.append({"role": "assistant", "content": assistant_text})
            
            st.session_state.history.append({"role": "user", "content": user_text})
            st.session_state.history.append({"role": "assistant", "content": assistant_text})
            
            # Show tool events / rounds in expander
            if result.get("rounds"):
                with st.expander("🛠️ Xem chi tiết Tool Trace & Rounds"):
                    st.json(result["rounds"])
                    
        except Exception as e:
            turn_record.update({"status": "provider_error", "error": str(e)})
            st.error(f"Lỗi: {str(e)}")
            
        turn_record["ended_at"] = now_iso()
        st.session_state.transcript["turns"].append(turn_record)
        write_transcript(st.session_state.transcript_path, st.session_state.transcript)
        st.toast(f"Transcript saved: {st.session_state.transcript_path.name}")