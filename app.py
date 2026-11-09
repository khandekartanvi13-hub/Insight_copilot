
import os
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# Configure the page
st.set_page_config(
    page_title="Insight Copilot",
    page_icon="📊",
    layout="wide"
)

# Load the Groq API key from Streamlit secrets
try:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

# Import the graph and chart module
from agent.graph import insight_copilot
import agent.tools as sales_tools

# App heading

# App heading
st.title("📊 Insight Copilot")
st.markdown(
    "### Turn your sales data into meaningful insights."
)
st.write(
    "Ask questions in natural language, explore sales performance, "
    "compare regions and products, and generate visual insights."
)

# Dataset information
with st.container(border=True):
    st.subheader("📁 Your Dataset: Sales Dataset 2024")
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", "2,000")
    col2.metric("Total Columns", "10")
    col3.metric("Time Period", "Jan – Dec 2024")

    st.caption(
        "Explore revenue, profit, costs, units sold, products, "
        "categories, regions and salesperson performance."
    )

# Example questions
st.subheader("💡 Try asking")
examples = [
    "Which region generated the highest revenue?",
    "Which product generated the highest profit?",
    "What is the total revenue?",
    "Compare revenue across product categories.",
    "Create a chart showing revenue by region."
]

cols = st.columns(2)
for i, example in enumerate(examples):
    if cols[i % 2].button(example, use_container_width=True):
        st.session_state.pending_question = example

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display previous conversation
for item in st.session_state.chat_history:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

        if item.get("plan"):
            with st.expander("View analysis plan"):
                st.markdown(item["plan"])

# Chat input
question = st.chat_input("Ask something about your sales data...")

# Handle example question clicks
if st.session_state.get("pending_question"):
    question = st.session_state.pending_question
    del st.session_state.pending_question

if question:

    with st.chat_message("user"):
        st.markdown(question)

    messages = []

    for item in st.session_state.chat_history:
        if item["role"] == "user":
            messages.append(HumanMessage(content=item["content"]))
        else:
            messages.append(AIMessage(content=item["content"]))

    messages.append(HumanMessage(content=question))

    sales_tools.latest_chart = None

    try:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your sales data..."):

                result = insight_copilot.invoke(
                    {
                        "messages": messages,
                        "user_question": question,
                        "plan": ""
                    },
                    config={"recursion_limit": 10}
                )

            plan = result.get("plan", "")
            answer = result["messages"][-1].content

            if plan:
                with st.expander("View analysis plan", expanded=True):
                    st.markdown(plan)

            st.markdown(answer)

            if sales_tools.latest_chart is not None:
                st.plotly_chart(
                    sales_tools.latest_chart,
                    use_container_width=True
                )

        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "plan": plan
        })

    except Exception as e:
        st.error(f"Something went wrong: {e}")

