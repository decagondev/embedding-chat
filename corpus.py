import openai
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

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

embeddings = []
for document in corpus:
    embedding_response = openai.Embedding.create(
        input=document,
        model="text-embedding-ada-002"
    )
    embeddings.append(embedding_response['data'][0]['embedding'])

query = "What is Fred's favorite color?"

query_embedding_response = openai.Embedding.create(
    input=query,
    model="text-embedding-ada-002"
)
query_embedding = query_embedding_response['data'][0]['embedding']

similarities = [cosine_similarity(np.array(query_embedding), np.array(embedding)) for embedding in embeddings]

most_similar_index = np.argmax(similarities)
closest_document = corpus[most_similar_index]
closest_file_name = file_names[most_similar_index]

print(f"The closest document to the query is from file '{closest_file_name}':")
print(f"Content: '{closest_document}'")
print(f"Similarity score: {similarities[most_similar_index]:.4f}")
