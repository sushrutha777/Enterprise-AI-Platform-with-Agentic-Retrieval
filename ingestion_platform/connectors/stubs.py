"""Connector stubs for future extensibility."""

from typing import List, Any
from ingestion_platform.connectors.base import BaseConnector
from ingestion_platform.core.models import StandardDocument
from app.core.logging import logger

class WebsiteConnector(BaseConnector):
    """Stub for crawling and extracting content from a website."""
    def extract(self, source: str) -> List[StandardDocument]:
        logger.warning(f"WebsiteConnector is a stub. Cannot extract {source}.")
        return []

class SQLConnector(BaseConnector):
    """Stub for running queries and extracting rows from an SQL database."""
    def extract(self, source: Any) -> List[StandardDocument]:
        logger.warning("SQLConnector is a stub.")
        return []

class GoogleDriveConnector(BaseConnector):
    """Stub for fetching documents from Google Drive."""
    def extract(self, source: Any) -> List[StandardDocument]:
        logger.warning("GoogleDriveConnector is a stub.")
        return []

class ConfluenceConnector(BaseConnector):
    """Stub for fetching pages from Confluence."""
    def extract(self, source: Any) -> List[StandardDocument]:
        logger.warning("ConfluenceConnector is a stub.")
        return []

class SharePointConnector(BaseConnector):
    """Stub for fetching files from SharePoint."""
    def extract(self, source: Any) -> List[StandardDocument]:
        logger.warning("SharePointConnector is a stub.")
        return []
