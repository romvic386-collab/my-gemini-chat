import streamlit as st
import google.generativeai as genai
from PIL import Image # Подключаем библиотеку для картинок
import time

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Gemini Vision", page_icon="👁️", layout="centered")

# --- ГЛОБАЛЬНАЯ ПАМЯТЬ ---
@st.cache_resource
def get_global_history():
    return []

global_history = get_global_history()

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("🎛️ Настройки")
    
    # 1. ВЫБОР КЛЮЧА
    available_keys = [k for k in st.secrets.keys() if k.startswith("KEY_")]
    if available_keys:
        selected_key_name = st.selectbox(
            "🔑 Выбери ключ:",
            options=available_keys,
            format_func=lambda x: f"Ключ #{x.split('_')[1]}"
        )
        API_KEY = st.secrets[selected_key_name]
    else:
        st.error("Добавь ключи в Secrets!")
        st.stop()

    # 2. ВЫБОР МОДЕЛИ
    # Для картинок лучше всего работают 1.5 Flash и 3.0 Pro (если доступна)
    selected_model = st.radio(
        "🧠 Модель:",
        options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-pro-preview"], 
        index=0 # Flash по умолчанию (быстрая и хорошо видит)
    )
    
    st.divider()

    # 🔥 3. ЗАГРУЗКА ФОТО 🔥
    st.header("🖼️ Загрузка фото")
    uploaded_file = st.file_uploader("Кидай картинку сюда:", type=["jpg", "png", "jpeg", "webp"])
    
    image_to_send = None
    if uploaded_file is not None:
        # Открываем и показываем картинку
        image_to_send = Image.open(uploaded_file)
        st.image(image_to_send, caption="Готово к отправке", use_container_width=True)
        st.success("Фото прикреплено! Теперь пиши запрос в чат.")

    st.divider()
    
    # 4. УПРАВЛЕНИЕ
    if st.button("🗑️ Стереть историю"):
        global_history.clear()
        st.rerun()

# --- КОНФИГУРАЦИЯ ---
genai.configure(api_key=API_KEY)

# --- ИНТЕРФЕЙС ЧАТА ---
st.title(f"👁️ Чат ({selected_model})")

if "messages" not in st.session_state:
    st.session_state.messages = global_history

# Отрисовка истории
for message in global_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ОБРАБОТКА ЗАПРОСА ---
if prompt := st.chat_input("Напиши вопрос по картинке..."):
    
    # 1. Показываем вопрос пользователя
    # Если есть картинка, добавляем пометку в текст истории
    user_text_display = prompt
    if image_to_send:
        user_text_display = f"🖼️ [Отправлено фото] {prompt}"

    global_history.append({"role": "user", "content": user_text_display})
    
    with st.chat_message("user"):
        st.markdown(user_text_display)
        # Если картинка есть сейчас, покажем её в чате тоже
        if image_to_send:
            st.image(image_to_send, width=300)

    # 2. Генерируем ответ
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            model = genai.GenerativeModel(selected_model)
            
            # Формируем запрос: Текст + Картинка (если есть) или просто Текст
            if image_to_send:
                request_content = [prompt, image_to_send]
            else:
                request_content = prompt

            # Стриминг ответа
            response = model.generate_content(request_content, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01)
            
            message_placeholder.markdown(full_response)
            global_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Ошибка: {e}")
