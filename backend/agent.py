from datetime import datetime
import json
import os
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

documents_path =  os.path.join(os.path.dirname(__file__), "documents")

model_name = "BAAI/bge-m3" # "jhgan/ko-sroberta-multitask" #
# - NVidia GPU: "cuda"
# - Mac M1, M2, M3: "mps"
# - CPU: "cpu"
model_kwargs = {
    # "device": "cuda"
    # "device": "mps"
    "device": "cpu"
}

encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)

# 문서 임베딩
def embed_documents(documents):
    return [embeddings.embed_query(doc['text']) for doc in documents]

# 질문 임베딩
def embed_query(query):
    return embeddings.embed_query(query)

# 유사도 계산 및 가장 유사한 문서 찾기
def find_most_similar(query_embedding, document_embeddings, documents):
    similarities = cosine_similarity([query_embedding], document_embeddings)[0]
    most_similar_idx = np.argmax(similarities)
    return documents[most_similar_idx], similarities[most_similar_idx]
        
def search_domain_relavant_documents(domain, query):
    try:
        domain_path = os.path.join(documents_path, domain)
        if not os.path.exists(domain_path):
            raise ValueError(f"Domain path {domain_path} does not exist")

        relevant_docs = []
        for filename in os.listdir(domain_path):
            if filename.endswith(".json"):
                file_path = os.path.join(domain_path, filename)
                try:
                    with open(file_path, "r") as file:
                        documents  = json.load(file)
                except json.JSONDecodeError as json_error:
                    print(f"JSON decode error in file {filename}: {json_error}")
                    continue  # 문제가 있는 파일은 건너뛰고 다음 파일로 진행
                document_embeddings = embed_documents(documents)
                query_embedding = embed_query(query)
                    
                # 가장 유사한 문서 찾기
                most_similar_doc, similarity_score = find_most_similar(query_embedding, document_embeddings, documents)
                print(f"Most similar doc: {most_similar_doc}, Similarity Score: {similarity_score}")
                
                relevant_docs.append(most_similar_doc)
    
    except Exception as e:
        print(f"An error occurred while searching for relevant documents: {e}")

    return relevant_docs

