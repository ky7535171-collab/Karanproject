""" BHARATIYA JNANA PARAMPARA - STREAMLIT DIGITIZATION PROTOTYPE Run: pip install streamlit pandas streamlit run iks_streamlit_app.py """

import csv
import io
import json
import random
import sqlite3
import time
import unicodedata

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Bharatiya Jnana Parampara | Digital Archive",
    page_icon="ЁЯУЬ",
    layout="wide",
)

# ----------------------------- DATA ---------------------------------
CATALOGUE = [
    {"id":"IKS-001","title":"Rigveda","script":"Devanagari","creator":"Traditional Vedic rishis","period":"c. 1500тАУ1200 BCE (approx.)","domain":"Vedic literature"},
    {"id":"IKS-002","title":"Arthashastra","script":"Devanagari","creator":"Kautilya (traditional attribution)","period":"date and layers debated","domain":"Statecraft and economics"},
    {"id":"IKS-003","title":"Charaka Samhita","script":"Devanagari","creator":"Charaka (traditional attribution)","period":"composite text; dates debated","domain":"Ayurveda and medicine"},
    {"id":"IKS-004","title":"Sushruta Samhita","script":"Devanagari","creator":"Sushruta (traditional attribution)","period":"composite text; dates debated","domain":"Ayurveda and surgery"},
    {"id":"IKS-005","title":"Aryabhatiya","script":"Devanagari","creator":"Aryabhata","period":"499 CE","domain":"Mathematics and astronomy"},
    {"id":"IKS-006","title":"Brahmasphutasiddhanta","script":"Devanagari","creator":"Brahmagupta","period":"628 CE","domain":"Mathematics and astronomy"},
    {"id":"IKS-007","title":"Ashtadhyayi","script":"Devanagari","creator":"Panini","period":"c. 5thтАУ4th century BCE (approx.)","domain":"Grammar and linguistics"},
    {"id":"IKS-008","title":"Lilavati","script":"Devanagari","creator":"Bhaskaracharya","period":"12th century CE","domain":"Mathematics"},
    {"id":"IKS-009","title":"Natyashastra","script":"Devanagari","creator":"Bharata Muni (traditional attribution)","period":"composite text; dates debated","domain":"Performing arts"},
    {"id":"IKS-010","title":"Yoga Sutras","script":"Devanagari","creator":"Patanjali (traditional attribution)","period":"date debated","domain":"Philosophy and yoga"},
    {"id":"IKS-011","title":"Sulba Sutras","script":"Devanagari","creator":"Baudhayana and other authors","period":"early first millennium BCE (approx.)","domain":"Geometry"},
    {"id":"IKS-012","title":"Vaisheshika Sutra","script":"Devanagari","creator":"Kanada (traditional attribution)","period":"date debated","domain":"Natural philosophy"},
]

VOWELS = {"рдЕ":"a","рдЖ":"─Б","рдЗ":"i","рдИ":"─л","рдЙ":"u","рдК":"┼л","рдЛ":"с╣Ы","рдП":"e","рдР":"ai","рдУ":"o","рдФ":"au"}
MATRAS = {"рд╛":"─Б","рд┐":"i","реА":"─л","реБ":"u","реВ":"┼л","реГ":"с╣Ы","реЗ":"e","реИ":"ai","реЛ":"o","реМ":"au"}
CONS = {"рдХ":"k","рдЦ":"kh","рдЧ":"g","рдШ":"gh","рдЩ":"с╣Е","рдЪ":"c","рдЫ":"ch","рдЬ":"j","рдЭ":"jh","рдЮ":"├▒","рдЯ":"с╣н","рда":"с╣нh","рдб":"с╕Н","рдв":"с╕Нh","рдг":"с╣З","рдд":"t","рде":"th","рдж":"d","рдз":"dh","рди":"n","рдк":"p","рдл":"ph","рдм":"b","рдн":"bh","рдо":"m","рдп":"y","рд░":"r","рд▓":"l","рд╡":"v","рд╢":"┼Ы","рд╖":"с╣г","рд╕":"s","рд╣":"h"}
VIRAMA = "реН"
OTHER = {"рдВ":"с╣Г","рдГ":"с╕е","рдБ":"m╠Р","рд╜":"тАЩ","реР":"oс╣Г","ред":"ред","рее":"рее"}

