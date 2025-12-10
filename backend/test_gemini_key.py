
from __future__ import annotations
import os
import logging
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini

# ---------------------------------------------------------------------------
# Setup Logging to avoid Agno errors
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env
load_dotenv()

def test_key():
    print("---------------------------------------------------------------------------")
    print("🔍 Gemini API Key Verification Script (v2)")
    print("---------------------------------------------------------------------------")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = os.getenv("google_api_key") or os.getenv("YOUR_GOOGLE_API_KEY")

    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
        return

    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
    print(f"🔑 Found key: {masked_key}")

    print("\nAttempting to connect to Gemini (gemini-2.0-flash-001) via Agent...")
    
    try:
        # Create a minimal agent
        agent = Agent(
            model=Gemini(id="gemini-2.0-flash-001", api_key=api_key),
            description="You are a connection tester.",
        )
        
        # Run a simple query
        response = agent.run("Hello! Reply with 'OK' if connected.")
        
        print("\n✅ SUCCESS! The API key is valid and working.")
        print(f"🤖 Response: {response.content}")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        if "403" in str(e):
            print("   -> Permission Denied. Key invalid or model access restricted.")

if __name__ == "__main__":
    test_key()
