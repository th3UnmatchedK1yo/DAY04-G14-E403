from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS = ROOT / "artifacts"
TRANSCRIPTS = ROOT / "transcripts"
VERSION_CONFIGS = {
    "v0": (
        ARTIFACTS / "versions" / "v0_system_prompt.md",
        ARTIFACTS / "versions" / "v0_tools.yaml",
    ),
    "v1": (
        ARTIFACTS / "versions" / "v1_system_prompt.md",
        ARTIFACTS / "versions" / "v0_tools.yaml",
    ),
    "v2": (
        ARTIFACTS / "versions" / "v2_system_prompt.md",
        ARTIFACTS / "versions" / "v0_tools.yaml",
    ),
    "v3": (
        ARTIFACTS / "system_prompt.md",
        ARTIFACTS / "tools.yaml",
    ),
}

load_lab_env(ROOT)


@st.cache_resource
def get_provider(provider_name: str) -> Any:
    return make_provider(provider_name)


@st.cache_data
def load_version(version: str) -> dict[str, Any]:
    prompt_path, tools_path = VERSION_CONFIGS[version]
    prompt = prompt_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
    artifact = build_artifact_version(version, prompt_path, tools_path)
    return {
        "prompt_path": prompt_path,
        "tools_path": tools_path,
        "prompt": prompt,
        "tools": to_openai_tools(declarations),
        "artifact": artifact,
    }


def new_transcript(
    *,
    version: str,
    provider_name: str,
    model: str | None,
    config: dict[str, Any],
    prefix: str = "ui",
) -> tuple[dict[str, Any], Path]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(
        [prefix, safe_slug(version), safe_slug(provider_name), timestamp]
    )
    path = TRANSCRIPTS / f"{transcript_id}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(config["artifact"]),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(config["prompt_path"]),
        "tools": str(config["tools_path"]),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "source": "streamlit_ui",
        "turns": [],
    }
    return transcript, path


