"""
FastAPI gateway entry point.

This module defines the FastAPI application used as the central gateway for the
fullstack template.  It wires together various routers (e.g. for user
management) and exposes a minimal root endpoint for health checks.  To run the
gateway in development mode, execute:

```bash
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from datetime import datetime

from .users import router as users_router

app = FastAPI(title="Gateway API", description="Gateway service for the fullstack template")

# Configure CORS.  In this template we allow requests from any origin.  Adjust the
# `allow_origins` list to restrict to trusted domains in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers.  Additional routers should be added here.
app.include_router(users_router, prefix="/users", tags=["users"])


class TextData(BaseModel):
    text: str
    timestamp: str
    source: str


@app.get("/")
async def read_root() -> dict[str, str]:
    """Return a simple message confirming that the gateway is alive."""
    return {"message": "Gateway is working"}


@app.post("/process-text")
async def process_text(data: TextData):
    """
    Process text data from frontend and print to console.
    
    This endpoint receives JSON data from the frontend form and prints it
    to the console (allegis) for debugging/logging purposes.
    """
    try:
        # 알기지에 print (console 출력)
        print("=" * 50)
        print("📝 FRONTEND에서 전송된 데이터:")
        print(f"📄 텍스트: {data.text}")
        print(f"⏰ 타임스탬프: {data.timestamp}")
        print(f"🔗 소스: {data.source}")
        print(f"🕐 처리 시간: {datetime.now().isoformat()}")
        print("=" * 50)
        
        # 성공 응답 반환
        return {
            "status": "success",
            "message": "데이터가 성공적으로 처리되었습니다",
            "received_text": data.text,
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"데이터 처리 중 오류가 발생했습니다: {str(e)}")


@app.get("/service/ping")
async def proxy_ping() -> dict:
    """
    Proxy a request to the example microservice.

    This endpoint demonstrates a simple reverse proxy.  When invoked, it
    dispatches an HTTP request to the `service` container's `/ping` endpoint
    using an asynchronous HTTP client and returns the JSON payload verbatim.
    In production you could extend this pattern to perform service discovery,
    authentication or response transformation.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get("http://service:8000/ping")
        response.raise_for_status()
        return response.json()