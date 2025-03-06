# Task 2: Changi Airport Chatbot

## Overview
This project is a Retrieval-Augmented Generation (RAG) chatbot designed to answer queries about Changi Airport. It integrates web scraping, vector databases (Pinecone), and OpenAI's GPT model with LangChain to retrieve relevant information before generating responses.


## Features
- **Web Scraping:** Extracts relevant information from Changi Airport's website.
- **Vector Database:** Stores extracted text embeddings using Pinecone.
- **Retrieval-Augmented Generation (RAG):** Retrieves relevant context before generating responses.
- **Flask API:** Provides a RESTful interface for chatbot interaction.
- **Cloud Deployment:** Hosted on Google Cloud Run for scalable access.

## Web Scraping
The web scraper extracts information from Changi Airport's website using Selenium and BeautifulSoup. The scraper:
1. Navigates the main page and extracts all main navigation links.
2. Visits each page and collects headings, sub-headings, and paragraphs.
3. Stores the scraped data in `changi_airport_full_data.json` for later retrieval.


## Chatbot API
The chatbot is accessible via a Flask API, which retrieves relevant context from Pinecone before generating a response using OpenAI's GPT model.

### API Endpoint
**Base URL:** `https://chatbot-598837118358.us-central1.run.app`

**Endpoint:**
```
POST /chatbot
```
**Example Request:**
```json
{
    "query": "What activities are available at Changi Airport?"
}
```
**Example Response:**
```json
{
    "query": "What activities are available at Changi Airport?",
    "response": "Changi Airport offers a variety of activities including shopping, dining, entertainment, and relaxation at lounges."
}
```

## Testing the API with Postman
1. Open Postman.
2. Select `POST` request.
3. Enter the deployed API URL: `https://chatbot-598837118358.us-central1.run.app/chatbot`
4. Go to the `Body` tab, select `raw`, and choose `JSON`.
5. Enter the test query:
   ```json
   {
       "query": "What attractions are available at Changi Airport?"
   }
   ```
6. Click `Send` to receive the chatbot's response.


---