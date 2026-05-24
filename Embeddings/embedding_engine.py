import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
# from langchain_openai import OpenAIEmbeddings # Uncomment if you switch to OpenAI later
from dotenv import load_dotenv

load_dotenv()

def get_embedding_model(provider="huggingface_api", model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """
    Factory function to easily switch embedding providers.
    Defaults to cloud API to respect 512MB RAM limits on free hosting tiers.
    """
    if provider == "huggingface_api":
        # Pulls your free access token safely from environment variables
        hf_token = os.getenv("HF_TOKEN")
        
        if not hf_token:
            print("[Engine] WARNING: HF_TOKEN missing(HIGH RAM DANGER!).")
            return HuggingFaceEmbeddings(model_name=model_name)
            
        print(f"[Engine] Routing embeddings to Hugging Face Cloud API: {model_name}")
        return HuggingFaceInferenceAPIEmbeddings(
            api_key=hf_token,
            model_name=model_name
        )

    elif provider == "local":
        print(f"[Engine] Loading local HuggingFace model: {model_name} (Requires >400MB RAM)")
        return HuggingFaceEmbeddings(model_name=model_name)
    
    elif provider == "openai":
        # Ensure os.environ["OPENAI_API_KEY"] is set before calling this
        print(f"[Engine] Loading OpenAI model: {model_name}")
        # return OpenAIEmbeddings(model=model_name)
        raise NotImplementedError("OpenAI configuration is ready but currently commented out.")
        
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")