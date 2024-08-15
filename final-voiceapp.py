import streamlit as st
from anthropic import Anthropic
from elevenlabs import save
from elevenlabs.client import ElevenLabs

st.title("Voice Chat")

# API 키 입력
anthropic_api_key = st.text_input("Enter Anthropic API Key:", type="password")
elevenlabs_api_key = st.text_input("Enter ElevenLabs API Key:", type="password")

if anthropic_api_key and elevenlabs_api_key:
    client = Anthropic(api_key=anthropic_api_key)
    elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

    if "anthropic_model" not in st.session_state:
        st.session_state["anthropic_model"] = "claude-3-haiku-20240307"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                audio_file = message.get("audio_file")
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")

    if prompt := st.chat_input("무엇을 도와드릴까요?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Anthropic API에 보낼 메시지에서 `audio_file` 필드를 제거
        messages_for_api = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]

        with st.chat_message("assistant"):
            response = client.messages.create(
                model=st.session_state["anthropic_model"],
                max_tokens=500,
                system="사용자의 말에 간결하게 대답하고, 늘 한국어 존대말을 사용해.",
                messages=messages_for_api  # 수정된 메시지 리스트를 API에 전달
            )
            assistant_response = response.content[0].text
            st.markdown(assistant_response)

            with st.spinner("Generating audio..."):
                audio = elevenlabs_client.generate(
                    text=assistant_response,
                    voice="Hojung Lee",
                    model="eleven_multilingual_v2"
                )
                
                # 임시 파일명 생성
                temp_filename = f"temp_audio_{len(st.session_state.messages)}.mp3"
                
                # 오디오 저장
                save(audio, temp_filename)
                
                # 저장된 오디오 파일 열기 및 재생
                with open(temp_filename, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")
                
                # 세션 상태에 오디오 파일 경로 저장
                st.session_state.messages.append({"role": "assistant", "content": assistant_response, "audio_file": temp_filename})


else:
    st.warning("Please enter both API keys to start the chat.")
