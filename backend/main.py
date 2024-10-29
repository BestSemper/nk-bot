# main.py
from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.output_parsers import JsonOutputParser
from agent import ChatAgent

app = FastAPI()
chat_agent = ChatAgent()
origins = ["*"]
# origins = ["http://localhost:3000", "http://23.21.39.159"],  # 프론트엔드 주소

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatResponseParams(BaseModel):
    answer_from_ai: Union[str, None] = None
    
class ChatRequestParams(BaseModel):
    member_id: int
    question: str

@app.post("/chat", response_model=ChatResponseParams)
async def chat(params: ChatRequestParams):
    try:
        # Invoke the chain with the updated params
        response = await chat_agent.get_response(params)

        print(f"response: {response.content}")
        return {"answer_from_ai": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8501)