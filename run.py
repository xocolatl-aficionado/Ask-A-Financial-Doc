import streamlit as st
from llama_index.core import VectorStoreIndex
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

# --- Initialization and API Key Setup ---
def initialize_keys():
    """Automatically sets API keys from environment variables."""
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llama_cloud_key = os.getenv("LLAMA_CLOUD_API_KEY")
    
    if openai_api_key and llama_cloud_key:
        st.success("API Keys loaded successfully from environment variables!")
    else:
        st.error(
            "API Keys are missing from environment variables. "
            "Please set OPENAI_API_KEY and LLAMA_CLOUD_API_KEY in your environment."
        )

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

def parse_and_index_single_document(uploaded_file):
    """Parses and indexes a single document."""
    # Check if nodes for this document are already cached
    cached_data = load_cache(uploaded_file.name)
    if cached_data:
        return cached_data  # Return cached index and nodes

    # Save the uploaded file locally
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    doc = LlamaParse(result_type="markdown").load_data(uploaded_file.name)

    # Parse document into nodes
    node_parser = MarkdownElementNodeParser(
        llm=OpenAI(model="gpt-4o-mini"), num_workers=4
    )
    nodes = node_parser.get_nodes_from_documents(doc)
    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)
    
    # Combine nodes
    combined_nodes = base_nodes + objects + get_page_nodes(doc)

    # Create the index
    index = VectorStoreIndex(nodes=combined_nodes)
    
    # Save the index and nodes to cache
    save_cache(uploaded_file.name, (index, combined_nodes))

    return index, combined_nodes  # Return both index and nodes


def manage_uploaded_documents(uploaded_files):
    """Manages multiple documents and creates a query engine for selected ones."""
    st.session_state["doc_indices"] = {}
    
    for uploaded_file in uploaded_files:
        index, nodes = parse_and_index_single_document(uploaded_file)
        st.session_state["doc_indices"][uploaded_file.name] = (index, nodes)

    st.session_state["active_query_engines"] = list(st.session_state["doc_indices"].values())


# --- Dynamic Query Engine Creation ---
def create_query_engine_from_selected_docs(selected_docs):
    """Creates a combined query engine from selected documents."""
    if selected_docs:
        selected_indices = [
            st.session_state["doc_indices"][doc_name] for doc_name in selected_docs
        ]
        # Combine nodes from selected indices
        combined_nodes = sum((nodes for _, nodes in selected_indices), [])  # Accessing nodes from tuple
        combined_index = VectorStoreIndex(combined_nodes)
        return combined_index.as_query_engine(similarity_top_k=5)
    return None


# --- Streamlit UI Components ---

# Step 1: Document Upload
st.subheader("Step 2: Upload and Select Documents")
uploaded_files = st.file_uploader(
    "Upload one or more financial documents (PDF)", accept_multiple_files=True
)
if uploaded_files:
    st.success("Files uploaded successfully!")
    if st.button("Process Documents"):
        with st.spinner("Processing documents..."):
            manage_uploaded_documents(uploaded_files)
        st.success("Documents processed and indexed!")

# Step 2: Document Selection
if "doc_indices" in st.session_state:
    st.subheader("Step 3: Select Documents for Query")
    selected_docs = st.multiselect(
        "Select documents to include in your query:",
        options=list(st.session_state["doc_indices"].keys()),
    )
    if st.button("Create Query Engine"):
        st.session_state["current_query_engine"] = create_query_engine_from_selected_docs(selected_docs)
        st.success("Query engine created for selected documents!")

# Step 3: Query Interface
st.subheader("Step 4: Query Your Documents")
if "current_query_engine" in st.session_state:
    query = st.text_input("Enter your query:")
    if st.button("Run Query"):
        with st.spinner("Fetching results..."):
            response = st.session_state["current_query_engine"].query(query)
        st.markdown(f"**Query Response:**\n\n{response}")
else:
    st.info("Please select documents and create a query engine first.")
