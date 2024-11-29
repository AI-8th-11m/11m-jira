import streamlit as st
from streamlit_chat import message

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

import numpy as np

import os
import openai
from openai import OpenAI


# 제목
st.title("꼬꼬무")
st.write(
    "미해결 사건에 대해 이야기를 하는 챗봇 입니다." 
    "대화를 시작하고 싶으시다면, 채팅을 시작해주세요."
)



# #챗봇 만들기
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []  

# for content in st.session_state.chat_history:
#     with st.chat_message(content["role"]):
#         st.markdown(content['message'])    

# if prompt := st.chat_input("메시지를 입력하세요."):
#     with st.chat_message("user"):
#         st.markdown(prompt)
#         st.session_state.chat_history.append({"role": "user", "message": prompt})

#     with st.chat_message("ai"):                
#         response = f'{prompt}...? 나는 아직 네가 하는 말 반복하는 것 밖에 못 해. 아직 구현이 안 됐거든. 조금만 기다려줘!'
#         st.markdown(response)
#         st.session_state.chat_history.append({"role": "ai", "message": response})


import streamlit as st

# Streamlit 상태 관리 초기화
if "page" not in st.session_state:
    st.session_state.page = "settings"
if "history" not in st.session_state:
    st.session_state.history = {}  # 세션별 대화 기록 저장
if "current_session" not in st.session_state:
    st.session_state.current_session = None  # 현재 세션 ID

# 페이지 전환 함수
def go_to_chat():
    st.session_state.page = "chat"

def go_to_settings():
    st.session_state.page = "settings"

# 대화 기록 저장 함수
def save_message(session_id, user_message, bot_message):
    if session_id not in st.session_state.history:
        st.session_state.history[session_id] = []  # 새로운 세션 초기화
    st.session_state.history[session_id].append((user_message, bot_message))



# 유저 설정 화면
if st.session_state.page == "settings":
    # 중앙 정렬
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("유저 설정 화면")
        st.subheader("사용자 정보 입력")

        # 사용자 입력
        session_id = st.text_input("세션 ID를 입력하세요", placeholder="예: session123")
        language = st.selectbox("사용할 언어를 선택하세요", options=["한국어", "English", "日本語"])

        # 버튼: 저장 후 넘어가기
        if st.button("저장 후 넘어가기"):
            if session_id:
                st.session_state.session_id = session_id
                st.session_state.language = language
                st.session_state.current_session = session_id
                st.session_state.history[session_id] = []  # 새로운 세션 초기화
                go_to_chat()
            else:
                st.warning("세션 ID를 입력해주세요!")

# 채팅 화면
elif st.session_state.page == "chat":
    # 사이드바: 세션 ID 선택
    st.sidebar.title("세션 관리")
    session_list = list(st.session_state.history.keys())
    selected_session = st.sidebar.selectbox("저장된 세션 ID", options=["현재 세션"] + session_list)

    if selected_session != "현재 세션":
        st.session_state.current_session = selected_session

    # 중앙 정렬
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("채팅 화면")

        # 현재 세션 정보 표시
        st.write(f"세션 ID: {st.session_state.current_session}")
        st.write(f"사용 언어: {st.session_state.language}")



        # # 대화 기록 출력
        # st.write("### 대화 기록")
        # for user_msg, bot_msg in st.session_state.history[st.session_state.current_session]:
        #     st.write(f"**유저**: {user_msg}")
        #     st.write(f"**챗봇**: {bot_msg}")

        # 메시지 입력
        user_input = st.text_input("메시지를 입력하세요:")
        if user_input:
            bot_response = f"챗봇 응답 예시 ({user_input})"  # 실제 모델 연동 가능
            save_message(st.session_state.current_session, user_input, bot_response)
            st.experimental_rerun()  # 화면 갱신


        #챗봇 만들기
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []  

        for content in st.session_state.chat_history:
            # with st.chat_message(content["role"]):
            #     st.markdown(content['message'])    
            # if user_input = st.text_input("메시지를 입력하세요."):
            if user_input:
                bot_response = f"챗봇 응답 예시 ({user_input})"  # 실제 모델 연동 가능
                save_message(st.session_state.current_session, user_input, bot_response)
                st.experimental_rerun()  # 화면 갱신
                st.session_state.chat_history.append({"role": "user", "message": user_input})


            # with st.chat_message("ai"):                
            #     response = f'{prompt}...? 나는 아직 네가 하는 말 반복하는 것 밖에 못 해. 아직 구현이 안 됐거든. 조금만 기다려줘!'
            #     st.markdown(response)
            #     st.session_state.chat_history.append({"role": "ai", "message": response})

                # # 세팅 화면으로 돌아가기 버튼
                # if st.button("세팅 화면으로 돌아가기"):
                #     go_to_settings()


