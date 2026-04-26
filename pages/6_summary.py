import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.gemini_client import stream_generate
from utils.storage import save_draft

st.set_page_config(page_title="文章要約", page_icon="📋", layout="wide")
st.title("📋 文章要約")
st.markdown("長い文章を指定の長さ・形式で要約します。議事録・記事・レポートなどに対応。")
st.markdown("---")

col1, col2 = st.columns([3, 2])

with col1:
    original_text = st.text_area(
        "要約する文章",
        placeholder="ここに要約したい文章を貼り付けてください...",
        height=300,
    )

with col2:
    summary_length = st.select_slider(
        "要約の長さ",
        options=["3行", "5行", "100文字", "200文字", "300文字", "500文字"],
        value="5行",
    )
    summary_format = st.selectbox(
        "出力形式",
        ["文章形式", "箇条書き", "見出し付き箇条書き", "Q&A形式", "TLDR（一文要約）+詳細"],
    )
    summary_focus = st.multiselect(
        "重点的にまとめる内容",
        ["結論・結果", "数値・データ", "課題・問題点", "解決策・提案", "背景・経緯", "アクションアイテム"],
        default=["結論・結果"],
    )
    language = st.radio("出力言語", ["日本語", "英語", "日英両方"], horizontal=True)
    temperature = st.slider("要約の柔軟度", 0.0, 1.0, 0.2, 0.1, help="低いほど原文に忠実、高いほど意訳します")

st.markdown("---")

if st.button("要約する", type="primary", use_container_width=True):
    if not original_text:
        st.warning("文章を入力してください。")
    else:
        focus_str = "、".join(summary_focus) if summary_focus else "全体的な内容"
        lang_str = {
            "日本語": "日本語で出力してください。",
            "英語": "英語で出力してください。",
            "日英両方": "日本語と英語の両方で出力してください。",
        }[language]

        format_instructions = {
            "文章形式": "自然な文章形式でまとめてください。",
            "箇条書き": "箇条書き（・）でポイントをまとめてください。",
            "見出し付き箇条書き": "カテゴリごとに見出しを付けた箇条書きでまとめてください。",
            "Q&A形式": "想定される質問とその答えのQ&A形式でまとめてください。",
            "TLDR（一文要約）+詳細": "最初に一文の「TLDR」要約を書き、次に詳細をまとめてください。",
        }[summary_format]

        prompt = f"""あなたは文章要約の専門家です。以下の文章を要約してください。

【原文】
{original_text}

【条件】
長さ: {summary_length}程度
形式: {format_instructions}
重点項目: {focus_str}
{lang_str}

- 原文の重要な情報を漏らさず、簡潔にまとめてください
- 独自の解釈や推測を加えず、原文に基づいて要約してください
"""

        with st.spinner("要約中..."):
            output_area = st.empty()
            full_text = ""
            for chunk in stream_generate(prompt, temperature=temperature):
                full_text += chunk
                output_area.markdown(full_text)

        st.success("完了！")

        char_count = len(original_text)
        summary_count = len(full_text)
        reduction = round((1 - summary_count / char_count) * 100) if char_count > 0 else 0
        st.caption(f"元の文章: {char_count}文字 → 要約: {summary_count}文字（{reduction}%削減）")

        col_save1, col_save2 = st.columns([3, 1])
        with col_save1:
            save_title = st.text_input("保存タイトル", value="要約文章", key="summary_save_title")
        with col_save2:
            st.write("")
            st.write("")
            if st.button("下書き保存", key="summary_save"):
                save_draft(save_title, full_text, "その他")
                st.success("保存しました！")

        st.download_button(
            label="ダウンロード",
            data=full_text,
            file_name="summary.txt",
            mime="text/plain",
        )
