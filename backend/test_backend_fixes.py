#!/usr/bin/env python3
"""
Test script to verify backend changes work correctly
Run this AFTER starting the Flask server with: python app.py
"""

import requests
import os
import time
from pathlib import Path

API_BASE = "http://localhost:5000"

def test_backend():
    print("=" * 60)
    print("TESTING BACKEND FIXES")
    print("=" * 60)
    
    # Test 1: Check if /upload requires conversationId
    print("\n[TEST 1] Upload should require conversationId")
    print("-" * 60)
    
    test_pdf = Path("test.pdf")
    if test_pdf.exists():
        with open(test_pdf, "rb") as f:
            files = {"file": f}
            resp = requests.post(f"{API_BASE}/upload", files=files)
            print(f"Response: {resp.json()}")
            if "error" in resp.json() and "Conversation ID" in str(resp.json()):
                print("✓ PASS: Backend correctly requires conversationId")
            else:
                print("✗ FAIL: Backend did not validate conversationId")
    else:
        print("⚠ SKIP: test.pdf not found")
    
    # Test 2: Upload with conversationId
    print("\n[TEST 2] Upload with conversationId should work")
    print("-" * 60)
    
    if test_pdf.exists():
        conv_id = "test-conv-001"
        with open(test_pdf, "rb") as f:
            files = {"file": f}
            data = {"conversationId": conv_id}
            resp = requests.post(f"{API_BASE}/upload", files=files, data=data)
            print(f"Response: {resp.json()}")
            if "chunks" in resp.json():
                print(f"✓ PASS: File uploaded with {resp.json().get('chunks')} chunks")
                print(f"  Stored for conversation: {conv_id}")
            else:
                print("✗ FAIL: Upload did not return chunks info")
    
    # Test 3: Chat without conversationId should fail
    print("\n[TEST 3] Chat should require conversationId")
    print("-" * 60)
    
    resp = requests.post(
        f"{API_BASE}/chat",
        json={"message": "Test question"}
    )
    print(f"Response: {resp.json()}")
    if "error" in resp.json() and "Conversation ID" in str(resp.json()):
        print("✓ PASS: Backend correctly requires conversationId for chat")
    else:
        print("✗ FAIL: Backend did not validate conversationId for chat")
    
    # Test 4: Chat with wrong conversationId
    print("\n[TEST 4] Chat with non-existent conversationId")
    print("-" * 60)
    
    resp = requests.post(
        f"{API_BASE}/chat",
        json={
            "message": "Test question",
            "conversationId": "non-existent-conv"
        }
    )
    print(f"Response: {resp.json()}")
    if "Please upload a file first" in str(resp.json()):
        print("✓ PASS: Backend correctly handles missing conversation")
    
    # Test 5: Chat with correct conversationId (if upload succeeded)
    if test_pdf.exists():
        print("\n[TEST 5] Chat with correct conversationId")
        print("-" * 60)
        
        time.sleep(1)  # Give backend time to process
        resp = requests.post(
            f"{API_BASE}/chat",
            json={
                "message": "What is in the document?",
                "conversationId": "test-conv-001"
            }
        )
        print(f"Response: {resp.json()}")
        if "response" in resp.json():
            response = resp.json()
            print(f"✓ PASS: Got response from correct conversation")
            print(f"  - Response: {response['response'][:100]}...")
            print(f"  - Sources: {response.get('sources', [])}")
            print(f"  - Chunks used: {response.get('chunks_used', 0)}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_backend()
    except requests.ConnectionError:
        print("✗ ERROR: Could not connect to Flask server at http://localhost:5000")
        print("Make sure Flask is running with: python app.py")
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
