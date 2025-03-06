# Use an official lightweight Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app


# Install dependencies directly
RUN pip install --no-cache-dir \
    flask \
    python-dotenv \
    sentence-transformers \
    langchain \
    langchain-openai \
    langchain-huggingface \
    pinecone-client \
    langchain-pinecone \
    langchain-core \
    gunicorn
# Copy the rest of the application code
COPY chatbot.py . 
COPY .env .

# Step 4: Pre-download model inside Docker
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-roberta-large-v1')"

# Expose the port Flask runs on
EXPOSE 8080


# Command to run the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "chatbot:app"]
