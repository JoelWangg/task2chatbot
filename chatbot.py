from sentence_transformers import SentenceTransformer
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os

# 🔹 Load environment variables
load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ✅ Initialize Flask app
app = Flask(__name__)


# ✅ Use HuggingFaceEmbeddings to ensure compatibility
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-roberta-large-v1")

# ✅ Connect to Pinecone using the same embeddings
pinecone_index_name = "changi-chatbot"
vector_store = PineconeVectorStore(index_name=pinecone_index_name, embedding=embedding_model)

# ✅ Retrieval mechanism (use same embeddings for searching)
retriever = vector_store.as_retriever(search_kwargs={"k": 7})  # Retrieve top 7 documents

# ✅ Use OpenAI for answering
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key, temperature=0.4)

# ✅ Define Prompt Template
prompt_template = PromptTemplate(
    template="""
    You are a chatbot, use the following context to answer the question accurately:
    
    Context: {context}
    
    Question: {question}
    
    Answer:""",
    input_variables=["context", "question"]
)

# ✅ RAG Pipeline
def retrieve_context(query):
    """Retrieve relevant context from Pinecone"""
    docs = retriever.invoke(query)

    # ✅ Debugging: Print retrieved documents
    print("\n🔍 Retrieved Documents from Pinecone:")
    for i, doc in enumerate(docs):
        print(f"\n📄 Document {i+1}:\n{doc.page_content}\n")

    return "\n\n".join([doc.page_content for doc in docs])

@app.route("/chatbot", methods=["POST"])
def chat():
    """Accepts a query and returns chatbot response."""
    data = request.json
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    rag_chain = (
        RunnableLambda(retrieve_context)  # Retrieve context
        | (lambda ctx: {"context": ctx, "question": query})  # Prepare query
        | prompt_template  # Format prompt
        | llm  # Call GPT
        | StrOutputParser()  # Extract answer
    )

    answer = rag_chain.invoke(query)
    return jsonify({"query": query, "response": answer})

    
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),  # <-- Critical change
        debug=os.environ.get("DEBUG", "false").lower() == "true"  # Safer debug handling
    )