def run_turn(
    *,
    user_text: str,
    version: str,
    provider_name: str,
    model: str | None,
    history: list[dict[str, str]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    config = load_version(version)
    messages = [
        {"role": "system", "content": config["prompt"]},
        *trim_history(history, 5),
        {"role": "user", "content": user_text},
    ]
    started_at = now_iso()
    try:
        result = run_model_tool_loop(
            provider=get_provider(provider_name),
            messages=messages,
            tools=config["tools"],
            model=model,
            max_tool_rounds=4,
        )
        record = {
            "started_at": started_at,
            "ended_at": now_iso(),
            "user": user_text,
            **result,
        }
        return result, record
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        result = {
            "status": "provider_error",
            "assistant_text": error,
            "rounds": [],
            "tool_events": [],
            "error": error,
        }
        record = {
            "started_at": started_at,
            "ended_at": now_iso(),
            "user": user_text,
            **result,
        }
        return result, record


def render_trace(result: dict[str, Any], *, key_prefix: str) -> None:
    status = result.get("status", "unknown")
    rounds = result.get("rounds", [])
    tool_events = result.get("tool_events", [])
    st.caption(
        f"Status: `{status}` · {len(rounds)} round(s) · "
        f"{len(tool_events)} tool event(s)"
    )
    if not rounds:
        return

    with st.expander("Tool trace", expanded=bool(tool_events)):
        for index, round_record in enumerate(rounds, start=1):
            st.markdown(f"**Round {round_record.get('round', index)}**")
            calls = round_record.get("tool_calls", [])
            if calls:
                for call_index, call in enumerate(calls, start=1):
                    st.code(
                        f"{call.get('name')}("
                        f"{json.dumps(call.get('args', {}), ensure_ascii=False, sort_keys=True)}"
                        ")",
                        language="text",
                    )
            else:
                st.caption("Không gọi tool ở round này.")

            for event_index, event in enumerate(
                round_record.get("tool_results", []), start=1
            ):
                result_payload = event.get("result", {})
                label = f"{event.get('tool', 'tool')} result"
                if isinstance(result_payload, dict) and result_payload.get("error"):
                    st.error(
                        f"{label}: {result_payload.get('error')} — "
                        f"{result_payload.get('message', '')}"
                    )
                else:
                    st.json(
                        event,
                        expanded=False,
                    )
            if index < len(rounds):
                st.divider()


def ensure_chat_state(
    *,
    version: str,
    provider_name: str,
    model: str | None,
) -> None:
    identity = (version, provider_name, model)
    if st.session_state.get("chat_identity") == identity:
        return
    config = load_version(version)
    transcript, path = new_transcript(
        version=version,
        provider_name=provider_name,
        model=model,
        config=config,
    )
    st.session_state.chat_identity = identity
    st.session_state.chat_messages = []
    st.session_state.chat_history = []
    st.session_state.chat_transcript = transcript
    st.session_state.chat_transcript_path = path


def render_chat(
    *,
    version: str,
    provider_name: str,
    model: str | None,
) -> None:
    ensure_chat_state(
        version=version,
        provider_name=provider_name,
        model=model,
    )
    config = load_version(version)
    artifact = config["artifact"]

    left, right = st.columns([2, 1])
    with left:
        st.caption(f"Artifact: `{artifact.artifact_version}`")
    with right:
        if st.button("Xóa hội thoại", use_container_width=True):
            st.session_state.pop("chat_identity", None)
            st.rerun()

    for index, message in enumerate(st.session_state.chat_messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_trace(message["result"], key_prefix=f"chat-{index}")

    user_text = st.chat_input("Nhập yêu cầu research…")
    if not user_text:
        return

    st.session_state.chat_messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("Agent đang xử lý…"):
            result, turn_record = run_turn(
                user_text=user_text,
                version=version,
                provider_name=provider_name,
                model=model,
                history=st.session_state.chat_history,
            )
        assistant_text = result.get("assistant_text") or "(Không có response text)"
        st.markdown(assistant_text)
        render_trace(result, key_prefix=f"chat-live-{len(st.session_state.chat_messages)}")

    st.session_state.chat_messages.append(
        {
            "role": "assistant",
            "content": assistant_text,
            "result": result,
        }
    )
    st.session_state.chat_history.extend(
        [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": assistant_text},
        ]
    )
    transcript = st.session_state.chat_transcript
    turn_record["turn_index"] = len(transcript["turns"]) + 1
    transcript["turns"].append(turn_record)
    write_transcript(st.session_state.chat_transcript_path, transcript)

    st.caption(
        "Transcript: "
        f"`{st.session_state.chat_transcript_path.relative_to(ROOT)}`"
    )


def render_comparison(
    *,
    provider_name: str,
    model: str | None,
) -> None:
    st.write(
        "Chạy cùng một request trên nhiều artifact. Mỗi kết quả hiển thị "
        "artifact version, response và full tool trace."
    )
    st.warning(
        "Comparison gọi tool thật. Không dùng yêu cầu đã xác nhận gửi Telegram "
        "hoặc nội dung nhạy cảm."
    )
    scenario = st.text_area(
        "Scenario",
        value="Tóm tắt 5 tweet mới nhất giúp mình",
        height=100,
    )
    selected_versions = st.multiselect(
        "Versions",
        options=list(VERSION_CONFIGS),
        default=["v0", "v3"],
    )

    if st.button(
        "Chạy so sánh",
        type="primary",
        disabled=not scenario.strip() or not selected_versions,
    ):
        comparison_results: dict[str, Any] = {}
        progress = st.progress(0, text="Đang chạy comparison…")
        for index, version in enumerate(selected_versions, start=1):
            config = load_version(version)
            result, record = run_turn(
                user_text=scenario.strip(),
                version=version,
                provider_name=provider_name,
                model=model,
                history=[],
            )
            transcript, path = new_transcript(
                version=version,
                provider_name=provider_name,
                model=model,
                config=config,
                prefix="comparison",
            )
            record["turn_index"] = 1
            transcript["turns"].append(record)
            write_transcript(path, transcript)
            comparison_results[version] = {
                "artifact_version": config["artifact"].artifact_version,
                "result": result,
                "transcript": str(path.relative_to(ROOT)),
            }
            progress.progress(
                index / len(selected_versions),
                text=f"Đã chạy {version}",
            )
        progress.empty()
        st.session_state.comparison_results = comparison_results

    results = st.session_state.get("comparison_results", {})
    if not results:
        return

    tabs = st.tabs(list(results))
    for tab, (version, payload) in zip(tabs, results.items()):
        with tab:
            st.caption(f"Artifact: `{payload['artifact_version']}`")
            st.caption(f"Transcript: `{payload['transcript']}`")
            st.markdown(payload["result"].get("assistant_text") or "(Không có response text)")
            render_trace(payload["result"], key_prefix=f"compare-{version}")


st.set_page_config(
    page_title="Research Agent Eval Lab",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Research Agent Eval Lab")
st.caption("Chat, inspect tool traces, and compare artifact versions.")

with st.sidebar:
    st.header("Runtime")
    provider_name = st.selectbox(
        "Provider",
        options=["openrouter", "openai", "anthropic", "gemini"],
        index=0,
    )
    version = st.selectbox("Artifact version", options=list(VERSION_CONFIGS), index=3)
    model_text = st.text_input(
        "Model override",
        value="openai/gpt-4o-mini" if provider_name == "openrouter" else "",
        help="Để trống để dùng default model của provider.",
    )
    model = model_text.strip() or None
    config = load_version(version)
    st.divider()
    st.subheader("Evidence")
    st.code(config["artifact"].artifact_version, language="text")
    st.caption(f"Prompt: `{config['prompt_path'].relative_to(ROOT)}`")
    st.caption(f"Tools: `{config['tools_path'].relative_to(ROOT)}`")
    st.caption(f"Prompt hash: `{config['artifact'].prompt_hash[:12]}`")
    st.caption(f"Tools hash: `{config['artifact'].tools_hash[:12]}`")
    st.caption("Secrets are loaded server-side and are never displayed.")

chat_tab, comparison_tab = st.tabs(["Chat + trace", "So sánh versions"])
with chat_tab:
    render_chat(
        version=version,
        provider_name=provider_name,
        model=model,
    )
with comparison_tab:
    render_comparison(
        provider_name=provider_name,
        model=model,
    )
