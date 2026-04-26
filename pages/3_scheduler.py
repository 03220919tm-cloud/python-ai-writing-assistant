import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date, time

sys.path.append(str(Path(__file__).parent.parent))
from utils.storage import load_drafts, save_draft, delete_draft, update_draft
from utils.api_key import show_sidebar_input

st.set_page_config(page_title="文章スケジューラー", page_icon="📅", layout="wide")
show_sidebar_input()
st.title("📅 文章スケジューラー")
st.markdown("下書き文章の保存・管理・予約日時の設定ができます。")
st.markdown("---")

tab1, tab2 = st.tabs(["📋 下書き一覧", "✏️ 新規作成・保存"])

with tab1:
    drafts = load_drafts()

    if not drafts:
        st.info("保存された下書きはありません。「新規作成・保存」タブから追加できます。")
    else:
        category_filter = st.selectbox(
            "カテゴリで絞り込み",
            ["すべて"] + sorted(set(d["category"] for d in drafts)),
        )

        filtered = drafts if category_filter == "すべて" else [d for d in drafts if d["category"] == category_filter]

        st.markdown(f"**{len(filtered)} 件**の下書きが見つかりました。")
        st.markdown("---")

        for draft in reversed(filtered):
            created = datetime.fromisoformat(draft["created_at"]).strftime("%Y/%m/%d %H:%M")
            scheduled = draft.get("scheduled_at")
            scheduled_label = f" | 🕐 予約: {scheduled}" if scheduled else ""

            with st.expander(f"**{draft['title']}**　`{draft['category']}`　{created}{scheduled_label}"):
                edited_content = st.text_area(
                    "内容",
                    value=draft["content"],
                    height=200,
                    key=f"content_{draft['id']}",
                )
                edited_title = st.text_input(
                    "タイトル",
                    value=draft["title"],
                    key=f"title_{draft['id']}",
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("更新保存", key=f"update_{draft['id']}"):
                        update_draft(draft["id"], edited_title, edited_content)
                        st.success("更新しました！")
                        st.rerun()
                with col2:
                    st.download_button(
                        "ダウンロード",
                        data=draft["content"],
                        file_name=f"{draft['title']}.txt",
                        mime="text/plain",
                        key=f"dl_{draft['id']}",
                    )
                with col3:
                    if st.button("削除", key=f"delete_{draft['id']}", type="secondary"):
                        delete_draft(draft["id"])
                        st.success("削除しました。")
                        st.rerun()

with tab2:
    st.subheader("新しい文章を保存する")

    new_title = st.text_input("タイトル", placeholder="文章のタイトルを入力してください")
    new_category = st.selectbox(
        "カテゴリ",
        ["ブログ記事", "メール返信", "SNS投稿", "その他"],
    )
    new_content = st.text_area("本文", placeholder="ここに文章を入力してください...", height=300)

    st.markdown("**予約日時（任意）**")
    col1, col2 = st.columns(2)
    with col1:
        use_schedule = st.checkbox("予約日時を設定する")
    if use_schedule:
        with col1:
            sched_date = st.date_input("予約日", value=date.today())
        with col2:
            sched_time = st.time_input("予約時刻", value=time(9, 0))
        scheduled_at = datetime.combine(sched_date, sched_time).strftime("%Y/%m/%d %H:%M")
    else:
        scheduled_at = None

    if st.button("保存する", type="primary", use_container_width=True):
        if not new_title:
            st.warning("タイトルを入力してください。")
        elif not new_content:
            st.warning("本文を入力してください。")
        else:
            save_draft(new_title, new_content, new_category, scheduled_at)
            msg = f"保存しました！" + (f"（予約: {scheduled_at}）" if scheduled_at else "")
            st.success(msg)
            st.balloons()
