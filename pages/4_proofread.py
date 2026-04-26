import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.gemini_client import stream_generate
from utils.storage import save_draft

st.set_page_config(page_title="文章校正・改善", page_icon="✏️", layout="wide")
st.title("✏️ 文章校正・改善")
st.markdown("文章のミスや改善点を指摘し、より良い文章に仕上げます。")
st.markdown("---")

original_text = st.text_area(
    "校正・改善したい文章",
    placeholder="ここに文章を貼り付けてください...",
    height=200,
)

col1, col2 = st.columns(2)
with col1:
    check_modes = st.multiselect(
        "チェック項目",
        ["誤字・脱字", "文法・表現の誤り", "読みやすさの改善", "冗長な表現の削除", "論理的な流れ", "敬語・言葉遣い"],
        default=["誤字・脱字", "文法・表現の誤り", "読みやすさの改善"],
    )
    output_style = st.radio(
        "出力スタイル",
        ["改善文のみ出力", "修正点の解説付き", "元文と改善文を並べて表示"],
        index=1,
    )

with col2:
    target_style = st.selectbox(
        "目標文体",
        ["変更なし（現状のまま改善）", "ビジネス文書", "ブログ・Web記事", "SNS投稿", "学術・レポート"],
    )
    preserve_length = st.checkbox("文字数をなるべく維持する", value=False)
    temperature = st.slider("修正の積極度", 0.0, 1.0, 0.3, 0.1, help="低いほど最小限の修正、高いほど大胆に改善します")

st.markdown("---")

if st.button("校正・改善する", type="primary", use_container_width=True):
    if not original_text:
        st.warning("文章を入力してください。")
    elif not check_modes:
        st.warning("チェック項目を1つ以上選択してください。")
    else:
        checks_str = "、".join(check_modes)
        style_str = f"目標文体: {target_style}\n" if target_style != "変更なし（現状のまま改善）" else ""
        length_str = "文字数は元の文章とほぼ同じになるよう心がけてください。\n" if preserve_length else ""

        output_instructions = {
            "改善文のみ出力": "改善した文章のみ出力してください。",
            "修正点の解説付き": "まず修正点を箇条書きで解説し、次に改善した文章を出力してください。",
            "元文と改善文を並べて表示": "元の文章と改善した文章を「【元の文章】」「【改善後】」の見出しで並べて表示してください。",
        }[output_style]

        prompt = f"""あなたは日本語の文章校正の専門家です。以下の文章を校正・改善してください。

【元の文章】
{original_text}

【チェック項目】
{checks_str}

【条件】
{style_str}{length_str}{output_instructions}
- 自然で読みやすい日本語になるよう改善してください
"""

        with st.spinner("校正・改善中..."):
            output_area = st.empty()
            full_text = ""
            for chunk in stream_generate(prompt, temperature=temperature):
                full_text += chunk
                output_area.markdown(full_text)

        st.success("完了！")

        col_save1, col_save2 = st.columns([3, 1])
        with col_save1:
            save_title = st.text_input("保存タイトル", value="校正済み文章", key="proof_save_title")
        with col_save2:
            st.write("")
            st.write("")
            if st.button("下書き保存", key="proof_save"):
                save_draft(save_title, full_text, "その他")
                st.success("保存しました！")

        st.download_button(
            label="ダウンロード",
            data=full_text,
            file_name="proofread_result.txt",
            mime="text/plain",
        )
