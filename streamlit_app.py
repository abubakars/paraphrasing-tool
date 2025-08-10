import streamlit as st
import nltk
from nltk.corpus import wordnet as wn
import random
import re

# Download small datasets
nltk.download("wordnet")
nltk.download("omw-1.4")

st.set_page_config(page_title="Academic Paraphraser", layout="wide")
st.title("Academic Paraphraser")

# --- Academic phrase bank ---
phrase_replacements = {
    "in order to": "to",
    "due to the fact that": "because",
    "in the course of": "during",
    "it is important to note that": "notably",
    "a number of": "several",
    "with regard to": "regarding",
    "on the other hand": "conversely",
    "as a result": "therefore",
    "in addition": "moreover",
    "for the purpose of": "for"
}

# Common academic-friendly synonyms filter
common_academic_words = set([
    "method", "approach", "process", "concept", "analysis",
    "data", "information", "research", "study", "finding",
    "increase", "decrease", "significant", "relevant",
    "important", "use", "apply", "result", "impact", "affect"
])

def get_synonym(word):
    """Get a natural academic synonym if available."""
    synsets = wn.synsets(word)
    synonyms = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            name = lemma.name().replace("_", " ")
            if name.lower() != word.lower():
                if " " not in name and name.isalpha() and len(name) <= 12:
                    synonyms.add(name)
    if synonyms:
        filtered = [s for s in synonyms if s.lower() in common_academic_words]
        if filtered:
            return random.choice(filtered)
        return random.choice(list(synonyms))
    return None

def apply_phrase_bank(text):
    """Replace phrases with academic-friendly versions."""
    for old, new in phrase_replacements.items():
        text = re.sub(rf"\b{re.escape(old)}\b", new, text, flags=re.IGNORECASE)
    return text

def add_transitions(text):
    """Insert transitions to make flow more human."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    transitions = ["However,", "Moreover,", "Therefore,"]
    for i in range(1, len(sentences)):
        if random.random() < 0.15:
            sentences[i] = transitions[i % len(transitions)] + " " + sentences[i][0].lower() + sentences[i][1:]
    return " ".join(sentences)

def paraphrase(text, replace_prob=0.3):
    """Replace words with synonyms and humanize tone, preserving numbers."""
    text = apply_phrase_bank(text)
    words = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    new_words = []
    for w in words:
        # Skip numbers (integers, decimals, years, citations)
        if re.match(r"^\d+([\.,]\d+)*%?$", w):
            new_words.append(w)
            continue
        # Replace normal words with synonyms occasionally
        if re.match(r"^\w+$", w) and random.random() < replace_prob:
            syn = get_synonym(w)
            if syn:
                if w[0].isupper():
                    syn = syn.capitalize()
                new_words.append(syn)
                continue
        new_words.append(w)
    result = "".join(
        [w if re.match(r"[^\w\s]", w) else " " + w for w in new_words]
    ).strip()
    result = add_transitions(result)
    return result

# --- UI ---
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
