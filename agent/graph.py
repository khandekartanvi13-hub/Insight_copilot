
import os
from typing import TypedDict, Annotated

from langchain_groq import ChatGroq
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AnyMessage
)
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from agent.tools import (
    sales_data_query,
    calculate_sales_metric,
    create_sales_chart
)


# 1. Initialize the LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.environ.get("GROQ_API_KEY")
)


# 2. Register tools
tools = [
    sales_data_query,
    calculate_sales_metric,
    create_sales_chart
]

llm_with_tools = llm.bind_tools(tools)


# 3. Define typed graph state
class InsightState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_question: str
    plan: str


# 4. Generate a short visible analysis plan
def plan_node(state: InsightState):

    question = state["user_question"]

    response = llm.invoke([
        SystemMessage(content=(
            "You are Insight Copilot, a sales data analyst. "
            "Create a short, user-visible action plan in 2-3 bullet points. "
            "Explain what data you need and which analysis or visualization "
            "you intend to perform. Do not reveal private chain-of-thought."
        )),
        HumanMessage(content=question)
    ])

    return {"plan": response.content}


# 5. Agent decides which tools to use
def agent_node(state: InsightState):

    response = llm_with_tools.invoke([
        SystemMessage(content=(
            "You are Insight Copilot, an intelligent sales analytics assistant. "
            "Use the available tools to answer questions about the sales dataset. "
            "Choose tools based on the user's request. "
            "You may use multiple tools when necessary. "
            "Never invent figures. Base your answer on tool results. "
            "Include supporting numbers and explain why the result matters. "
            "If a chart is requested, use the charting tool."
        ))
    ] + state["messages"])

    return {"messages": [response]}


# 6. Create the graph
workflow = StateGraph(InsightState)

workflow.add_node("plan", plan_node)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "plan")
workflow.add_edge("plan", "agent")

# Conditional edge:
# If the LLM requests a tool, execute it.
# Otherwise, finish the conversation.
workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        END: END
    }
)

# After tools execute, return to the agent
workflow.add_edge("tools", "agent")


# 7. Compile the graph
insight_copilot = workflow.compile()

print("Insight Copilot LangGraph created successfully!")
