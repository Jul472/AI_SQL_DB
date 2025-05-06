import streamlit as st
import pandas as pd
import backend

db_class = backend.db_handler()

uploaded_file = st.file_uploader("Carga un archivo CSV", type="csv", key="uploader_key")

delimiter = st.radio(
    "Delimitador", [",", ";"], horizontal=True
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding='latin-1')
        st.dataframe(df.head())
        #Database creation
        db_class.df_to_db(df)
    except pd.errors.ParserError as e:
        st.error(f'Verifica el delimitador: {e}')

#Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#Display chat history on app re-run
for message in st.session_state.messages:
    msg = st.chat_message(message["role"])
    msg.write(message["content"])

#React to user input
if prompt := st.chat_input("Consulta"):
    #Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    #Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    #Get response
    response = db_class.query_db(prompt)
    #Written Query Response 
    st.chat_message("assistant").write(response["query"])
    #Query Output
    st.chat_message("assistant").dataframe(response["result"])
    #Close Connection
    db_class.close()
    #Add messages to history chat
    st.session_state.messages.append({"role": "assistant", "content": response})
