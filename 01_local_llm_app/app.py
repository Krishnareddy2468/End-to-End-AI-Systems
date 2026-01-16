import streamlit as st
import ollama

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Local LLM Chat",
    page_icon="🤖",
    layout="centered"
)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("**Configure your AI assistant**")
st.sidebar.divider()

model_name = st.sidebar.selectbox(
    "🤖 Select Model",
    ["llama3.2", "mistral", "phi3"],
    help="Choose which LLM model to use for responses"
)

temperature = st.sidebar.slider(
    "🌡️ Temperature",
    0.0, 1.0, 0.7, 0.1,
    help="Controls response creativity. Low (0.0-0.3) = Focused & consistent. Medium (0.4-0.8) = Balanced. High (0.9-1.0) = Creative & varied"
)

# Temperature indicator
if temperature <= 0.3:
    st.sidebar.caption("🎯 Mode: **Focused & Precise**")
elif temperature <= 0.8:
    st.sidebar.caption("⚖️ Mode: **Balanced & Natural**")
else:
    st.sidebar.caption("🎨 Mode: **Creative & Experimental**")

# ---------------- SESSION FLAGS ----------------
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False

# ---------------- CONTROLS ----------------
st.sidebar.divider()

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("Stop", use_container_width=True, help="Stop response generation", key="stop_btn"):
        st.session_state.stop_generation = True

with col2:
    if st.button("Clear", use_container_width=True, help="Clear chat history", key="clear_btn"):
        st.session_state.messages = [
            {"role": "assistant", "content": "How can I help you today?"}
        ]
        st.rerun()

# Sidebar footer
st.sidebar.divider()
st.sidebar.caption("✨ **Running Locally**")
st.sidebar.caption("🔒 No data leaves your device")



# ---------------- HEADER ----------------
st.title("🤖 Local LLM Chatbot")
st.caption("Runs 100% locally • No APIs • Full Privacy")
st.divider()

# ---------------- CHAT MEMORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you today?"}
    ]

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).markdown(msg["content"])

# ---------------- USER INPUT ----------------
prompt = st.chat_input("Ask me anything...")

if prompt:
    # reset stop flag for new request
    st.session_state.stop_generation = False

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        response_box = st.empty()
        full_response = ""

        try:
            stream = ollama.chat(
                model=model_name,
                messages=st.session_state.messages,
                options={"temperature": temperature},
                stream=True
            )

            for chunk in stream:
                if st.session_state.stop_generation:
                    full_response += " [Generation stopped]"
                    break

                if "message" in chunk and chunk["message"]["content"]:
                    token = chunk["message"]["content"]
                    full_response += token
                    response_box.markdown(full_response + "▌")

            response_box.markdown(full_response)
            
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
            
        except Exception as e:
            error_msg = f"❌ **Error**: {str(e)}"
            response_box.error(error_msg)
            st.error(
                "**Troubleshooting:**\n\n"
                "1. ✓ Is Ollama running? Start it with `ollama serve`\n\n"
                f"2. ✓ Is the model '{model_name}' installed? Try `ollama pull {model_name}`\n\n"
                "3. ✓ Check if Ollama is accessible at http://localhost:11434"
            )

# ---------------- EXPORT CHAT ----------------
# Only show export if there are messages (beyond initial greeting)
if len(st.session_state.messages) > 2:
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        if st.button("Export Chat", use_container_width=True):
            chat_text = "\n\n".join(
                f"{m['role'].upper()}: {m['content']}"
                for m in st.session_state.messages
                if m["role"] != "system"
            )

            st.download_button(
                label="⬇️ Download",
                data=chat_text,
                file_name="local_llm_chat.txt",
                mime="text/plain",
                use_container_width=True
            )
