import openai
from pinecone import Pinecone
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index = os.getenv("PINECONE_INDEX")

pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(pinecone_index)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

corpus_directory = "./corpus"

corpus = []
file_names = []

for file_name in os.listdir(corpus_directory):
    if file_name.endswith(".txt"):
        file_path = os.path.join(corpus_directory, file_name)
        with open(file_path, "r", encoding="utf-8") as file:
            corpus.append(file.read())
            file_names.append(file_name)

for i, document in enumerate(corpus):
    embedding_response = openai.Embedding.create(
        input=document,
        model="text-embedding-ada-002"
    )
    embedding = embedding_response['data'][0]['embedding']

    index.upsert([(file_names[i], embedding)])

def chat_with_context(query):
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
    
    match = query_results['matches'][0]
    closest_document = corpus[file_names.index(match['id'])]
    similarity_score = match['score']
    
    # Prepare context for the chat
    context = f"Context from document '{match['id']}':\n{closest_document}\n\nQuery: {query}"

    # Send the context and query to OpenAI's Chat API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": context}
        ]
    )

    # Output the response
    return response['choices'][0]['message']['content']

# Simple chat interface
print("Chat Interface (type 'exit' to quit)")
while True:
    user_query = input("\nYour query: ")
    if user_query.lower() == "exit":
        print("Exiting chat. Goodbye!")
        break
    
    chat_response = chat_with_context(user_query)
    print("\nAssistant Response:")
    print(chat_response)
