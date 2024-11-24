import streamlit as st
import os
import sys
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_parse import LlamaParse
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker
from llama_index.core.schema import TextNode
from copy import deepcopy
from dotenv import load_dotenv
import pickle
import json
import time as time
import nest_asyncio
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.replicate import Replicate
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

# Initialize the app with Streamlit
st.title("LLM Document Processor")
st.write("Select a document path and query its contents.")
def initialize_keys():
    """Automatically sets API keys from environment variables."""
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        sys.exit("API Key are missing. Please set OPENAI_API_KEY in your environment.")
    llama_cloud_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not llama_cloud_key:
        sys.exit("API Key are missing. Please set LLAMA_CLOUD_API_KEY in your environment.")
    #replicate_api_key = os.getenv("REPLICATE_API_TOKEN")
    #if not replicate_api_key:
        #sys.exit("API Key are missing. Please set REPLICATE_API_TOKEN in your environment.")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        sys.exit("API Key are missing. Please set GOOGLE_API_KEY in your environment.")
# --- Backend Helper Functions ---
def load_config(config_file="config.json"):
    """Load configuration settings from a JSON file."""
    with open(config_file, "r") as f:
        config = json.load(f)
    return config

# --- Utility Functions ---
def save_cache(file_name, data):
    """Saves the cache to a pickle file."""
    cache_file_path = f"cached_nodes/{file_name}.pkl"
    os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
    with open(cache_file_path, "wb") as f:
        pickle.dump(data, f)

def load_cache(file_name):
    """Loads the cached data from a pickle file."""
    cache_file_path = f"cached_nodes/{file_name}.pkl"
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "rb") as f:
            return pickle.load(f)
    return None

def initialize_llm(config):
    """Initialize the LLM based on the provided configuration."""
    llm_config = config.get("llm", {})
    llm_type = llm_config.get("type", "").lower()
    
    if llm_type == "openai":
        model_name = llm_config.get("model", "")
        return OpenAI(model=model_name)
    elif llm_type == "huggingface":
        model_name = llm_config.get("model", "")
        tokenizer_name = llm_config.get("tokenizer", model_name)  # Default to model name if no tokenizer is specified
        return HuggingFaceLLM(model_name=model_name, tokenizer_name=tokenizer_name)
    elif llm_type == "replicate":
        model_name = llm_config.get("model", "")
        return Replicate(model=model_name)
    elif llm_type == "gemini":
        model_name = llm_config.get("model", "")  # Default model if not specified
        return Gemini(model=model_name)
    else:
        raise ValueError(f"Unsupported LLM type: {llm_type}")

def initialize_embedding_model(config):
    """Initialize the embedding model based on the provided configuration."""
    embedding_config = config.get("embedding_model", {})
    model_type = embedding_config.get("type", "").lower()

    if model_type == "openai":
        model_name = embedding_config.get("model_name", "text-embedding-ada-002")
        return OpenAIEmbedding(model=model_name)
    elif model_type == "huggingface":
        model_name = embedding_config.get("model_name", "BAAI/bge-small-en-v1.5")
        return HuggingFaceEmbedding(model_name=model_name)
    elif model_type == "gemini":
        model_name = embedding_config.get("model_name", "models/text-embedding-004")
        return GeminiEmbedding(model_name=model_name)
    else:
        raise ValueError(f"Unsupported embedding model type: {model_type}")

def get_page_nodes(docs, separator="\n---\n"):
    """Split each document into page nodes, by separator."""
    nodes = []
    for doc in docs:
        doc_chunks = doc.text.split(separator)
        for doc_chunk in doc_chunks:
            node = TextNode(
                text=doc_chunk,
                metadata=deepcopy(doc.metadata),
            )
            nodes.append(node)
    return nodes

# --- Document Processing ---
def parse_and_index_single_document(file_path, model, embedding_model, verbosity=False):
    """
    Parses and indexes a single document with a specific embedding model.
    """
    file_name = f"{os.path.basename(file_path)}_{model.model.replace('/', '_')}_{embedding_model.model_name.replace('/', '_')}"
    cached_data = load_cache(file_name)
    if cached_data:
        if verbosity:
            print("Fetching indexes from cache...")
        return cached_data  # Return cached index and nodes

    if verbosity:
        print(f"Processing document: {file_name}")
    doc = LlamaParse(result_type="markdown").load_data(file_path)

    # Parse document into nodes
    node_parser = MarkdownElementNodeParser(
        llm=model, num_workers=4
    )
    nodes = node_parser.get_nodes_from_documents(doc)
    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)

    # Combine nodes
    combined_nodes = base_nodes + objects + get_page_nodes(doc)

    # Create the index
    index = VectorStoreIndex(nodes=combined_nodes, embedding_model=embedding_model)
    
    # Save the index and nodes to cache
    save_cache(file_name, (index, combined_nodes))

    return index, combined_nodes  # Return both index and nodes

def create_query_engine(combined_nodes, embedding_model, reranker=None, verbosity=False):
    """
    Creates a combined query engine from selected documents and embedding model.
    """

    # Create the combined index
    combined_index = VectorStoreIndex(combined_nodes, embedding_model=embedding_model)
    if not reranker:
        return combined_index.as_query_engine(
            #response_mode="tree_summarize",
            streaming=True,
            similarity_top_k=5,
            verbose=verbosity,
        )

    # Apply the recursive query engine with reranker
    return combined_index.as_query_engine(
        similarity_top_k=5,
        node_postprocessors=[reranker],
        verbose=verbosity,
    )

# --- Streamlit Interactivity ---
nest_asyncio.apply()

# Load configuration and initialize models
config = load_config("config.json")
initialize_keys()
llm_choice = initialize_llm(config)
embedding_model = initialize_embedding_model(config)

# Display dropdown to select document
document_paths = [
    "./TSLA-10Q-Sep2024.pdf",
    "./PANW-10Q-Oct2024.pdf"
]

document_choice = st.selectbox("Select Document", document_paths)
query_engines = {}

# If a document is selected, process it and display results
if document_choice:
    document_name = os.path.splitext(os.path.basename(document_choice))[0]
    st.write(f"Processing document: {document_choice}")

    # Process the selected document
    _, document_nodes = parse_and_index_single_document(document_choice, llm_choice, embedding_model, verbosity=True)

    # Create a query engine for the document
    query_engine = create_query_engine(document_nodes, embedding_model)

    # Store the query engine in the dictionary with the document name as the key
    query_engines[document_name] = query_engine

    st.write(f"Query engine for '{document_name}' created!")
    # Create a text input field for the user to enter a custom query
    query = st.text_input("Enter your query:")

    if query:
        now = time.time()

        # Execute the query and get the response
        response = query_engines[document_name].query(query)

        # Display the response and elapsed time
        st.write(f"Query: {query}:\n{response}")
        st.write(f"Elapsed: {round(time.time() - now, 2)}s")
    else:
        st.write("Please enter a query to proceed.")

    #query = "How did the Research and development expenses change in the quarter ending in October 2024 compared to the quarter ending in October 2023?"  


