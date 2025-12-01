import streamlit as st
import google.generativeai as genai

# --- ВСТАВЬ СВОЙ КЛЮЧ СЮДА ---
API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=API_KEY)

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="My Gemini Hub", page_icon="🎛️")

# --- БОКОВАЯ ПАНЕЛЬ (ВЫБОР МОДЕЛИ) ---
with st.sidebar:
    st.title("⚙️ Настройки")
    
    # Создаем выпадающий список
    selected_model = st.radio(
        "Выберите модель:",
        options=["gemini-2.5-pro", "gemini-2.5-flash"], # Твои модели из скринов
        captions=["Умная и мощная (Reasoning)", "Быстрая и легкая"], # Подписи
        index=0 # По умолчанию выбрана первая
    )
    
    st.divider()
    st.info(f"Активна: **{selected_model}**")
    
    # Кнопка очистки чата (для удобства)
    if st.button("🗑️ Очистить историю"):
        st.session_state.messages = []
        st.rerun()

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
st.title(f"💬 Чат с {selected_model}")

# Инициализация истории
if "messages" not in st.session_state:
    st.session_state.messages = []

# Показываем переписку
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Напиши запрос..."):
    # 1. Показываем вопрос юзера
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Генерируем ответ выбранной моделью
    try:
        # Тут мы подставляем переменную selected_model, которую выбрали в меню
        model = genai.GenerativeModel(selected_model)
        
        with st.chat_message("assistant"):
            # Создаем пустой контейнер для эффекта "печатания" (стриминг)
            message_placeholder = st.empty()
            full_response = ""
            
            # Включаем потоковую передачу (чтобы текст появлялся постепенно)
            response = model.generate_content(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"Ошибка API ({selected_model}): {e}")