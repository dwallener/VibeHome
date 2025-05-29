import os
os.environ["TRANSFORMERS_NO_TF"] = "1"

import streamlit as st
import json
from sentence_transformers import SentenceTransformer, util

# crap to avoid other crap
import sys
import types
import torch

# Monkey patch torch.classes to not break Streamlit watcher
if not hasattr(torch, "classes"):
    torch.classes = types.SimpleNamespace()
elif "__path__" not in dir(torch.classes):
    torch.classes.__path__ = types.SimpleNamespace(_path=[])


# Load ZIP code data
with open("vibehome_zipcode_tags.json", "r") as f:
    zip_data = json.load(f)

# Prepare text corpus
zip_texts = [f"{item['zip']} - {'; '.join(item['tags'])}" for item in zip_data]
zip_tags = [item['tags'] for item in zip_data]
zip_codes = [item['zip'] for item in zip_data]

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Streamlit UI
st.set_page_config(page_title="VibeHome", page_icon="🏠")
st.title("🏠 VibeHome")
st.write("Describe the life you want to live. We’ll suggest neighborhoods that match your vibe.")

query = st.text_input("Your vibe:", placeholder="I'm a beach-loving version of Andy Warhol")

if query:
    query_embedding = model.encode(query, convert_to_tensor=True)
    corpus_embeddings = model.encode(zip_texts, convert_to_tensor=True)
    scores = util.cos_sim(query_embedding, corpus_embeddings)[0]

    top_k = 5
    top_indices = scores.argsort(descending=True)[:top_k]

    st.subheader("🔍 Top Matching ZIP Codes")
    for idx in top_indices:
        zip_code = zip_codes[idx]
        tags = zip_tags[idx]
        st.markdown(f"**{zip_code}**  \nTags: `{', '.join(tags)}`  \nScore: {scores[idx].item():.3f}")

