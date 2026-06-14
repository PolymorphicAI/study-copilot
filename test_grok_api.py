"""
Study Copilot - Grok API Key Diagnostic Tool
Tests if your Grok API key is working correctly
"""

import os
import requests
import json

def test_grok_api():
    """Test if Grok API is working"""
    
    api_key = os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")
    
    print("\n" + "="*70)
    print("🔍 GROK API DIAGNOSTIC TOOL")
    print("="*70 + "\n")
    
    # Step 1: Check if API key is set
    print("Step 1: Checking if XAI_API_KEY is set...")
    if not api_key:
        print("❌ XAI_API_KEY is NOT set!")
        print("\nTo fix this, run:")
        print("  export XAI_API_KEY='your-actual-grok-key-here'")
        print("\nThen verify it was set:")
        print("  echo $XAI_API_KEY")
        return False
    
    if api_key == "your-key-here" or api_key.startswith("your-"):
        print("⚠️  XAI_API_KEY is set to a placeholder value!")
        print(f"   Current value: {api_key}")
        print("\nYou need a real API key from https://console.x.ai/")
        return False
    
    print(f"✅ XAI_API_KEY is set")
    print(f"   Value: {api_key[:20]}...{api_key[-10:]} (masked)")
    
    # Step 2: Test API connection
    print("\nStep 2: Testing Grok API connection...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Say 'Hello from Grok!' and nothing else."
            }
        ],
        "model": "grok-beta",
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        print("📡 Sending test request to Grok API...")
        # X.AI Grok API endpoint
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API connection successful!")
            data = response.json()
            message = data['choices'][0]['message']['content']
            print(f"   Response: {message}")
            return True
        
        elif response.status_code == 401:
            print("❌ Authentication failed (401)")
            print("   Your API key might be invalid or expired")
            print("   Get a new one at: https://console.x.ai/")
            print(f"\n   Response: {response.text}")
            return False
        
        elif response.status_code == 429:
            print("⚠️  Rate limited (429)")
            print("   You're making too many requests")
            print("   Wait a moment and try again")
            return False
        
        else:
            print(f"❌ API returned error {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ Request timed out (no response for 10 seconds)")
        print("   Check your internet connection or try again later")
        return False
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Grok API")
        print("   Check your internet connection")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_grok_api()
    
    print("\n" + "="*70)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("\nYour Grok API is working correctly.")
        print("You can now run: python backend/main_grok.py")
    else:
        print("❌ TESTS FAILED")
        print("\nFix the issue above, then try again.")
    print("="*70 + "\n")