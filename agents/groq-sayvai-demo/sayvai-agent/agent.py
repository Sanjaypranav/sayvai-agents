# Groq agent
from langchain.agents import AgentExecutor, tool
from langchain.agents.format_scratchpad.openai_tools import \
    format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import \
    OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq


@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)


tools = [get_word_length]

chat = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")
llm_with_tools = chat.bind_tools(tools)

# system = """You are talking to Gabby, a personal assistant who was trained to
# answer any questions you might have about Puretalk.ai and Meca Technologies LLC.
# Gabby reads a lot and knows a lot about the latest technology in the market such
# as Artificial intelligence, Machine Learning, Algorithms, Conversational AI,
# voice cloning, SDK and more. Gabby has been working for Puretalk.ai and Meca
# Technologies for 3 years now and knows everything about the company.
# Gabby can help you schedule an appointment to talk to a Puretalk.ai
# representative, appointments can be scheduled for the next day only or 24 hours
# from the time you made the appointment. Puretalk.ai representatives are
# available Monday through Friday, from 8:00 AM to 5:00 PM EST.  Gabby can tell
# you about all the products that puretalk.ai has, such as Puretalk Voice cloning"""
# human = "{text}"
# prompt = ChatPromptTemplate.from_messages(
#     [("system", system), ("human", human)])

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are very powerful assistant, but don't know current events",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)


agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
print((agent_executor.invoke(
    {"input": "How many letters in the word eudca"})))
