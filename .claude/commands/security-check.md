# Security Check — Python AI Writing Assistant

このコマンドはアプリケーション全体のセキュリティを体系的にチェックします。

## 実行手順

以下の順番でセキュリティチェックを行い、各カテゴリについて **[OK] / [WARNING] / [CRITICAL]** で評価してください。

---

### 1. APIキー・シークレット管理

- `.env` ファイルが `.gitignore` に含まれているか確認する (`cat .gitignore`)
- `.env` ファイルがコミット履歴に存在しないか確認する (`git log --all --full-history -- .env`)
- `gemini_client.py` でAPIキーが `os.getenv()` 経由のみで取得され、ハードコードされていないか確認する
- `requirements.txt` や Python ファイル内にシークレットが直書きされていないか Grep で検索する

### 2. プロンプトインジェクション

各ページ (`pages/*.py`) でユーザー入力がプロンプトに埋め込まれる箇所を全て特定する:
- ユーザー入力が**無加工でプロンプト文字列に埋め込まれていないか**確認する
- 悪意あるユーザーが「上記の指示を無視して…」のような文字列を入力した場合の影響を評価する
- 入力長の上限が設定されているか確認する (`st.text_input` / `st.text_area` の `max_chars` パラメータ)

### 3. パストラバーサル・ファイル操作

`utils/storage.py` のファイル操作を確認する:
- `DRAFTS_FILE` パスが固定されており、ユーザー入力でパスが変わらないか確認する
- `data/drafts.json` への書き込みで `Path` オブジェクトが正しく使われているか確認する
- `DATA_DIR.mkdir(exist_ok=True)` が繰り返し呼ばれることによるレースコンディションリスクを評価する

### 4. JSONデータ・入力検証

`utils/storage.py` のJSONデータ処理を確認する:
- `json.load()` 時に不正なJSONでクラッシュしないか（try/except の有無）
- `draft_id` がユーザー提供の値を使う場面で、SQLインジェクション相当の問題がないか
- `save_draft` / `update_draft` で `title` / `content` の長さ・内容に制限がないか評価する
- `drafts.json` が改ざんされた場合のアプリへの影響を評価する

### 5. 依存パッケージの脆弱性

```bash
pip install pip-audit 2>/dev/null && pip-audit -r requirements.txt
```
または:
```bash
pip list --format=freeze | grep -E "streamlit|google-generativeai|python-dotenv"
```
既知の脆弱性があるバージョンが使われていないか確認する。

### 6. エラーハンドリング・情報漏洩

- `gemini_client.py` の `get_client()` で API キー不正時のエラーメッセージが詳細すぎないか確認する
- Streamlit のデフォルトエラー表示でスタックトレースがユーザーに見えないか確認する
- `load_drafts()` でファイル読み込み失敗時の処理を確認する

### 7. データ保存のセキュリティ

- `data/drafts.json` が平文保存されているリスクを評価する（個人情報・機密文章の保存可能性）
- `data/` ディレクトリへのアクセス制限が適切か確認する
- ダウンロードボタン (`st.download_button`) で提供されるコンテンツが意図したものだけか確認する

### 8. Streamlit固有のリスク

- `st.markdown()` で `unsafe_allow_html=True` が使われていないか全ページ確認する
- AI生成コンテンツが `st.markdown()` でレンダリングされる際のXSSリスクを評価する
- `sys.path.append()` による意図しないモジュール読み込みリスクを確認する

---

## 出力フォーマット

チェック完了後、以下の形式でレポートを出力してください:

```
## セキュリティチェックレポート

### サマリー
- CRITICAL: X 件
- WARNING: Y 件
- OK: Z 件

### 詳細

#### [CRITICAL/WARNING/OK] カテゴリ名
- **問題**: （何が問題か）
- **場所**: （ファイル名:行番号）
- **リスク**: （攻撃シナリオ・影響）
- **修正方法**: （具体的な対処法とコード例）

---
```

CRITICAL は即時対応が必要、WARNING は推奨対応、OK は問題なしです。
