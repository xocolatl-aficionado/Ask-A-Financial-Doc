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
        model = embedding_config.get("model_name", "text-embedding-ada-002")
        return OpenAIEmbedding(model=model)
    elif llm_provider == "huggingface":
        model = embedding_config.get("model_name", "BAAI/bge-small-en-v1.5")
        return HuggingFaceEmbedding(model_name=model)
    elif llm_provider == "gemini":
        model = embedding_config.get("model_name", "models/text-embedding-004")
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

llm_options = {
    "Gemini gemini-1.5-pro-002": {"llm": {"type": "gemini", "model": "models/gemini-1.5-pro-002"}},
    "OpenAI gpt-4o-mini": {"llm": {"type": "openai", "model": "gpt-4o-mini"}}
}

embedding_options = {
    "Gemini text-embedding-004": {"embedding_model": {"type": "gemini", "model_name": "models/text-embedding-004"}},
    "OpenAI text-embedding-ada-002": {"embedding_model": {"type": "openai", "model_name": "text-embedding-ada-002"}},
    "OpenAI text-embedding-3-small": {"embedding_model": {"type": "openai", "model_name": "text-embedding-3-small"}},
    "OpenAI text-embedding-3-large": {"embedding_model": {"type": "openai", "model_name": "text-embedding-3-large"}}
}

st.title("Ask a Financial Doc")

# Directory containing PDFs
pdf_directory = "./"
pdf_files = [file for file in os.listdir(pdf_directory) if file.endswith(".pdf")]

if not pdf_files:
    st.error("No PDF files found in the directory.")
    st.stop()

st.subheader("Select a Document")

# Initialize session state for selected file
if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

# Display PDF files as tiles
cols = st.columns(3)  # Adjust the number of columns as needed
for i, pdf_file in enumerate(pdf_files):
    col = cols[i % 3]
    if col.button(pdf_file):
        st.session_state.selected_file = os.path.join(pdf_directory, pdf_file)

if st.session_state.selected_file:
    st.success(f"Selected File: {os.path.basename(st.session_state.selected_file)}")
else:
    st.warning("Please select a document to proceed.")
    st.stop()

st.subheader("Model Selection")

# Add LLM and Embedding Model selection
selected_llm_name = st.selectbox("Choose an LLM", list(llm_options.keys()))
selected_llm = llm_options[selected_llm_name]["llm"]
selected_embedding_name = st.selectbox("Choose an Embedding Model", list(embedding_options.keys()))
selected_embedding = embedding_options[selected_embedding_name]["embedding_model"]

merged_config = {
    "llm": selected_llm,
    "embedding_model": selected_embedding
}
# Input fields
query = st.text_area("Query", help="Enter your query here.")
retrieval_depth = st.number_input("Retrieval Depth", min_value=1, max_value=100, value=3, help="Set the depth for document retrieval.")
verbose = st.checkbox("Verbose Mode", value=True, help="Enable verbose mode for detailed output.")
show_chunks = st.checkbox("Show Retrieval Chunks", value=False, help="Enable to view detailed retrieval chunks.")

if st.button("Run Query"):
    try:

        # Initialize models
        initialize_keys()
        llm_choice = initialize_llm(merged_config)
        embedding_model = initialize_embedding_model(merged_config)

        st.write(f"Selected LLM: {llm_choice.model}")
        st.write(f"Selected Embedding Model: {embedding_model.model_name}")

        # Process the document and query
        document_name = os.path.splitext(os.path.basename(st.session_state.selected_file))[0]

        _, document_nodes = parse_and_index_single_document(st.session_state.selected_file, llm_choice, embedding_model, verbosity=verbose)

        query_engine = create_query_engine(document_nodes, embedding_model, retreival_depth=retrieval_depth, verbosity=verbose)
        st.write(f"Query engine created for the document: **{document_name}**")

        if query:
            now = time.time()
            response = query_engine.query(query)
            elapsed_time = round(time.time() - now, 2)

            st.subheader("_Query Response_")
            st.write(response.response)
            if show_chunks:
                st.subheader("Retrieval Context")
                retrieval_context = [response.source_nodes[i].get_content() for i in range(retrieval_depth)]
                for i, context in enumerate(retrieval_context, 1):
                    st.write(f"Context {i}:")
                    st.write(context)

            if verbose:
                st.write(f"Elapsed Time: {elapsed_time}s")
        else:
            st.warning("Please enter a query to proceed.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")