"""
Email delivery module for TwistedNews.
Sends email notifications with generated commentary.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List
from pathlib import Path

import config
from models import CommentaryResult

logger = logging.getLogger(__name__)


def send_email_notification(results: List[CommentaryResult]) -> bool:
    """
    Send email notification with commentary results.
    
    Args:
        results: List of CommentaryResult objects
        
    Returns:
        True if email sent successfully, False otherwise
    """
    # Validate email configuration
    if not all([config.EMAIL_USERNAME, config.EMAIL_PASSWORD, config.EMAIL_RECIPIENT]):
        logger.error("Email configuration incomplete. Check environment variables.")
        return False
    
    try:
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = config.EMAIL_USERNAME
        msg['To'] = config.EMAIL_RECIPIENT
        msg['Subject'] = f"News Article Commentary - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Generate email body
        html_body = _generate_html_body(results)
        text_body = _generate_text_body(results)
        
        # Attach both plain text and HTML versions
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email via SMTP
        logger.info(f"Sending email to {config.EMAIL_RECIPIENT}")
        
        server = smtplib.SMTP(config.EMAIL_SMTP_HOST, int(config.EMAIL_SMTP_PORT))
        server.starttls()
        server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully with {len(results)} commentaries")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        return False


def _generate_text_body(results: List[CommentaryResult]) -> str:
    """Generate plain text email body."""
    
    lines = []
    lines.append("TwistedNews - News Article Commentary")
    lines.append("=" * 50)
    lines.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
    lines.append("")
    lines.append(f"Total Commentaries Generated: {len(results)}")
    lines.append("")
    
    for i, result in enumerate(results, 1):
        lines.append(f"{i}. {result.language.upper()} ({result.language_code})")
        lines.append(f"   Articles Processed: {result.article_count}")
        lines.append(f"   Mode: {result.mode} | Tone: {result.tone} | Gain: {result.gain}")
        lines.append("")
        lines.append("   COMMENTARY:")
        lines.append("   " + "-" * 70)
        # Add commentary with indentation
        for line in result.commentary.split('\n'):
            lines.append(f"   {line}")
        lines.append("   " + "-" * 70)
        lines.append(f"   Output File: {result.output_file}")
        lines.append("")
    
    lines.append("-" * 50)
    lines.append("Powered by TwistedPair API")
    lines.append("MRA News Analysis System")
    
    return "\n".join(lines)


def _generate_html_body(results: List[CommentaryResult]) -> str:
    """Generate HTML email body."""
    
    html = """
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                background-color: #f5f5f5;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 8px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0 0 10px 0;
                font-size: 2.2em;
                font-weight: 300;
            }}
            .header p {{
                margin: 0;
                font-size: 1.1em;
                opacity: 0.95;
            }}
            .summary {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 25px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .summary h2 {{
                margin: 0 0 15px 0;
                color: #667eea;
                font-size: 1.4em;
            }}
            .stat {{
                display: inline-block;
                background: #f0f4ff;
                padding: 10px 20px;
                border-radius: 5px;
                margin: 5px;
                font-weight: 500;
            }}
            .commentary-item {{
                background: white;
                padding: 25px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .commentary-title {{
                color: #667eea;
                font-size: 1.5em;
                font-weight: bold;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
            }}
            .language-badge {{
                background: #667eea;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.7em;
                margin-left: 10px;
                font-weight: normal;
            }}
            .meta {{
                color: #666;
                font-size: 0.95em;
                margin: 10px 0;
                line-height: 1.8;
            }}
            .meta-item {{
                margin: 5px 0;
            }}
            .meta-label {{
                font-weight: 600;
                color: #444;
                display: inline-block;
                min-width: 150px;
            }}
            .file-path {{
                background: #f8f9fa;
                padding: 8px 12px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 0.85em;
                color: #6c757d;
                margin-top: 15px;
                word-break: break-all;
                border-top: 1px solid #dee2e6;
                padding-top: 10px;
            }}
            .commentary-content {{
                background: #fafbfc;
                padding: 20px;
                border-radius: 6px;
                border: 1px solid #e1e4e8;
                margin-top: 15px;
                font-size: 0.95em;
                line-height: 1.8;
                color: #24292e;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            .commentary-content h1,
            .commentary-content h2,
            .commentary-content h3 {{
                color: #667eea;
                margin-top: 20px;
                margin-bottom: 10px;
            }}
            .commentary-content p {{
                margin: 10px 0;
            }}
            .footer {{
                margin-top: 40px;
                padding: 25px;
                background: #2c3e50;
                color: white;
                border-radius: 8px;
                text-align: center;
            }}
            .footer p {{
                margin: 8px 0;
            }}
            .footer strong {{
                color: #667eea;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📰 News Article Commentary</h1>
            <p>{}
        </div>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="stat">🌍 Languages: {}</div>
            <div class="stat">📝 Total Articles: {}</div>
            <div class="stat">💬 Commentaries: {}</div>
        </div>
    """.format(
        datetime.now().strftime('%B %d, %Y'),
        len(results),
        sum(r.article_count for r in results),
        len(results)
    )
    
    # Add each commentary
    for i, result in enumerate(results, 1):
        html += f"""
        <div class="commentary-item">
            <div class="commentary-title">
                {result.language.title()}
                <span class="language-badge">{result.language_code}</span>
            </div>
            <div class="meta">
                <div class="meta-item">
                    <span class="meta-label">📄 Articles Processed:</span> {result.article_count}
                </div>
                <div class="meta-item">
                    <span class="meta-label">🎛️ TwistedPair Mode:</span> {result.mode}
                </div>
                <div class="meta-item">
                    <span class="meta-label">🎵 Tone:</span> {result.tone}
                </div>
                <div class="meta-item">
                    <span class="meta-label">🔊 Gain:</span> {result.gain}/10
                </div>
                <div class="meta-item">
                    <span class="meta-label">⏰ Generated:</span> {datetime.fromisoformat(result.timestamp).strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            </div>
            <div class="commentary-content">
                {result.commentary}
            </div>
            <div class="file-path">
                💾 Output file: {result.output_file}
            </div>
        </div>
        """
    
    html += """
        <div class="footer">
            <p><strong>TwistedNews</strong></p>
            <p>Automated news commentary powered by TwistedPair API</p>
            <p>Part of the MRA News Analysis System</p>
        </div>
    </body>
    </html>
    """
    
    return html
