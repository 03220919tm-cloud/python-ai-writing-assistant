import os
import streamlit as st


def get_api_key() -> str | None:
    """Returns API key from session state first, then .env."""
    return st.session_state.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")


def show_sidebar_input():
    """Renders the API key input in the sidebar."""
    with st.sidebar:
        st.markdown("---")
        key = st.text_input(
            "Gemini API キー",
            type="password",
            value=st.session_state.get("gemini_api_key", ""),
            placeholder="AIza...",
            help="Google AI Studio (https://aistudio.google.com/) で取得できます",
        )
        if key:
            st.session_state["gemini_api_key"] = key
        elif "gemini_api_key" not in st.session_state and not os.getenv("GEMINI_API_KEY"):
            st.warning("APIキーを入力してください")
