import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

def get_chatbot_response(user_query, chat_history):
    """
    Takes a query and the current history list, 
    returns the AI response and updated history.
    """
    # 1. Initialize LLM
    llm = ChatGroq(
        temperature=0.7, 
        groq_api_key=os.getenv("groq_key"), 
        model_name="llama-3.1-8b-instant"
    )

    # 2. Add current user query to history
    chat_history.append(HumanMessage(content=user_query))

    # 3. Get response from Groq
    try:
        response = llm.invoke(chat_history)
        bot_text = response.content
        
        # 4. Add AI response to history
        chat_history.append(AIMessage(content=bot_text))
        
        return bot_text, chat_history
    except Exception as e:
        return f"Error: {str(e)}", chat_history