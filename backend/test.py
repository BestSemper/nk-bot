from langchain_ollama import ChatOllama
import asyncio

async def get_ai_response(question):
    # chat_model = ChatOllama(model="llama3.1", temperature=0.5)
    chat_model = ChatOllama(
        model = "llama3",
        temperature = 0.8,
        num_predict = 256,
        # other params ...
    )
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question}
    ]
    
    try:
        response = await chat_model.ainvoke(messages)
        return response.content
    except Exception as e:
        print(f"Error occurred: {e}")
        return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."

async def main():
    question = "한국의 수도는 어디인가요?"
    answer = await get_ai_response(question)
    print(f"질문: {question}")
    print(f"AI 응답: {answer}")

if __name__ == "__main__":
    asyncio.run(main())