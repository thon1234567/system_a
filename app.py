import streamlit as st
import pandas as pd
import google.generativeai as genai

# 🚪 START: Add API key input page (non-destructive addition)
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if not st.session_state.api_key:
    st.set_page_config(page_title="Enter API Key", page_icon="🔑", layout="centered")
    st.title("🔐 Enter Your Google API Key")
    user_api = st.text_input("Google API Key", type="password")

    if user_api:
        st.session_state.api_key = user_api
        st.rerun()

    st.stop()
# 🚪 END: API key input logic

st.set_page_config(page_title="Inventory Assistant", page_icon="📦", layout="centered")
st.title("Inventory Assistant Chatbot")

# 🔐 Configure Gemini
API_KEY = st.session_state.api_key  # 👈 Use user's entered key instead of hardcoded
genai.configure(api_key=API_KEY)

# 📄 Load inventory data
df = pd.read_csv("inventory_data.csv")

# 📚 Build inventory summary string with all columns
inventory_summary = ""
for _, row in df.iterrows():
    inventory_summary += (
        f"- Item: {row['ItemName']}\n"
        f"  ID: {row['ItemID']}\n"
        f"  Category: {row['Category']}\n"
        f"  Type: {row['ItemType']}\n"
        f"  Quantity in Stock: {row['QuantityInStock']} {row['Unit']}\n"
        f"  Cost per Unit: {row['Cost']}\n"
        f"  Reorder Point: {row['ReorderPoint']}\n"
        f"  Location: {row['Location']}\n"
        f"  Lead Time: {row['LeadTimeDays']} days\n"
        f"  Last Received: {row['LastReceived']}\n\n"
    )

# 🧠 Define system behavior
SYSTEM_INSTRUCTION = f"""
You are a helpful office inventory assistant. Use the following detailed inventory data to answer questions accurately.
Do not guess any values. Only respond based on the information provided below.
If asked about stock, cost, restocking, or location, refer to the appropriate field.
Format answers clearly and compactly — no need for full paragraphs.

{inventory_summary}
"""

GENERATION_CONFIG = genai.types.GenerationConfig(temperature=0.7)

# 🔁 Initialize chat session
if "chat" not in st.session_state:
    base_model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config=GENERATION_CONFIG
    )
    st.session_state.chat = base_model.start_chat(history=[])

chat = st.session_state.chat

# 🧾 Display prior chat messages
for turn in chat.history:
    role = "assistant" if turn.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(turn.parts[0].text)

# 📝 Chat input and response generation
if prompt := st.chat_input("Ask about inventory..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = chat.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)

    except Exception as err:
        st.error(f"An error occurred: {err}")
