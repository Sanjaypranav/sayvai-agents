"""GmailToolkit Template"""
import pandas as pd
from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_experimental.agents.agent_toolkits import \
    create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
# langchain agent main'
from sayvai_tools.tools.google_sheets.append_data import AppendDataTool
from sayvai_tools.tools.google_sheets.create_spreadsheet import \
    CreateSpreadsheetTool
from sayvai_tools.tools.google_sheets.get_cell_values import GetCellValuesTool
from sayvai_tools.tools.google_sheets.update_spreadsheet import \
    UpdateSpreadsheetTool
from sayvai_tools.tools.google_sheets.utils import get_sheets_credentials

# Create a new LangChain instance
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

df = pd.read_csv(
    "data/AAPL.csv",
)

db = SQLDatabase.from_uri("sqlite:///sayvai.db")
toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(temperature=0))
context = toolkit.get_context()
# print(context)
tools = toolkit.get_tools()
prefix = """I am an assistant for SayvAI Software LLP, tasked with managing
Google Sheets using the following tools:
"""
for key, value in context.items():
    prefix += f"{key}: {value}\n"

agent_as_tool = create_pandas_dataframe_agent(
    llm=llm,
    df=df,
    prefix=prefix,
    extra_tools=tools,
    verbose=True,
)

while True:
    human_input = input("Human: ")
    print(agent_as_tool.run(human_input))
