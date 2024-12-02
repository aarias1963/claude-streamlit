import streamlit as st
import anthropic
import time
from typing import List
import PyPDF2
import io
import pandas as pd
import re
import uuid

class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class ChatApp:
    def __init__(self, api_key: str):
        self.client = anthropic.Client(api_key=api_key)
        
    def generate_response(self, messages: List[ChatMessage], pdf_content: str = "") -> str:
        try:
            # Mensaje del sistema para búsqueda exhaustiva
            system_message = {
                "role": "system",
                "content": """Eres un asistente especializado en análisis exhaustivo de documentos. Cuando se te pida buscar o analizar información:
                1. Debes realizar una búsqueda EXHAUSTIVA y COMPLETA de TODAS las actividades, ejercicios o elementos que cumplan con los criterios especificados.
                2. No debes omitir ningún resultado que cumpla con los criterios de búsqueda.
                3. Organiza los resultados de forma clara, preferiblemente en formato tabular cuando sea apropiado.
                4. Si encuentras múltiples elementos, debes listarlos TODOS, no solo algunos ejemplos.
                5. Si la búsqueda inicial no es completa, debes realizar búsquedas adicionales hasta agotar todas las posibilidades.
                6. Confirma explícitamente cuando hayas completado la búsqueda exhaustiva.
                """
            }
            
            # Si hay contenido del PDF, añadirlo al contexto
            if pdf_content:
                context_message = ChatMessage(
                    "user", 
                    f"Contexto del PDF:\n\n{pdf_content}\n\nPor favor, realiza una búsqueda exhaustiva y completa en este contenido para responder a mis preguntas."
                )
                formatted_messages = [system_message] + [{"role": "user", "content": context_message.content}]
            else:
                formatted_messages = [system_message]
            
            # Añadir el resto de mensajes
            formatted_messages.extend([
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ])
            
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

def detect_and_convert_csv(text):
    lines = text.split('\n')
    csv_blocks = []
    current_block = []
    in_csv_block = False
    
    for line in lines:
        is_csv_line = (',' in line or '\t' in line) and len(line.strip()) > 0
        
        if is_csv_line:
            if not in_csv_block:
                in_csv_block = True
            current_block.append(line)
        else:
            if in_csv_block:
                if len(current_block) > 1:
                    csv_blocks.append(current_block)
                current_block = []
                in_csv_block = False
            st.write(line)
    
    if in_csv_block and len(current_block) > 1:
        csv_blocks.append(current_block)
    
    for i, block in enumerate(csv_blocks):
        try:
            block_id = str(uuid.uuid4())
            
            df = pd.read_csv(io.StringIO('\n'.join(block)))
            
            st.dataframe(df)
            
            col1, col2 = st.columns(2)
            
            csv_data = df.to_csv(index=False)
            with col1:
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv_data,
                    file_name=f"datos_{i}.csv",
                    mime="text/csv",
                    key=f"csv_{block_id}"
                )
            
            excel_data = io.BytesIO()
            df.to_excel(excel_data, index=False, engine='openpyxl')
            excel_data.seek(0)
            with col2:
                st.download_button(
                    label="📥 Descargar Excel",
                    data=excel_data,
                    file_name=f"datos_{i}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"excel_{block_id}"
                )
            
        except Exception as e:
            st.error(f"Error al procesar datos tabulares: {str(e)}")
            st.text('\n'.join(block))

def main():
    st.set_page_config(page_title="Chat con Claude 3.5 Sonnet", page_icon="🤖", layout="wide")
    
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
    Si cargas un PDF, Claude realizará búsquedas exhaustivas en su contenido.
    """)

    if st.session_state.pdf_content:
        st.info(f"📄 PDF cargado y listo para búsquedas exhaustivas")

    if st.sidebar.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.re
