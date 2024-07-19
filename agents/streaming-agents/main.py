# Description: This is a streaming agent for Langchain. It uses websockets to stream the output of the agent to the client.

import asyncio
from typing import AsyncIterable

import websockets
from csv_agent import SayvaiCRMToolkitAgent
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from gmail_agent import SayvaiGmailAgent
from langchain.callbacks import AsyncIteratorCallbackHandler
from pydantic import BaseModel

app = FastAPI(
    title="Langchain Streaming Agent",
    description="A streaming agent for Langchain",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    message: str


agent = SayvaiGmailAgent()
agent.initialize_tools()
agent_ex = agent.initialize_agent_executor()


@app.get('/query-stream/')
async def stream(query: str):
    print(f'Query receieved: {query}')
    return StreamingResponse(agent.response_generator(query), media_type='text/event-stream')

# -------------------------------------web socket implementation---------------------------------------------#
# --------------------------------------------------------------------------------------------------------#
# Websockets set
ws_connections = set()


async def invoke(message: str, websocket: WebSocket) -> None:
    ws_connections.add(websocket)
    try:
        # response = agent.invoke(message)
        # print("response", response)
        # for words in response.split(" "):
        #     await websocket.send_text(words)
        # agent has streaming=True, so we can use the async generator
        for response in list(agent_ex.invoke(input={"input": message})["output"].split(" ")):
            print("response", response)
            await websocket.send_text(response)
            await asyncio.sleep(0.1)  # Adjust sleep time as needed
    finally:
        ws_connections.remove(websocket)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await invoke(data, websocket)
    except websockets.exceptions.ConnectionClosedOK:
        pass


@app.post("/invoke")
async def invoke_endpoint(item: Item):
    return {"message": item.message}

# --------------------------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------------------------------------#
