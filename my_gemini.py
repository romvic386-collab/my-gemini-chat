import streamlit as st
import google.generativeai as genai
import time

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Gemini Hub", page_icon="🛡️", layout="centered")

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("🎛️ Настройки")
    
    # 1. ВЫБОР КЛЮЧА (Мульти-ключ)
    # Мы ищем в секретах все переменные, которые начинаются на KEY_
    available_keys = [k for k in st.secrets.keys() if k.startswith("KEY_")]
    
    if available_keys:
        selected_key_name = st.selectbox(
            "🔑 Выбери ключ API:",
            options=available_keys,
            format_func=lambda x: f"Ключ #{x.split('_')[1]} ({x})" # Красивое название
        )
        API_KEY = st.secrets[selected_key_name]
    else:
        st.error("Нет ключей! Добавь KEY_1, KEY_2 в Secrets.")
        st.stop()

    st.divider()

    # 2. ВЫБОР МОДЕЛИ
    selected_model = st.radio(
        "🧠 Модель:",
        options=["gemini-2.5-pro", "gemini-2.5-flash", "gemini-3-pro-preview"], 
        index=1 # По умолчанию Flash (быстрая)
    )
    
    st.divider()
    
    # 3. УПРАВЛЕНИЕ ИСТОРИЕЙ
    if st.button("🗑️ Стереть всё"):
        st.session_state.messages = []
        st.rerun()

    # Кнопка скачивания истории
    chat_history_text = ""
    if "messages" in st.session_state:
        for msg in st.session_state.messages:
            chat_history_text += f"{msg['role'].upper()}: {msg['content']}\n\n"
            
    st.download_button(
        label="💾 Скачать диалог (.txt)",
        data=chat_history_text,
        file_name="gemini_chat_history.txt",
        mime="text/plain"
    )

# --- НАСТРОЙКА API ---
genai.configure(api_key=API_KEY)

# --- ОСНОВНОЙ ЧАТ ---
st.title(f"💬 Чат ({selected_model})")

# Инициализация (если пусто)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Показываем сообщения
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Напиши запрос..."):
    # Добавляем вопрос пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Генерируем ответ
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            model = genai.GenerativeModel(selected_model)
            response = model.generate_content(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                    # Небольшая задержка для плавности (можно убрать)
                    time.sleep(0.01) 
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Ошибка: {e}")
            st.warning("💡 Совет: Если лимит исчерпан (429), просто выбери другой Ключ в меню слева!")
