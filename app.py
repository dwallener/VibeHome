import json
import streamlit as st
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer, util
import torch

# Load listings with precomputed embeddings
with open("listings_with_embeddings.json", "r") as f:
    listings = json.load(f)

# Separate metadata and embeddings
listing_texts = []
embeddings = []
for listing in listings:
    listing_texts.append(listing["description"] or "")
    embeddings.append(torch.tensor(listing["embedding"]))

# Stack into single tensor
embedding_tensor = torch.stack(embeddings)

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Streamlit UI
st.set_page_config(page_title="VibeHome", page_icon="🏠")
st.title("🏠 VibeHome")
st.write("Describe the life you want to live. We’ll find homes that match your vibe.")

query = st.text_input("Your vibe:", placeholder="I'm a beach-loving version of Andy Warhol")

if query:
    # Embed the query
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Make sure both tensors are on same device (CPU)
    query_embedding = query_embedding.cpu()
    embedding_tensor = embedding_tensor.cpu()

    # Compute similarity scores
    scores = util.cos_sim(query_embedding, embedding_tensor)[0]
    top_k = 5
    top_indices = scores.argsort(descending=True)[:top_k]

    # Plot vibe scores
    st.subheader("📊 Vibe Score")
    fig, ax = plt.subplots()
    top_scores = [scores[i].item() for i in top_indices]
    # top_labels = [listings[i]["address"] for i in top_indices]
    top_listings = [listings[i] for i in top_indices]
    top_labels = [
        str(listing.get("address") or "Unknown") 
        for listing in top_listings
    ]    
    ax.barh(top_labels, top_scores, color="skyblue")
    ax.invert_yaxis()
    ax.set_xlabel("Semantic Similarity")
    ax.set_title("Top Matching Listings")
    st.pyplot(fig)

    # Show listing cards
    st.subheader("🏡 Top Listings")
    for i in top_indices:
        l = listings[i]
        st.markdown(f"### {l['address']}, {l['city']}")
        st.markdown(f"💲 {l['price']} | 🛏 {l['beds']} | 🛁 {l['baths']} | 📐 {l['sqft']} sqft")
        if l.get("image_urls"):
            st.image(l["image_urls"][0], width=400)
        st.markdown(f"✨ Score: {scores[i].item():.4f}")
        st.markdown("---")