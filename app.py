import streamlit as st

st.set_page_config(
    page_title="AI Writing Tool",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("✍️ AI ライティングツール")
st.markdown("---")

st.markdown("""
### ようこそ！

このツールは **Gemini AI** を使ったパーソナル・ライティングアシスタントです。
サイドバーから使いたい機能を選んでください。

---

### 機能一覧

| ページ | 機能 |
|--------|------|
| 📝 ブログ記事 | テーマを入力するだけでブログ記事を自動生成 |
| 📧 メール返信 | 受信メールへの返信文を自動作成 |
| 📅 スケジューラー | 生成した文章の下書き保存・管理 |
| ✏️ 文章校正 | 文章のミスを指摘・改善提案 |
| 📱 SNS投稿 | Twitter/Instagramの投稿文を生成 |
| 📋 要約 | 長い文章を指定の長さに要約 |

---

### 初期設定

`.env` ファイルに Gemini API キーを設定してください:

```
GEMINI_API_KEY=your_api_key_here
```

API キーは [Google AI Studio](https://aistudio.google.com/) で取得できます。
""")

st.sidebar.success("上のメニューから機能を選択してください")
