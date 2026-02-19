"""
Chatbot UI for Streamlit
"""

import streamlit as st
import logging
from pathlib import Path

from chatbot.local_llm import OllamaChat
from chatbot.api_llm import OpenAIChat
from chatbot.prompts import get_system_prompt, get_context_injection

logger = logging.getLogger(__name__)


def initialize_chat_state():
    """Initialize chat session state"""
    
    if "chat_mode" not in st.session_state:
        st.session_state.chat_mode = "ollama"
    
    if "chat_instance" not in st.session_state:
        st.session_state.chat_instance = None
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "chat_ready" not in st.session_state:
        st.session_state.chat_ready = False


def get_chat_instance(mode: str, api_key: str = None):
    """Get chat instance"""
    
    try:
        if mode == "ollama":
            chat = OllamaChat("mistral")
            if chat.initialize():
                return chat
            else:
                raise RuntimeError("Ollama not available")
        
        elif mode == "openai":
            chat = OpenAIChat("gpt-3.5-turbo", api_key)
            if chat.initialize():
                return chat
            else:
                raise RuntimeError("OpenAI API not configured")
        
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    except Exception as e:
        logger.error(f"Chat init error: {e}")
        return None


def show_chatbot_page():
    """Chatbot page"""
    
    initialize_chat_state()
    
    st.markdown("## 🤖 AI Agricultural Assistant")
    
    st.info("""
    Ask your questions about:
    - 💭 How to use the system
    - 📊 Understanding predictions
    - 🌾 Agricultural advice
    - 📈 Optimize yield
    """)
    
    # Mode selector
    col1, col2 = st.columns([1, 3])
    
    with col1:
        mode = st.radio(
            "Chat Mode:",
            ["ollama", "openai"],
            format_func=lambda x: "🏠 Local" if x == "ollama" else "🌐 API",
            key="chat_mode_radio"
        )
    
    with col2:
        if mode == "openai":
            api_key = st.text_input(
                "OpenAI API Key:",
                type="password",
                help="sk-..."
            )
        else:
            api_key = None
    
    # Expertise level
    level = st.select_slider(
        "Your level:",
        options=["Beginner", "Intermediate", "Expert"],
        value="Intermediate"
    )
    
    # Init chat
    if not st.session_state.chat_ready:
        if st.button("🚀 Start Chat", use_container_width=True):
            with st.spinner("⏳ Initializing..."):
                chat = get_chat_instance(mode, api_key)
                
                if chat:
                    level_map = {
                        "Beginner": "simple",
                        "Intermediate": "default",
                        "Expert": "expert"
                    }
                    system_prompt = get_system_prompt(level_map[level])
                    chat.set_context(system_prompt)
                    
                    st.session_state.chat_instance = chat
                    st.session_state.chat_ready = True
                    st.rerun()
                else:
                    st.error(f"❌ Unable to start {mode}")
    
    # Chat interface
    if st.session_state.chat_ready:
        chat = st.session_state.chat_instance
        
        st.success(f"✓ Chat ready ({chat.model_name})")
        
        # Messages display
        messages_container = st.container()
        
        with messages_container:
            for msg in chat.get_history():
                if msg['role'] != 'system':
                    with st.chat_message(msg['role']):
                        st.write(msg['content'])
        
        # Input
        user_input = st.chat_input(
            "Your question...",
            key="chat_input"
        )
        
        if user_input:
            # Show user message
            with st.chat_message("user"):
                st.write(user_input)
            
            # Generate response
            try:
                with st.spinner("🤔 Thinking..."):
                    response = chat.chat(user_input)
                
                # Show response
                with st.chat_message("assistant"):
                    st.write(response.text)
                    
                    if response.tokens_used > 0:
                        st.caption(f"Tokens: {response.tokens_used}")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Chat error: {e}", exc_info=True)
        
        # Controls
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear history", use_container_width=True):
                chat.clear_history()
                chat.set_context(get_system_prompt())
                st.rerun()
        
        with col2:
            if st.button("🔄 Change mode", use_container_width=True):
                st.session_state.chat_ready = False
                st.rerun()
