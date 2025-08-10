import streamlit as st
import nltk
from nltk.corpus import wordnet as wn
import random
import re

# Download datasets (small)
nltk.download("wordnet")
nltk.download("omw-1.4")

st.set_page_config(page_title="Academic Paraphraser", layout="wide")
st.title("Professional Academic & Scientific Paraphraser (No AI, No Roman Numbers)")

# Phrase replacements for more formal tone
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
    "for the purpose of": "for",
    "this shows that": "this demonstrates that",
    "this means": "this indicates",
    "good": "beneficial",
    "bad": "detrimental"
}

# Preferred academic vocabulary
preferred_academic_words = {
    "use": "utilize",
    "show": "demonstrate",
    "get": "obtain",
    "find": "determine",
    "start": "commence",
    "end": "terminate",
    "help": "assist",
    "try": "attempt",
    "need": "require"
}

def get_synonym(word):
    """Return academic synonym if available."""
    if word.lower() in preferred_academic_words:
        return preferred_academic_words[word.lower()].capitalize() if word[0].isupper() else preferred_academic_words[word.lower()]
    synsets = wn.synsets(word)
    synonyms = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            name = lemma.name().replace("_", " ")
            if name.lower() != word.lower():
                if name.isalpha() and len(name) <= 15:
                    synonyms.add(name)
    if synonyms:
        return random.choice(list(synonyms))
    return None

def apply_phrase_bank(text):
    for old, new in phrase_replacements.items():
        text = re.sub(rf"\b{re.escape(old)}\b", new, text, flags=re.IGNORECASE)
    return text

def restructure_sentences(text):
    """Academic-style restructuring."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    structured = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        # Reorder for formal flow
        s = re.sub(r"^(Because|Although|Since) (.+?), (.+)$", r"\1 \2, \3", s)
        # Merge short sentences
        if len(s.split()) < 8 and structured:
            structured[-1] = structured[-1].rstrip(".") + ", and " + s[0].lower() + s[1:]
        else:
            structured.append(s)
    return " ".join(structured)

def paraphrase(text, replace_prob=0.3):
    text = apply_phrase_bank(text)
    words = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    new_words = []
    for w in words:
        # Keep numbers and avoid Roman numerals
        if re.match(r"^\d+([\.,]\d+)*%?$", w):
            new_words.append(w)
            continue
        # Skip Roman numerals entirely
        if re.match(r"^(?=[MDCLXVI])(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$", w, flags=re.IGNORECASE):
            new_words.append(w)  # Just keep original without converting
            continue
        if re.match(r"^\w+$", w) and random.random() < replace_prob:
            syn = get_synonym(w)
            if syn:
                new_words.append(syn if w.islower() else syn.capitalize())
                continue
        new_words.append(w)
    result = "".join([w if re.match(r"[^\w\s]", w) else " " + w for w in new_words]).strip()
    result = restructure_sentences(result)
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
