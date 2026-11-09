# Insight Copilot – Design Write-up

## 1. Overview

Insight Copilot is an AI-powered sales analytics chatbot designed to help users explore and understand sales data through natural language queries. It allows users to obtain insights, perform calculations, and generate visualizations without manually writing code or queries.

## 2. Architecture and Technology Choices

The application is built using Python, LangGraph, LangChain, Groq, Pandas, Plotly, and Streamlit.

LangGraph was selected to manage the agent workflow because it supports state management, conditional routing, and tool execution. Unlike a simple linear LLM call, this architecture allows the agent to decide which tool is appropriate for a particular user request.

A typed state maintains the conversation messages, user question, and analysis plan throughout the workflow.

## 3. Agent Workflow

The workflow begins when a user submits a question. A planning node generates a short explanation of the intended analysis. The agent node then determines whether a tool is required and selects the appropriate tool.

The application provides three analytical tools:

- **Sales Data Query:** Retrieves and analyzes relevant information from the sales dataset.
- **Metric Calculation:** Performs numerical calculations such as total revenue and profit.
- **Chart Generation:** Creates interactive visualizations using Plotly.

Conditional edges control the workflow. When a tool is required, the graph routes execution to the tool node and then returns to the agent for a final response. Otherwise, the agent can respond directly.

## 4. Data Processing and User Interface

Pandas is used to load and process the Excel sales dataset. Plotly generates interactive charts, while Streamlit provides the conversational interface and displays analysis plans, answers, and visualizations.

The application maintains conversation history during a session to support multi-turn interactions.

## 5. Design Considerations

The application separates the agent workflow, analytical tools, and user interface into different modules to improve maintainability. API credentials are managed through environment variables and Streamlit secrets rather than being stored in source code.

The modular architecture also makes it easier to introduce additional analytical tools and datasets in the future.

## 6. Conclusion

Insight Copilot demonstrates how an LLM-based agent can combine reasoning, tool selection, data analysis, and visualization to make business intelligence more accessible through natural language.
