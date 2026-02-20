"""
Language detection from article filenames.
Detects language based on characters in the filename title.
"""

import re
import logging

logger = logging.getLogger(__name__)


def detect_language_from_filename(filename: str) -> str:
    """
    Detect language from filename title.
    
    Filename format: YYYYMMDD_HHMMSS_title_in_original_language.md
    
    Args:
        filename: The markdown filename
        
    Returns:
        Language string: 'chinese', 'russian', 'hebrew', 'arabic', or 'spanish'
    """
    # Extract title part (everything after second underscore, before .md)
    # Pattern: YYYYMMDD_HHMMSS_title.md
    parts = filename.split('_', 2)
    if len(parts) < 3:
        logger.warning(f"Invalid filename format: {filename}")
        return 'unknown'
    
    # Remove .md extension
    title = parts[2].replace('.md', '')
    
    # Detect language by character ranges
    
    # Chinese: CJK Unified Ideographs
    if re.search(r'[\u4e00-\u9fff]', title):
        return 'chinese'
    
    # Russian: Cyrillic
    if re.search(r'[\u0400-\u04ff]', title):
        return 'russian'
    
    # Hebrew
    if re.search(r'[\u0590-\u05ff]', title):
        return 'hebrew'
    
    # Arabic
    if re.search(r'[\u0600-\u06ff]', title):
        return 'arabic'
    
    # Spanish: Latin characters with specific patterns
    # If it has accented characters or Spanish-specific letters
    if re.search(r'[áéíóúüñÁÉÍÓÚÜÑ¿¡]', title):
        return 'spanish'
    
    # Default to Spanish if Latin alphabet (fallback for unaccented Spanish)
    if re.search(r'[a-zA-Z]', title):
        return 'spanish'
    
    logger.warning(f"Could not detect language for: {filename}")
    return 'unknown'


def extract_date_from_filename(filename: str) -> str:
    """
    Extract YYYYMMDD from filename.
    
    Args:
        filename: The markdown filename
        
    Returns:
        Date string in YYYYMMDD format
    """
    parts = filename.split('_')
    if len(parts) >= 1:
        return parts[0]
    return ''


def extract_time_from_filename(filename: str) -> str:
    """
    Extract HHMMSS from filename.
    
    Args:
        filename: The markdown filename
        
    Returns:
        Time string in HHMMSS format
    """
    parts = filename.split('_')
    if len(parts) >= 2:
        return parts[1]
    return ''


def extract_title_from_filename(filename: str) -> str:
    """
    Extract title from filename (in original language).
    
    Args:
        filename: The markdown filename
        
    Returns:
        Title string (URL-encoded characters will be preserved)
    """
    parts = filename.split('_', 2)
    if len(parts) >= 3:
        title = parts[2].replace('.md', '')
        # Replace underscores with spaces for readability
        title = title.replace('_', ' ')
        return title
    return ''