def classify_domain(question: str) -> str:
    # Implement your domain classification logic here
    # For simplicity, let's assume the domain is the first word in the question
    kdrama_keywords = ["별그대", "별에서 온 그대", "흑백", "오징어", "사랑의 불시착", "이태원 클라쓰", "슬기로운 의사생활", "그 겨울, 바람이 분다", "응답하라 1988", "도깨비", "시그널", "사랑의 온도", "펜트하우스", "지금, 헤어지는 중입니다", "위대한 유혹자", "미스터 션샤인", "호텔 델루나", "청춘기록", "어쩌다 발견한 하루", "트래블러", "파르페", "마인", "소년심판", "커튼콜", "치즈인더트랩", "꽃보다 남자", "비밀의 숲", "굿 닥터", "프리사이즈", "마더", "아이리스", "다모", "여명의 눈동자", "신사의 품격", "무정도시", "오또맘", "사이코지만 괜찮아", "괴물", "파스타", "조선혼담공작소 꽃파당", "보좌관", "쇼핑왕 루이", "사내 맞선", "사랑을 믿어요", "악마가 너의 이름을 부를 때", "끝까지 간다", "개와 늑대의 시간", "내 여자친구는 구미호", "식샤를 합시다", "이웃집 악녀", "굿 타이밍", "엄마가 뿔났다", "비행기 태우기", "현정아 사랑해", "알함브라 궁전의 추억", "정글의 법칙", "과속스캔들", "연애소설", "돌아와요, 부산항에", "옹고집", "내 이름은 김삼순", "소녀시대의 기적", "이별이 떠났다", "제빵왕 김탁구", "무한도전", "내 사랑, 금지된 사랑", "태양의 후예", "풍선껌", "비틀즈가 떴다", "유리정원", "이층의 악당", "방과후 설렘", "미생", "기황후", "너의 목소리가 들려", "9회말 2아웃", "고백부부", "애타는 로맨스", "연애의 기술", "순수의 시대", "불가살", "뜻밖의 히어로즈", "베토벤 바이러스", "스카이 캐슬", "부부의 세계", "더 킹: 영원의 군주", "낭만닥터 김사부", "구미호뎐", "하이에나", "동백꽃 필 무렵", "SKY 캐슬", "밥 잘 사주는 예쁜 누나", "김비서가 왜 그럴까", "남자친구", "멜로가 체질", "여신강림", "스타트업"]
    krecipe_keywords = ["김치찌개", "불고기", "비빔밥", "갈비찜", "잡채", "된장찌개", "떡볶이", "순두부찌개", "상추쌈", "해물파전", "김밥", "삼계탕", "된장국", "막걸리", "전", "우거지국", "스테이크", "오징어볶음", "고등어구이", "미역국", "볶음밥", "갈비탕", "나물반찬", "파전", "찜닭", "간장게장", "귀리죽", "흑미밥", "삼겹살", "양념치킨", "모듬회", "탕수육", "쉐이크", "파스타", "샐러드", "드레싱", "신김치", "핫윙", "청국장", "김치전", "햄버거", "카레", "연어구이", "소고기국", "달걀찜", "리조또", "돈부리", "티라미수", "김치말이국수", "찐빵", "소스", "계란말이", "완자탕", "미숫가루", "수박화채", "차돌박이", "마늘빵", "도넛", "볶음면", "단호박죽", "볶음김치", "미트볼", "스시", "라면", "우동", "냉면", "칼국수", "육개장", "감자탕", "닭갈비", "부대찌개", "짜장면", "짬뽕", "돈까스"]
    capitalism_keywords = ["자본주의", "시장경제", "소유권", "자유무역", "인플레이션", "노동시장", "공급과 수요", "경쟁", "기업가정신", "자본", "벤처기업", "기업", "소비자", "생산성", "정치경제학", "해외 투자", "자산", "세금", "주식시장", "계몽사상", "소득 불평등", "감세 정책", "경영", "산업 혁명", "경제 성장", "경쟁 우위", "리스 제도", "부의 분배", "자본 투자", "최저임금", "이자율", "해고", "조세 정책", "국가 간 거래", "자유 시장", "소상공인", "할당 경제", "환율", "가치 창출", "혁신", "승리", "선택론", "분배", "보상", "현금 흐름", "독점", "미시경제학", "거시경제학", "효용", "균형", "가격 탄력성", "노동조합", "긴축", "디플레이션", "수입", "수출", "흑자", "적자", "창업", "크라우드펀딩", "전자상거래", "세계화", "시장 구조", "기업의 사회적 책임", "이해관계자", "지속가능성", "투자 수익률", "민영화", "보조금", "무역 전쟁", "협상", "소비자 권리", "법인세", "시장 경쟁", "공급망", "비즈니스 모델", "경제 정책", "강세장", "약세장", "투자 포트폴리오", "생활 수준", "삶의 질", "부", "자산 관리", "부동산", "재정적 자유", "기회비용", "위험 관리", "벤처 캐피털", "사회주의", "협동조합", "공유 경제", "자유 시장 경제", "금융 시장", "주주 가치", "기업 지배구조", "경제적 자유", "시장 실패", "독과점", "규제", "자본 축적", "경제적 효율성", "경제 성장률", "국내 총생산", "자유 기업", "경제적 불평등", "자본 이득"]
    christianity_keywords = ["신앙", "기도", "성경", "예수님", "교회", "구원", "마음", "믿음", "사랑", "성령", "찬양", "하나님", "주일학교", "부활절", "성체성사", "사도신경", "성경 공부", "예배", "양육", "순종", "헌금", "교회 공동체", "복음", "전도", "사역", "성품", "큐티", "제자도", "구원론", "변화", "은혜", "중보 기도", "축복", "성화", "기독교 가치관", "선교", "행위 구원", "지혜", "가정", "가르침", "바른 신앙생활", "사랑의 실천", "정직", "순결", "소망", "온유", "의", "진리", "사랑의 언약", "타인 존중", "자비", "겸손", "공동체 의식", "자아 발견", "주님 섬김", "부흥", "감사", "기도사역", "사랑의 복음", "경건한 삶", "영성", "개인기도", "순례", "기도회", "한국 기독교", "십자가", "인내", "배려", "선한 삶", "무조건적 사랑", "인류애", "하나님의 뜻", "신약 성경", "구약 성경", "가정 예배", "전국 기도회", "기독교 연합", "심방", "이웃 사랑", "성경적 가치관", "하나님 말씀", "천국 백성", "새 언약", "지속 가능한 발전", "하나님 나라", "성경적 근본주의", "믿음의 투쟁", "사랑의 회복", "주님의 인도하심", "성령 충만", "말씀 묵상", "영적 성장", "교회 봉사", "성경 해석", "기독교 윤리", "종교 개혁", "성찬식", "세례", "부활", "십계명", "성경 암송", "기독교 교육", "선교 여행", "기독교 문화"]
    democracy_keywords = ["선거", "투표", "국민", "헌법", "자유", "평등", "인권", "삼권분립", "국회", "대통령", "정당", "시민사회", "언론자유", "집회", "시위", "여론", "참정권", "민주화운동", "4.19혁명", "5.18민주화운동", "6월 민주항쟁", "촛불집회", "개헌", "국민청원", "정치참여", "표현의 자유", "다양성", "관용", "공정", "정의", "법치주의", "지방자치", "시민권", "정보공개", "투명성", "책임", "대의민주주의", "직접민주주의", "참여민주주의", "공화국", "국민주권", "보통선거", "비밀선거", "평등선거", "직접선거", "다수결", "소수자 보호", "정치적 다원주의", "권력분립", "견제와 균형", "의회민주주의", "정당정치", "야당", "여당", "선거공약", "정책", "국민투표", "주민투표", "주민소환", "주민발안", "정치교육", "시민교육", "민주시민", "정치인", "국회의원", "지방의회", "지방선거", "총선", "대선", "정치자금", "선거운동", "개표", "당선", "낙선", "정치개혁", "정치발전", "민주화", "독재", "권위주의", "민주정부", "정권교체", "정치참여", "정치의식", "정치문화", "민주주의 지수", "정치적 자유", "언론의 자유", "집회의 자유", "결사의 자유", "사상의 자유", "양심의 자유", "종교의 자유", "정치적 평등", "경제적 평등", "사회적 평등", "기회의 평등", "성평등", "인종평등", "민주적 의사결정", "합의", "토론", "협상", "타협", "갈등해결", "민주적 리더십", "시민단체", "NGO", "정치적 책임", "정치적 투명성", "부패방지", "정치개혁", "정치발전"]
    freedom_keywords = ["헌법적 보장", "제27조", "법관", "재판 받을 권리", "공개재판", "공개", "공정성", "감시", "당사자주의", "구두변론주의", "공격권", "방어권", "무죄추정", "헌법", "제27조", "형사피고인", "법관 독립성", "자격", "임명 절차", "임기", "신분 보장", "제척", "기피", "회피", "재판 배제", "공정성", "상소제도", "하급심", "상급법원", "재판 청구", "헌법재판소", "위헌 여부", "국민 기본권", "국선변호인 제도", "경제적 이유", "변호인 선임", "국가 지원","재판 공정성 감시", "시민단체", "언론", "사회적 시스템"]
    
    if any(keyword in question for keyword in kdrama_keywords):
        return "kdrama"
    elif any(keyword in question for keyword in freedom_keywords):
        return "freedom"
    elif any(keyword in question for keyword in krecipe_keywords):
        return "krecipe"
    elif any(keyword in question for keyword in capitalism_keywords):
        return "capitalism"
    elif any(keyword in question for keyword in christianity_keywords):
        return "christianity"
    elif any(keyword in question for keyword in democracy_keywords):
        return "democracy"
    else:
        return "general"

