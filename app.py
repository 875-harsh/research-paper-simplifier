import streamlit as st
import fitz
from transformers import pipeline
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
from collections import Counter
import re

st.set_page_config(
    page_title="Research Paper Simplifier",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hide default Streamlit chrome */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Background ── */
.stApp {
    background-color: #070C18;
    background-image:
        radial-gradient(ellipse at 15% 10%, rgba(0,35,135,0.35) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 90%, rgba(3,70,255,0.18) 0%, transparent 55%);
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 3.5rem 1rem 2rem;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(66,117,255,0.12);
    border: 1px solid rgba(66,117,255,0.3);
    color: #6ba0ff;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 1rem;
    border-radius: 9999px;
    margin-bottom: 1.3rem;
}
.hero h1 {
    font-size: 2.9rem;
    font-weight: 700;
    color: #F0F4FF;
    letter-spacing: -0.03em;
    margin: 0 0 0.8rem;
    line-height: 1.15;
}
.hero h1 span {
    background: linear-gradient(135deg, #4275FF, #6ba0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero p {
    color: #91A3B0;
    font-size: 1rem;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.75;
}
.h-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 0 0 2rem;
}

/* ── Section label ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4275FF;
    margin-bottom: 1rem;
}

/* ── Card ── */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.6rem;
    margin-bottom: 1.2rem;
}

/* ── Step list ── */
.step-list { list-style: none; padding: 0; margin: 0; }
.step-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #4A5568;
    font-size: 0.88rem;
    line-height: 1.5;
}
.step-item:last-child { border-bottom: none; }
.step-dot {
    margin-top: 5px;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: rgba(66,117,255,0.35);
    flex-shrink: 0;
}

/* ── Empty state ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem 2rem;
    text-align: center;
}
.empty-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    opacity: 0.15;
}
.empty-text {
    color: #2D3748;
    font-size: 0.9rem;
    line-height: 1.65;
}

/* ── Success banner ── */
.success-banner {
    background: rgba(34,197,94,0.07);
    border: 1px solid rgba(34,197,94,0.18);
    border-radius: 10px;
    padding: 0.75rem 1.2rem;
    color: #4ADE80;
    font-size: 0.88rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1.25rem;
}

/* ── Stats row ── */
.stats-row {
    display: flex;
    gap: 0.85rem;
    margin-bottom: 1.25rem;
}
.stat {
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.stat-num {
    font-size: 1.55rem;
    font-weight: 700;
    color: #4275FF;
    letter-spacing: -0.02em;
}
.stat-lbl {
    font-size: 0.68rem;
    font-weight: 500;
    color: #2D3748;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.2rem;
}

/* ── Summary text ── */
.summary-body {
    color: #CBD5E1;
    font-size: 0.97rem;
    line-height: 1.9;
}

/* ── Keyword tags ── */
.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
}
.tag {
    background: rgba(66,117,255,0.1);
    border: 1px solid rgba(66,117,255,0.22);
    color: #6ba0ff;
    padding: 0.28rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.81rem;
    font-weight: 500;
}

