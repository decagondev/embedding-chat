import os
import openai
from pinecone import Pinecone
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index = os.getenv("PINECONE_INDEX")

pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(pinecone_index)

app = Flask(__name__)
CORS(app)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Endpoint to upload a text file for embedding and storing in Pinecone.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    file_content = file.read().decode("utf-8")
    file_name = file.filename

    embedding_response = openai.Embedding.create(
        input=file_content,
        model="text-embedding-ada-002"
    )
    embedding = embedding_response['data'][0]['embedding']

    metadata = {
        "file_name": file_name,
        "content": file_content[:5000],
        "length": len(file_content)
    }

    index.upsert([(file_name, embedding, metadata)])

    return jsonify({"message": f"File '{file_name}' uploaded and vectorized successfully."}), 200

@app.route("/chat", methods=["POST"])
def chat():
    """
    Endpoint to chat using the uploaded documents as context.
    """
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "Query not provided"}), 400

    query_embedding_response = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002"
    )
    query_embedding = query_embedding_response['data'][0]['embedding']

    query_results = index.query(
        vector=query_embedding,
        top_k=1,
        include_metadata=True
    )

    if not query_results['matches']:
        return jsonify({"error": "No matching documents found."}), 404

    match = query_results['matches'][0]
    metadata = match['metadata']
    similarity_score = match['score']

    context = f"Context from document '{metadata['file_name']}':\n{metadata['content']}...\n\nQuery: {query}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": context}
        ]
    )

    assistant_response = response['choices'][0]['message']['content']

    return jsonify({
        "query": query,
        "response": assistant_response,
        "similarity_score": similarity_score,
        "document_metadata": metadata
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)