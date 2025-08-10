import streamlit as st
import re
import random
import nltk
import language_tool_python
from nltk.corpus import wordnet as wn

# Download NLTK data (only runs the first time)
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("wordnet")
nltk.download("omw-1.4")

# Initialize grammar checker
tool = language_tool_python.LanguageTool('en-US')

# Preferred academic replacements
preferred_academic_words = {
    "show": "demonstrate",
    "prove": "establish",
    "get": "obtain",
    "start": "commence",
    "keep": "maintain",
    "help": "assist",
    "try": "endeavour",
    "need": "require",
    "use": "utilize",
    "find": "discover",
    "big": "substantial",
    "small": "minute",
    "good": "beneficial",
    "bad": "detrimental",
    "think": "consider",
    "say": "assert",
    "tell": "inform",
    "begin": "initiate",
    "important": "significant",
    "main": "primary"
}

# Words for numbers to avoid changing
number_words = {
    "zero","one","two","three","four","five","six","seven","eight","nine","ten",
    "eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen",
    "twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety","hundred","thousand",
    "first","second","third","fourth","fifth","sixth","seventh","eighth","ninth","tenth",
    "eleventh","twelfth","thirteenth","fourteenth","fifteenth","sixteenth","seventeenth","eighteenth","nineteenth",
    "twentieth","thirtieth","fortieth","fiftieth","sixtieth","seventieth","eightieth","ninetieth","hundredth","thousandth"
}

# Function to get safe academic synonym
def get_synonym(word):
    if word.lower() in preferred_academic_words:
        return preferred_academic_words[word.lower()].capitalize() if word[0].isupper() else preferred_academic_words[word.lower()]
    
    if word.lower() in number_words or any(char.isdigit() for char in word):
        return None

    synonyms = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            name = lemma.name().replace("_", " ")
            if (
                name.lower() != word.lower()
                and name.isalpha()
                and len(name) <= 15
                and not re.match(r"^(?=[MDCLXVI]{2,}$)(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$", name)
                and not name.isupper()
            ):
                synonyms.add(name)

    return random.choice(list(synonyms)) if synonyms else None

# Paraphrase function
def paraphrase_text(text, strength=0.4):
    tokens = nltk.word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    new_tokens = []

    for word, pos in pos_tags:
        if re.match(r"^[^\w]+$", word):
            new_tokens.append(word)
            continue

        if pos.startswith(("NN", "VB", "JJ", "RB")) and random.random() < strength:
            synonym = get_synonym(word)
            new_tokens.append(synonym if synonym else word)
        else:
            new_tokens.append(word)

    return " ".join(new_tokens)

# Grammar correction function
def correct_grammar(text):
    matches = tool.check(text)
    return language_tool_python.utils.correct(text, matches)

# Streamlit UI
st.title("Academic Paraphrasing & Grammar Tool (Non-AI)")
st.write("Rewrites text into an academic tone and checks grammar, preserving numbers. No AI used.")

input_text = st.text_area("Enter your text:", height=200)
strength = st.slider("Paraphrasing Strength", 0.0, 1.0, 0.4)

if st.button("Paraphrase & Correct"):
    if input_text.strip():
        paraphrased = paraphrase_text(input_text, strength)
        corrected = correct_grammar(paraphrased)
        st.subheader("Paraphrased & Corrected Output")
        st.write(corrected)
    else:
        st.warning("Please enter some text.")
