# document_extraction/content_understanding.py

import logging
import time
from typing import Any, cast
import requests
import os
from dotenv import load_dotenv

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
AZURE_SUBSCRIPTION_KEY = os.getenv("AZURE_SUBSCRIPTION_KEY")
ANALYZER_ID = os.getenv("ANALYZER_ID")


class AzureContentUnderstandingClient:
    def __init__(self) -> None:
        if not AZURE_ENDPOINT:
            raise ValueError("AZURE_ENDPOINT is missing in .env")
        if not AZURE_API_VERSION:
            raise ValueError("AZURE_API_VERSION is missing in .env")
        if not AZURE_SUBSCRIPTION_KEY:
            raise ValueError("AZURE_SUBSCRIPTION_KEY is missing in .env")
        if not ANALYZER_ID:
            raise ValueError("ANALYZER_ID is missing in .env")

        self._endpoint = AZURE_ENDPOINT.rstrip("/")
        self._api_version = AZURE_API_VERSION
        self._headers = {
            "Ocp-Apim-Subscription-Key": AZURE_SUBSCRIPTION_KEY,
            "x-ms-useragent": "cu-fastapi-client",
        }

        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    def _get_analyze_url(self) -> str:
        return (
            f"{self._endpoint}"
            f"/contentunderstanding/analyzers/{ANALYZER_ID}:analyze"
            f"?api-version={self._api_version}"
            f"&stringEncoding=utf16"
        )

    def begin_analyze(self, file_bytes: bytes, filename: str) -> requests.Response:
        headers = {"Content-Type": "application/octet-stream"}
        headers.update(self._headers)

        response = requests.post(
            url=self._get_analyze_url(),
            headers=headers,
            data=file_bytes,
        )

        response.raise_for_status()
        self._logger.info(f"Analyzing file: {filename}")
        return response

    def poll_result(
        self,
        response: requests.Response,
        timeout_seconds: int = 600,
        polling_interval_seconds: int = 2,
    ) -> dict[str, Any]:

        operation_location = response.headers.get("operation-location")
        if not operation_location:
            raise ValueError("Operation location not found in response headers.")

        start_time = time.time()

        while True:
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Analysis operation timed out.")

            result_response = requests.get(
                operation_location,
                headers=self._headers,
            )

            result_response.raise_for_status()
            result = cast(dict[str, Any], result_response.json())

            status = result.get("status", "").lower()

            if status == "succeeded":
                self._logger.info("Analysis completed successfully.")
                return result

            if status == "failed":
                self._logger.error("Analysis failed.")
                raise RuntimeError(result)

            time.sleep(polling_interval_seconds)


def analyze_document(file_bytes: bytes, filename: str):
    client = AzureContentUnderstandingClient()

    response = client.begin_analyze(
        file_bytes=file_bytes,
        filename=filename,
    )

    result = client.poll_result(response)

    return result