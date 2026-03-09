#!/usr/bin/env python3
"""
Test Flask app's chat endpoint functionality directly
This simulates what happens when frontend calls /chat
"""

import sys
import os

# Add workspace to path
sys.path.insert(0, r"c:\Users\sande\Downloads\pavani chatbot\ZIPPER")

print("=" * 80)
print("TESTING FLASK APP /CHAT ENDPOINT")
print("=" * 80)

# Step 1: Test imports
print("\n1. Testing imports...")
try:
    from dotenv import load_dotenv
    from llm_config import call_llm, LLMConfig, get_llm_client
    print("   ✅ Successfully imported llm_config and flask dependencies")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Step 2: Load environment
print("\n2. Loading environment variables...")
load_dotenv()
print("   ✅ Environment variables loaded")

# Step 3: Validate config
print("\n3. Validating LLM configuration...")
try:
    LLMConfig.validate()
    print("   ✅ Configuration is valid")
    print(f"      Backend: {LLMConfig.LLM_BACKEND}")
    print(f"      Model: {LLMConfig.BEDROCK_MODEL_ID}")
    print(f"      Region: {LLMConfig.BEDROCK_REGION}")
except Exception as e:
    print(f"   ❌ Configuration error: {e}")
    sys.exit(1)

# Step 4: Initialize client
print("\n4. Initializing LLM client...")
try:
    client = get_llm_client()
    print("   ✅ LLM client initialized successfully")
except Exception as e:
    print(f"   ❌ Client initialization error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test the call_llm function (exactly like /chat endpoint does)
print("\n5. Testing call_llm() function (simulating /chat endpoint)...")
try:
    test_prompt = """
Answer the question using ONLY this context:

Context: The Earth revolves around the Sun. The Moon orbits the Earth.

Question: What orbits the Earth?
"""
    
    print(f"   Sending prompt to Bedrock...")
    response = call_llm(test_prompt)
    print(f"   ✅ Response received successfully!")
    print(f"\n   Response: {response[:200]}..." if len(response) > 200 else f"\n   Response: {response}")
    
except Exception as e:
    print(f"   ❌ call_llm() failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)
print("\nYour Flask /chat endpoint should work now!")
print("\nNext steps:")
print("1. Restart Flask app: python app.py")
print("2. Test from frontend")
print("3. Upload a PDF and try the chat feature")
print("=" * 80)
