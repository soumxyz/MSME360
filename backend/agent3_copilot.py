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
    import re
    query = user_message.lower()
    
    # Dynamically extract context from the system prompt if present
    score = "78"
    band = "Low"
    factors_list = []
    
    score_match = re.search(r"Model Score:\s*(\d+)\s*/\s*100\s*\((.*?)\s*Risk\)", system_prompt)
    if score_match:
        score = score_match.group(1)
        band = score_match.group(2)
        
    factors_match = re.search(r"SHAP Factors:\s*(\[.*?\])", system_prompt, re.DOTALL)
    if factors_match:
        try:
            factors_list = json.loads(factors_match.group(1).strip())
        except Exception:
            pass

    if "why" in query or "score" in query or "factor" in query:
        pos_drivers = [f"[{f['label']}] ({f['detail']})" for f in factors_list if f['direction'] == '+']
        neg_drivers = [f"[{f['label']}] ({f['detail']})" for f in factors_list if f['direction'] == '-']
        
        resp = f"The business has a credit score of {score}/100, which corresponds to the {band} Risk category. "
        if pos_drivers:
            resp += f"The key positive factors contributing to this rating are: {', '.join(pos_drivers[:2])}. "
        if neg_drivers:
            resp += f"The primary negative/risk factors identified are: {', '.join(neg_drivers[:2])}."
        return resp
        
    if "loan" in query or "safe" in query:
        # Standard dynamic loan recommendation based on the score
        score_val = int(score)
        max_loan = "₹45L" if score_val >= 75 else ("₹25L" if score_val >= 55 else "₹10L (Requires Collateral)")
        return f"Based on cash flows and a score of {score}/100, a maximum exposure of {max_loan} over 24 months is suggested. Debt serviceability parameters are calculated accordingly."
        
    return f"This is a dynamic mock response for Business. Rating is {score}/100 ({band} Risk). Set GEMINI_API_KEY or OPENROUTER_API_KEY in the environment to connect to a live LLM model."