CORPUS = [
    ("V-01","Rigveda 3.62.10","реР рднреВрд░реНрднреБрд╡рдГ рд╕реНрд╡рдГ рддрддреНрд╕рд╡рд┐рддреБрд░реНрд╡рд░реЗрдгреНрдпрдВ рднрд░реНрдЧреЛ рджреЗрд╡рд╕реНрдп рдзреАрдорд╣рд┐ рдзрд┐рдпреЛ рдпреЛ рдирдГ рдкреНрд░рдЪреЛрджрдпрд╛рддреН"),
    ("V-02","Bhagavad Gita 2.47","рдХрд░реНрдордгреНрдпреЗрд╡рд╛рдзрд┐рдХрд╛рд░рд╕реНрддреЗ рдорд╛ рдлрд▓реЗрд╖реБ рдХрджрд╛рдЪрди ред рдорд╛ рдХрд░реНрдордлрд▓рд╣реЗрддреБрд░реНрднреВрд░реНрдорд╛ рддреЗ рд╕рдЩреНрдЧреЛрд╜рд╕реНрддреНрд╡рдХрд░реНрдордгрд┐ рее"),
    ("V-03","Yoga Sutra 1.2","рдпреЛрдЧрд╢реНрдЪрд┐рддреНрддрд╡реГрддреНрддрд┐рдирд┐рд░реЛрдзрдГ"),
    ("V-04","Isha Upanishad 1","рдИрд╢рд╛рд╡рд╛рд╕реНрдпрдорд┐рджрдВ рд╕рд░реНрд╡рдВ рдпрддреНрдХрд┐рдЮреНрдЪ рдЬрдЧрддреНрдпрд╛рдВ рдЬрдЧрддреН"),
    ("V-05","Brihadaranyaka Upanishad 1.3.28","рдЕрд╕рддреЛ рдорд╛ рд╕рджреНрдЧрдордп рддрдорд╕реЛ рдорд╛ рдЬреНрдпреЛрддрд┐рд░реНрдЧрдордп рдореГрддреНрдпреЛрд░реНрдорд╛рдореГрддрдВ рдЧрдордп"),
]

CONFUSIONS = {"рдм":"рд╡","рд╡":"рдм","рдШ":"рдз","рдз":"рдШ","рдо":"рдн","рдн":"рдо","рдЯ":"рда","рда":"рдЯ","рди":"рдг","рдг":"рди","рд╕":"рд╢","рд╢":"рд╕"}
CONCEPTS = {
    "Ashtadhyayi":"Rule-based grammar",
    "Aryabhatiya":"Mathematical computation",
    "Brahmasphutasiddhanta":"Arithmetic and zero",
    "Sulba Sutras":"Geometrical construction",
    "Yoga Sutras":"Structured philosophical concepts",
    "Sushruta Samhita":"Organised procedural knowledge",
}

# -------------------------- CORE FUNCTIONS --------------------------
def to_iast(text):
    """Limited educational Devanagari-to-IAST mapping."""
    result, i = [], 0
    while i < len(text):
        ch = text[i]
        if ch in CONS:
            result.append(CONS[ch])
            nxt = text[i+1] if i+1 < len(text) else ""
            if nxt == VIRAMA:
                i += 2
                continue
            if nxt in MATRAS:
                result.append(MATRAS[nxt])
                i += 2
                continue
            result.append("a")
        elif ch in VOWELS:
            result.append(VOWELS[ch])
        elif ch in MATRAS:
            result.append(MATRAS[ch])
        elif ch in OTHER:
            result.append(OTHER[ch])
        else:
            result.append(ch)
        i += 1
    return "".join(result)

def fold(text):
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.replace("с╣З","n").replace("с╣Г","m").replace("с╕е","h").replace("┼Ы","s").replace("с╣г","s").replace("с╣н","t").replace("с╕Н","d").replace("с╣Ы","r")

def search_corpus(query):
    q = fold(query.strip())
    if not q:
        return []
    found = []
    for ident, source, devanagari in CORPUS:
        roman = to_iast(devanagari)
        if q in fold(roman):
            found.append({"ID":ident, "Source":source, "Devanagari":devanagari, "IAST":roman})
    return found

