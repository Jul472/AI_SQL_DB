import pandas as pd
import sqlite3
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

db = None

class db_handler:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.cur = self.conn.cursor()

    def df_to_db(self, dataframe):
        global db
        # dataframe.to_sql("data", conn, if_exists="replace", index=False)
        dataframe.to_sql("data", self.conn, if_exists="replace", index=False)
        # db = SQLDatabase(engine=conn)

    def query_db(self, user_input):
        self.cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='data'")
        table_info = self.cur.fetchall()
        response = chain.invoke({
            "table_info": table_info,
            "input": user_input
        })
        result = pd.read_sql_query(response.content, self.conn)

        return {"query":response.content, "result": result}

    def close(self):
        self.conn.close()

#Create Model
model = ChatGoogleGenerativeAI(
    google_api_key=GOOGLE_API_KEY,
    model="gemini-2.0-flash",
    temperature=0
)

#Chat prompt template
system_template = """
1. Dada una pregunta escribe la query en sqlite3 para responder dicha pregunta correctamente. 
2. Escribe la query sin agregar palabras o caracteres adicionales/especiales como, ```, #, *, etc.  
3. Pon atención a solo usar las columnas que ves en la descripción del schema. 
4. No escribas la query para columnas que no existen.
5. Solo usa las siguientes tablas: {table_info}
6. A menos que el usuario te pida un número especifico de registros que quiere obtener, siempre muestra tu query con todos los resultados.
"""

human_template = "{input}"

prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("human", human_template)
])

chain = prompt | model