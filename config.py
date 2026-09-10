# Configuration for AI Medical Knowledge Base

# LLM Settings
MODEL_NAME = "mistral"  # Change to "llama2" for Llama 2, or "neural-chat" etc.
MODEL_TEMPERATURE = 0.3  # Lower = more deterministic, Higher = more creative

# PDF Extraction Settings
PDF_CHUNK_SIZE = 1000
PDF_CHUNK_OVERLAP = 200

# Vector Index Settings
EMBEDDING_MODEL = "mistral"
RETRIEVAL_K = 5  # Number of documents to retrieve for each query

# Paths
PDF_DIR = "pdfs"
MARKDOWN_DIR = "data/markdown"
VECTORSTORE_DIR = "data/vectorstore"

# Medical domain context
SYSTEM_PROMPT = """You are a medical expert specializing in neurosurgery and glioblastoma disease.
You have deep knowledge of treatment protocols, surgical techniques, radiation therapy, and chemotherapy options.
Provide evidence-based answers based on the provided research literature.
If information is not available in the knowledge base, clearly state this.
Always cite the source when possible."""
