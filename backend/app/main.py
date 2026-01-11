import json
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.config import get_settings
from app.api.routes import chat, products, health
from app.models.database import init_db

# Configure root logging to capture all module logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

# Set specific loggers to INFO level to ensure our logs show
for logger_name in ["app", "app.api", "app.core", "app.services"]:
    logging.getLogger(logger_name).setLevel(logging.INFO)

logger = logging.getLogger("app")


class ResponseLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # call the actual route handler
        response = await call_next(request)

        # try to capture the response body (works for normal JSON responses;
        # for streaming responses we rebuild the Response)
        body_text = "<unavailable>"
        try:
            if hasattr(response, "body_iterator"):
                body = b""
                async for chunk in response.body_iterator:
                    # append chunks instead of overwriting
                    if isinstance(chunk, (bytes, bytearray)):
                        body += chunk
                    else:
                        body += str(chunk).encode("utf-8")
                # rebuild response so body is preserved for client
                resp = Response(content=body, status_code=response.status_code,
                                headers=dict(response.headers), media_type=response.media_type)
                response = resp
                body_text = body.decode("utf-8", errors="replace")
            else:
                # many Response objects expose .body or can be awaited
                if hasattr(response, "body"):
                    body = response.body
                    if isinstance(body, (bytes, bytearray)):
                        body_text = body.decode("utf-8", errors="replace")
                    else:
                        body_text = str(body)
                else:
                    # fallback: try to await .body()
                    body_bytes = await response.body()
                    body_text = body_bytes.decode("utf-8", errors="replace")
        except Exception:
            body_text = "<error reading body>"

        # truncate long bodies
        if len(body_text) > 2000:
            body_text = body_text[:2000] + "...(truncated)"

        # try to extract a 'source' field from JSON if present
        source_tag = ""
        try:
            j = json.loads(body_text)
            if isinstance(j, dict) and "source" in j:
                source_tag = f" source={j['source']}"
        except Exception:
            pass

        logger.info(f"{request.method} {request.url.path} -> status={response.status_code}{source_tag} body={body_text}")

        return response
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    await init_db()
    print("✓ Database initialized")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
     title="Mobile Phone Shopping Assistant",
     description="AI-powered conversational agent for phone shopping",
     version="1.0.0",
     lifespan=lifespan
 )

app.add_middleware(ResponseLoggerMiddleware)
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Mobile Phone Shopping Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
