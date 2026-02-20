#!/usr/bin/env python3
"""
TwistedNews - News Article Commentary Generator

Processes translated news articles from MRA, groups them by original language,
and generates commentary using TwistedPair API.

Author: AI Assistant
Date: 2026-02-19
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from collections import defaultdict

# Import project modules
import config
from models import NewsArticle, LanguageGroup, CommentaryResult
from language_detector import (
    detect_language_from_filename,
    extract_date_from_filename,
    extract_time_from_filename,
    extract_title_from_filename
)
from twistedpair_client import TwistedPairClient
from email_delivery import send_email_notification
import prompts

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TwistedNewsProcessor:
    """Main processor for TwistedNews application."""
    
    def __init__(self, articles_dir: Path = None, output_dir: Path = None):
        """
        Initialize processor.
        
        Args:
            articles_dir: Directory containing news article markdown files
            output_dir: Directory for output commentary files
        """
        self.articles_dir = articles_dir or config.NEWS_ARTICLES_DIR
        self.output_dir = output_dir or config.OUTPUT_DIR
        self.twistedpair_client = TwistedPairClient()
        
        logger.info(f"TwistedNews Processor initialized")
        logger.info(f"Articles directory: {self.articles_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def read_articles(self, target_date: str = None) -> List[NewsArticle]:
        """
        Read all markdown articles from directory.
        
        Args:
            target_date: Optional YYYYMMDD filter (default: today)
            
        Returns:
            List of NewsArticle objects
        """
        if target_date is None:
            target_date = datetime.now().strftime('%Y%m%d')
        
        logger.info(f"Reading articles for date: {target_date}")
        
        articles = []
        md_files = list(self.articles_dir.glob("*.md"))
        
        logger.info(f"Found {len(md_files)} total markdown files")
        
        for filepath in md_files:
            filename = filepath.name
            
            # Extract date from filename
            file_date = extract_date_from_filename(filename)
            
            # Filter by target date
            if file_date != target_date:
                continue
            
            # Detect language from filename
            language = detect_language_from_filename(filename)
            if language == 'unknown':
                logger.warning(f"Unknown language for file: {filename}")
                continue
            
            # Read file content
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                article = NewsArticle(
                    filepath=str(filepath),
                    filename=filename,
                    date=file_date,
                    time=extract_time_from_filename(filename),
                    title=extract_title_from_filename(filename),
                    language=language,
                    content=content
                )
                
                articles.append(article)
                
            except Exception as e:
                logger.error(f"Error reading file {filepath}: {e}")
                continue
        
        logger.info(f"Successfully read {len(articles)} articles for {target_date}")
        return articles
    
    def group_by_language(self, articles: List[NewsArticle]) -> Dict[str, LanguageGroup]:
        """
        Group articles by their original language.
        
        Args:
            articles: List of NewsArticle objects
            
        Returns:
            Dictionary mapping language to LanguageGroup
        """
        groups = defaultdict(list)
        
        for article in articles:
            groups[article.language].append(article)
        
        language_groups = {}
        for language, article_list in groups.items():
            language_code = config.LANGUAGE_CODES.get(language, language.upper()[:2])
            date = article_list[0].date if article_list else ''
            
            group = LanguageGroup(
                language=language,
                language_code=language_code,
                date=date,
                articles=article_list
            )
            
            language_groups[language] = group
            logger.info(f"Grouped {len(article_list)} articles for language: {language} ({language_code})")
        
        return language_groups
    
    def generate_commentary(self, language_group: LanguageGroup) -> CommentaryResult:
        """
        Generate commentary for a language group using TwistedPair.
        
        Args:
            language_group: LanguageGroup with articles
            
        Returns:
            CommentaryResult with generated commentary
        """
        logger.info(f"Generating commentary for {language_group.language} ({language_group.get_article_count()} articles)")
        
        # Build prompt based on configured style
        prompt_style = config.PROMPT_STYLE.lower()
        
        if prompt_style == "comprehensive":
            prompt_text = prompts.build_commentary_prompt(language_group)
            logger.info(f"Using comprehensive analytical prompt ({len(prompt_text)} chars)")
        elif prompt_style == "simple":
            prompt_text = prompts.build_simple_summary_prompt(language_group)
            logger.info(f"Using simple summary prompt ({len(prompt_text)} chars)")
        elif prompt_style == "raw":
            prompt_text = language_group.get_combined_content()
            logger.info(f"Using raw content without prompt wrapper ({len(prompt_text)} chars)")
        else:
            logger.warning(f"Unknown prompt style '{prompt_style}', using comprehensive")
            prompt_text = prompts.build_commentary_prompt(language_group)
        
        # Generate commentary via TwistedPair
        result = self.twistedpair_client.generate_commentary(prompt_text)
        
        # Create output filename
        output_filename = f"{language_group.date}_{language_group.language_code}.md"
        output_path = self.output_dir / output_filename
        
        # Save commentary to file
        self._save_commentary(output_path, language_group, result)
        
        commentary_result = CommentaryResult(
            language=language_group.language,
            language_code=language_group.language_code,
            date=language_group.date,
            article_count=language_group.get_article_count(),
            commentary=result.output,
            output_file=str(output_path),
            mode=result.mode,
            tone=result.tone,
            gain=result.gain,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Commentary saved to: {output_path}")
        return commentary_result
    
    def _save_commentary(self, output_path: Path, group: LanguageGroup, result):
        """Save commentary to markdown file."""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# News Commentary - {group.language.title()}\n\n")
            f.write(f"**Date:** {group.date}\n\n")
            f.write(f"**Language:** {group.language} ({group.language_code})\n\n")
            f.write(f"**Article Count:** {group.get_article_count()}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**TwistedPair Settings:**\n")
            f.write(f"- Mode: {result.mode}\n")
            f.write(f"- Tone: {result.tone}\n")
            f.write(f"- Gain: {result.gain}\n")
            f.write(f"- Model: {result.model}\n\n")
            f.write("---\n\n")
            
            # Write commentary
            f.write("## Commentary\n\n")
            f.write(result.output)
            f.write("\n\n---\n\n")
            
            # Write article list
            f.write("## Processed Articles\n\n")
            for i, article in enumerate(group.articles, 1):
                f.write(f"{i}. **{article.title}** ({article.time})\n")
            f.write("\n")
    
    def process(self, target_date: str = None, send_email: bool = True) -> List[CommentaryResult]:
        """
        Main processing pipeline.
        
        Args:
            target_date: Target date in YYYYMMDD format (default: today)
            send_email: Whether to send email notification
            
        Returns:
            List of CommentaryResult objects
        """
        logger.info("=" * 60)
        logger.info("TwistedNews Processing Started")
        logger.info("=" * 60)
        
        # Check TwistedPair server
        if not self.twistedpair_client.is_healthy():
            raise ConnectionError("TwistedPair server is not available. Please start it first.")
        
        # Read articles
        articles = self.read_articles(target_date)
        
        if not articles:
            logger.warning("No articles found for processing")
            return []
        
        # Group by language
        language_groups = self.group_by_language(articles)
        
        # Generate commentary for each language
        results = []
        for language, group in language_groups.items():
            try:
                result = self.generate_commentary(group)
                results.append(result)
            except Exception as e:
                logger.error(f"Error generating commentary for {language}: {e}")
                continue
        
        logger.info("=" * 60)
        logger.info(f"Processing Complete: {len(results)} commentaries generated")
        logger.info("=" * 60)
        
        # Send email notification
        if send_email and results:
            try:
                send_email_notification(results)
            except Exception as e:
                logger.error(f"Error sending email: {e}")
        
        return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='TwistedNews - News Commentary Generator')
    parser.add_argument(
        '--date',
        type=str,
        help='Target date in YYYYMMDD format (default: today)',
        default=None
    )
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Skip email notification'
    )
    parser.add_argument(
        '--articles-dir',
        type=str,
        help='Override articles directory path',
        default=None
    )
    
    args = parser.parse_args()
    
    # Override config if specified
    articles_dir = Path(args.articles_dir) if args.articles_dir else None
    
    try:
        processor = TwistedNewsProcessor(articles_dir=articles_dir)
        results = processor.process(
            target_date=args.date,
            send_email=not args.no_email
        )
        
        if results:
            print(f"\n✓ Successfully generated {len(results)} commentaries")
            for result in results:
                print(f"  - {result.language}: {result.output_file}")
        else:
            print("\n⚠ No commentaries generated")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
