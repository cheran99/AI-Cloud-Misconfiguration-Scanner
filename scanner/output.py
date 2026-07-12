import markdown
import os
from datetime import datetime

def save_report(report_text):
    html_body = markdown.markdown(report_text, extensions=['tables'])
    html_content = f"""
    <html>
        <head>
            <style>
                body {{
                    background-color: #0d1117;
                    color: #e6edf3;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    max-width: 960px;
                    margin: 40px auto;
                    padding: 0 24px;
                    line-height: 1.6;
                }}
                h1 {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #58a6ff;
                    border-bottom: 2px solid #21262d;
                    padding-bottom: 12px;
                }}
                h2 {{
                    color: #f0883e;
                    font-size: 20px;
                    margin-top: 32px;
                }}
                h3 {{
                    color: #7ee787;
                    font-size: 16px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 16px 0;
                    font-size: 14px;
                }}
                th, td {{
                    border: 1px solid #30363d;
                    padding: 10px 14px;
                    text-align: left;
                }}
                th {{
                    background-color: #161b22;
                    color: #58a6ff;
                    font-weight: 600;
                }}
                tr:nth-child(even) {{
                    background-color: #161b22;
                }}
                ul, ol {{
                    padding-left: 24px;
                }}
                li {{
                    margin: 4px 0;
                }}
                code {{
                    background-color: #161b22;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: monospace;
                    color: #f85149;
                }}
                p {{
                    margin: 12px 0;
                }}
            </style>
        <title>Cloud Misconfiguration Report</title>
        </head>
        <body>
            {html_body}
        </body>
    </html>
    """

    os.makedirs("reports", exist_ok=True)
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d_%H-%M")
    with open(f"reports/report_{formatted_date}.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Report saved to reports/report_{formatted_date}.html")