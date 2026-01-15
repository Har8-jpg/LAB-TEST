import streamlit as st
import nltk
from nltk.tokenize import sent_tokenize
from PyPDF2 import PdfReader

# Download required NLTK resources
nltk.download("punkt")
nltk.download("punkt_tab")

st.set_page_config(
    page_title="Text Chunking using NLTK",
    layout="wide"
)

st.title("📄 Text Chunking using NLTK Sentence Tokenizer")
st.write("Extract text from a PDF and perform semantic sentence chunking.")

uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_pdf is not None:
    reader = PdfReader(uploaded_pdf)

    # Step 2: Extract text from PDF
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + " "

    st.success("PDF text extracted successfully.")

    # Step 3: Sentence tokenization
    sentences = sent_tokenize(full_text)

    st.subheader("📌 Extracted Sentences (Index 58–68)")

    if len(sentences) >= 68:
        selected_sentences = sentences[58:69]

        for i, sentence in enumerate(selected_sentences, start=58):
            st.write(f"**Sentence {i}:** {sentence}")
    else:
        st.warning("The document does not contain enough sentences.")

    # Step 4: Semantic Chunking Output
    st.subheader("🧠 Semantic Sentence Chunking Result")
    st.write(selected_sentences)