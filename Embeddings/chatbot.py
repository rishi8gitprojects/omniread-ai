import os
import json
from openai import OpenAI
from Embeddings.vector_db import query_database, COLLECTION_NAME, DB_DIR
from Embeddings.embedding_engine import get_embedding_model
from langchain_chroma import Chroma

# Bypassed HF Router: Moving directly to Groq's blazing fast, free-tier engine
MODEL_IDENTIFIER = "llama-3.3-70b-versatile"

def _get_client(groq_api_key):
    return OpenAI(
        base_url="https://api.groq.com/openai/v1", 
        api_key=groq_api_key
    )

def _retrieve_entire_book_context(user_query, groq_api_key):
    """
    Retrieves a stratified sample of the book (beginning, middle, and end) 
    to provide a holistic summary without violating Groq's 12,000 TPM free-tier limit.
    """
    # FIXED: Changed from "local" to "huggingface_api" to prevent server RAM crash
    embeddings = get_embedding_model(provider="huggingface_api")
    
    db = Chroma(
        persist_directory=DB_DIR,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )
    db_data = db.get()
    
    if not db_data or not db_data.get("documents"):
        print(f"❌ DATABASE CHECK: Chroma returned 0 documents globally at {DB_DIR}!")
        return ""
    
    all_chunks = db_data["documents"]
    total_chunks = len(all_chunks)
    
    # GROQ FREE TIER SAFETY LIMIT: ~12,000 Tokens Per Minute
    MAX_SAFE_CHUNKS = 12
    
    if total_chunks <= MAX_SAFE_CHUNKS:
        sampled_chunks = all_chunks
        print(f"✅ DATABASE CHECK: Feeding all {total_chunks} chunks directly to Llama 3.3...")
    else:
        print(f"⚖️ Document is {total_chunks} chunks. Taking {MAX_SAFE_CHUNKS} strategic samples to bypass Groq limits...")
        step_size = max(1, total_chunks // MAX_SAFE_CHUNKS)
        sampled_chunks = [all_chunks[i] for i in range(0, total_chunks, step_size)][:MAX_SAFE_CHUNKS]
    
    full_text_context = "\n\n---\n\n".join(sampled_chunks)
    return full_text_context

def handle_semantic_query(user_query, chat_history, hf_token):
    """
    Parses intent via LLM, structures sliding academic short-term memory arrays, 
    and returns a fluid contextual response.
    """
    client = _get_client(hf_token)

    # 1. Compress Conversational Logs into Contextualized Memory String
    history_context = ""
    if chat_history:
        history_context = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in chat_history[-4:]])

    # 2. Semantic Intent Check
    router_messages = [
        {
            "role": "system", 
            "content": (
                "You are an intent classification engine for literary research text. Analyze the user's research query "
                "and determine if it demands an exhaustive, holistic evaluation of the entire text ('GLOBAL_SYNTHESIS' "
                "for full text summaries, macro-character sketch developments, critical analysis, or overall thematic breakdowns) "
                "or a localized snippet check ('LOCAL_EXAMINATION' for specific factual lookups, literal words, or single tracking metrics).\n\n"
                "Respond strictly with a JSON object containing the key 'intent' set to either 'GLOBAL_SYNTHESIS' or 'LOCAL_EXAMINATION'. "
                "Do not output any markdown blocks, backticks, or conversational text."
            )
        },
        {
            "role": "user", 
            "content": f"Conversational History Context:\n{history_context}\n\nCurrent Research Query: {user_query}"
        }
    ]

    intent = "LOCAL_EXAMINATION" # Default to fast lookup for simple queries
    try:
        completion = client.chat.completions.create(
            model=MODEL_IDENTIFIER,
            messages=router_messages,
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        raw_response = completion.choices[0].message.content.strip()
        
        # SAFELY PARSE RAW SUPPORTS REGARDLESS OF BACKTICKS
        if "```" in raw_response:
            raw_response = raw_response.split("```")[1].replace("json", "").strip()
            
        parsed_json = json.loads(raw_response)
        intent = parsed_json.get("intent", "LOCAL_EXAMINATION")
    except Exception as e:
        print(f"⚙️ Router warning (Fallback to Local): {str(e)}")
        intent = "LOCAL_EXAMINATION"

    # 3. Pipeline Assignment & Context Assembly
    if intent == "GLOBAL_SYNTHESIS":
        context_text = _retrieve_entire_book_context(user_query, hf_token)
        system_prompt = (
            "You are an insightful and creative Literature Research Assistant.\n"
            "Your goal is to provide a beautifully written, engaging, and deeply thoughtful explanation of the story, "
            "focusing on character insights, emotional growth, and core themes based on the provided text.\n\n"
            "Directives:\n"
            "1. Write using clear, natural, and accessible English. Completely avoid heavy academic jargon.\n"
            "2. Be creative and narrative-driven in your analysis.\n"
            "3. Structure your response into clear, readable paragraphs with friendly markdown headers."
        )
    else:
        # Try local snippet parsing first
        retrieved_chunks = query_database(user_query, k=4)
        context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_chunks])
        
        # SAFE INTERLOCK CRADLE FALLBACK
        if not context_text.strip():
            print("⚠️ Local semantic search returned 0 chunks. Swapping to Full Context Scan pipeline...")
            context_text = _retrieve_entire_book_context(user_query, hf_token)
            intent = "GLOBAL_SYNTHESIS"
            
        system_prompt = (
            "You are a helpful and clear Factual Text Guide.\n"
            "Your objective is to find the exact details, facts, or lines the user is asking about from the provided snippets and explain them clearly.\n\n"
            "Directives:\n"
            "1. Use simple, direct, and conversational language to break down the facts.\n"
            "2. Keep your explanation closely tied to the provided context bits."
        )

    # Final protection wall
    if not context_text.strip():
        return "The system could not retrieve any text from your document database. Please re-upload your PDF file above."

    # 4. Assemble Final Messages Array
    analysis_messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    if chat_history:
        for turn in chat_history[-4:]: 
            analysis_messages.append({"role": turn["role"], "content": turn["content"]})
            
    analysis_messages.append({
        "role": "user", 
        "content": f"TEXTUAL REFERENCE CONTEXT:\n{context_text}\n\nFOLLOW-UP RESEARCH QUERY: {user_query}"
    })

    # 5. Execute with Balanced, Creative Temperatures
    analysis_completion = client.chat.completions.create(
        model=MODEL_IDENTIFIER,
        messages=analysis_messages,
        temperature=0.7 if intent == "GLOBAL_SYNTHESIS" else 0.3
    )

    return analysis_completion.choices[0].message.content