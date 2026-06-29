from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sac_assistant.flow import SacFlow

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    intent: str
    source: str = ""


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    flow = SacFlow()
    flow.kickoff(inputs={"question": request.question})
    return ChatResponse(
        answer=flow.state.answer,
        intent=flow.state.intent,
        source=flow.state.source,
    )