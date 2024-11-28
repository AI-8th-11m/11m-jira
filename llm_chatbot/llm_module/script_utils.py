import os
import time
import openai
import random
import threading
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationSummaryMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 자체 제작 모듈
from llm_module.docs_utils import documents_filter

openai.api_key = os.environ.get("MY_OPENAI_API_KEY")


def generate_script(summaries):
    """
    대화 LLM이 전달할 이야기의 대본 생성

    Parameters:
        summaries: 필터링된 텍스트 데이터

    Returns:
        텍스트 데이터
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=openai.api_key,
        max_tokens=5000,
        temperature=0.0,
    )
    prompt = ChatPromptTemplate.from_template(
        """
    persona = script writer
    language = only in korean
    least 3000 tokens
    use input,
    refer to sample,
    write about time, character, event,
    write only fact
    ignore the mere listing of facts and write N/A
 
    <sample>
    # title : title of script
    # prologue 1 : song, movie, book, show about subject
    - coontent :
    # prologue 2 : explain about subject
    - coontent :
    # prologue 3 : explain about character
    - coontent :
    # exposition 1 : historical background of subject
    - coontent :
    # exposition 2 : history of character
    - coontent :
    # exposition 3 : beginning of event
    - coontent :
    # development 1 : situation, action, static of character
    - coontent :
    # development 2 : influence of event
    - coontent :
    # development 3 : reaction of people
    - coontent :
    # climax 1 : event and effect bigger
    - coontent :
    # climax 2 : dramatic action, conflict
    - coontent :
    # climax 3 : falling Action
    - coontent :
    # denouement : resolution
    - coontent :
    # epilogue : message, remaining
    - coontent :
    </sample>

    <input>
    {summaries}
    </input>

    """
    )
    chain = prompt | llm | StrOutputParser()
    script = chain.invoke({"summaries": summaries})
    return script


def script_maker(INPUT: str):
    print("다소 시간이 소요될 수 있습니다.")
    messages = [
        "처리 중...",
        "잠시만 기다려주세요.",
        "계속 진행 중입니다.",
        "몇 초 후에 완료됩니다.",
        "끝나가고 있어요.",
    ]

    # 메시지를 랜덤으로 출력하는 함수 (백그라운드에서 실행)
    def print_random_messages(stop_event):
        while not stop_event.is_set():  # stop_event가 set될 때까지 메시지를 계속 출력
            print(random.choice(messages))
            time.sleep(20)  # 1초마다 메시지를 출력

    stop_event = threading.Event()
    message_thread = threading.Thread(
        target=print_random_messages, args=(stop_event,), daemon=True
    )
    message_thread.start()

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=100
    )
    if INPUT.startswith("http"):
        url = INPUT
        web_docs = WebBaseLoader(url).load()
        if web_docs[0].metadata["title"]:
            title = web_docs[0].metadata["title"]
        else:
            title = ""
        docs = f"title : {title} \n\n" + web_docs[0].page_content
    else:
        docs = str(INPUT)
    documents = [Document(page_content=docs)]
    SPLITS = text_splitter.split_documents(documents)
    refined = documents_filter(SPLITS)
    new_script = generate_script(refined)

    stop_event.set()
    return new_script
