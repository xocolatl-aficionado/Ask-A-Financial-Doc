import os
import sys
from llama_index.core import VectorStoreIndex
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_parse import LlamaParse
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.core.schema import TextNode
from copy import deepcopy
from dotenv import load_dotenv
import pickle
import json
import argparse
import time as time
import nest_asyncio
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.replicate import Replicate
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

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
        model = llm_config.get("model", "")
        return OpenAI(model=model)
    elif llm_type == "huggingface":
        model = llm_config.get("model", "")
        tokenizer_name = llm_config.get("tokenizer", model)  # Default to model name if no tokenizer is specified
        return HuggingFaceLLM(model_name=model, tokenizer_name=tokenizer_name)
    elif llm_type == "replicate":
        model = llm_config.get("model", "")
        return Replicate(model=model)
    elif llm_type == "gemini":
        model = llm_config.get("model", "")  # Default model if not specified
        return Gemini(model=model)
    else:
        raise ValueError(f"Unsupported LLM type: {llm_type}")

def initialize_embedding_model(config):
    """Initialize the embedding model based on the provided configuration."""
    embedding_config = config.get("embedding_model", {})
    llm_provider = embedding_config.get("type", "").lower()

    if llm_provider == "openai":
        model = embedding_config.get("model", "text-embedding-ada-002")
        return OpenAIEmbedding(model=model)
    # elif llm_provider == "huggingface":
    #     model = embedding_config.get("model", "BAAI/bge-small-en-v1.5")
    #     return HuggingFaceEmbedding(model_name=model)
    elif llm_provider == "gemini":
        model = embedding_config.get("model", "models/text-embedding-004")
        return GeminiEmbedding(model_name=model)
    else:
        raise ValueError(f"Unsupported embedding model type: {llm_provider}")

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

def create_query_engine(combined_nodes, embedding_model, retreival_depth =5, reranker=None, verbosity=True):
    """
    Creates a combined query engine from selected documents and embedding model.
    """

    # Create the combined index
    combined_index = VectorStoreIndex(combined_nodes, embedding_model=embedding_model)
    if not reranker:
        return combined_index.as_query_engine(
            #response_mode="tree_summarize",
            similarity_top_k = retreival_depth,
            verbose=verbosity,
        )

    # Apply the recursive query engine with reranker
    return combined_index.as_query_engine(
        similarity_top_k = retreival_depth,
        node_postprocessors=[reranker],
        verbose=verbosity,
    )

# --- Main Script ---
def load(document_choice, retreival_depth, verbose):
    """
    Main function for running the query pipeline.
    
    Arguments:
        document_choice (str): Path to the document.
        query (str): Query string.
        retreival_depth (int): Depth for document retrieval.
        verbose (bool): Verbose mode.
    """
    
    #nest_asyncio.apply()

    # Load configuration and initialize models
    config = load_config("config.json")
    initialize_keys()
    llm_choice = initialize_llm(config)
    embedding_model = initialize_embedding_model(config)
    
    print(f"LLM: {llm_choice.model}")
    print(f"Embedding Model: {embedding_model.model_name}")

    if not document_choice:
        sys.exit("No document path provided. Please add paths to your documents.")
    query_engines = {}
    document_name = os.path.splitext(os.path.basename(document_choice))[0]
    
    _, document_nodes = parse_and_index_single_document(document_choice, llm_choice, embedding_model, verbosity=verbose)

    query_engine = create_query_engine(document_nodes, embedding_model, retreival_depth=retreival_depth, verbosity=verbose)
    query_engines[document_name] = query_engine
    print(f"Query engine made for {document_name} document")
    return query_engines

def run_query(query, query_engine, document_name, retrieval_depth, verbose=False):
    """
    Execute a query using the provided query engine and return the result.

    Parameters:
        query (str): The query to execute.
        query_engine (object): The query engine to process the query.
        document_name(str): The name of the document.
        retrieval_depth (int): The number of retrieval chunks to include in the context.
        verbose (bool): Whether to print verbose output.

    Returns:
        tuple: A tuple containing the response answer (str) and retrieval context (list).
    """
    if not query:
        raise ValueError("Please enter a query to proceed.")

    start_time = time.time()
    response = query_engine[document_name].query(query)
    
    if verbose:
        elapsed_time = round(time.time() - start_time, 2)
        print(f"Query: {query}\n\nResponse: {response.response}")
        print(f"Elapsed Time: {elapsed_time}s")

    retrieval_context = [
        response.source_nodes[i].get_content() for i in range(retrieval_depth)
    ]
    return (response.response, retrieval_context)

if __name__ == "__main__":
    #
    # USAGE: python script.py --document_choice "./TSLA-10Q-Sep2024.pdf" --query "What was the net income in 2023?"
    #
    # Argument parser for command-line arguments
    parser = argparse.ArgumentParser(
        description="Query processing pipeline for document retrieval and summarization."
    )

    # Add arguments
    parser.add_argument(
        "--document_choice",
        type=str,
        default="./TSLA-10Q-Sep2024.pdf",
        help="Path to the document to process (default: ./TSLA-10Q-Sep2024.pdf).",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="What is the net income in 2024?",
        help="Query string to ask the document (default: 'What is the net income in 2024?').",
    )
    parser.add_argument(
        "--retrieval_depth",
        type=int,
        default=5,
        help="Number of retrieval steps (default: 5).",
    )
    parser.add_argument(
        "--verbose",
        default=True,
        help="Enable verbose output.",
    )

    # Parse arguments
    args = parser.parse_args()
    document_choice=args.document_choice
    query=args.query
    retrieval_depth=args.retrieval_depth
    verbose=args.verbose

    query_engine = load(document_choice, retrieval_depth, verbose)
    document_name = os.path.splitext(os.path.basename(document_choice))[0]

    run_query(
         query=query, query_engine=query_engine, document_name=document_name, retrieval_depth=retrieval_depth, verbose=verbose
    )
    