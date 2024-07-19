from typing import *

import chainlit as cl
from agent import SayvaiDemoAgent
from chainlit.sync import run_sync
from langchain.llms.openai import OpenAI
from langchain.tools import BaseTool


@cl.on_chat_start
def start():
    agentdemo = SayvaiDemoAgent()
    agentdemo.initialize_tools()
    agentdemo.initialize_agent_executor()

    cl.user_session.set("agent", agentdemo)


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")  # type: AgentExecutor
    res = agent.invoke(message.content)
    await cl.Message(content=res).send()
