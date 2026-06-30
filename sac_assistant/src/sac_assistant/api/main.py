from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from sac_assistant.flow import SacFlow

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    answer: str
    intent: str
    source: str = ""
    token_usage: TokenUsage


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
def chat(request: Request, body: ChatRequest) -> ChatResponse:
    flow = SacFlow()
    flow.kickoff(inputs={"question": body.question})
    return ChatResponse(
        answer=flow.state.answer,
        intent=flow.state.intent,
        source=flow.state.source,
        token_usage=TokenUsage(
            prompt_tokens=flow.state.prompt_tokens,
            completion_tokens=flow.state.completion_tokens,
            total_tokens=flow.state.total_tokens,
        ),
    )
