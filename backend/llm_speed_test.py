import requests
import time

URL = "https://poqwul39r6.execute-api.ap-south-1.amazonaws.com/chat"

payload = {
    "model": "qwen",
    "messages": [
        {"role": "user", "content": "Say hello in one sentence."}
    ],
    "max_tokens": 50,
    "temperature": 0.2
}

start = time.time()
r = requests.post(URL, json=payload)
end = time.time()

print("Time taken:", round(end - start, 2), "seconds")
print(r.json()["choices"][0]["message"]["content"])

