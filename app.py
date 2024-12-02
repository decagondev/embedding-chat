import openai
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

favorite_colors = [
    "Freds favorite color is Red",
    "Wilmas favorite color is Blue",
    "Bettys favorite color is Green"
]
embeddings = []
for i in range(len(favorite_colors)):
    embedding_response = openai.Embedding.create(
        input=favorite_colors[i],
        model="text-embedding-ada-002"
    )
    embeddings.append(embedding_response['data'][0]['embedding'])


query = "What is Wilma's favorite color?"

query_embedding_response = openai.Embedding.create(
    input=query,
    model="text-embedding-ada-002"
)
query_embedding = query_embedding_response['data'][0]['embedding']

similarities = [cosine_similarity(np.array(query_embedding), np.array(embedding)) for embedding in embeddings]

most_similar_index = np.argmax(similarities)
closest_document = favorite_colors[most_similar_index]

print(f"The closest document to the query is: '{closest_document}' with a similarity score of {similarities[most_similar_index]:.4f}")















