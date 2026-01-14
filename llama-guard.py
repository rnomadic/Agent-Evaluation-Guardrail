import json
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# --- CONFIGURATION ---
# Replace with your actual inference server (vLLM, Ollama, or TGI)
LLAMA_GUARD_URL = "http://localhost:11434/api/chat" 
LLAMA_GUARD_MODEL = "llama-guard3:1b"  # or "llama-guard3:8b"

class LlamaGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Capture the request body
        body = await request.body()
        try:
            payload = json.loads(body) if body else {}
            user_input = payload.get("prompt") or payload.get("content", "")
        except json.JSONDecodeError:
            user_input = ""

        # 2. Pre-Processing: Scan Input for Jailbreaks/Harm
        if user_input:
            is_safe, category = await self.check_safety(user_input, role="user")
            if not is_safe:
                return JSONResponse(
                    status_code=403,
                    content={"error": "Insecure input detected", "policy_violation": category}
                )

        # 3. Process the request through the app logic
        response = await call_next(request)

        # 4. Post-Processing: Scan Output for PII/Toxic Content
        # (Note: This simple example assumes a standard JSON response, not streaming)
        if response.status_code == 200:
            response_body = [section async for section in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body)) # Reconstruct iterator
            
            try:
                out_data = json.loads(response_body[0].decode())
                bot_output = out_data.get("response") or out_data.get("content", "")
                
                if bot_output:
                    is_safe, category = await self.check_safety(bot_output, role="assistant", user_input=user_input)
                    if not is_safe:
                        return JSONResponse(
                            status_code=403,
                            content={"error": "Insecure response generated", "policy_violation": category}
                        )
            except Exception:
                pass # Skip if not JSON or parsing fails

        return response

    async def check_safety(self, text: str, role: str, user_input: str = ""):
        """Calls Llama Guard 3 to classify the content."""
        async with httpx.AsyncClient() as client:
            messages = []
            if role == "assistant" and user_input:
                messages.append({"role": "user", "content": user_input})
            
            messages.append({"role": role, "content": text})

            try:
                res = await client.post(
                    LLAMA_GUARD_URL,
                    json={
                        "model": LLAMA_GUARD_MODEL,
                        "messages": messages,
                        "stream": False
                    },
                    timeout=5.0
                )
                result_text = res.json().get("message", {}).get("content", "").strip()
                
                # Llama Guard returns "safe" or "unsafe\nS<number>"
                if "unsafe" in result_text.lower():
                    # Extract the S-category (e.g., S7 for Privacy/PII)
                    category = result_text.split("\n")[-1] if "\n" in result_text else "Unknown"
                    return False, category
                return True, None
            except Exception as e:
                print(f"Safety Check Failed: {e}")
                return True, None # Fail-safe (allow if checker is down)

# --- APP SETUP ---
app = FastAPI()
app.add_middleware(LlamaGuardMiddleware)

@app.post("/chat")
async def chat_endpoint(request: Request):
    # Your core LLM logic here
    return {"response": "This is a safe response from the AI."}

# Helper to reconstruct response body after reading
from starlette.concurrency import iterate_in_threadpool