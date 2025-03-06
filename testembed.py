from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings

# Load models
st_model = SentenceTransformer("sentence-transformers/all-roberta-large-v1")
hf_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-roberta-large-v1")

# Generate a test embedding
test_text = "Hello, world!"
st_embedding = st_model.encode(test_text)
hf_embedding = hf_model.embed_query(test_text)

# Print dimensions
print("SentenceTransformer embedding dimension:", len(st_embedding))
print("HuggingFaceEmbeddings embedding dimension:", len(hf_embedding))
