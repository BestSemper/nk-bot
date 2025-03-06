# nk-bot


## How to run the frontend
cd frontend
npm run dev

## How to run the backend
cd backend
source nk-bot-api/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8501 --reload

## How to create the base llm model
ollama create EEVE-Korean-10.8B -f EEVE-Korean-Instruct-10.8B-v1.0-GGUF/Modelfile