import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()

def generate_report(findings):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    report = {
        "findings": findings,
    }

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=10000,
            messages=[{
                "role": "user",
                "content": f"Generate a report based on the following findings: {json.dumps(report['findings'])}"
            }]
        )
        return response.content[0].text
    
    except Exception as e:
        print(f"Error occurred while generating report: {e}")
        return None