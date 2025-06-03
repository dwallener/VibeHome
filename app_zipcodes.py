import os
import json
import streamlit as st
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer, util

# Load ZIP/tag data
with open("vibehome_zipcode_tags.json", "r") as f:
    zip_data = json.load(f)

# Prepare text data for embedding
zip_texts = [f"{item['zip']} - {'; '.join(item['tags'])}" for item in zip_data]
zip_codes = [item['zip'] for item in zip_data]
zip_tags = [item['tags'] for item in zip_data]

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Streamlit app UI
st.set_page_config(page_title="VibeHome", page_icon="🏠")
st.title("🏠 VibeHome")
st.write("Describe the life you want to live. We’ll suggest Miami ZIP codes that match your vibe.")

query = st.text_input("Your vibe:", placeholder="I'm a beach-loving version of Andy Warhol")

if query:
    # Encode user query
    query_embedding = model.encode(query, convert_to_tensor=True)
    corpus_embeddings = model.encode(zip_texts, convert_to_tensor=True)

    # Compute similarity scores
    scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
    top_k = 5
    top_indices = scores.argsort(descending=True)[:top_k]

    # 🎯 Vibe Score Graph
    st.subheader("📊 Vibe Score")
    top_scores = [scores[i].item() for i in top_indices]
    top_labels = [zip_codes[i] for i in top_indices]

    fig, ax = plt.subplots()
    ax.barh(top_labels, top_scores, color="skyblue")
    ax.invert_yaxis()
    ax.set_xlabel("Semantic Similarity")
    ax.set_title("Top Matches")
    st.pyplot(fig)

    # 🗺️ List matching ZIPs with Google Maps links
    st.subheader("🔍 Matching Neighborhoods")
    for idx in top_indices:
        zip_code = zip_codes[idx]
        tags = zip_tags[idx]
        score = scores[idx].item()

        st.markdown(f"### {zip_code}")
        st.markdown(f"**Tags:** `{', '.join(tags)}`")
        st.markdown(f"**Vibe Score:** {score:.3f}")
        st.markdown(f"[📍 View on Google Maps](https://www.google.com/maps/place/{zip_code})")
        st.markdown("---")