def distance(a, b):
    prev = list(range(len(b)+1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j]+1, cur[-1]+1, prev[j-1]+(x != y)))
        prev = cur
    return prev[-1]

def cer(ref, hyp):
    return distance(ref, hyp) / max(1, len(ref))

def wer(ref, hyp):
    return distance(ref.split(), hyp.split()) / max(1, len(ref.split()))

def noise(text, rate, seed=9):
    rng = random.Random(seed)
    out = []
    for ch in text:
        if ch in CONFUSIONS and rng.random() < rate:
            out.append(CONFUSIONS[ch])
        elif ch != " " and rng.random() < rate/10:
            continue
        else:
            out.append(ch)
    return "".join(out)

def evaluate(rate):
    refs = [x[2] for x in CORPUS]
    hyps = [noise(x, rate, 9+i) for i, x in enumerate(refs)]
    return (
        sum(cer(a,b) for a,b in zip(refs,hyps))/len(refs),
        sum(wer(a,b) for a,b in zip(refs,hyps))/len(refs),
    )

def build_graph_data():
    nodes, edges = set(), []
    for item in CATALOGUE:
        title, author, domain = item["title"], item["creator"], item["domain"]
        nodes.update([title, author, domain])
        edges.extend([
            {"From":title, "Relation":"attributed_to", "To":author},
            {"From":title, "Relation":"belongs_to", "To":domain},
        ])
    for title, concept in CONCEPTS.items():
        nodes.update([title, concept])
        edges.append({"From":title, "Relation":"illustrates", "To":concept})
    return nodes, edges

def build_db():
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.executescript(""" CREATE TABLE Author(AuthorID INTEGER PRIMARY KEY, Name TEXT, Era TEXT); CREATE TABLE Manuscript(ManuscriptID INTEGER PRIMARY KEY, Title TEXT, Language TEXT, Script TEXT, Category TEXT, AuthorID INTEGER REFERENCES Author(AuthorID)); CREATE TABLE Digitization(DigitizationID INTEGER PRIMARY KEY, ManuscriptID INTEGER UNIQUE REFERENCES Manuscript(ManuscriptID), ScanDate TEXT, Format TEXT, Resolution TEXT); CREATE TABLE Repository(RepositoryID INTEGER PRIMARY KEY, Name TEXT, Location TEXT, DigitizationID INTEGER REFERENCES Digitization(DigitizationID)); CREATE TABLE User(UserID INTEGER PRIMARY KEY, Name TEXT, AccessLevel TEXT); """)
    authors = [(1,"Charaka","Ancient"),(2,"Sushruta","Ancient"),(3,"Vagbhata","Classical"),(4,"Unknown","Unknown"),(5,"Kautilya","Mauryan")]
    manus = [
        (1,"Charaka Samhita","Sanskrit","Devanagari","Ayurveda",1),
        (2,"Sushruta Samhita","Sanskrit","Devanagari","Ayurveda",2),
        (3,"Ashtanga Hridayam","Sanskrit","Devanagari","Ayurveda",3),
        (4,"Surya Siddhanta","Sanskrit","Devanagari","Astronomy",4),
        (5,"Arthashastra (Excerpt)","Sanskrit","Devanagari","Governance",5),
    ]
    digi = [
        (1,1,"2026-08-10","PDF / OCR-Text","600 dpi"),
        (2,2,"2026-08-11","Image / TIFF","600 dpi"),
        (3,3,"2026-08-12","PDF","300 dpi"),
        (4,4,"2026-08-13","Scanned Image","400 dpi"),
        (5,5,"2026-08-14","PDF / OCR-Text","600 dpi"),
    ]
    db.executemany("INSERT INTO Author VALUES(?,?,?)", authors)
    db.executemany("INSERT INTO Manuscript VALUES(?,?,?,?,?,?)", manus)
    db.executemany("INSERT INTO Digitization VALUES(?,?,?,?,?)", digi)
    db.executemany("INSERT INTO Repository VALUES(?,?,?,?)", [(d[0],"BJP Digital Archive","Server-1",d[0]) for d in digi])
    db.executemany("INSERT INTO User VALUES(?,?,?)", [(1,"Researcher","Full"),(2,"Student","Read"),(3,"Public","Read")])
    return db

