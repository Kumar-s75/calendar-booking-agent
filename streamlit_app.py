import streamlit as st
import requests
import json
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Calendar Booking Agent",
    page_icon="📅",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        align-self: flex-end;
        max-width: 80%;
        margin-left: auto;
    }
    .assistant-message {
        background-color: #f8f9fa;
        color: #333;
        align-self: flex-start;
        max-width: 80%;
        border: 1px solid #dee2e6;
    }
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().timestamp()}"

# App header
st.title("📅 Calendar Booking Agent")
st.markdown("Welcome! I'm your AI assistant for booking appointments. I can help you check availability and schedule meetings on your Google Calendar.")

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def send_message(message: str) -> str:
    """Send message to the backend API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "message": message,
                "session_id": st.session_state.session_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"Connection error: {str(e)}. Please make sure the backend is running."

# Chat interface
st.subheader("💬 Chat with your booking assistant")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

# Chat input
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message here...",
            placeholder="e.g., 'I want to book a meeting for tomorrow at 2 PM'",
            label_visibility="collapsed"
        )
    
    with col2:
        submit_button = st.form_submit_button("Send", use_container_width=True)

# Process user input
if submit_button and user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show loading spinner
    with st.spinner("Assistant is thinking..."):
        # Get response from backend
        response = send_message(user_input)
    
    # Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to update the chat display
    st.rerun()

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ How to use")
    st.markdown("""
    **I can help you with:**
    - 📅 Check available time slots
    - ➕ Book new appointments
    - 👀 View existing events
    - 📋 Get current date
    
    **Example requests:**
    - "What's available tomorrow?"
    - "Book a meeting with John at 2 PM"
    - "Schedule a doctor appointment for Friday"
    - "Show me my events for today"
    """)
    
    st.header("🔧 System Status")
    
    # Health check
    try:
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")
    
    st.markdown(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit, FastAPI, and LangChain")
