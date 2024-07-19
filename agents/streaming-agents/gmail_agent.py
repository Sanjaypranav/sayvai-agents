# Gmail agent
import asyncio

import websockets
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

"""GmailToolkit Template"""
from queue import Queue
from threading import Thread

from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.agent_toolkits import GmailToolkit
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
# langchain agent main'
from sayvai_tools.tools import GetDate

from handler import MyCustomHandler

streamer_queue = Queue()
handler = MyCustomHandler(streamer_queue)


# Create a new LangChain instance
llm = ChatOpenAI(model="gpt-3.5-turbo-0125",
                 streaming=True,
                 callbacks=[handler],)

# instructions = """You are an assistant who used to help to perform all action related to Gmail."""
# base_prompt = hub.pull("langchain-ai/openai-functions-template")
# print(base_prompt)
# prompt = base_prompt.partial(instructions=instructions)

_SYSTEM_PROMPT: str = (
    """You are an assistant for SayvAI Software LLP. You are asked to perform based on the user's request.
    You can use following tools to perform the actions:

    <Tools>
    1) GmailCreateDraft - Create a draft email
    2) GmailSendMessage - Send a message
    3) GmailSearch - Search for emails
    4) GmailGetMessage - Get a message 
    5) GmailGetThread - Get a thread
    5) GetDate - Get current date and time (returns only current date and time, utilise current date and time to calculate future or past date and time)
    </Tools>

    Rules:-
    1) To get previous dates and future dates use GetDate tool and calculate the date and time. 
    2) IF user asks about get me tommorow's mail /messages (respond with it is not possible )
    3) if the user asks to do tasks that are related to Gmail,Use the tools and do actions as per reuirements
    4) Agent can aither talk about questions related to Sayvai or utilize the tools to perform actions based on human input 


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


class SayvaiGmailAgent:

    def __init__(self):
        self.llm = llm
        self.prompt = prompt
        self.tools = None
        self.gmailkit = GmailToolkit()
        self.memory = ConversationBufferWindowMemory(
            memory_key="agent_memory",
            window_size=10,
        )

    def initialize_tools(self) -> str:
        self.tools = self.gmailkit.get_tools()
        self.tools.append(
            Tool(
                func=GetDate()._run,
                name="GetDateTool",
                description="""A tool that takes no input and returns the current date and time."""
            ),

        )
        return "Tools Initialized"

    def initialize_agent_executor(self, verbose: bool = False) -> AgentExecutor:
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            prompt=self.prompt,
            tools=self.tools,
        )
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=verbose,
            memory=self.memory
        )
        return self.agent_executor

    def invoke(self, message) -> str:
        return self.agent_executor.invoke(input={"input": message})["output"]

    def generate(self, query):
        self.agent_executor.invoke(input={"input": query})["output"]

    def start_generation(self, query):
        # Creating a thread with generate function as a target
        thread = Thread(target=self.generate, kwargs={"query": query})
        # Starting the thread
        thread.start()

    async def response_generator(self, query):
        # Start the generation process
        self.start_generation(query)

        # Starting an infinite loop
        while True:
            # Obtain the value from the streamer queue
            value = streamer_queue.get()
            # Check for the stop signal, which is None in our case
            if value == None:
                # If stop signal is found break the loop
                break
            # Else yield the value
            yield value
            # statement to signal the queue that task is done
            streamer_queue.task_done()

            # guard to make sure we are not extracting anything from
            # empty queue
            await asyncio.sleep(0.1)
