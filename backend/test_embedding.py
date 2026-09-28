from app.services.embeddings import generate_embedding

text = "Artificial Intelligence is transforming healthcare."

embedding = generate_embedding(text)

print("Length:", len(embedding))
print(embedding[:10])