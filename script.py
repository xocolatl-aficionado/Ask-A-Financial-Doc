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
import os
import time
import json

# --- Load Configuration ---
def load_config(config_file="config.json"):
    """
    Load configuration settings from a JSON file.
    """
    with open(config_file, "r") as f:
        config = json.load(f)
    return config

# --- Initialize LLM ---
def initialize_llm(config):
    """
    Initialize the LLM based on the provided configuration.
    """
    llm_config = config.get("llm", {})
    llm_type = llm_config.get("type", "").lower()
    
    if llm_type == "openai":
        model_name = llm_config.get("model", "gpt-3.5-turbo")
        return OpenAI(model=model_name)
    else:
        raise ValueError(f"Unsupported LLM type: {llm_type}")

# --- Initialize Embedding Model ---
def initialize_embedding_model(config):
    """
    Initialize the embedding model based on the provided configuration.
    """
    embedding_config = config.get("embedding_model", {})
    model_type = embedding_config.get("type", "").lower()

    if model_type == "openai":
        model_name = embedding_config.get("model_name", "text-embedding-ada-002")
        return OpenAIEmbedding(model=model_name)
    elif model_type == "huggingface":
        model_name = embedding_config.get("model_name", "BAAI/bge-small-en-v1.5")
        return HuggingFaceEmbedding(model_name=model_name)
    else:
        raise ValueError(f"Unsupported embedding model type: {model_type}")
    
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

# --- Embedding Model Selection ---
def get_embedding_model(model_name="text-embedding-ada-002"):
    """
    Returns the embedding model based on the name provided.
    """
    if model_name.startswith("text-embedding"):
        return OpenAIEmbedding(model=model_name)
    elif model_name == "BAAI/bge-small-en-v1.5":
        return HuggingFaceEmbedding(model_name=model_name)
    else:
        raise ValueError(f"Unsupported model: {model_name}")

# --- Initialization and API Key Setup ---
def initialize_keys():
    """Automatically sets API keys from environment variables."""
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llama_cloud_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not openai_api_key or not llama_cloud_key:
        sys.exit("API Keys are missing. Please set OPENAI_API_KEY and LLAMA_CLOUD_API_KEY in your environment.")

initialize_keys()

# --- Helper Functions ---
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

def parse_and_index_single_document(file_path, model, embedding_model, verbosity=False):
    """
    Parses and indexes a single document with a specific embedding model.
    """
    file_name = f"{os.path.basename(file_path)}_{embedding_model.model_name.replace('/', '_')}"
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

def create_query_engine(selected_files, model, embedding_model, reranker=None, verbosity=False):
    """
    Creates a combined query engine from selected documents and embedding model.
    """
    combined_nodes = []
    for file_path in selected_files:
        _, nodes = parse_and_index_single_document(file_path, model, embedding_model, verbosity)
        combined_nodes.extend(nodes)

    # Create the combined index
    combined_index = VectorStoreIndex(combined_nodes, embedding_model=embedding_model)
    if not reranker:
        return combined_index.as_query_engine(
        similarity_top_k=5,
        verbose=verbosity,
        )

    # Apply the recursive query engine with reranker
    return combined_index.as_query_engine(
        similarity_top_k=5,
        node_postprocessors=[reranker],
        verbose=verbosity,
    )

# --- Main Script ---
def main(verbosity=False):
    # Hardcoded or user-specified document paths
    document_paths = [
        "./TSLA-10Q-Sep2024.pdf",
    ]
    # Load configuration
    config = load_config("config.json")
    
    # Initialize LLM and Embedding Models
    llm_choice = initialize_llm(config)
    embedding_model = initialize_embedding_model(config)

    # You can now use `llm` and `embedding_model` in your pipeline
    print(f"LLM: {llm_choice.model}")
    print(f"Embedding Model: {embedding_model.model_name}")

    # Check if documents are available
    if not document_paths:
        sys.exit("No document paths provided. Please add paths to your documents.")

    # Parse and index documents
    if verbosity:
        print("Processing documents...")

    # Select all documents for the query
    if verbosity:
        print("Selecting all documents for the query engine...")
    reranker = FlagEmbeddingReranker(
        top_n=5,
        model="BAAI/bge-reranker-large",
    )
    query_engine = create_query_engine(document_paths, llm_choice, embedding_model, None, verbosity)
    if verbosity:
        print("Query engine created!")

    # Example query
    query = "How much revenue did we get in 2023 in the form of automotive regulatory credits?"  
    if verbosity:
        print(f"Running query: {query}")
    now = time.time()
    response = query_engine.query(query)
    print(f"Elapsed: {round(time.time() - now, 2)}s")
    
    print(f"Query: {query}:\n{response}")

    if verbosity:
        for i in range(5):
            print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<CHUNK {i}>>>>>>>>>>>>>>>>>>>>>>>>")
            print(f"DEBUGGING: {response.source_nodes[i].get_content()}")



if __name__ == "__main__":
    
    verbosity = False  # Set to True for verbose output, False for only the answer
    main(verbosity)
    