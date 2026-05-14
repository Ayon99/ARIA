import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def investigate(anomaly, baseline):
    
    # Step 1 — Triage
    triage_prompt = f"""
You are a security analyst. Analyze this suspicious authentication event and respond in JSON only.
No preamble, no explanation, just raw JSON.

Event: {json.dumps(anomaly, indent=2)}
User baseline: {json.dumps(baseline, indent=2)}

Respond with exactly this structure:
{{
    "severity": "LOW|MEDIUM|HIGH|CRITICAL",
    "confidence": 0.0 to 1.0,
    "attack_pattern": "brief description",
    "is_false_positive": true or false
}}
"""
    triage_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": triage_prompt}],
        temperature=0.1
    )
    
    triage_raw = triage_response.choices[0].message.content.strip()
    
    # clean any markdown backticks if model adds them
    triage_raw = triage_raw.replace("```json", "").replace("```", "").strip()
    triage = json.loads(triage_raw)
    
    # Step 2 — Full incident report
    report_prompt = f"""
You are a senior security analyst writing an incident report.

Suspicious event: {json.dumps(anomaly, indent=2)}
User baseline: {json.dumps(baseline, indent=2)}
Initial triage: {json.dumps(triage, indent=2)}

Write a structured incident report with these exact sections:

SUMMARY
2-3 sentences in plain English a non-technical person can understand.

WHAT HAPPENED
Technical breakdown of the event.

WHY IT IS SUSPICIOUS
Compare against the user baseline.

MITRE ATT&CK
Technique ID and name from the event data.

RECOMMENDED ACTIONS
3 specific immediate actions numbered 1, 2, 3.

Keep it concise and factual. No fluff.
"""
    report_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": report_prompt}],
        temperature=0.2
    )
    
    report_text = report_response.choices[0].message.content.strip()
    
    # Final output
    return {
        "severity": triage["severity"],
        "confidence": triage["confidence"],
        "attack_pattern": triage["attack_pattern"],
        "is_false_positive": triage["is_false_positive"],
        "mitre_technique": anomaly.get("mitre_technique", "Unknown"),
        "report": report_text
    }