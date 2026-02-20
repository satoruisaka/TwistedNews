"""
prompts.py - Prompt templates for TwistedNews commentary generation

This module contains prompt templates that wrap the article content
to guide the LLM in generating useful commentary.
"""

from typing import List
from models import NewsArticle, LanguageGroup


def build_commentary_prompt(language_group: LanguageGroup) -> str:
    """
    Build a comprehensive prompt for generating news commentary.
    
    Args:
        language_group: Group of articles in the same language
        
    Returns:
        Formatted prompt with instructions and article content
    """
    
    # Language-specific context
    language_names = {
        'chinese': 'Chinese',
        'russian': 'Russian',
        'hebrew': 'Hebrew',
        'arabic': 'Arabic',
        'spanish': 'Spanish'
    }
    
    language_name = language_names.get(language_group.language, language_group.language.title())
    article_count = language_group.get_article_count()
    
    # Build the prompt
    prompt = f"""You are an expert news analyst tasked with providing insightful commentary on {language_name} news articles.

TASK: Analyze the following {article_count} news article{"s" if article_count > 1 else ""} and provide a comprehensive commentary that:

1. **Identifies Key Themes**: Extract the main topics and recurring themes across all articles
2. **Highlights Connections**: Show how different articles relate to each other or to broader trends
3. **Provides Context**: Offer historical, political, or cultural context where relevant
4. **Analyzes Implications**: Discuss what these developments might mean for the region or world
5. **Notes Divergent Perspectives**: If articles present different viewpoints, highlight these differences

GUIDELINES:
- Write in clear, analytical prose
- Focus on substance over style
- Synthesize information across articles rather than summarizing each one individually
- Draw connections and identify patterns
- Be objective and balanced
- Length: Aim for 500-800 words total

---

ARTICLES TO ANALYZE:

"""
    
    # Add each article
    for i, article in enumerate(language_group.articles, 1):
        prompt += f"\n### Article {i}: {article.title}\n"
        prompt += f"**Published**: {article.date} {article.time}\n\n"
        prompt += article.content
        prompt += "\n\n---\n\n"
    
    # Add closing instruction
    prompt += """
Now provide your comprehensive analytical commentary based on these articles:
"""
    
    return prompt


def build_simple_summary_prompt(language_group: LanguageGroup) -> str:
    """
    Build a simpler prompt focused on summarization.
    
    Args:
        language_group: Group of articles in the same language
        
    Returns:
        Formatted prompt for summarization
    """
    
    article_count = language_group.get_article_count()
    
    prompt = f"""Summarize the following {article_count} news article{"s" if article_count > 1 else ""}.

For each article, provide:
1. Main topic (1 sentence)
2. Key points (2-3 bullet points)
3. Significance (1 sentence)

Then provide an overall synthesis showing how these articles relate to each other.

---

"""
    
    # Add articles
    for i, article in enumerate(language_group.articles, 1):
        prompt += f"\n## Article {i}: {article.title}\n\n"
        prompt += article.content
        prompt += "\n\n---\n\n"
    
    return prompt


def build_custom_prompt(
    language_group: LanguageGroup,
    instruction: str,
    include_metadata: bool = True
) -> str:
    """
    Build a custom prompt with user-specified instructions.
    
    Args:
        language_group: Group of articles in the same language
        instruction: Custom instruction for the LLM
        include_metadata: Whether to include article metadata
        
    Returns:
        Formatted custom prompt
    """
    
    prompt = f"{instruction}\n\n---\n\n"
    
    for i, article in enumerate(language_group.articles, 1):
        if include_metadata:
            prompt += f"\n### Article {i}: {article.title}\n"
            prompt += f"**Date**: {article.date} | **Time**: {article.time}\n\n"
        else:
            prompt += f"\n### Article {i}\n\n"
        
        prompt += article.content
        prompt += "\n\n---\n\n"
    
    return prompt
