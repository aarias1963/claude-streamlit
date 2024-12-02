import streamlit as st
import anthropic
import pandas as pd
import PyPDF2
import io

class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

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
    st.set_page_config(
        page_title="Chat con Claude",
        page_icon="🤖",
        layout="wide"
    )

    # Sidebar
    st.sidebar.title("⚙️ Configuración")
    api_key = st.sidebar.text_input("API Key de Anthropic", type="password")

    # PDF uploader en sidebar
    st.sidebar.markdown("### 📄 Cargar PDF")
    pdf_file = st.sidebar.file_uploader("Sube un archivo PDF", type=['pdf'])

    # Botón de limpieza en sidebar
    st.sidebar.markdown("### 🗑️ Gestión del Chat")
    if st.sidebar.button("Limpiar Conversación", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pdf_content" not in st.session_state:
        st.session_state.pdf_content = ""

    # Main content
    st.title("💬 Chat con Claude 3.5 Sonnet")
    st.markdown("""
    Esta aplicación te permite chatear con Claude 3.5 Sonnet usando la API de Anthropic.
    Si cargas un PDF, Claude realizará búsquedas exhaustivas en su contenido.
    """)

    # Check for API key
    if not api_key:
        st.warning("👈 Introduce tu API Key en la barra lateral para comenzar.")
        return

    try:
        # Initialize Anthropic client
        client = anthropic.Client(api_key=api_key)
        
        # Process PDF if uploaded
        if pdf_file:
            if "last_pdf" not in st.session_state or st.session_state.last_pdf != pdf_file.name:
                with st.spinner("Procesando PDF..."):
                    st.session_state.pdf_content = extract_text_from_pdf(pdf_file)
                    st.session_state.last_pdf = pdf_file.name
                st.sidebar.success(f"PDF cargado: {pdf_file.name}")

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message.role):
                st.write(message.content)

        # Chat input
        if prompt := st.chat_input("Escribe tu mensaje aquí..."):
            # Add user message
            st.session_state.messages.append(ChatMessage("user", prompt))
            with st.chat_message("user"):
                st.write(prompt)

            # Get and display assistant response
            with st.chat_message("assistant"):
                try:
                    # Create system message
                    messages = [{
                        "role": "system",
                        "content": """Eres un asistente especializado en análisis exhaustivo de documentos. Cuando se te pida buscar o analizar información:
                        1. Realiza una búsqueda EXHAUSTIVA y COMPLETA de TODAS las actividades, ejercicios o elementos que cumplan con los criterios especificados.
                        2. No omitas ningún resultado que cumpla con los criterios de búsqueda.
                        3. Organiza los resultados de forma clara, preferiblemente en formato tabular cuando sea apropiado.
                        4. Si encuentras múltiples elementos, debes listarlos TODOS, no solo algunos ejemplos.
                        5. Si la búsqueda inicial no es completa, realiza búsquedas adicionales hasta agotar todas las posibilidades.
                        6. Confirma explícitamente cuando hayas completado la búsqueda exhaustiva."""
                    }]

                    # Add PDF content if exists
                    if st.session_state.pdf_content:
                        messages.append({
                            "role": "user",
                            "content": f"Contexto del PDF:\n\n{st.session_state.pdf_content}"
                        })

                    # Add conversation history
                    for msg in st.session_state.messages:
                        messages.append({"role": msg.role, "content": msg.content})

                    # Get response from Claude
                    with st.spinner('Realizando búsqueda exhaustiva...'):
                        response = client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=4096,
                            messages=messages
                        )

                        assistant_response = response.content[0].text
                        st.write(assistant_response)
                        st.session_state.messages.append(ChatMessage("assistant", assistant_response))

                except Exception as e:
                    st.error(f"Error en la comunicación con Claude: {str(e)}")

    except Exception as e:
        st.error(f"Error de inicialización: {str(e)}")

if __name__ == "__main__":
    main()
