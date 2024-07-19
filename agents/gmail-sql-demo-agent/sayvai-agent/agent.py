"""GmailToolkit Template"""
# langchain agent main'
from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain.memory import ConversationTokenBufferMemory
from langchain_community.agent_toolkits import GmailToolkit, SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
# langchain agent main'
from sayvai_tools.tools import GetDate

# Create a new LangChain instance
# llm = ChatOpenAI(base_url="https://api.groq.com/openai/v1",
#                  api_key="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",
#                  model="mixtral-8x7b-32768",
#                  streaming=False)
llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")


db = SQLDatabase.from_uri("sqlite:///sayvai-agent/my_db4.db")
toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(temperature=0))
context = toolkit.get_context()

_SYSTEM_PROMPT: str = (
    """You are an assistant for SayvAI Software LLP, expected to act in response to user queries and tasks. 
    Here are the tools at your disposal:
Rules:

- Utilize the GetDate tool to compute past or future dates and times.
- If the user requests for tomorrow's mail/messages, inform them it's not feasible.
For Gmail-related tasks, employ the appropriate tools to fulfill the requirements.
- The assistant may either address questions concerning Sayvai or utilize the tools to execute actions based on 
human input.
- if user wants to send an email, the assistant should send it using GmailSendMessage.


    """
)

# Your role is an assistant for SayvAI Software LLP. You are asked to perform based on the user's request. You MUST ensure that your answer is unbiased and avoids relying on stereotypes. You can use the following tools to perform the actions: GmailCreateDraft, GmailSendMessage, GmailSearch, GmailGetMessage, GmailGetThread, GetDate. Your task is to use these tools to perform actions as per the user's requirements. You MUST use the same language based on the user's request. Remember to avoid negative language like 'don't'. Agent, Answer a question given in a natural, human-like manner. You will be penalized if you don't. You MUST guide step-by-step thinking. You MUST use output primers. You MUST clearly state the requirements that the model must follow in order to produce content, in the form of keywords, regulations, hints, or instructions. You MUST use leading words like writing 'think step by step'. To inquire about a specific topic or idea and test your understanding, you can use the following phrase: 'Teach me any [theorem/topic/rule name] and include a test at the end, and let me know if my answers are correct after I respond, without providing the answers beforehand.' Your task is to perform actions related to Gmail. Your task is to utilize the tools to perform actions based on human input. Your task is to initiate or continue a text using specific words, phrases, or sentences. I'm providing you with the beginning Gmail tools: <Tools> 1) GmailCreateDraft - Create a draft email 2) GmailSendMessage - Send a message 3) GmailSearch - Search for emails 4) GmailGetMessage - Get a message 5) GmailGetThread - Get a thread 5) GetDate - Get current date and time (returns only current date and time, utilize current date and time to calculate future or past date and time) </Tools> Use the tools to perform actions based on human input. Remember to do actions as per the requirements. Follow the rules to get previous dates and future dates. Use the GetDate tool and calculate the date and time. Remember to use the same language based on the user's request. If the user asks to perform tasks that are related to Gmail, use the tools and do actions as per the requirements. If the user asks for tomorrow's mail/messages, respond with 'It's not possible.'

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        ("human", "{agent_memory} {input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

prompt = prompt.partial(**context)


class SayvaiDemoAgent:

    def __init__(self):
        self.llm = llm
        self.prompt = prompt
        self.tools = None
        self.gmailkit = GmailToolkit()
        self.memory = ConversationTokenBufferMemory(
            llm=self.llm,
            memory_key="agent_memory"
        )

    def _add_sql_tools(self):
        for sql_tool in toolkit.get_tools():
            self.tools.append(
                sql_tool
            )

    def initialize_tools(self) -> str:
        self.tools = self.gmailkit.get_tools()
        self._add_sql_tools()
        self.tools.append(
            Tool(
                func=GetDate()._run,
                name="GetDateTool",
                description="""A tool that takes no input and returns the current date and time."""
            ),

        )
        return "Tools Initialized"

    def initialize_agent_executor(self) -> AgentExecutor:
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            prompt=self.prompt,
            tools=self.tools,
        )
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory
        )
        return "Agent Executor Initialized"

    def invoke(self, message) -> str:
        return self.agent_executor.invoke(input={"input": message})


agent = SayvaiDemoAgent()
agent.initialize_tools()
agent.initialize_agent_executor()
while True:
    agent.invoke(input("Enter your message here=> "))