def search_db(db, keyword):
    start = time.perf_counter()
    like = f"%{keyword}%"
    rows = db.execute(""" SELECT 'DR-' || printf('%03d', m.ManuscriptID), m.Title, a.Name, m.Language, d.Format, m.Category FROM Manuscript m JOIN Author a ON a.AuthorID = m.AuthorID JOIN Digitization d ON d.ManuscriptID = m.ManuscriptID WHERE m.Title LIKE ? OR a.Name LIKE ? OR m.Language LIKE ? OR m.Category LIKE ? ORDER BY m.ManuscriptID """, (like,)*4).fetchall()
    return rows, time.perf_counter() - start

# ----------------------------- UI -----------------------------------
st.markdown(""" <style> .stApp {background: #f5f0e7;} [data-testid="stSidebar"] {background: #eee3d4;} h1, h2, h3 {color: #6b1717;} div[data-testid="stMetric"] {background: #fffaf2; padding: 14px; border: 1px solid #dfcdb9; border-radius: 10px;} </style> """, unsafe_allow_html=True)

st.title("ЁЯУЬ Bharatiya Jnana Parampara")
st.caption("Digitization Prototype | Indian Knowledge Systems")
st.sidebar.title("Digital Archive")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Manuscript Catalogue", "Devanagari тЖТ IAST", "Sanskrit Text Search",
     "OCR Evaluation", "Knowledge Graph", "Database Search"],
)
st.sidebar.info("Educational prototype using illustrative catalogue and sample text records.")

if page == "Dashboard":
    st.header("Digital Archive Dashboard")
    c1,c2,c3 = st.columns(3)
    c1.metric("Catalogue Records", len(CATALOGUE))
    c2.metric("Digitized Passages", len(CORPUS))
    c3.metric("Database Tables", 5)
    st.subheader("Project Modules")
    st.markdown(""" - **Manuscript Catalogue:** browse and download catalogue records. - **Transliteration:** convert supported Devanagari characters into IAST. - **Sanskrit Text Search:** search sample digitized passages using Romanized text. - **OCR Evaluation:** view simulated Character Error Rate (CER) and Word Error Rate (WER). - **Knowledge Graph:** inspect links between texts, authors, domains and concepts. - **Database Search:** search sample manuscript records stored in SQLite. """)
    st.warning("The OCR module uses simulated character substitutions and deletions. It is not a real OCR engine.")

elif page == "Manuscript Catalogue":
    st.header("Digital Manuscript Catalogue")
    df = pd.DataFrame(CATALOGUE)
    col1,col2 = st.columns(2)
    domain = col1.selectbox("Filter by domain", ["All"] + sorted(df["domain"].unique().tolist()))
    keyword = col2.text_input("Search title or creator")
    filtered = df.copy()
    if domain != "All":
        filtered = filtered[filtered["domain"] == domain]
    if keyword:
        mask = filtered.astype(str).apply(lambda col: col.str.contains(keyword, case=False, na=False)).any(axis=1)
        filtered = filtered[mask]
    st.caption(f"{len(filtered)} record(s) displayed")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button("тмЗя╕П Download catalogue CSV", df.to_csv(index=False).encode("utf-8-sig"),
                       "catalogue.csv", "text/csv")
    st.download_button("тмЗя╕П Download catalogue JSON",
                       json.dumps(CATALOGUE, ensure_ascii=False, indent=2).encode("utf-8"),
                       "catalogue.json", "application/json")

elif page == "Devanagari тЖТ IAST":
    st.header("Devanagari to IAST Transliteration")
    st.write("Enter Devanagari text below. This is a limited educational mapping, not a full Vedic transliterator.")
    sample = "рдпреЛрдЧрд╢реНрдЪрд┐рддреНрддрд╡реГрддреНрддрд┐рдирд┐рд░реЛрдзрдГ"
    text_input = st.text_area("Devanagari input", value=sample, height=120)
    if st.button("Transliterate", type="primary"):
        st.subheader("IAST Output")
        st.code(to_iast(text_input), language=None)
    st.caption("Example: рдпреЛрдЧрд╢реНрдЪрд┐рддреНрддрд╡реГрддреНрддрд┐рдирд┐рд░реЛрдзрдГ")

