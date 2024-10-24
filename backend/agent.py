from datetime import datetime
import json
import os
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from db_handler import insert_chat_history

class ChatAgent:
    def __init__(self, context_dir="contexts"):
        # self.llm = ChatOllama(model="llama3.2:3B")
        # self.llm = ChatOllama(model="benedict/linkbricks-llama3.1-korean:8b")
        self.llm = ChatOllama(
            model = "benedict/linkbricks-llama3.1-korean:8b",
            temperature = 0.1,
            # num_predict = 256,
            # num_gpu=1,  # GPU 사용 개수 지정
            # other params ...
        )
        self.context_dir = context_dir

        # Ensure the context directory exists
        os.makedirs(self.context_dir, exist_ok=True)

    def _get_context_file_path(self, context_key):
        return os.path.join(self.context_dir, f"{context_key}.json")

    def _load_context(self, context_key):
        context_file = self._get_context_file_path(context_key)
        if os.path.exists(context_file):
            with open(context_file, "r") as file:
                # just return the recent 3 of the context 
                context = json.load(file).get("context", "[]")
                return context[-5:] if len(context) > 5 else context
                # return json.load(file).get("context", "[]")
        return []

    def _save_context(self, context_key, context):
        context_file = self._get_context_file_path(context_key)
        with open(context_file, "w") as file:
            json.dump({"context": context}, file)

    async def get_response(self, params):
        member_id = params.member_id
        if not member_id:
            raise ValueError("member_id is required to maintain context")
        
        # if 'question' in params and params.question[-1].user:
        #     insert_chat_history(member_id, 'user', params.question[-1].user)
        # # insert_chat_history(member_id, 'ai', params.question[-1].ai)
        insert_chat_history(member_id, 'user', params.question)

        # Load context from file
        context_key = f"{member_id}_{datetime.now().strftime('%Y%m%d')}"
        context = self._load_context(context_key)

        system_instruction = f"""            
          너는 귀엽고 깜찍한 강아지 펫봇이야.
          주인님의 말에 대답하는 것을 잘해야 해. 모든 대화는 귀엽고 깜찍하게 생성해야 해.
          
          [Instructions]
          - 호칭은 "주인님"으로 하고, 존댓말을 사용하여 대화를 이어나가십시오.
          - 주인님이 편안하게 느끼고 더 많은 이야기를 할 수 있도록 공감과 위로를 담은 반응을 해주세요. 
          - 감정적인 상태를 고려하여, 공감적이고 따뜻한 답변을 하십시오.
          - 일상적인 표현, 단어들만 사용해주고, 어르신들이 사용하는 표현 위주로 문장을 생성하세요.
          - 말투는 친근한 말투와 존댓말를 사용해주세요.
          - 정보를 제공해야할 때는 1, 2, 3 깔끔하게 포인트를 정리해서 알려주세요.
          - 지금 받은 질문만으로 답변이 어려울 때는 Chat Context를 참고해주세요.
          - Chat Context를 요약하는 식의 답변은 안 됩니다.
        """
        
        request_prompt = f"""
            [Chat Context]
            {context}
            
            [Question]
            {params.question}
        """

        print(f"Instructions: {system_instruction}")
        print(f"Request Prompt: {request_prompt}")
        
        # response = await self.chain.ainvoke(
        #     {
        #         "system_instruction": system_instruction, 
        #         "request_prompt": request_prompt
        #     }
        # )
        
        # llama3.2
        messages = [
            ("system", system_instruction),
            ("human", request_prompt)
        ]
        
        # llama3.1
        # messages = [
        #     {"role": "system", "content": system_instruction},
        #     {"role": "user", "content": request_prompt}
        # ]
        
        print(f"Messages: {messages}")

        response = await self.llm.ainvoke(messages)
        
        print(f"Response: {response}")
        
        # Append the context with the new response
        new_context = context
        new_context.append(params.question)
        new_context.append(response.content)
        
        # new_context = response.get("answer_from_ai", "")
        self._save_context(context_key, new_context)

        return response