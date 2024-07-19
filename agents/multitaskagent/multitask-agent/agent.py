# agent.py
# This file contains the agent class, which is the main class for the multitask-agent.
from langchain.agents import AgentType
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.agents.agent_toolkits import \
    create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

db = SQLDatabase.from_uri("sqlite:///Chinook.db")

toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(temperature=0))
context = toolkit.get_context()
tools = toolkit.get_tools()
prompt = toolkit.get_context()
table_info = prompt["table_info"]
table_names = prompt["table_names"]
prompt = f"tables available {table_names}, table info {table_info}"

prefix_ = """You are a Sayvai CRM assistant and You have assigned to do tasks 
you can use tools to perform tasks and \n""" + prompt

llm = ChatOpenAI()

agents = create_pandas_dataframe_agent(
    df=df,
    llm=llm,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    prefix=prefix_,
    extra_tools=tools,
)

while True:
    human_input = input("You: ")
    agents.invoke(input=human_input)
