import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.gemini_client import stream_generate
from utils.storage import save_draft
from utils.api_key import show_sidebar_input

st.set_page_config(page_title="メール返信生成", page_icon="📧", layout="wide")
show_sidebar_input()
st.title("📧 メール返信生成")
st.markdown("受信したメールを貼り付けると、適切な返信文を自動生成します。")
st.markdown("---")

col1, col2 = st.columns([3, 2])

with col1:
    received_email = st.text_area(
        "受信メール本文",
        placeholder="ここに受信したメールの本文を貼り付けてください...",
        height=250,
    )
    reply_intent = st.text_area(
        "返信の意図・伝えたいこと",
        placeholder="例: 承諾する、断る、質問する、日程調整する...",
        height=80,
    )

with col2:
    reply_tone = st.selectbox(
        "返信のトーン",
        ["丁寧・ビジネス", "フレンドリー", "簡潔・シンプル", "感謝を強調", "謝罪を含む"],
    )
    sender_name = st.text_input("送信者名（あなたの名前）", placeholder="例: 山田太郎")
    recipient_name = st.text_input("宛先の相手名", placeholder="例: 鈴木様")
    include_greeting = st.checkbox("冒頭の挨拶を含める", value=True)
    include_closing = st.checkbox("締めの挨拶を含める", value=True)
    num_variations = st.radio("生成パターン数", [1, 2, 3], horizontal=True)
    temperature = st.slider("バリエーション", 0.0, 1.0, 0.5, 0.1, help="高いほど多様な表現になります")

st.markdown("---")

if st.button("返信文を生成する", type="primary", use_container_width=True):
    if not received_email:
        st.warning("受信メールを入力してください。")
    else:
        greeting_str = "冒頭に適切な挨拶を含める。" if include_greeting else "冒頭の挨拶は不要。"
        closing_str = "末尾に適切な締めの挨拶を含める。" if include_closing else "締めの挨拶は不要。"
        sender_str = f"送信者: {sender_name}\n" if sender_name else ""
        recipient_str = f"宛先: {recipient_name}\n" if recipient_name else ""
        intent_str = f"返信の意図: {reply_intent}\n" if reply_intent else ""

        prompt = f"""あなたはメール文章のプロフェッショナルです。以下の受信メールに対する返信文を作成してください。

【受信メール】
{received_email}

【条件】
{sender_str}{recipient_str}{intent_str}トーン: {reply_tone}
{greeting_str}
{closing_str}
{"パターンを" + str(num_variations) + "つ生成し、それぞれ「--- パターン1 ---」のように区切ってください。" if num_variations > 1 else ""}

- 自然で読みやすい日本語で書いてください
- 返信の意図を明確に伝えてください
- メールの内容に沿った適切な返信にしてください
"""

        with st.spinner("返信文を生成中..."):
            output_area = st.empty()
            full_text = ""
            for chunk in stream_generate(prompt, temperature=temperature):
                full_text += chunk
                output_area.markdown(full_text)

        st.success("生成完了！")

        st.markdown("---")
        col_save1, col_save2 = st.columns([3, 1])
        with col_save1:
            save_title = st.text_input(
                "保存タイトル",
                value=f"メール返信_{recipient_name or '相手'}",
                key="email_save_title",
            )
        with col_save2:
            st.write("")
            st.write("")
            if st.button("下書き保存", key="email_save"):
                save_draft(save_title, full_text, "メール返信")
                st.success("下書きを保存しました！")

        st.download_button(
            label="テキストファイルでダウンロード",
            data=full_text,
            file_name="email_reply.txt",
            mime="text/plain",
        )