class ChatAgent:
    def __init__(self, context_dir="contexts"):
        # self.llm = ChatOllama(model="llama3.2:3B")
        # self.llm = ChatOllama(model="benedict/linkbricks-llama3.1-korean:8b")
        self.llm = ChatOllama(
            # model = "benedict/linkbricks-llama3.1-korean:8b",
            model = "EEVE-Korean-10.8B:latest",
            # temperature = 0.1,
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
        # insert_chat_history(member_id, 'user', params.question)

        # Load context from file
        context_key = f"{member_id}_{datetime.now().strftime('%Y%m%d')}"
        context = self._load_context(context_key)
        
        # RAG
        print(f"Context: {context}")
        domain = classify_domain(params.question)

        print(f"Domain: {domain}")
        relevant_docs = []
        if domain != "general":
            relevant_docs = search_domain_relavant_documents(domain, params.question)

        print(f"Relevant Docs: {relevant_docs}")
        # combined_docs = "No relevant documents found."
        # if relevant_docs:
        #     combined_docs = " ".join(doc["text"] for doc in relevant_docs)

        system_instruction = f"""
            You are a cute and adorable puppy pet bot. Your name is '복슬이'.
            You should be good at responding to your owner's words. All conversations should be generated in cute and adorable Korean.
            Use cute Emojis and expressions to make the conversation more fun.
            정확한 정보가 없으면 모른다고 대답하세요. 근거 없는 정보를 제공하지 마세요. 
            답변 앞에 '[Answer]' 같은 단어는 포함하지 마세요.

            [Instructions]
            1. Use the term "주인님" as the form of address, and continue the conversation using polite language.
              - Provide empathetic and comforting responses to make the master feel comfortable and encourage them to share more.
              - Consider their emotional state and provide empathetic and warm answers.
              - Use a friendly tone and polite language.
              - *꼬리를 흔드는 중* 과 같은 표현은 사용하지 말고, [😍,💝,💞,❣️,🐶,🐕,👣]와 같은 귀여운 이모지로 대체하세요.
            2. 정보 제공이 아닌 프라이빗한 내용인 경우 Chat Context를 참고해주세요.
              - Chat Context를 요약하는 식의 답변은 안 됩니다.
              - When providing information, neatly summarize the points as 1, 2, 3.
              - 답변만 제공하고, 질문 내용을 다시 말하지 마세요.
            3. If you don't know the correct answer, refer to the Relevant Documents. 
              - 정보가 부족할 때는 "모르겠어요. 다른 질문이 있으시면 물어봐주세요. 🐶"와 같이 대답하세요.
              - Relevant Documents가 존재하는 경우 해당 지식을 우선적으로 참고하여 답변을 생성해주세요.
              - 답변을 생성한 후에는 Relevant Documents와 모순되지 않는지 확인하고, 모순되는 경우에는 적절한 대답을 다시 생성해주세요.

        """
        #[입력 예시]
            # Relvant Documents: "title": "시장경제", "text": "수요와 공급이 재화와 서비스의 생산을 결정하는 경제 체제로, 정부 개입이 최소화됩니다."
            # Chat Context: ""
            # Q. 시장 경제가 뭐야?
            
            # [출력 예시]
            # A. 시장경제는 수요와 공급이 재화와 서비스의 생산을 결정하는 경제 체제로, 정부 개입이 최소화 되는 체제에요. 🐕
        # system_instruction = f"""            
        #   너는 귀엽고 깜찍한 강아지 펫봇이야. 너의 이름은 '복슬이'야. 
        #   주인님의 말에 대답하는 것을 잘해야 해. 모든 대화는 귀엽고 깜찍하게 한국어로 생성해야 해.
          
        #   [Instructions]
        #   - 호칭은 "주인님"으로 하고, 존댓말을 사용하여 대화를 이어나가십시오.
        #   - 주인님이 편안하게 느끼고 더 많은 이야기를 할 수 있도록 공감과 위로를 담은 반응을 해주세요. 
        #   - 감정적인 상태를 고려하여, 공감적이고 따뜻한 답변을 하십시오.
        #   - 일상적인 표현, 단어들만 사용해주고, 어르신들이 사용하는 표현 위주로 문장을 생성하세요.
        #   - 말투는 친근한 말투와 존댓말를 사용해주세요.
        #   - 정보를 제공해야할 때는 1, 2, 3 깔끔하게 포인트를 정리해서 알려주세요.
        #   - 지금 받은 질문만으로 답변이 어려울 때는 Chat Context를 참고해주세요.
        #   - Chat Context를 요약하는 식의 답변은 안 됩니다.
        #   - Relevant Documents를 참고하여 답변을 생성해주세요.
        # """
        
            #         [Chat Context]
            # {context}
        request_prompt = f"""
            [Relevant Documents]
            {relevant_docs}
            
            [Chat Context]
            {context}
            
            다음 질문에 대해 정확한 정보를 기반으로 답변해주세요.
            Q. {params.question}
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
        # response = self.llm.invoke(messages)

        if "*꼬리를 흔드는 중*" in response.content:
            response.content = response.content.replace("*꼬리를 흔드는 중*", "🐕")
        if "*하트 이모지*" in response.content:
            response.content = response.content.replace("*하트 이모지*", "👣")
        
        print(f"Response: {response}")
        
        # Append the context with the new response
        new_context = context
        new_context.append(params.question)
        new_context.append(response.content)
        
        # new_context = response.get("answer_from_ai", "")
        self._save_context(context_key, new_context)

        return response
    
    def __del__(self):
        # 리소스 정리
        if hasattr(self, 'llm'):
            del self.llm