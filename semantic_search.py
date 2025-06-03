import json
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load listing embeddings
with open("listings_with_embeddings.json", "r") as f:
    listings = json.load(f)

# Build embedding matrix and metadata
embedding_matrix = np.array([listing["embedding"] for listing in listings], dtype=np.float32)
metadata = [listing for listing in listings]

# User input
query = input("Describe your vibe: ")  # e.g., "I'm a beach-loving version of Andy Warhol"

# Embed query
query_embedding = model.encode(query)

# Compute similarity
scores = util.cos_sim(query_embedding, embedding_matrix)[0].cpu().numpy()

# Get top matches
top_k = 5
top_indices = scores.argsort()[::-1][:top_k]

# Print matches
print("\nTop vibe-matched listings:")
for i in top_indices:
    listing = metadata[i]
    print(f"\n🏡 {listing['address']}, {listing['city']}")
    print(f"💲 {listing['price']} | 🛏 {listing['beds']} | 🛁 {listing['baths']} | 📐 {listing['sqft']} sqft")
    print(f"🖼️ {listing['image_urls'][0] if listing['image_urls'] else 'No image'}")
    print(f"✨ Score: {scores[i]:.4f}")
    