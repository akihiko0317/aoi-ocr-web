"""Azure Document Intelligence OCRエンジン（Streamlit版）"""

import base64
from dataclasses import dataclass
from typing import Optional, Tuple

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.core.exceptions import (
    HttpResponseError,
    ServiceRequestError,
    ClientAuthenticationError
)

# Azure モデルID
AZURE_MODEL_ID = "prebuilt-layout"


@dataclass
class OCRResult:
    """OCR結果"""
    full_text: str
    page_count: int


class AzureOCREngine:
    """Azure Document Intelligence APIクライアント"""

    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self._client: Optional[DocumentIntelligenceClient] = None

    def _get_client(self) -> DocumentIntelligenceClient:
        """クライアントの遅延初期化"""
        if self._client is None:
            self._client = DocumentIntelligenceClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.api_key)
            )
        return self._client

    def analyze_document_bytes(self, file_bytes: bytes) -> OCRResult:
        """
        PDFバイトデータを解析してOCR結果を返す

        Args:
            file_bytes: PDFファイルのバイトデータ

        Returns:
            OCRResult: 抽出されたテキストとページ数

        Raises:
            ValueError: APIキーが無効またはファイル形式が不正な場合
            ConnectionError: ネットワークエラーの場合
            RuntimeError: その他のAPIエラーの場合
        """
        client = self._get_client()

        try:
            # Base64エンコードしてbodyパラメータで渡す
            base64_content = base64.b64encode(file_bytes).decode('utf-8')

            poller = client.begin_analyze_document(
                model_id=AZURE_MODEL_ID,
                body={"base64Source": base64_content}
            )

            result: AnalyzeResult = poller.result()

            return OCRResult(
                full_text=result.content if result.content else "",
                page_count=len(result.pages) if result.pages else 1
            )

        except ClientAuthenticationError:
            raise ValueError(
                "Azure APIキーが無効です。エンドポイントとAPIキーを確認してください。"
            )
        except ServiceRequestError:
            raise ConnectionError(
                "Azure APIに接続できません。ネットワーク接続を確認してください。"
            )
        except HttpResponseError as e:
            if e.status_code == 429:
                raise RuntimeError(
                    "APIリクエスト制限に達しました。しばらく待ってから再試行してください。"
                )
            elif e.status_code == 400:
                raise ValueError(
                    "ファイル形式が不正です。有効なPDFファイルをアップロードしてください。"
                )
            else:
                raise RuntimeError(f"Azure APIエラー: {e.message}")

    def test_connection(self) -> Tuple[bool, str]:
        """
        API接続テスト（小さなテストデータで認証確認）

        Returns:
            (成功フラグ, メッセージ)
        """
        try:
            client = self._get_client()

            # 最小限のPDFデータでテスト（1x1の白いPDF）
            # 認証エラーがあればここで検出される
            test_pdf = (
                b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj "
                b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj "
                b"3 0 obj<</Type/Page/MediaBox[0 0 1 1]/Parent 2 0 R>>endobj "
                b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n "
                b"\n0000000058 00000 n \n0000000115 00000 n \n"
                b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
            )

            base64_content = base64.b64encode(test_pdf).decode('utf-8')
            poller = client.begin_analyze_document(
                model_id=AZURE_MODEL_ID,
                body={"base64Source": base64_content}
            )
            poller.result()

            return True, "接続成功"
        except ClientAuthenticationError:
            return False, "認証エラー: APIキーを確認してください"
        except ServiceRequestError:
            return False, "接続エラー: ネットワークを確認してください"
        except HttpResponseError as e:
            if e.status_code == 401 or e.status_code == 403:
                return False, "認証エラー: APIキーを確認してください"
            # その他のエラーでも接続自体は成功している
            return True, "接続成功"
        except Exception as e:
            return False, f"エラー: {str(e)}"
