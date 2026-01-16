import streamlit as st
import ollama

# Set the page configuration
st.set_page_config(
    page_title="My Local AI",
    page_icon="🤖"
)

st.title("🤖 Local Llama Chatbot")
st.caption("Running locally with Llama 3.2 - No Data Leaves This PC!")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you today?"}
    ]
# Display chat messages from history on app rerun
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])
# Handle user input
if prompt := st.chat_input("What is on your mind?"):
    
    # 1️⃣ Save & display user message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    st.chat_message("user").write(prompt)

    # 2️⃣ Assistant response container
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        # 3️⃣ Call local LLM (Ollama)
        stream = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        # 4️⃣ Stream tokens
        for chunk in stream:
            if chunk["message"]["content"]:
                content = chunk["message"]["content"]
                full_response += content
                response_placeholder.markdown(full_response + "▌")

        # 5️⃣ Final output
        response_placeholder.markdown(full_response)

    # 6️⃣ Save assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )
