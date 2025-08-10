import streamlit as st
import nltk
from nltk.corpus import wordnet as wn
import random
import re

# Ensure small datasets are available
nltk.download("wordnet")
nltk.download("omw-1.4")

st.set_page_config(page_title="Simple Academic Paraphraser", layout="wide")
st.title("Simple Rule-Based Paraphraser (No AI)")

def get_synonym(word):
    """Get one synonym from WordNet if available."""
    synsets = wn.synsets(word)
    synonyms = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            name = lemma.name().replace("_", " ")
            if name.lower() != word.lower():
                synonyms.add(name)
    if synonyms:
        return random.choice(list(synonyms))
    return None

def paraphrase(text, replace_prob=0.3):
    """Replace words with synonyms at given probability."""
    words = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)  # keep punctuation separate
    new_words = []
    for w in words:
        if re.match(r"^\w+$", w) and random.random() < replace_prob:
            syn = get_synonym(w)
            if syn:
                if w[0].isupper():
                    syn = syn.capitalize()
                new_words.append(syn)
                continue
        new_words.append(w)
    return "".join(
        [w if re.match(r"[^\w\s]", w) else " " + w for w in new_words]
    ).strip()

text = st.text_area("Paste your text here:", height=200)

replace_strength = st.slider("Replacement strength", 0.0, 1.0, 0.3)

if st.button("Paraphrase"):
    if not text.strip():
        st.warning("Please enter some text.")
    else:
        output = paraphrase(text, replace_strength)
        st.subheader("Paraphrased Text")
        st.write(output)
        st.download_button("Download Result", output, file_name="paraphrased.txt")