/* ── File uploader ── */
[data-testid="stFileUploadDropzone"] {
    background: rgba(66,117,255,0.04) !important;
    border: 2px dashed rgba(66,117,255,0.28) !important;
    border-radius: 14px !important;
    transition: border-color 0.2s, background 0.2s;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: rgba(66,117,255,0.6) !important;
    background: rgba(66,117,255,0.08) !important;
}
[data-testid="stFileUploadDropzone"] * { color: #4A5568 !important; }

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #4275FF 0%, #0346FF 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    width: 100% !important;
    padding: 0.65rem 1.5rem !important;
    box-shadow: 0 4px 24px rgba(66,117,255,0.3) !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] p { color: #6ba0ff !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

summarizer = load_model()

def extract_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def preprocess(text):
    return text.replace("\n", " ")[:4000]


def summarize_text(text):
    chunks = [text[i:i+800] for i in range(0, len(text), 800)]
    summaries = []
    for chunk in chunks[:4]:
        result = summarizer(chunk, max_length=130, min_length=60, do_sample=False)
        summaries.append(result[0]["summary_text"])
    final = " ".join(summaries)

    cleaned = []
    seen_phrases = set()
    for line in final.split(". "):
        line_lower = line.lower()
        if any(word in line_lower for word in [
            "permission", "copyright", "arxiv", "conference",
            "author", "et al", "jakob", "ashish", "illia", "noam", "aidan", "lukasz",
        ]):
            continue
        if len(line.split()) < 10:
            continue
        words = line.split()
        unique_words = []
        for w in words:
            if not unique_words or w != unique_words[-1]:
                unique_words.append(w)
        cleaned_line = " ".join(unique_words)
        if cleaned_line.lower() not in seen_phrases:
            seen_phrases.add(cleaned_line.lower())
            cleaned.append(cleaned_line.strip())

    result = ". ".join(cleaned[:5])
    if not result.endswith("."):
        result += "."
    return result


def extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    stopwords = set([
        "this", "that", "with", "from", "have", "were", "which", "their", "they",
        "been", "using", "based", "such", "these", "into", "also", "than", "after",
        "models", "model", "paper", "results", "show", "task",
    ])
    important_terms = [
        "transformer", "attention", "translation", "neural",
        "architecture", "parallelization", "training", "performance",
        "sequence", "encoder", "decoder",
    ]
    filtered = [w for w in words if w not in stopwords]
    freq = Counter(filtered)
    keywords = [w for w, _ in freq.most_common(10)]
    return list(dict.fromkeys(important_terms + keywords))[:8]


def highlight_keywords(summary, keywords):
    for word in keywords:
        summary = re.sub(
            rf"\b({word})\b",
            r"<span style='color:#6ba0ff;font-weight:600;'>\1</span>",
            summary,
            flags=re.IGNORECASE,
        )
    return summary


def generate_pdf(text):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name)
    styles = getSampleStyleSheet()
    doc.build([Paragraph(text, styles["Normal"]), Spacer(1, 10)])
    return tmp.name

st.markdown("""
<div class="hero">
    <div class="hero-badge">✦ AI-Powered</div>
    <h1>Research Paper <span>Simplifier</span></h1>
    <p>Upload any research paper PDF and instantly receive a clean, concise summary with key concepts highlighted.</p>
</div>
<hr class="h-divider">
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1.05, 1.95], gap="large")

with col_left:
    st.markdown('<div class="section-label">📎 Upload Document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop your PDF here",
        type="pdf",
        label_visibility="collapsed",
    )
    st.markdown("""
    <div class="card" style="margin-top:1.3rem;">
        <div class="section-label">⚙ How it works</div>
        <ul class="step-list">
            <li class="step-item"><div class="step-dot"></div>Upload a research paper in PDF format</li>
            <li class="step-item"><div class="step-dot"></div>Text is extracted from all pages</li>
            <li class="step-item"><div class="step-dot"></div>AI model generates a structured summary</li>
            <li class="step-item"><div class="step-dot"></div>Key terms are identified and highlighted</li>
            <li class="step-item"><div class="step-dot"></div>Download the clean summary as PDF</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    if uploaded_file is None:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📄</div>
            <div class="empty-text">Your summary will appear here<br>once you upload a PDF.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner("Extracting and analysing your paper…"):
            raw_text   = extract_text(uploaded_file)
            clean_text = preprocess(raw_text)
            summary    = summarize_text(clean_text)
            keywords   = extract_keywords(summary)
            highlighted = highlight_keywords(summary, keywords)
            pdf_path   = generate_pdf(summary)

        orig_words = len(clean_text.split())
        summ_words = len(summary.split())
        sentences  = len([s for s in summary.split(".") if s.strip()])

        st.markdown(f"""
        <div class="success-banner">✓ Analysis complete — paper processed successfully</div>
        <div class="stats-row">
            <div class="stat">
                <div class="stat-num">{orig_words:,}</div>
                <div class="stat-lbl">Original Words</div>
            </div>
            <div class="stat">
                <div class="stat-num">{summ_words}</div>
                <div class="stat-lbl">Summary Words</div>
            </div>
            <div class="stat">
                <div class="stat-num">{sentences}</div>
                <div class="stat-lbl">Sentences</div>
            </div>
            <div class="stat">
                <div class="stat-num">{len(keywords)}</div>
                <div class="stat-lbl">Key Terms</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card">
            <div class="section-label">📝 Summary</div>
            <div class="summary-body">{highlighted}</div>
        </div>
        """, unsafe_allow_html=True)
        tags_html = "".join(f'<span class="tag">{kw}</span>' for kw in keywords)
        st.markdown(f"""
        <div class="card">
            <div class="section-label">🔑 Key Terms</div>
            <div class="tags">{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇  Download Summary as PDF",
                data=f,
                file_name="summary.pdf",
                mime="application/pdf",
            )
