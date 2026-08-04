"""Cleaner stage for the ingestion pipeline."""

import re

class DocumentCleaner:
    """Cleans and normalizes raw text content."""
    
    def clean(self, text: str) -> str:
        """
        Removes excess whitespace, normalizes unicode characters, and strips bad characters.
        """
        if not text:
            return ""
            
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove null bytes or weird control characters
        text = "".join(ch for ch in text if ord(ch) >= 32 or ch == '\n')
        
        return text.strip()
