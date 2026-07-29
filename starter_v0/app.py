import streamlit as st
import json
from pathlib import Path

from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop, trim_history
from env_loader import load_lab_env

# Đảm bảo load biến môi trường từ .env
ROOT = Path(__file__).parent
load_lab_env(ROOT)

st.set_page_config(page_title="Research Agent UI", page_icon="🤖")
st.title("Research Agent Demo")

# Cấu hình ở Sidebar
with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"])
    model_override = st.text_input("Model (để trống sẽ dùng default của provider)", value="")
    version = st.text_input("Version", value="v0")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lại lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "rounds" in msg and msg["rounds"]:
            with st.expander("🛠 Xem chi tiết gọi Tool (Tool Trace)"):
                st.json(msg["rounds"])

# Nhận input mới từ user
if prompt := st.chat_input("Hãy yêu cầu Research Agent làm gì đó..."):
    # Thêm user prompt vào state và hiển thị
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Hiển thị ô chờ của trợ lý
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # 1. Tải cấu hình, tools, system prompt
        ARTIFACTS_DIR = ROOT / "artifacts"
        system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
        tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
        openai_tools = to_openai_tools(tool_declarations)
        provider = make_provider(provider_name)
        selected_model = model_override if model_override else getattr(provider, "default_model", None)
        
        # 2. Xây dựng history context
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
        messages_for_llm = [
            {"role": "system", "content": system_prompt},
            *trim_history(history, window=5),
            {"role": "user", "content": prompt},
        ]
        
        # 3. Gọi hàm loop chính (run_model_tool_loop tái sử dụng từ chat.py)
        import importlib
        import chat
        import tools
        importlib.reload(tools)
        importlib.reload(chat)
        with st.spinner("Agent đang suy nghĩ và gọi công cụ..."):
            result = chat.run_model_tool_loop(
                provider=provider,
                messages=messages_for_llm,
                tools=openai_tools,
                model=selected_model,
                max_tool_rounds=4,
            )
        
        assistant_text = result.get("assistant_text", "")
        message_placeholder.markdown(assistant_text)
        
        rounds = result.get("rounds", [])
        if rounds:
            with st.expander("🛠 Xem chi tiết gọi Tool (Tool Trace)"):
                st.json(rounds)
            
    # Lưu phản hồi của trợ lý vào state
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_text,
        "rounds": rounds
    })
