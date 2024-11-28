import streamlit as st
import anthropic
import time
from typing import List
import PyPDF2
import io

class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class ChatApp:
    def __init__(self, api_key: str):
        self.client = anthropic.Client(api_key=api_key)
        
    def generate_response(self, messages: List[ChatMessage], pdf_content: str = "") -> str:
        try:
            # Si hay contenido del PDF, añadirlo al contexto
            if pdf_content:
                context_message = ChatMessage(
                    "user", 
                    f"Contexto del PDF:\n\n{pdf_content}\n\nPor favor, ten en cuenta este contexto para responder a mis siguientes preguntas."
                )
                messages = [context_message] + messages
            
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

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error al procesar el PDF: {str(e)}"

def main():
    st.set_page_config(page_title="Chat con Claude 3.5 Sonnet", page_icon="🤖")
    
    # Configuración de la barra lateral
    st.sidebar.title("⚙️ Configuración")
    api_key = st.sidebar.text_input("API Key de Anthropic", type="password")
    
    # Subida de PDF
    st.sidebar.markdown("### 📄 Cargar PDF")
    pdf_file = st.sidebar.file_uploader("Sube un archivo PDF", type=['pdf'])
    
    # Inicialización de estados
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pdf_content" not in st.session_state:
        st.session_state.pdf_content = ""
    
    # Procesar PDF cuando se sube
    if pdf_file:
        if "last_pdf" not in st.session_state or st.session_state.last_pdf != pdf_file.name:
            with st.spinner("Procesando PDF..."):
                st.session_state.pdf_content = extract_text_from_pdf(pdf_file)
                st.session_state.last_pdf = pdf_file.name
                st.sidebar.success(f"PDF cargado: {pdf_file.name}")
    
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
    Si cargas un PDF, Claude podrá responder preguntas sobre su contenido.
    """)

    # Mostrar estado del PDF
    if st.session_state.pdf_content:
        st.info(f"📄 PDF cargado y listo para consultas")

    # Botón para limpiar la conversación en la barra lateral
    if st.sidebar.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()

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
            with st.spinner("Generando respuesta..."):
                response = st.session_state.chat_app.generate_response(
                    st.session_state.messages,
                    st.session_state.pdf_content
                )
            message_placeholder.write(response)
        
        # Guardar respuesta del asistente
        assistant_message = ChatMessage("assistant", response)
        st.session_state.messages.append(assistant_message)

if __name__ == "__main__":
    main()
