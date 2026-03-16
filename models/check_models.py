import os
import requests

# Retrieve the API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable not found.")
    print("Please set it using: export GEMINI_API_KEY='your_key_here'")
else:
    print("Querying Google to list available models...")
    try:
        response = requests.get(url)

        if response.status_code == 200:
            models = response.json().get("models", [])
            print("\nAVAILABLE MODELS FOR YOUR KEY:")
            for m in models:
                # Show only models that support content generation
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    print(f"- {m['name'].replace('models/', '')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Connection error: {e}")
