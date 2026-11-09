
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
st.title("📊 Insight Copilot")
st.caption("Your AI-powered sales data analysis assistant")

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

if question:

    # Display the user's question
    with st.chat_message("user"):
        st.markdown(question)

    # Save conversation history as LangChain messages
    messages = []

    for item in st.session_state.chat_history:
        if item["role"] == "user":
            messages.append(HumanMessage(content=item["content"]))
        else:
            messages.append(AIMessage(content=item["content"]))

    messages.append(HumanMessage(content=question))

    # Reset chart for this question
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

            # Display chart if the charting tool was used
            if sales_tools.latest_chart is not None:
                st.plotly_chart(
                    sales_tools.latest_chart,
                    use_container_width=True
                )

        # Save this conversation turn
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
