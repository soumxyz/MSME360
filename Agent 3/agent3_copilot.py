import os
import json
import urllib.request
import urllib.error

# Keys must come from the environment; never hardcode secrets in source.
# Without keys the copilot falls back to the local mock generator below.
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

def call_llm(system_prompt: str, user_message: str):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    # 1. Try Gemini API first if configured
    if GEMINI_KEY:
        # Re-format chat messages to Gemini's native generateContent schema
        gemini_contents = []
        
        # We concatenate system prompt and user query to fit Gemini's simple structure
        combined_text = f"System Instructions:\n{system_prompt}\n\nUser Query: {user_message}"
        gemini_contents.append({
            "parts": [{"text": combined_text}]
        })
            
        # Send the key as a header, not a query param, so it never lands in server/proxy logs
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_KEY,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        data = {"contents": gemini_contents}
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res["candidates"][0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            print(f"Gemini API returned HTTP error: {e.code}. Response: {e.read().decode('utf-8')}")
        except Exception as e:
            print(f"Gemini API general failure: {e}. Trying OpenRouter next...")

    # 2. Try OpenRouter API next if configured
    if OPENROUTER_KEY:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "MSME Credit Workspace",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        data = {
            "model": "google/gemini-2.5-flash",
            "messages": messages,
            "max_tokens": 400
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"OpenRouter API call failed: {e}. Falling back to mock generator...")

    # 3. Fallback to Local Mock responses if API keys are missing/rate-limited
    query = user_message.lower()
    if "why" in query or "score" in query:
        return "The business has a score of 78/100 (Low Risk). The primary positive driver is regular GST filing (filed on time in 12/12 months), and the primary negative driver is a slight increase in monthly revenue volatility."
    if "loan" in query or "safe" in query:
        return "Based on monthly revenue cash flow, a maximum loan of ₹35L over 24 months is suggested. Ratios indicate comfortable debt serviceability."
    return "This is a grounded mock response. To enable real generative responses, please ensure GEMINI_API_KEY or OPENROUTER_API_KEY is configured in your backend environment."
