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
    with open("build.log", "r", errors="ignore") as f:
        lines = f.readlines()

    error_lines = [
        line.strip()
        for line in lines
        if "[ERROR]" in line
    ]

    if error_lines:
        build_log = "\n".join(error_lines)
    else:
        build_log = "".join(lines[-100:])

except Exception as e:
    print(f"Unable to read build.log: {e}")
    exit(1)

prompt = f"""
Analyze this Maven build failure.

Provide:

1. Root Cause
2. File causing issue
3. Exact Fix
4. Corrected Code Snippet (if applicable)

Build Errors:

{build_log}
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
        print("BUILD FAILURE ANALYSIS")
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
