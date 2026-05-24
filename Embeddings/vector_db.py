# Embeddings/vector_db.py
import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from Embeddings.embedding_engine import get_embedding_model

DB_DIR = "./chroma_storage"
COLLECTION_NAME = "web_uploaded_docs"

def process_pdf_bytes(pdf_bytes, file_name):
    """
    Extracts text from raw PDF bytes and returns LangChain Document objects.
    """
    documents = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                # Store page content along with helpful metadata tracking
                metadata = {"source": file_name, "page": page_num + 1}
                documents.append(Document(page_content=text, metadata=metadata))
    return documents

def chunk_and_store(pdf_bytes, file_name):
    """
    Takes PDF bytes, splits them into semantic paragraphs/chunks, 
    and inserts them into ChromaDB using our active embedding engine.
    """
    # 1. Extract text from the byte stream
    raw_docs = process_pdf_bytes(pdf_bytes, file_name)
    if not raw_docs:
        return 0
        
    # 2. Split the text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_chunks = text_splitter.split_documents(raw_docs)
    
    # 3. Get our embedding model from File 1
    embeddings = get_embedding_model(provider="local")
    
    # 4. Save to ChromaDB 
    # FIXED: Changed embedding_function to embedding to prevent TypeError
    db = Chroma.from_documents(
        documents=split_chunks,
        embedding=embeddings,          
        persist_directory=DB_DIR,
        collection_name=COLLECTION_NAME
    )
    return len(split_chunks)

def query_database(user_query, k=2):
    """
    Searches the existing vector space for matching document chunks.
    """
    embeddings = get_embedding_model(provider="local")
    
    # Load connection to the existing database folder
    db = Chroma(
        persist_directory=DB_DIR,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )
    
    # Debug trace tool: Check database record health directly in console
    total_vectors = db._collection.count()
    print(f"⚙️ [DB DEBUG] Current vector count inside collection on query run: {total_vectors}")
    
    if total_vectors == 0:
        return []
        
    return db.similarity_search(user_query, k=k)