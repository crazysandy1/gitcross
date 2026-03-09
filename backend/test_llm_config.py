#!/usr/bin/env python3
"""
LLM Configuration Test Script
Tests that all components can communicate correctly with the LLM
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_configuration():
    """Test that configuration is valid"""
    print("\n" + "="*80)
    print("TEST 1: Configuration Validation")
    print("="*80)
    
    try:
        from llm_config import LLMConfig
        LLMConfig.validate()
        print("✅ Configuration is valid")
        
        config_dict = LLMConfig.get_config_dict()
        print("\nCurrent Configuration:")
        for key, value in config_dict.items():
            # Mask sensitive values
            if "KEY" in key or "SECRET" in key:
                value = "***MASKED***" if value else "(not set)"
            print(f"  {key}: {value}")
        return True
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        return False

def test_bedrock_backend():
    """Test Bedrock backend if enabled"""
    print("\n" + "="*80)
    print("TEST 2: Bedrock Backend")
    print("="*80)
    
    from llm_config import LLMConfig
    
    if LLMConfig.LLM_BACKEND != "bedrock":
        print("⏭️  Bedrock not enabled (LLM_BACKEND != 'bedrock'), skipping")
        return None
    
    try:
        print(f"Testing Bedrock with model: {LLMConfig.BEDROCK_MODEL_ID}")
        
        # Try to import boto3
        try:
            import boto3
        except ImportError:
            print("❌ boto3 not installed. Run: pip install boto3")
            return False
        
        # Try to create client
        try:
            bedrock = boto3.client(
                service_name="bedrock-runtime",
                region_name=LLMConfig.BEDROCK_REGION,
            )
            print(f"✅ Bedrock client created for region: {LLMConfig.BEDROCK_REGION}")
        except Exception as e:
            print(f"❌ Failed to create Bedrock client: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Bedrock test failed: {e}")
        return False

def test_llama_backend():
    """Test LLAMA backend if enabled"""
    print("\n" + "="*80)
    print("TEST 3: LLAMA Backend")
    print("="*80)
    
    from llm_config import LLMConfig
    
    if LLMConfig.LLM_BACKEND != "llama":
        print("⏭️  LLAMA not enabled (LLM_BACKEND != 'llama'), skipping")
        return None
    
    try:
        import requests
        
        print(f"Testing LLAMA server at: {LLMConfig.LLAMA_SERVER_URL}")
        
        # Try to ping the server
        try:
            response = requests.get(
                f"{LLMConfig.LLAMA_SERVER_URL.rsplit('/', 1)[0]}/health",
                timeout=5
            )
            if response.status_code == 200:
                print(f"✅ LLAMA server is responding")
                return True
            else:
                print(f"⚠️  LLAMA server responded with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to LLAMA server at {LLMConfig.LLAMA_SERVER_URL}")
            print("   Make sure your LLAMA server is running")
            return False
    except Exception as e:
        print(f"❌ LLAMA test failed: {e}")
        return False

def test_llm_client():
    """Test LLM client initialization"""
    print("\n" + "="*80)
    print("TEST 4: LLM Client Initialization")
    print("="*80)
    
    try:
        from llm_config import get_llm_client, LLMConfig
        
        print(f"Initializing LLM client for backend: {LLMConfig.LLM_BACKEND}")
        client = get_llm_client()
        print(f"✅ LLM client initialized successfully")
        print(f"   Backend: {client.backend}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize LLM client: {e}")
        return False

def test_call_llm():
    """Test actual LLM call"""
    print("\n" + "="*80)
    print("TEST 5: LLM Call Test")
    print("="*80)
    
    try:
        from llm_config import call_llm, LLMConfig
        
        print(f"Sending test message to {LLMConfig.LLM_BACKEND}...")
        
        response = call_llm("Say 'LLM configuration is working correctly' exactly as written.")
        
        if response:
            print(f"✅ LLM Response received:")
            print(f"\n   {response}\n")
            return True
        else:
            print("⚠️  LLM returned empty response")
            return False
    
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_py():
    """Test that app.py can import the config"""
    print("\n" + "="*80)
    print("TEST 6: Flask App (app.py) Integration")
    print("="*80)
    
    try:
        # Check if app.py can import
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "app", 
            "app.py"
        )
        
        if spec is None:
            print("⚠️  app.py not found")
            return None
        
        print("✅ app.py can be imported")
        return True
    except Exception as e:
        print(f"⚠️  Could not test app.py: {e}")
        return None

def test_orchestrator_py():
    """Test that orchestrator.py can import the config"""
    print("\n" + "="*80)
    print("TEST 7: Orchestrator (orchestrator.py) Integration")
    print("="*80)
    
    try:
        # Check if orchestrator.py can import
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "orchestrator", 
            "orchestrator.py"
        )
        
        if spec is None:
            print("⚠️  orchestrator.py not found")
            return None
        
        print("✅ orchestrator.py can be imported")
        return True
    except Exception as e:
        print(f"⚠️  Could not test orchestrator.py: {e}")
        return None

def run_all_tests():
    """Run all tests and report results"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  LLM CONFIGURATION TEST SUITE".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    results = {}
    
    # Run tests
    results["Configuration"] = test_configuration()
    results["Bedrock"] = test_bedrock_backend()
    results["LLAMA"] = test_llama_backend()
    results["Client Init"] = test_llm_client()
    results["LLM Call"] = test_call_llm()
    results["Flask App"] = test_app_py()
    results["Orchestrator"] = test_orchestrator_py()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIP"
        print(f"{test_name:.<40} {status}")
    
    print("="*80)
    print(f"Total: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        print("\n❌ Some tests failed. Please check the output above.")
        return False
    else:
        print("\n✅ All tests passed! Your LLM configuration is working correctly.")
        return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
