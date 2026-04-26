import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.gemini_client import stream_generate
from utils.storage import save_draft
from utils.api_key import show_sidebar_input

st.set_page_config(page_title="ブログ記事生成", page_icon="📝", layout="wide")
show_sidebar_input()
st.title("📝 ブログ記事生成")
st.markdown("テーマや条件を入力して、ブログ記事を自動生成します。")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input("記事のテーマ・タイトル", placeholder="例: 初心者向けPython入門、健康的な朝食レシピ")
    keywords = st.text_input("含めたいキーワード（カンマ区切り）", placeholder="例: プログラミング, 初心者, 学習方法")
    audience = st.text_input("ターゲット読者", placeholder="例: プログラミング初心者、20代会社員")
    purpose = st.text_area("記事の目的・伝えたいこと", placeholder="例: 読者がPythonを始めるきっかけを作る", height=80)

with col2:
    article_length = st.select_slider(
        "記事の長さ",
        options=["短め（500字）", "標準（1000字）", "長め（2000字）", "詳細（3000字）"],
        value="標準（1000字）",
    )
    tone = st.selectbox(
        "文体・トーン",
        ["丁寧・フォーマル", "親しみやすい・カジュアル", "専門的・技術的", "エンタメ・面白い"],
    )
    include_sections = st.multiselect(
        "含めるセクション",
        ["導入・つかみ", "目次", "本文", "まとめ", "CTA（行動喚起）"],
        default=["導入・つかみ", "本文", "まとめ"],
    )
    temperature = st.slider("創造性", 0.0, 1.0, 0.7, 0.1, help="高いほど個性的な文章になります")

st.markdown("---")

length_map = {
    "短め（500字）": "約500文字",
    "標準（1000字）": "約1000文字",
    "長め（2000字）": "約2000文字",
    "詳細（3000字）": "約3000文字",
}

if st.button("記事を生成する", type="primary", use_container_width=True):
    if not topic:
        st.warning("テーマを入力してください。")
    else:
        sections_str = "、".join(include_sections) if include_sections else "自由構成"
        kw_str = f"キーワード: {keywords}\n" if keywords else ""
        audience_str = f"ターゲット読者: {audience}\n" if audience else ""
        purpose_str = f"目的: {purpose}\n" if purpose else ""

        prompt = f"""あなたはSEOとコンテンツマーケティングの専門家です。Googleで上位表示されやすく、かつ読者にとって価値あるブログ記事を作成してください。

テーマ: {topic}
{kw_str}{audience_str}{purpose_str}文体: {tone}
文字数: {length_map[article_length]}
含めるセクション: {sections_str}

【SEO要件】
- 記事の冒頭100文字以内にメインキーワードを自然に含める
- H2見出し（##）にキーワードや検索意図に沿った言葉を入れる
- 読者の「悩み → 原因 → 解決策」の流れで構成する
- 検索意図（知りたい・やりたい・行きたい・買いたい）を意識した内容にする
- 数字・具体例・体験談風の表現で信頼性と専門性を高める
- 「〇〇とは」「〇〇の方法」「〇〇のポイント」など検索されやすい表現を見出しに使う
- 最後にまとめと次のアクションを促すCTAを入れる

【品質要件】
- 他のサイトにない独自の視点や情報を1つ以上入れる
- 箇条書きや表を活用して読みやすくする
- 日本語で書く
"""

        with st.spinner("記事を生成中..."):
            output_area = st.empty()
            full_text = ""
            for chunk in stream_generate(prompt, temperature=temperature):
                full_text += chunk
                output_area.markdown(full_text)

        st.success("生成完了！")

        st.markdown("---")
        col_save1, col_save2 = st.columns([3, 1])
        with col_save1:
            save_title = st.text_input("保存タイトル", value=topic, key="blog_save_title")
        with col_save2:
            st.write("")
            st.write("")
            if st.button("下書き保存", key="blog_save"):
                save_draft(save_title, full_text, "ブログ記事")
                st.success("下書きを保存しました！📅 スケジューラーで確認できます。")

        st.download_button(
            label="テキストファイルでダウンロード",
            data=full_text,
            file_name=f"{topic}.txt",
            mime="text/plain",
        )
