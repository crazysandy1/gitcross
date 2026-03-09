from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import boto3
import json
import os

# -------------------------
# Load Environment Variables
# -------------------------
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

# -------------------------
# FastAPI App
# -------------------------
app = FastAPI(title="Bedrock Mistral API")

# -------------------------
# CORS (adjust in production)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Bedrock Client
# -------------------------
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=AWS_REGION,
)

# -------------------------
# Request Schema
# -------------------------
class ChatRequest(BaseModel):
    message: str

# -------------------------
# Health Check
# -------------------------
@app.get("/health")
def health():
    return {"status": "running"}

# -------------------------
# Chat Endpoint
# -------------------------
@app.post("/chat")
def chat(request: ChatRequest):

    prompt = f"""
    You are a helpful AI assistant.

    Question:
    {request.message}
    """

    body = {
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.3
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())

    return {
        "response": result.get("outputs", [{}])[0].get("text", "")
    }

# -------------------------
# Lambda Handler (Optional)
# -------------------------
from mangum import Mangum
handler = Mangum(app)