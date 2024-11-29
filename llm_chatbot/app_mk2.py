from llm_module.docs_utils import *
from llm_module.db_utils import *
from llm_module.script_utils import *
from llm_module.llm_utils import *
from llm_module.translator_module import translator
import random
import time
import streamlit as st

json_files = [
    "./llm_chatbot/documents/filtered_unsolved_cases.json",
    "./llm_chatbot/documents/korea_crime.json",
]
titles = title_json_data(json_files)
sample_titles = titles[0:11]
path = "./llm_chatbot/db/script_db"
db_name = "script_db"
script_db = load_vstore(db_name, path)
LANG_CODE = False

if "history" not in st.session_state:
    st.session_state["history"] = {}
if "session_list" not in st.session_state:
    st.session_state["session_list"] = []
if "current_session_id" not in st.session_state:
    st.session_state["current_session_id"] = "no session id"
if "title_list_expanded" not in st.session_state:
    st.session_state["title_list_expanded"] = False
if "conversation" not in st.session_state:
    st.session_state["conversation"] = {}


st.sidebar.title("사이드바 메뉴")


main_option = st.sidebar.selectbox("메뉴를 선택하세요", ["제목 리스트", "세션 리스트"])


if main_option == "제목 리스트":

    toggle_button = st.sidebar.button("제목 리스트 토글")
    if toggle_button:
        st.session_state["title_list_expanded"] = not st.session_state[
            "title_list_expanded"
        ]

    if st.session_state["title_list_expanded"]:
        st.sidebar.subheader("제목 리스트")
        for title in sample_titles:
            st.sidebar.write(title)
    else:
        st.sidebar.write("제목 리스트를 펼치려면 버튼을 클릭하세요.")

elif main_option == "세션 리스트":
    st.sidebar.subheader(f"**현재 세션 ID:** {st.session_state['current_session_id']}")
    st.sidebar.subheader("세션 리스트")
    session_list = st.session_state.get("session_list")
    for session in session_list:
        if st.sidebar.button(f"[{session['id']}]"):
            st.session_state.session_id = session["id"]
            st.session_state["current_session_id"] = session["id"]
            st.session_state.page = "session_page"
            st.rerun()


# session_id = 'test'
# st.session_state.session_id = session_id
# st.session_state['current_session_id'] = st.session_state.session_id


# 세팅 페이지 구현
def setting_page():
    st.title("유저 설정 화면")

    # 세션 ID와 언어 설정
    session_id = st.text_input("세션 ID를 입력하세요", placeholder="예: session123")
    language = st.selectbox(
        "사용할 언어를 선택하세요", options=["한국어", "English", "日本語"]
    )

    if st.button("저장 후 넘어가기"):
        if session_id:
            # 세션 정보 저장
            st.session_state.session_id = session_id
            st.session_state["current_session_id"] = session_id
            st.session_state["session_list"].append({"id": session_id})
            st.session_state.LANG = language
            st.session_state.current_session = session_id
            st.session_state.page = "check"  # 체크 페이지로 이동
            st.rerun()
        else:
            st.warning("세션 ID를 입력해주세요!")


# 점수 구간 설정
MIN_SCORE = 80
MAX_SCORE = 85
NEXT_SCORE = 95

# 초기 점수 설정
if "score" not in st.session_state:
    st.session_state.score = 0


# 체크 페이지 구현
def check_page():
    st.title("체크 페이지")
    query = st.text_input("어떤 이야기가 듣고 싶으신가요?", placeholder="예 : 아무거나")

    if query:
        with st.status("답변을 확인 중...", expanded=True) as status:
            if query is None or "아무거나" in query.strip():
                st.write("재미난 이야기를 가져오는 중...")
                choice = random.choice(sample_titles)
                query = choice
            relavence = evaluator(query, script_db)
            st.write(f"관련도 점수: {relavence[0]}")
            st.session_state.score += relavence[0]
        status.update(label="확인이 끝났습니다!", state="complete", expanded=False)

        if relavence[0] < 80:
            st.write("모르는 이야기입니다.")
            st.write("종료 : exit, 다시 물어보기 : return, 생성하기 : create")

            user_input = st.text_input("입력하세요.")
            if user_input.lower() == "exit":
                st.session_state.page = "settings"  # 세팅 페이지로 이동
                st.rerun()
            elif user_input.lower() == "return":
                st.session_state.page = "check"  # 체크 페이지로 돌아감
                st.rerun()
            elif user_input.lower() == "create":
                st.session_state.page = "create"  # 생성 페이지로 이동
                st.rerun()

        elif relavence[0] < 95 and relavence[0] >= 80:
            st.write("더 자세히 이야기 해주세요.")
            st.rerun()

        elif relavence[0] >= 95:
            script = relavence[1]
            st.session_state.page = "chat"  # 채팅 페이지로 이동
            st.session_state.query = query
            st.session_state.script = script
            time.sleep(1)
            st.rerun()


