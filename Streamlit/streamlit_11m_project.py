import streamlit as st

# 제목
st.title("🕸️꼬꼬무")
st.write(
    "미해결 사건에 대해 이야기를 하는 챗봇 입니다." 
    "대화를 시작하고 싶으시다면, 채팅을 시작해주세요."
)


#챗봇 만들기
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  

for content in st.session_state.chat_history:
    with st.chat_message(content["role"]):
        st.markdown(content['message'])    

if prompt := st.chat_input("메시지를 입력하세요."):
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "message": prompt})

    with st.chat_message("ai"):                
        response = f'{prompt}...? 나는 아직 네가 하는 말 반복하는 것 밖에 못 해. 아직 구현이 안 됐거든. 조금만 기다려줘!'
        st.markdown(response)
        st.session_state.chat_history.append({"role": "ai", "message": response})
