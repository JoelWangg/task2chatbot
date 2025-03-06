import os
import json
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

class VectorDBManager:
    def __init__(self):
        self.index_name = "changi-chatbot"
        self.embedding_model = SentenceTransformer("sentence-transformers/all-roberta-large-v1")  # Local model instead of OpenAI API
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
    def initialize_index(self):
        """Create or connect to Pinecone index"""
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=1024,  
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=os.getenv("PINECONE_ENV", "us-west-2")
                )
            )
            # Wait for index initialization
            while not self.pc.describe_index(self.index_name).status["ready"]:
                time.sleep(5)
        
        return self.pc.Index(self.index_name)
    
    def process_data(self, file_path):
        """Load and chunk JSON data"""
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # Extract and chunk text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        documents = []
        metadatas = []
        
        for page_id, page_data in data.items():
            for paragraph in page_data["paragraphs"]:
                # Split longer paragraphs into chunks
                chunks = text_splitter.split_text(paragraph)
                for chunk in chunks:
                    documents.append(chunk)
                    metadatas.append({
                        "page_id": page_id,
                        "source_url": page_data["page_url"],
                        "text": chunk
                    })
        
        return documents, metadatas
    
    def vectorize_and_store(self, documents, metadatas):
        """Vectorize and store directly in Pinecone using v2 API"""
        index = self.initialize_index()
        
        # Prepare batches (max 100 vectors per upsert operation)
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            batch_docs = documents[i:end_idx]
            batch_meta = metadatas[i:end_idx]
            
            # Get embeddings for this batch
            embeddings = self.embedding_model.encode(batch_docs, convert_to_numpy=True)

            
            # Prepare vectors for upsert
            vectors = []
            for j, (doc, embedding) in enumerate(zip(batch_docs, embeddings)):
                vectors.append({
                    "id": f"vec_{i+j}",
                    "values": embedding,
                    "metadata": {
                        **batch_meta[j],
                        "text": doc  # Include the text in metadata
                    }
                })
            
            # Upsert to Pinecone
            index.upsert(vectors=vectors)
            
            print(f"Processed batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")

if __name__ == "__main__":
    # Initialize components
    db_manager = VectorDBManager()
    
    # Process data
    documents, metadatas = db_manager.process_data("data/changi_airport_full_data_cleaned.json")
    
    # Vectorize and store
    db_manager.vectorize_and_store(documents, metadatas)
    print(f"✅ Successfully stored {len(documents)} vectors in Pinecone")