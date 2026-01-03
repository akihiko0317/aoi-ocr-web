"""決算書OCR ウェブ版 - メインアプリケーション"""

import streamlit as st
from src.ocr_engine import AzureOCREngine, OCRResult

# ページ設定
st.set_page_config(
    page_title="決算書OCR",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


def validate_pdf(file_bytes: bytes) -> tuple[bool, str]:
    """PDFファイルのバリデーション"""
    if not file_bytes.startswith(b"%PDF"):
        return False, "有効なPDFファイルではありません"
    max_size = 50 * 1024 * 1024  # 50MB
    if len(file_bytes) > max_size:
        return False, "ファイルサイズが大きすぎます（上限: 50MB）"
    return True, ""


def main():
    # セッション状態の初期化
    if "ocr_result" not in st.session_state:
        st.session_state.ocr_result = None
    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = None

    # サイドバー: API設定
    with st.sidebar:
        st.header("Azure API設定")

        endpoint = st.text_input(
            "エンドポイントURL",
            placeholder="https://your-resource.cognitiveservices.azure.com/",
            help="Azure PortalのDocument Intelligenceリソースから取得"
        )

        api_key = st.text_input(
            "APIキー",
            type="password",
            placeholder="キーを入力",
            help="Azure Portalの「キーとエンドポイント」から取得"
        )

        # 接続テスト
        col1, col2 = st.columns([1, 1])
        with col1:
            test_clicked = st.button(
                "接続テスト",
                disabled=not (endpoint and api_key),
                use_container_width=True
            )

        if test_clicked:
            with st.spinner("テスト中..."):
                engine = AzureOCREngine(endpoint, api_key)
                success, message = engine.test_connection()
                if success:
                    st.success(message)
                else:
                    st.error(message)

        st.divider()

        with st.expander("使い方"):
            st.markdown("""
            1. **Azure Portalで準備**
               - Document Intelligenceリソースを作成
               - 「キーとエンドポイント」からコピー

            2. **API設定を入力**
               - エンドポイントURL
               - APIキー

            3. **PDFをアップロード**
               - 画像ベースのPDFに対応
               - 最大50MBまで

            4. **OCR実行**
               - 処理完了後、テキストをダウンロード
            """)

    # メインエリア
    st.title("決算書OCR ウェブ版")
    st.caption("PDFファイルをテキストに変換します")

    # ファイルアップロード
    uploaded_file = st.file_uploader(
        "PDFファイルをアップロード",
        type=["pdf"],
        accept_multiple_files=False
    )

    if uploaded_file:
        st.info(f"📄 {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

        # 新しいファイルがアップロードされたら結果をリセット
        if st.session_state.uploaded_filename != uploaded_file.name:
            st.session_state.ocr_result = None
            st.session_state.uploaded_filename = uploaded_file.name

    # OCR実行可能条件
    can_execute = all([
        endpoint,
        api_key,
        uploaded_file is not None
    ])

    # 注意メッセージ
    if not endpoint or not api_key:
        st.warning("サイドバーでAzure APIの設定を入力してください")

    # OCR実行ボタン
    if st.button(
        "OCR実行",
        type="primary",
        disabled=not can_execute,
        use_container_width=True
    ):
        execute_ocr(endpoint, api_key, uploaded_file)

    # 結果表示
    if st.session_state.ocr_result:
        display_result()


def execute_ocr(endpoint: str, api_key: str, uploaded_file):
    """OCR処理を実行"""
    with st.spinner("OCR処理中... Azure APIに送信しています"):
        try:
            file_bytes = uploaded_file.read()

            # PDFバリデーション
            is_valid, error_msg = validate_pdf(file_bytes)
            if not is_valid:
                st.error(error_msg)
                return

            engine = AzureOCREngine(endpoint, api_key)
            result = engine.analyze_document_bytes(file_bytes)
            st.session_state.ocr_result = result
            st.success(f"OCR処理が完了しました（{result.page_count}ページ）")
            st.rerun()

        except ValueError as e:
            st.error(f"エラー: {e}")
        except ConnectionError as e:
            st.error(f"接続エラー: {e}")
        except RuntimeError as e:
            st.error(f"処理エラー: {e}")
        except Exception as e:
            st.error(f"予期しないエラー: {e}")


def display_result():
    """OCR結果を表示"""
    result: OCRResult = st.session_state.ocr_result

    st.subheader("抽出結果")

    # 統計情報
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ページ数", result.page_count)
    with col2:
        st.metric("文字数", f"{len(result.full_text):,}")
    with col3:
        st.metric("行数", len(result.full_text.splitlines()))

    # テキストプレビュー
    st.text_area(
        "抽出テキスト（プレビュー）",
        value=result.full_text,
        height=300,
        disabled=True
    )

    # ダウンロードボタン
    original_name = st.session_state.uploaded_filename or "output"
    if original_name.lower().endswith(".pdf"):
        original_name = original_name[:-4]
    output_filename = f"{original_name}_ocr.txt"

    st.download_button(
        label="テキストファイルをダウンロード",
        data=result.full_text.encode("utf-8"),
        file_name=output_filename,
        mime="text/plain",
        type="primary",
        use_container_width=True
    )


if __name__ == "__main__":
    main()
