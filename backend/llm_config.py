"""
=============================================================================
CENTRALIZED LLM CONFIGURATION
=============================================================================
This module manages ALL LLM communication across the entire application.
All services (Flask, FastAPI, Orchestrator) use this single source of truth.

Benefits:
- Easy to switch models by changing ONE environment variable
- Consistent configuration across all services
- Easy to modify LLM parameters globally
- Stable and maintainable code
=============================================================================
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMConfig:
    """
    Centralized LLM Configuration Management
    
    Supports two LLM backends:
    1. AWS Bedrock (Claude, Mistral, Llama, etc.)
    2. Local/Remote LLAMA Server (via HTTP)
    """
    
    # =========================================================================
    # LLM BACKEND TYPE
    # =========================================================================
    # Options: "bedrock" or "llama"
    LLM_BACKEND = os.getenv("LLM_BACKEND", "bedrock")
    
    # =========================================================================
    # BEDROCK CONFIGURATION (AWS)
    # =========================================================================
    BEDROCK_REGION = os.getenv("AWS_REGION", "ap-south-1")
    BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-haiku-4-5-20251001-v1:0")
    
    # Bedrock model parameters
    BEDROCK_MAX_TOKENS = int(os.getenv("BEDROCK_MAX_TOKENS", "512"))
    BEDROCK_TEMPERATURE = float(os.getenv("BEDROCK_TEMPERATURE", "0.2"))
    
    # AWS Credentials (optional - can use IAM role)
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
    
    # =========================================================================
    # LLAMA SERVER CONFIGURATION (Local/Remote HTTP)
    # =========================================================================
    LLAMA_SERVER_URL = os.getenv("LLAMA_SERVER_URL", "http://localhost:8000/chat")
    LLAMA_MODEL_NAME = os.getenv("LLAMA_MODEL_NAME", "qwen")
    
    # LLAMA model parameters
    LLAMA_MAX_TOKENS = int(os.getenv("LLAMA_MAX_TOKENS", "512"))
    LLAMA_TEMPERATURE = float(os.getenv("LLAMA_TEMPERATURE", "0.2"))
    
    # =========================================================================
    # SHARED PARAMETERS
    # =========================================================================
    # System prompt used across all services
    SYSTEM_PROMPT = os.getenv(
        "SYSTEM_PROMPT",
        """You are a helpful AI assistant. Provide accurate, clear, and concise responses."""
    )
    
    # Timeout for API calls (in seconds)
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Retry configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))  # seconds
    
    @classmethod
    def validate(cls):
        """Validate that the LLM configuration is correct"""
        if cls.LLM_BACKEND not in ["bedrock", "llama"]:
            raise ValueError(
                f"Invalid LLM_BACKEND: {cls.LLM_BACKEND}. "
                "Must be 'bedrock' or 'llama'."
            )
        
        if cls.LLM_BACKEND == "bedrock":
            if not cls.BEDROCK_MODEL_ID:
                raise ValueError(
                    "BEDROCK_MODEL_ID is required when LLM_BACKEND='bedrock'"
                )
        
        if cls.LLM_BACKEND == "llama":
            if not cls.LLAMA_SERVER_URL:
                raise ValueError(
                    "LLAMA_SERVER_URL is required when LLM_BACKEND='llama'"
                )
    
    @classmethod
    def get_config_dict(cls):
        """Get all configuration as a dictionary (useful for logging/debugging)"""
        return {
            "LLM_BACKEND": cls.LLM_BACKEND,
            "BEDROCK_REGION": cls.BEDROCK_REGION,
            "BEDROCK_MODEL_ID": cls.BEDROCK_MODEL_ID,
            "BEDROCK_MAX_TOKENS": cls.BEDROCK_MAX_TOKENS,
            "BEDROCK_TEMPERATURE": cls.BEDROCK_TEMPERATURE,
            "LLAMA_SERVER_URL": cls.LLAMA_SERVER_URL,
            "LLAMA_MODEL_NAME": cls.LLAMA_MODEL_NAME,
            "LLAMA_MAX_TOKENS": cls.LLAMA_MAX_TOKENS,
            "LLAMA_TEMPERATURE": cls.LLAMA_TEMPERATURE,
            "REQUEST_TIMEOUT": cls.REQUEST_TIMEOUT,
            "MAX_RETRIES": cls.MAX_RETRIES,
        }


class LLMClient:
    """
    Unified LLM Client
    Handles communication with either Bedrock or LLAMA server based on config
    """
    
    def __init__(self):
        """Initialize the LLM client based on configured backend"""
        LLMConfig.validate()
        self.backend = LLMConfig.LLM_BACKEND
        
        if self.backend == "bedrock":
            self._init_bedrock()
        elif self.backend == "llama":
            self._init_llama()
    
    def _init_bedrock(self):
        """Initialize Bedrock client"""
        import boto3
        
        print(f"[LLM Config] Initializing Bedrock client...")
        print(f"[LLM Config] Region: {LLMConfig.BEDROCK_REGION}")
        print(f"[LLM Config] Model: {LLMConfig.BEDROCK_MODEL_ID}")
        print(f"[LLM Config] AWS Key provided: {bool(LLMConfig.AWS_ACCESS_KEY_ID)}")
        print(f"[LLM Config] AWS Secret provided: {bool(LLMConfig.AWS_SECRET_ACCESS_KEY)}")
        
        session_kwargs = {
            "region_name": LLMConfig.BEDROCK_REGION,
        }
        
        # IMPORTANT: Explicitly add credentials if provided
        # This ensures boto3 uses the credentials from environment variables
        if LLMConfig.AWS_ACCESS_KEY_ID:
            session_kwargs["aws_access_key_id"] = LLMConfig.AWS_ACCESS_KEY_ID
            print(f"[LLM Config] Using AWS_ACCESS_KEY_ID from .env")
        
        if LLMConfig.AWS_SECRET_ACCESS_KEY:
            session_kwargs["aws_secret_access_key"] = LLMConfig.AWS_SECRET_ACCESS_KEY
            print(f"[LLM Config] Using AWS_SECRET_ACCESS_KEY from .env")
        
        # If no explicit credentials, boto3 will try: IAM role, ~/.aws/credentials, environment variables
        if not (LLMConfig.AWS_ACCESS_KEY_ID and LLMConfig.AWS_SECRET_ACCESS_KEY):
            print(f"[LLM Config] No explicit credentials in .env, using boto3 credential chain...")
        
        try:
            self.client = boto3.client(
                service_name="bedrock-runtime",
                **session_kwargs
            )
            print(f"[LLM Config] ✅ Bedrock client initialized successfully")
        except Exception as e:
            print(f"[LLM Config] ❌ Failed to initialize Bedrock client: {e}")
            raise
    
    def _init_llama(self):
        """Initialize LLAMA client (HTTP-based)"""
        import requests
        self.session = requests.Session()
    
    def call(self, user_prompt: str, system_prompt: str = None) -> str:
        """
        Call the LLM with a user prompt and optional system prompt
        
        Args:
            user_prompt: The user's message
            system_prompt: Optional system prompt (uses default if not provided)
        
        Returns:
            The LLM's response text
        """
        if system_prompt is None:
            system_prompt = LLMConfig.SYSTEM_PROMPT
        
        if self.backend == "bedrock":
            return self._call_bedrock(user_prompt, system_prompt)
        elif self.backend == "llama":
            return self._call_llama(user_prompt, system_prompt)
    
    def _call_bedrock(self, user_prompt: str, system_prompt: str) -> str:
        """Call AWS Bedrock"""
        import json
        
        print(f"[LLM Call] Calling Bedrock model: {LLMConfig.BEDROCK_MODEL_ID}")
        
        # Different model families have different prompt formats
        model_id = LLMConfig.BEDROCK_MODEL_ID
        
        try:
            if "claude" in model_id.lower():
                # Claude format
                print(f"[LLM Call] Using Claude format")
                body = {
                    "messages": [
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": LLMConfig.BEDROCK_MAX_TOKENS,
                    "system": system_prompt,
                    "temperature": LLMConfig.BEDROCK_TEMPERATURE,
                }
                response = self.client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body),
                    contentType="application/json",
                )
                result = json.loads(response["body"].read())
                return result.get("content", [{}])[0].get("text", "")
            
            elif "mistral" in model_id.lower():
                # Mistral format
                print(f"[LLM Call] Using Mistral format")
                body = {
                    "prompt": user_prompt,
                    "max_tokens": LLMConfig.BEDROCK_MAX_TOKENS,
                    "temperature": LLMConfig.BEDROCK_TEMPERATURE,
                }
                response = self.client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body),
                    contentType="application/json",
                )
                result = json.loads(response["body"].read())
                return result.get("outputs", [{}])[0].get("text", "")
            
            elif "llama" in model_id.lower():
                # Llama format
                print(f"[LLM Call] Using Llama format")
                body = {
                    "prompt": user_prompt,
                    "max_gen_len": LLMConfig.BEDROCK_MAX_TOKENS,
                    "temperature": LLMConfig.BEDROCK_TEMPERATURE,
                }
                response = self.client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body),
                    contentType="application/json",
                )
                result = json.loads(response["body"].read())
                return result.get("generation", "")
            
            else:
                raise ValueError(f"Unsupported Bedrock model: {model_id}")
        
        except Exception as e:
            print(f"[LLM Call] ❌ Error calling Bedrock: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _call_llama(self, user_prompt: str, system_prompt: str) -> str:
        """Call remote LLAMA server"""
        import requests
        
        payload = {
            "model": LLMConfig.LLAMA_MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": LLMConfig.LLAMA_TEMPERATURE,
            "max_tokens": LLMConfig.LLAMA_MAX_TOKENS,
        }
        
        try:
            response = self.session.post(
                LLMConfig.LLAMA_SERVER_URL,
                json=payload,
                timeout=LLMConfig.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to call LLAMA server: {e}")


# Global LLM client instance
_llm_client = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def call_llm(user_prompt: str, system_prompt: str = None) -> str:
    """
    Convenience function to call the LLM
    
    Usage:
        from llm_config import call_llm
        response = call_llm("What is the capital of France?")
    """
    client = get_llm_client()
    return client.call(user_prompt, system_prompt)


if __name__ == "__main__":
    # Test the configuration
    print("=" * 80)
    print("LLM CONFIGURATION")
    print("=" * 80)
    config = LLMConfig.get_config_dict()
    for key, value in config.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 80)
    print("Testing LLM Client...")
    print("=" * 80)
    try:
        client = get_llm_client()
        response = call_llm("Say 'LLM Configuration is working correctly'")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
