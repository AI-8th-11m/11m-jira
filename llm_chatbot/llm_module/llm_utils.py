import os
import openai
from openai import OpenAI
from operator import itemgetter
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_core.runnables import RunnableMap
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

openai.api_key = os.environ.get("MY_OPENAI_API_KEY")


def evaluator(query, db):
    """
    db에서 찾아온 스크립트가 적절한지 판단하는 함수

    Parameters:
        query : 사용자 입력
        db : 스크립트가 저장된 db
    Returns:
        연관 정도 점수
        스크립트 : 연관 정도가 적절한 경우
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=openai.api_key,
        max_tokens=100,
        temperature=0.0,
    )
    script_retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 1})
    script = script_retriever.invoke(query)[0].page_content
    prompt = ChatPromptTemplate.from_template(
        """
    persona : relavence check machine
    **return only integer score**
    1. extract subject of script
    2. check relavence between query and subject
    3. calculate elaborate score 
    4. maximum '100', minimum '0', 
    5. increas by '5'
    6. sample is about conversation
    <sample>
    script : 'title : 강다니엘 이모 사건, content : 나 아는사람 강다니엘 닮은 이모가 다시보게되는게 다시 그때처럼 안닮게 엄마보면 느껴지는걸수도 있는거임?'

    query : '사건'
    ai : '10'

    query : '이모'
    ai : '25'

    query : '이모 사건'
    ai : '80'

    query : '강다니엘 사건'
    ai : '85'

    query : '강다니엘 이모'
    ai : '95'
    </sample>

    <query>
    {query}
    </query>

    <script>
    {script}
    </script>
    """
    )
    chain = prompt | llm | StrOutputParser()
    score = chain.invoke({"query": query, "script": script})
    if not score:
        return [0, "N/A"]
    return [int(score), script]


def chain_maker(script, language='korean'):
    """
    스크립트를 바탕으로 대화를 이어나가는 llm chain 생성

    Parameters:
        script : 선택된 스크립트
    Returns:
        llm chain
    """
    prompt = PromptTemplate.from_template(
        """
    persona : story teller
    language : only {language}
    tell dramatic story like talking to friend,
    speak informally,
    progress chapter by chapter,
    **hide header like '###'**,
    start chapter with interesting question,
    wait user answer,
    give reaction to answer,
    do not use same reaction or same question,
    end of the script give no question and wrap up the story,
    notice if story finished and give message '종료하려면 exit'

    # script
    {script}

    #Previous Chat History:
    {chat_history}

    #Question: 
    {question} 
    """
    )

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai.api_key, temperature=0.3)

    # 단계 8: 체인(Chain) 생성
    chain = (
        RunnableMap(
            {
                "language": lambda inputs: language,  # language는 고정값으로 전달
                "script": lambda inputs: script,  # script는 고정값으로 전달
                "question": itemgetter("question"),  # 입력에서 question 추출
                "chat_history": itemgetter(
                    "chat_history"
                ),  # 입력에서 chat_history 추출
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def history_chain(chain, memory_store: dict):
    """
    맥락을 유지하면 대화하는 chain 생성

    Parameters:
        chain : script 를 찾아 답변하는 chain
        memory_store : 대화의 맥락이 저장될 공간
    Returns:
        memory history chain
    """

    def get_session_history(session_ids):
        print(f"[대화 세션ID]: {session_ids}")
        if session_ids not in memory_store:  # 세션 ID가 store에 없는 경우
            # 새로운 ChatMessageHistory 객체를 생성하여 store에 저장
            memory_store[session_ids] = ChatMessageHistory()
        return memory_store[session_ids]  # 해당 세션 ID에 대한 세션 기록 반환

    # 대화를 기록하는 RAG 체인 생성
    rag_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,  # 세션 기록을 가져오는 함수
        input_messages_key="question",  # 사용자의 질문이 템플릿 변수에 들어갈 key
        history_messages_key="chat_history",  # 기록 메시지의 키
    )
    return rag_with_history