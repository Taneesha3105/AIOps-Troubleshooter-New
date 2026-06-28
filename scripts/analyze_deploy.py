import os
import time

try:
    import google.generativeai as genai
except ImportError:
    print("google-generativeai package not installed")
    raise

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("GEMINI_API_KEY not found")
    exit(1)

genai.configure(api_key=API_KEY)

try:
    with open("deploy.log", "r", errors="ignore") as f:
        deploy_log = f.read()[-5000:]

except Exception as e:
    print(f"Unable to read deploy.log: {e}")
    exit(1)

prompt = f"""
Analyze this deployment failure.

Provide:

1. Root Cause
2. What failed
3. Suggested Fix
4. Verification Steps

Deploy Log:

{deploy_log}
"""

attempts = 3
backoff = 2

for attempt in range(1, attempts + 1):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(
            prompt,
            request_options={"timeout": 30}
        )

        print("\n" + "=" * 60)
        print("DEPLOY FAILURE ANALYSIS")
        print("=" * 60)
        print(response.text)
        print("=" * 60)

        exit(0)

    except Exception as e:
        msg = str(e)

        print(f"Attempt {attempt} failed: {msg}")

        transient = (
            "high demand" in msg.lower()
            or "resource exhausted" in msg.lower()
            or "timeout" in msg.lower()
            or "timed out" in msg.lower()
            or "504" in msg
        )

        if transient and attempt < attempts:
            time.sleep(backoff)
            backoff *= 2
            continue

        print(msg)
        exit(1)
