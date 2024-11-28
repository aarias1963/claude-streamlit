import streamlit as st
import anthropic
import time
from typing import List

class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class ChatApp:
    def __init__(self, api_key: str):
        # Inicializar el cliente de Anthropic con la API key proporcionada
        self.client = anthropic.Client(api_key=api_key)
        
    def generate_response(self, messages: List[ChatMessage]) -> str:
        try:
            # Convertir mensajes al formato esperado por la API
            formatted_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Crear el mensaje con Claude
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=formatted_messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error al generar respuesta: {str(e)}"

def main():
    st.set_page_config(page_title="Chat con Claude 3.5 Sonnet", page_icon="🤖")
    
    # Configuración de la barra lateral
    st.sidebar.title("⚙️ Configuración")
    api_key = st.sidebar.text_input("API Key de Anthropic", type="password")
    
    # Inicialización de estados
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Validación de API Key
    if not api_key:
        st.sidebar.warning("Por favor, introduce tu API Key de Anthropic para comenzar.")
        st.info("👈 Introduce tu API Key en la barra lateral para comenzar a chatear con Claude.")
        return
    
    # Inicializar la aplicación solo si hay API key
    if "chat_app" not in st.session_state or st.session_state.current_api_key != api_key:
        st.session_state.chat_app = ChatApp(api_key)
        st.session_state.current_api_key = api_key

    # Título y descripción
    st.title("💬 Chat con Claude 3.5 Sonnet")
    st.markdown("""
    Esta aplicación te permite chatear con Claude 3.5 Sonnet usando la API de Anthropic.
    """)

    # Botón para limpiar la conversación en la barra lateral
    if st.sidebar.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()  # Usando st.rerun() en lugar de experimental_rerun()

    # Mostrar mensajes existentes
    for msg in st.session_state.messages:
        with st.chat_message(msg.role):
            st.write(msg.content)

    # Campo de entrada del usuario
    if prompt := st.chat_input("Escribe tu mensaje aquí...", key="user_input"):
        # Agregar mensaje del usuario
        user_message = ChatMessage("user", prompt)
        st.session_state.messages.append(user_message)
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.write(prompt)

        # Generar y mostrar respuesta
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            response = st.session_state.chat_app.generate_response(st.session_state.messages)
            message_placeholder.write(response)
        
        # Guardar respuesta del asistente
        assistant_message = ChatMessage("assistant", response)
        st.session_state.messages.append(assistant_message)

if __name__ == "__main__":
    main()