elif page == "Sanskrit Text Search":
    st.header("Search Digitized Sanskrit Passages")
    query = st.text_input("Search Romanized Sanskrit", placeholder="Try: karma, yoga, gamaya")
    st.caption("Search is performed against the IAST transliteration of the sample corpus.")
    if query:
        hits = search_corpus(query)
        st.success(f"{len(hits)} result(s) found")
        if hits:
            for hit in hits:
                with st.container(border=True):
                    st.subheader(f'{hit["Source"]} ┬╖ {hit["ID"]}')
                    st.write("**Devanagari:**", hit["Devanagari"])
                    st.write("**IAST:**", hit["IAST"])
        else:
            st.info("No matching passage found. Try another keyword.")
    else:
        st.write("Sample passages")
        for ident, source, passage in CORPUS:
            with st.container(border=True):
                st.markdown(f"**{source} ┬╖ {ident}**")
                st.write(passage)

elif page == "OCR Evaluation":
    st.header("Synthetic OCR Error Evaluation")
    st.warning("This is a simulation, not real OCR processing. Errors are generated using predefined character confusions and occasional deletions.")
    rates = [0.05, 0.10, 0.20, 0.30]
    rows = []
    for rate in rates:
        c,w = evaluate(rate)
        rows.append({"Noise Rate":f"{rate:.0%}", "Average CER":round(c,3), "Average WER":round(w,3)})
    result_df = pd.DataFrame(rows)
    st.dataframe(result_df, use_container_width=True, hide_index=True)
    st.line_chart(result_df.set_index("Noise Rate")[["Average CER","Average WER"]])
    rate = st.slider("Select noise rate for sample", 0.0, 0.5, 0.2, 0.05)
    original = CORPUS[0][2]
    corrupted = noise(original, rate)
    a,b = st.columns(2)
    a.markdown("**Reference text**")
    a.write(original)
    b.markdown("**Simulated OCR output**")
    b.write(corrupted)
    st.metric("Sample CER", f"{cer(original, corrupted):.3f}")
    st.metric("Sample WER", f"{wer(original, corrupted):.3f}")

elif page == "Knowledge Graph":
    st.header("Knowledge Graph")
    nodes, edges = build_graph_data()
    st.metric("Total Nodes", len(nodes))
    st.metric("Total Edges", len(edges))
    edge_df = pd.DataFrame(edges)
    selected = st.selectbox("Select a manuscript", sorted(CATALOGUE, key=lambda x:x["title"]), format_func=lambda x:x["title"])
    title = selected["title"]
    st.subheader(f"Connections for {title}")
    related = edge_df[edge_df["From"] == title]
    if not related.empty:
        st.dataframe(related, use_container_width=True, hide_index=True)
    else:
        st.info("No additional concept link is listed for this manuscript.")
    with st.expander("View all graph relationships"):
        st.dataframe(edge_df, use_container_width=True, hide_index=True)
    with st.expander("View all graph nodes"):
        st.write(sorted(nodes))

elif page == "Database Search":
    st.header("SQLite Manuscript Database")
    st.caption("The prototype creates five tables: Author, Manuscript, Digitization, Repository and User.")
    db = build_db()
    keyword = st.text_input("Search by title, author, language or category", placeholder="Try: ayurveda, sanskrit, astronomy, kautilya")
    if keyword:
        rows, elapsed = search_db(db, keyword)
        st.success(f"{len(rows)} result(s) found")
        st.caption(f"Response time: {elapsed:.6f} seconds")
        if rows:
            result_df = pd.DataFrame(rows, columns=["Record ID","Title","Author","Language","Format","Category"])
            st.dataframe(result_df, use_container_width=True, hide_index=True)
        else:
            st.info("No matching records. Try another keyword.")
    else:
        st.write("Sample database records")
        rows, _ = search_db(db, "")
        st.dataframe(pd.DataFrame(rows, columns=["Record ID","Title","Author","Language","Format","Category"]),
                     use_container_width=True, hide_index=True)
    with st.expander("Database schema"):
        st.code("""Author(AuthorID, Name, Era) Manuscript(ManuscriptID, Title, Language, Script, Category, AuthorID) Digitization(DigitizationID, ManuscriptID, ScanDate, Format, Resolution) Repository(RepositoryID, Name, Location, DigitizationID) User(UserID, Name, AccessLevel)""")

st.divider()
st.caption("Bharatiya Jnana Parampara тАУ Digitization Prototype | Indian Knowledge Systems")
