Una aplicación web construida con Streamlit que te permite chatear con Claude 3.5 Sonnet utilizando la API de Anthropic.

## ✨ Características

- 💬 Interfaz de chat interactiva
- 🔑 Configuración segura de API Key desde la interfaz
- 📝 Historial de conversaciones
- 🔄 Botón para limpiar la conversación
- ⚡ Respuestas en tiempo real
- 🛡️ Manejo de errores

## 🔑 Requisitos

- Una API Key de Anthropic (puedes obtenerla en [console.anthropic.com](https://console.anthropic.com))

## 🛠️ Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/chat-claude.git
cd chat-claude
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 💻 Uso Local

1. Ejecuta la aplicación:
```bash
streamlit run app.py
```

2. Abre tu navegador en `http://localhost:8501`
3. Introduce tu API Key de Anthropic en la barra lateral
4. ¡Comienza a chatear con Claude!

## 🌐 Despliegue en Streamlit Cloud

1. Sube el código a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. La aplicación estará disponible en línea y cada usuario podrá usar su propia API Key

## 🔒 Seguridad

- La API Key se introduce de forma segura usando un campo de contraseña
- La API Key no se almacena en el código ni en archivos de configuración
- Cada usuario debe proporcionar su propia API Key

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
