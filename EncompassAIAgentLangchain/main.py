from typing import Annotated
from typing_extensions import TypedDict

import dotenv
import os
import asyncio
from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain.chat_models import init_chat_model

from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages

from encompass_devconnect_agent import EncompassDevConnectAgent

#from langchain_tavily import TavilySearch

load_dotenv()

# class State(TypedDict):
#     # Messages have the type "list". The `add_messages` function
#     # in the annotation defines how this state key should be updated
#     # (in this case, it appends messages to the list, rather than overwriting them)
#     messages:Annotated[list,add_messages]

# llm=ChatOpenAI(model=os.getenv('OPENAI_LLM_MODEL'), api_key=os.getenv('OPENAI_API_KEY'))

# ## Node Functionality
# def chatbot(state:State):
#     return {"messages":[llm.invoke(state["messages"])]}

# graph_builder=StateGraph(State)

# ## Adding node
# graph_builder.add_node("llmchatbot",chatbot)
# ## Adding Edges
# graph_builder.add_edge(START,"llmchatbot")
# graph_builder.add_edge("llmchatbot",END)

# ## compile the graph
# graph=graph_builder.compile()

# #tavily=TavilySearch(max_results=2)
# #tavily.invoke("What is langgraph")

# ## Custom function
# def multiply(a:int,b:int)->int:
#     """Multiply a and b

#     Args:
#         a (int): first int
#         b (int): second int

#     Returns:
#         int: output int
#     """
#     return a*b

# def main():
#     tools=[multiply]
#     llm_with_tools=llm.bind_tools(tools)

#     response=graph.invoke({"messages":"Hi"})
#     print(response["messages"][-1].content)

#     for event in graph.stream({"messages":"Hi How are you?"}):
#         for value in event.values():
#             print(value["messages"][-1].content)

async def main():
    agent = EncompassDevConnectAgent()
    response = await agent.arun("fetch top ten FHA loans")
    print(response["messages"][-1].content)
    # for event in agent.arun("Hi How are you?"):
    #     for value in event.values():
    #         print(value["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
