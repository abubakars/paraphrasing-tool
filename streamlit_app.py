import streamlit as st
import re
from random import choice, shuffle

# --- NLP imports ---
import nltk
from nltk.corpus import wordnet as wn
from nltk import pos_tag, word_tokenize, download

# Ensure required NLTK data is available
nltk_data = ["punkt", "averaged_perceptron_tagger", "wordnet", "omw-1.4"]
for pkg in nltk_data:
    try:
        nltk.data.find(pkg)
    except LookupError:
        download(pkg)

# --- Utility functions ---

POS_MAP = {
    'JJ': wn.ADJ,
    'JJR': wn.ADJ,
    'JJS': wn.ADJ,
    'NN': wn.NOUN,
    'NNS': wn.NOUN,
    'NNP': wn.NOUN,
    'NNPS': wn.NOUN,
    'RB': wn.ADV,
    'RBR': wn.ADV,
    'RBS': wn.ADV,
    'VB': wn.VERB,
    'VBD': wn.VERB,
    'VBG': wn.VERB,
    'VBN': wn.VERB,
    'VBP': wn.VERB,
    'VBZ': wn.VERB,
}

CITATION_REGEX = re.compile(r"\([^\)]*\d{4}[^\)]*\)|\[\d+\]")


def preserve_citations(text):
    """Replace citations with placeholders and return mapping."""
    placeholders = {}
    def repl(m):
        ph = f"__CITE_{len(placeholders)}__"
        placeholders[ph] = m.group(0)
        return ph
    t = CITATION_REGEX.sub(repl, text)
    return t, placeholders


def restore_citations(text, placeholders):
    for ph, val in placeholders.items():
        text = text.replace(ph, val)
    return text


def get_synonyms(word, pos):
    synsets = wn.synsets(word, pos=pos)
    lemmas = set()
    for s in synsets:
        for l in s.lemmas():
            name = l.name().replace('_', ' ')
            if name.lower() != word.lower():
                lemmas.add(name)
    return list(lemmas)


def choose_synonym(word, penn_pos, strength=0.5):
    # Map Penn tag to WordNet POS
    wn_pos = POS_MAP.get(penn_pos)
    if not wn_pos:
        return None
    syns = get_synonyms(word, wn_pos)
    if not syns:
        return None
    # Heuristic: shorter synonyms for conservative, more variety for aggressive
    if strength < 0.4:
        syns = [s for s in syns if abs(len(s) - len(word)) <= 3]
    # Filter out synonyms with punctuation or numeric
    syns = [s for s in syns if re.match(r"^[A-Za-z\s-]+$", s)]
    if not syns:
        return None
    return choice(syns)


def reorder_clause(sentence):
    # Very simple clause reordering: move leading adverbial clause after main clause if comma found
    if ',' in sentence:
        parts = [p.strip() for p in sentence.split(',')]
        if len(parts) >= 2:
            # swap first two parts sometimes
            parts[0], parts[1] = parts[1], parts[0]
            return ', '.join(parts)
    return sentence


def paraphrase_sentence(sentence, strength=0.5):
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    new_tokens = []
    replacements = []
    for (tok, tag) in tagged:
        # Skip punctuation and numbers
        if re.match(r"^[\W_]+$", tok) or re.match(r"^\d+$", tok):
            new_tokens.append(tok)
            continue
        # Try synonym replacement based on strength
        import random
        if random.random() < strength:
            syn = choose_synonym(tok, tag, strength)
            if syn:
                # keep capitalization
                if tok[0].isupper():
                    syn = syn.capitalize()
                new_tokens.append(syn)
                replacements.append((tok, syn))
                continue
        new_tokens.append(tok)
    out = ' '.join(new_tokens)
    # fix spacing for punctuation
    out = re.sub(r"\s+([.,;:?!])", r"\1", out)
    # reordering for stronger paraphrase
    if strength > 0.6:
        out = reorder_clause(out)
    return out, replacements


def paraphrase_text(text, strength=0.5):
    text, placeholders = preserve_citations(text)
    sentences = nltk.sent_tokenize(text)
    new_sentences = []
    all_replacements = []
    for s in sentences:
        new_s, reps = paraphrase_sentence(s, strength)
        new_sentences.append(new_s)
        all_replacements.extend(reps)
    out = ' '.join(new_sentences)
    out = restore_citations(out, placeholders)
    return out, all_replacements

# --- Streamlit UI ---

st.set_page_config(page_title="Rule-based Academic Paraphraser", layout="wide")
st.title("Rule-based Academic Paraphrasing Tool (No AI)")
st.markdown(
    "A Streamlit app that paraphrases using deterministic NLP methods (WordNet synonyms, simple clause reordering).\n\nDesigned for academic learning — keeps citations intact and provides highlighted replacements."
)

col1, col2 = st.columns([3,1])
with col1:
    text = st.text_area("Paste your academic text here", height=300)
    strength_label = st.select_slider("Paraphrase strength (conservative → aggressive)",
                                      options=["0.2","0.4","0.6","0.8"], value="0.4")
    strength = float(strength_label)
    preserve_caps = st.checkbox("Preserve original capitalization where possible", value=True)
    if st.button("Paraphrase"):
        if not text.strip():
            st.warning("Please enter some text to paraphrase.")
        else:
            with st.spinner("Paraphrasing..."):
                out, reps = paraphrase_text(text, strength=strength)
            st.success("Paraphrasing complete — review replacements below.")
            st.text_area("Paraphrased text", value=out, height=300)
            if reps:
                st.markdown("**Replacements made (original → replacement):**")
                for a,b in reps[:200]:
                    st.write(f"{a} → {b}")
            else:
                st.info("No synonyms were substituted (text may already be concise or no matching synonyms found).")
            st.download_button("Download paraphrased text", out, file_name="paraphrased.txt")

with col2:
    st.markdown("## Tips & Notes")
    st.markdown(
        "- This tool does **not** use large language models — it uses WordNet and simple heuristics.\n- It is best for learning how sentences can be rephrased; check the output for technical accuracy and disciplinary style.\n- Citations like (Smith et al., 2020) or [1] are preserved automatically.\n- For better results, rewrite long sentences into simpler clauses before paraphrasing."
    )
    st.markdown("---")
    st.markdown("## Limitations")
    st.markdown(
        "- Synonym replacement is context-free; some substitutions may be inappropriate for technical terms.\n- The app avoids changing numbers, citations and punctuation.\n- For publication-grade rewriting, a human editor is recommended."
    )

st.markdown("---")
st.markdown("Built as an educational tool — credit: rule-based paraphrasing using NLTK & WordNet.")
