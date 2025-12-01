import streamlit as st
import google.generativeai as genai
import time

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Gemini Hub", page_icon="🛡️", layout="centered")

# --- ГЛОБАЛЬНАЯ ПАМЯТЬ (Сохраняет историю при F5) ---
@st.cache_resource
def get_global_history():
    return [] # Создаем список один раз при запуске сервера

# Получаем доступ к "вечному" списку
global_history = get_global_history()

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("🎛️ Настройки")
    
    # 1. ВЫБОР КЛЮЧА
    available_keys = [k for k in st.secrets.keys() if k.startswith("KEY_")]
    if available_keys:
        selected_key_name = st.selectbox(
            "🔑 Выбери ключ API:",
            options=available_keys,
            format_func=lambda x: f"Ключ #{x.split('_')[1]}"
        )
        API_KEY = st.secrets[selected_key_name]
    else:
        st.error("Добавь ключи (KEY_1, KEY_2...) в Secrets!")
        st.stop()

    st.divider()

    # 2. ВЫБОР МОДЕЛИ
    selected_model = st.radio(
        "🧠 Модель:",
        options=["gemini-2.5-pro", "gemini-2.5-flash", "gemini-3-pro-preview"], 
        index=1
    )
    
    st.divider()
    
    # 3. УПРАВЛЕНИЕ ИСТОРИЕЙ
    if st.button("🗑️ Стереть историю (У всех)"):
        global_history.clear() # Очищаем глобальный список
        st.rerun()

    # Скачивание
    chat_history_text = ""
    for msg in global_history:
        chat_history_text += f"{msg['role'].upper()}: {msg['content']}\n\n"
            
    st.download_button(
        label="💾 Скачать диалог (.txt)",
        data=chat_history_text,
        file_name="gemini_history.txt",
        mime="text/plain"
    )

# --- НАСТРОЙКА API ---
genai.configure(api_key=API_KEY)

# --- ОСНОВНОЙ ЧАТ ---
st.title(f"💬 Чат ({selected_model})")

# Привязываем сессию к глобальной истории
# Теперь st.session_state.messages — это ссылка на global_history
if "messages" not in st.session_state:
    st.session_state.messages = global_history

# Показываем сообщения (берем их из глобальной памяти)
for message in global_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Напиши запрос..."):
    # Добавляем в ГЛОБАЛЬНЫЙ список
    global_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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
                    time.sleep(0.01)
            
            message_placeholder.markdown(full_response)
            # Сохраняем ответ тоже в ГЛОБАЛЬНЫЙ список
            global_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Ошибка: {e}")
