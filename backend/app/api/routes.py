from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List

from app.core.guardrails import CustomsGuardrails
from app.services.agent import CustomsAgentService
from app.services.ingestion import IngestionService

router = APIRouter()
guardrails = CustomsGuardrails()
agent_service = CustomsAgentService()
ingestion_service = IngestionService()

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str = Field(..., description="User's customs query")
    history: List[Message] = Field(default=[], description="Chat history")

class QueryResponse(BaseModel):
    response: str

@router.post("/query", response_model=QueryResponse)
async def process_query(payload: QueryRequest):
    # 1. Input Guardrails
    safety_check = guardrails.validate_input(payload.query)
    if not safety_check["is_safe"]:
        raise HTTPException(status_code=400, detail=safety_check["reason"])
    
    # 2. Format History
    chat_history = []
    for msg in payload.history[-6:]:  # Keep last 6 messages
        if msg.role == "user":
            chat_history.append(("human", msg.content))
        elif msg.role == "assistant":
            chat_history.append(("assistant", msg.content))

    # 3. Execute Agent
    try:
        executor = agent_service.create_executor()
        result = executor.invoke({
            "input": payload.query,
            "chat_history": chat_history
        })
        raw_response = result["output"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

    # 4. Output Guardrails
    out_safety_check = guardrails.validate_output(raw_response)
    if not out_safety_check["is_safe"]:
        raise HTTPException(status_code=500, detail=out_safety_check["reason"])

    return QueryResponse(response=out_safety_check["output"])

@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    result = await ingestion_service.ingest_file(file)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result