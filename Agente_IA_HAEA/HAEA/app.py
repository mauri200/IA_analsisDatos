import streamlit as st
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_groq import ChatGroq
import tabulate
from PIL import Image


import pip
pip.main(["install", "openpyxl"])

logo_url1 = './image1.jpeg'
st.sidebar.image(logo_url1)

logo_url2 = './image2.jpeg'
st.sidebar.image(logo_url2)

logo_url3 = './mauricio.jpeg'
st.sidebar.image(logo_url3)

def reiniciarChat():
    """Función que reinicia el chat cuando se cambia de archivo
    """    
    st.toast("File uploaded",icon='📄')
    # Inicializamos el historial de chat
    if "messages" in st.session_state:
        st.session_state.messages = []
        promtpSistema = " Eres un analista financiero experto y un analista de datos experto. Puedes hacer análisis y ofrecer recomendaciones, dando siempre respuestas claras y concretas, si te piden tablas o listas, las generas siempre en markdown"
        st.session_state.messages.append({"role": "system", "content": promtpSistema})

llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=st.secrets["GROQ_API"],
    
)

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Talk to the AI ​​agent about your data, ask it to perform analysis, and you can also give it recommendations", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

st.header('Hello, I am an Artificial Intelligence Agent, I am here to interact with your data, you can ask or ask me to perform some analysis and you can also ask me for recommendations! !')

# Menú lateral
with st.sidebar:
    st.subheader('Parámetros')
    archivo_cargado = st.file_uploader("Choose a file",type=['csv','xls','xlsx'],on_change =reiniciarChat)
    parUsarMemoria = st.checkbox("Remember the conversation",value=True)
    # Si existe un archivo cargado ejecutamos el código
    if archivo_cargado is not None:           
        # Se puede cargar con pandas si se tiene detectado el tipo de archivo
        if '.csv' in archivo_cargado.name:
            df = pd.read_csv(archivo_cargado)
        elif '.xls' in archivo_cargado.name:
            df = pd.read_excel(archivo_cargado, engine='openpyxl')
        # Creamos el agente con el dataframe
        agent = create_pandas_dataframe_agent(llm,df,allow_dangerous_code=True)    
# Inicializamos el historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    
   

# Muestra mensajes de chat desde la historia en la aplicación cada vez que la aplicación se ejecuta
with st.container():
    for message in st.session_state.messages:
        if message["role"]!="system": # Omitimos el prompt de sistem
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


# Mostramos el campo para el prompt del usuario
prompt=st.chat_input("What do you want to know?")


if prompt:
     # Mostrar mensaje de usuario en el contenedor de mensajes de chat
    st.chat_message("user").markdown(prompt)
    # Agregar mensaje de usuario al historial de chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Si requerimos usar la memoria entregamos siempre el historial de chat
    if parUsarMemoria:
        messages=[                
                    {
                        "role": m["role"],
                        "content": m["content"]
                    }
                    for m in st.session_state.messages
                ]
    else:
        # Si no se usa la memoria solo se entrega el prompt de sistema y la consulta del usuario
        messages=[                
                    {
                        "role": m["role"],
                        "content": m["content"]
                    }
                    for m in [st.session_state.messages[0],st.session_state.messages[-1]]
                ]    
    respuesta=agent.run(messages)
    
    # Mostrar respuesta del asistente en el contenedor de mensajes de chat
    with st.chat_message("assistant"):                        
        # Mostramos la respuesta
        st.write(respuesta)                                    
    # Agregar respuesta de asistente al historial de chat
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    