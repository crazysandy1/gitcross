#!/usr/bin/env python3
"""
AWS Credentials Diagnostic Script
Helps identify credential and Bedrock access issues
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("AWS CREDENTIALS & BEDROCK DIAGNOSTIC")
print("=" * 80)

# Check 1: Environment variables loaded
print("\n1. CHECKING ENVIRONMENT VARIABLES")
print("-" * 80)

aws_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
bedrock_model = os.getenv("BEDROCK_MODEL_ID")

print(f"AWS_ACCESS_KEY_ID: {'✅ SET' if aws_key else '❌ NOT SET'}")
if aws_key:
    print(f"  First 4 chars: {aws_key[:4]}...")
print(f"AWS_SECRET_ACCESS_KEY: {'✅ SET' if aws_secret else '❌ NOT SET'}")
if aws_secret:
    print(f"  First 4 chars: {aws_secret[:4]}...")
print(f"AWS_REGION: {aws_region if aws_region else '❌ NOT SET'}")
print(f"BEDROCK_MODEL_ID: {bedrock_model if bedrock_model else '❌ NOT SET'}")

# Check 2: boto3 installation
print("\n2. CHECKING BOTO3 INSTALLATION")
print("-" * 80)

try:
    import boto3
    print("✅ boto3 is installed")
    print(f"   Version: {boto3.__version__}")
except ImportError:
    print("❌ boto3 is NOT installed")
    print("   Fix: pip install boto3")
    sys.exit(1)

# Check 3: Try to create Bedrock client
print("\n3. TESTING BEDROCK CLIENT CREATION")
print("-" * 80)

try:
    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name=aws_region if aws_region else "ap-south-1",
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
    )
    print("✅ Bedrock client created successfully")
except Exception as e:
    print(f"❌ Failed to create Bedrock client:")
    print(f"   Error: {str(e)}")

# Check 4: Try to list available models
print("\n4. TESTING BEDROCK MODEL LISTING")
print("-" * 80)

try:
    bedrock_models = boto3.client(
        service_name="bedrock",
        region_name=aws_region if aws_region else "ap-south-1",
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
    )
    
    response = bedrock_models.list_foundation_models()
    models = response.get("modelSummaries", [])
    
    print(f"✅ Successfully listed Bedrock models")
    print(f"   Available models: {len(models)}")
    
    # Check if our model is available
    model_ids = [m["modelId"] for m in models]
    if bedrock_model and bedrock_model in model_ids:
        print(f"   ✅ Your model '{bedrock_model}' is AVAILABLE")
    elif bedrock_model:
        print(f"   ❌ Your model '{bedrock_model}' is NOT available")
        print(f"\n   Available models similar to yours:")
        for mid in model_ids:
            if any(x in mid for x in bedrock_model.split(".")):
                print(f"      - {mid}")
    
except Exception as e:
    print(f"❌ Failed to list models:")
    print(f"   Error: {str(e)}")
    print(f"\n   Possible causes:")
    print(f"   1. Invalid AWS credentials")
    print(f"   2. No Bedrock access in this region")
    print(f"   3. IAM permissions missing")

# Check 5: Try actual model invocation
print("\n5. TESTING MODEL INVOCATION")
print("-" * 80)

if bedrock_model:
    try:
        import json
        
        # Determine model family for correct format
        if "mistral" in bedrock_model.lower():
            body = {
                "prompt": "Say 'Test successful'",
                "max_tokens": 100,
                "temperature": 0.2
            }
        elif "claude" in bedrock_model.lower():
            body = {
                "messages": [{"role": "user", "content": "Say 'Test successful'"}],
                "max_tokens": 100,
                "temperature": 0.2
            }
        else:
            body = {
                "prompt": "Say 'Test successful'",
                "max_tokens": 100,
                "temperature": 0.2
            }
        
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=aws_region if aws_region else "ap-south-1",
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
        )
        
        response = bedrock_runtime.invoke_model(
            modelId=bedrock_model,
            body=json.dumps(body),
            contentType="application/json",
        )
        
        print(f"✅ Model invocation SUCCESSFUL")
        print(f"   Model: {bedrock_model}")
        print(f"   Status Code: {response['ResponseMetadata']['HTTPStatusCode']}")
        
    except Exception as e:
        print(f"❌ Model invocation FAILED:")
        print(f"   Error: {str(e)}")
        print(f"\n   Possible causes:")
        print(f"   1. Invalid credentials")
        print(f"   2. Model not available in region")
        print(f"   3. Insufficient permissions")
        print(f"   4. Invalid model format")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

all_ok = (
    aws_key and 
    aws_secret and 
    aws_region and 
    bedrock_model
)

if all_ok:
    print("\n✅ CONFIGURATION LOOKS GOOD!")
    print("\nNext steps:")
    print("1. Restart your Flask app: python app.py")
    print("2. Test the chat endpoint again")
    print("3. If still failing, check Bedrock IAM permissions")
else:
    print("\n❌ MISSING CONFIGURATION")
    print("\nFix these issues:")
    if not aws_key:
        print("  - Set AWS_ACCESS_KEY_ID in .env")
    if not aws_secret:
        print("  - Set AWS_SECRET_ACCESS_KEY in .env")
    if not aws_region:
        print("  - Set AWS_REGION in .env")
    if not bedrock_model:
        print("  - Set BEDROCK_MODEL_ID in .env")

print("\n" + "=" * 80)
print("For more help, see: LLM_CONFIG_SETUP.md")
print("=" * 80 + "\n")