# 생성 페이지 구현
def create_page():
    st.title("생성 페이지")
    st.write("새로운 스크립트를 입력할 수 있습니다.")

    text_input = st.text_area("URL 또는 텍스트를 입력해주세요.")
    if text_input:
        with st.status("스크립트를 생성중입니다...", expanded=True) as status:
            st.write("작가가 문서를 읽어보는 중...")
            time.sleep(2)
            st.write("스크립트를 작성하는 중...")
            time.sleep(2)
            st.write("창작의 고통을 느끼는 중...")
            new_script = script_maker(text_input)
            st.write(f"생성된 스크립트: {new_script}")
            st.write("DB에 추가합니다...")
            time.sleep(2)
            script_db = load_vstore("script_db", "./llm_chatbot/db/script_db")
            add_to_vstore(new_script, script_db)
            status.update(
                label="작업이 종료되었습니다.", state="complete", expanded=False
            )

    if st.button("돌아가기"):
        st.session_state.page = "check"
        time.sleep(1)
        st.rerun()


def chat_page(script):
    st.title("채팅 페이지")
    st.write("이제 채팅을 시작할 수 있습니다.")
    ID = st.session_state.get("session_id")
    LANG = st.session_state.get("LANG")
    QUERY = st.session_state.get("query")
    if "messages" not in st.session_state:
        init_history = [{"role": "assistant", "content": 'no history yet'}]
        chain = streamlit_chain(script, init_history, LANG)
        init_response = chain.invoke(
            {"question": QUERY},
            config={"configurable": {"session_id": ID}},
        )
        st.session_state["messages"] = [{"role": "assistant", "content": init_response}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        if prompt.lower() == "exit":
            st.write("대화를 종료합니다.")
            st.session_state["conversation"][f"{ID}_history"] = st.session_state["messages"]
            st.session_state["conversation"][f"{ID}_script"] = script
            del st.session_state["messages"]
            st.session_state.page = "settings"
            st.rerun()

        # elif LANG_CODE:
        #     prompt = translator(prompt, LANG_CODE)

        st.session_state.messages.append({"role": "user", "content": prompt})
        prompt = stream_data(prompt)
        st.chat_message("user").write_stream(prompt)

        history = st.session_state['messages']
        chain= streamlit_chain(script, history, LANG)
        msg = chain.invoke(
            {"question": prompt},
            config={"configurable": {"session_id": ID}},
        )
        st.session_state.messages.append({"role": "assistant", "content": msg})
        msg = stream_data(msg)
        st.chat_message("assistant").write_stream(msg)

    if st.button("대화 종료"):
        st.session_state.page = "messages"
        st.session_state["conversation"][f"{ID}_history"] = st.session_state["messages"]
        st.session_state["conversation"][f"{ID}_script"] = script
        del st.session_state["messages"]
        st.session_state.page = "settings"
        time.sleep(1)
        st.rerun()


def session_page():
    ID = st.session_state["session_id"]
    LANG = st.session_state.get("LANG")
    st.title(f"{ID}페이지")
    st.write("다시 채팅을 시작할 수 있습니다.")

    st.session_state["messages"] = st.session_state["conversation"][f"{ID}_history"]
    script = st.session_state["conversation"][f"{ID}_script"]

    chain = streamlit_chain(script, st.session_state["messages"], LANG)

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        if prompt.lower() == "exit":
            st.write("대화를 종료합니다.")
            st.session_state.page = "settings"
            st.rerun()

        # elif LANG_CODE:
        #     prompt = translator(prompt, LANG_CODE)

        st.session_state.messages.append({"role": "user", "content": prompt})
        prompt = stream_data(prompt)
        st.chat_message("user").write_stream(prompt)

        msg = chain.invoke(
            {"question": prompt},
            config={"configurable": {"session_id": ID}},
        )
        st.session_state.messages.append({"role": "assistant", "content": msg})
        msg = stream_data(msg)
        st.chat_message("assistant").write_stream(msg)

    if st.button("대화 종료"):
        st.session_state.page = "messages"
        st.session_state["conversation"][f"{ID}_history"] = st.session_state["messages"]
        st.session_state["conversation"][f"{ID}_script"] = script
        del st.session_state["messages"]
        st.session_state.page = "settings"
        time.sleep(1)
        st.rerun()


if "page" not in st.session_state:
    st.session_state.page = "settings"

if st.session_state.page == "settings":
    setting_page()
elif st.session_state.page == "check":
    check_page()
elif st.session_state.page == "create":
    create_page()
elif st.session_state.page == "chat":
    chat_page(st.session_state.script)
elif st.session_state.page == "session_page":
    session_page()
