# Embedding tool

# embedding_engine.py
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_openai import OpenAIEmbeddings # Uncomment if you switch to OpenAI later

def get_embedding_model(provider="local", model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """
    Factory function to easily switch embedding providers.
    """
    if provider == "local":
        print(f"[Engine] Loading local HuggingFace model: {model_name}")
        return HuggingFaceEmbeddings(model_name=model_name)
    
    elif provider == "openai":
        # Ensure os.environ["OPENAI_API_KEY"] is set before calling this
        print(f"[Engine] Loading OpenAI model: {model_name}")
        # return OpenAIEmbeddings(model=model_name)
        raise NotImplementedError("OpenAI configuration is ready but currently commented out.")
        
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")