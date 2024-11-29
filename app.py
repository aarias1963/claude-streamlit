import streamlit as st
import anthropic
import time
from typing import List
import PyPDF2
import io
import pandas as pd
import re

class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class ChatApp:
    def __init__(self, api_key: str):
        self.client = anthropic.Client(api_key=api_key)
        
    def generate_response(self, messages: List[ChatMessage], pdf_content: str = "") -> str:
        try:
            if pdf_content:
                context_message = ChatMessage(
                    "user", 
                    f"Contexto del PDF:\n\n{pdf_content}\n\nPor favor, ten en cuenta este contexto para responder a mis siguientes preguntas."
                )
                messages = [context_message] + messages
            
            formatted_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
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

def detect_and_convert_csv(text):
    # Buscar contenido que parezca CSV (líneas con comas o tabulaciones)
    lines = text.split('\n')
    csv_blocks = []
    current_block = []
    in_csv_block = False
    
    for line in lines:
        # Detectar si la línea parece ser CSV (contiene comas o tabs y tiene estructura consistente)
        is_csv_line = (',' in line or '\t' in line) and len(line.strip()) > 0
        
        if is_csv_line:
            if not in_csv_block:
                in_csv_block = True
            current_block.append(line)
        else:
            if in_csv_block:
                if len(current_block) > 1:  # Al menos cabecera y una fila
                    csv_blocks.append(current_block)
                current_block = []
                in_csv_block = False
            st.write(line)
    
    # No olvidar el último bloque si termina el texto con CSV
    if in_csv_block and len(current_block) > 1:
        csv_blocks.append(current_block)
    
    # Procesar cada bloque CSV encontrado
    for block in csv_blocks:
        try:
            # Convertir el bloque a DataFrame
            df = pd.read_csv(io.StringIO('\n'.join(block)))
            
            # Mostrar el DataFrame con Streamlit
            st.dataframe(df)
            
            # Añadir botón de descarga
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv_data,
                file_name="datos.csv",
                mime="text/csv"
            )
            
            # Añadir botón de descarga Excel
            excel_data = io.BytesIO()
            df.to_excel(excel_data, index=False, engine='openpyxl')
            excel_data.seek(0)
            st.download_button(
                label="📥 Descargar Excel",
                data=excel_data,
                file_name="datos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Error al procesar datos tabulares: {str(e)}")
            st.text('\n'.join(block))

def main():
    st.set_page_config(page_title="Chat con Claude 3.5 Sonnet", page_icon="🤖")
    
    st.sidebar.title("⚙️ Configuración")
    api_key = st.sidebar.text_input("API Key de Anthropic", type="password")
    
    st.sidebar.markdown("### 📄 Cargar PDF")
    pdf_file = st.sidebar.file_uploader("Sube un archivo PDF", type=['pdf'])
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pdf_content" not in st.session_state:
        st.session_state.pdf_content = ""
    
    if pdf_file:
        if "last_pdf" not in st.session_state or st.session_state.last_pdf != pdf_file.name:
            with st.spinner("Procesando PDF..."):
                st.session_state.pdf_content = extract_text_from_pdf(pdf_file)
                st.session_state.last_pdf = pdf_file.name
                st.sidebar.success(f"PDF cargado: {pdf_file.name}")
    
    if not api_key:
        st.sidebar.warning("Por favor, introduce tu API Key de Anthropic para comenzar.")
        st.info("👈 Introduce tu API Key en la barra lateral para comenzar a chatear con Claude.")
        return
    
    if "chat_app" not in st.session_state or st.session_state.current_api_key != api_key:
        st.session_state.chat_app = ChatApp(api_key)
        st.session_state.current_api_key = api_key

    st.title("💬 Chat con Claude 3.5 Sonnet")
    st.markdown("""
    Esta aplicación te permite chatear con Claude 3.5 Sonnet usando la API de Anthropic.
    Si cargas un PDF, Claude podrá responder preguntas sobre su contenido.
    """)

    if st.session_state.pdf_content:
        st.info(f"📄 PDF cargado y listo para consultas")

    if st.sidebar.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg.role):
            if msg.role == "assistant":
                detect_and_convert_csv(msg.content)
            else:
                st.write(msg.content)

    if prompt := st.chat_input("Escribe tu mensaje aquí...", key="user_input"):
        user_message = ChatMessage("user", prompt)
        st.session_state.messages.append(user_message)
        
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Generando respuesta..."):
                response = st.session_state.chat_app.generate_response(
                    st.session_state.messages,
                    st.session_state.pdf_content
                )
            detect_and_convert_csv(response)
        
        assistant_message = ChatMessage("assistant", response)
        st.session_state.messages.append(assistant_message)

if __name__ == "__main__":
    main()
