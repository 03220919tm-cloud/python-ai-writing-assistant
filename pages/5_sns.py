import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.gemini_client import stream_generate
from utils.storage import save_draft
from utils.api_key import show_sidebar_input

st.set_page_config(page_title="SNS投稿文生成", page_icon="📱", layout="wide")
show_sidebar_input()
st.title("📱 SNS投稿文生成")
st.markdown("伝えたいことを入力するだけで、各SNSに最適な投稿文を自動生成します。")
st.markdown("---")

col1, col2 = st.columns([3, 2])

with col1:
    post_theme = st.text_area(
        "投稿のテーマ・伝えたいこと",
        placeholder="例: 今日のカフェで飲んだラテが絶品だった。写真も撮った。",
        height=120,
    )
    reference_url = st.text_input(
        "参考URL・リンク（任意）",
        placeholder="例: https://example.com/article",
    )

with col2:
    platforms = st.multiselect(
        "投稿するSNS",
        ["Twitter/X", "Instagram", "Facebook", "LinkedIn", "Threads", "note"],
        default=["Twitter/X"],
    )
    post_tone = st.selectbox(
        "投稿のトーン",
        ["カジュアル・日常的", "プロフェッショナル", "感情的・共感", "情報提供・有益", "ユーモア・面白い"],
    )
    use_emoji = st.checkbox("絵文字を使う", value=True)
    use_hashtag = st.checkbox("ハッシュタグを付ける", value=True)
    num_posts = st.radio("生成パターン数", [1, 2, 3], horizontal=True)
    temperature = st.slider("創造性", 0.0, 1.0, 0.8, 0.1)

st.markdown("---")

PLATFORM_RULES = {
    "Twitter/X": "140文字以内、短くインパクトある文章",
    "Instagram": "キャプション形式、改行多め、ハッシュタグは最後にまとめる",
    "Facebook": "300〜500文字程度、親しみやすい文体",
    "LinkedIn": "ビジネス向け、300〜600文字、学びや実績を含める",
    "Threads": "500文字以内、カジュアル、会話的な文体",
    "note": "800〜1500文字のイントロ文、読者を引き込む書き出し",
}

if st.button("投稿文を生成する", type="primary", use_container_width=True):
    if not post_theme:
        st.warning("投稿のテーマを入力してください。")
    elif not platforms:
        st.warning("SNSプラットフォームを1つ以上選択してください。")
    else:
        emoji_str = "絵文字を積極的に使ってください。" if use_emoji else "絵文字は使わないでください。"
        hashtag_str = "関連するハッシュタグを付けてください。" if use_hashtag else "ハッシュタグは不要です。"
        url_str = f"投稿に「{reference_url}」のリンクを含めてください。" if reference_url else ""
        pattern_str = f"各プラットフォームで{num_posts}パターン生成し、「--- パターン1 ---」で区切ってください。" if num_posts > 1 else ""

        platforms_detail = "\n".join([f"- {p}: {PLATFORM_RULES.get(p, '')}" for p in platforms])

        prompt = f"""あなたはSNSマーケティングの専門家です。以下の内容で各SNSに最適な投稿文を生成してください。

【テーマ・内容】
{post_theme}

【対象SNSと文字数・形式ルール】
{platforms_detail}

【条件】
トーン: {post_tone}
{emoji_str}
{hashtag_str}
{url_str}
{pattern_str}

各SNSの投稿文を「=== Twitter/X ===" のように見出しで区切って出力してください。
それぞれのSNSの特性に合わせた最適な文章にしてください。
"""

        with st.spinner("投稿文を生成中..."):
            output_area = st.empty()
            full_text = ""
            for chunk in stream_generate(prompt, temperature=temperature):
                full_text += chunk
                output_area.markdown(full_text)

        st.success("生成完了！")

        col_save1, col_save2 = st.columns([3, 1])
        with col_save1:
            save_title = st.text_input("保存タイトル", value=f"SNS投稿_{post_theme[:20]}", key="sns_save_title")
        with col_save2:
            st.write("")
            st.write("")
            if st.button("下書き保存", key="sns_save"):
                save_draft(save_title, full_text, "SNS投稿")
                st.success("保存しました！")

        st.download_button(
            label="ダウンロード",
            data=full_text,
            file_name="sns_posts.txt",
            mime="text/plain",
        )
