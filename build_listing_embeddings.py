import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Load listings
with open("listings_by_coordinates.json", "r") as f:
    listings = json.load(f)

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Embed and attach to listings
for listing in tqdm(listings, desc="Embedding listings"):
    text = f"{listing.get('address', '')}, {listing.get('city', '')}. {listing.get('description', '')}"
    embedding = model.encode(text).tolist()
    listing["embedding"] = embedding

# Save with embeddings
with open("listings_with_embeddings.json", "w") as f:
    json.dump(listings, f, indent=2)

print(f"✅ Embedded {len(listings)} listings and saved to listings_with_embeddings.json")