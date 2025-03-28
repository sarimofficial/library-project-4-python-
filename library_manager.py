import datetime
import json
import os
import time
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie

# Load lottie animation for the sidebar
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None
import requests
from fpdf import FPDF
import base64

# Set page configuration
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'library' not in st.session_state:
    st.session_state.library = []
if 'uploaded_pdfs' not in st.session_state:
    st.session_state.uploaded_pdfs = []
if 'selected_book' not in st.session_state:
    st.session_state.selected_book = None
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'library'

# Create uploads directory if not exists
os.makedirs("uploads", exist_ok=True)

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def load_library():
    if os.path.exists("library.json"):
        with open("library.json", "r") as file:
            st.session_state.library = json.load(file)

def save_library():
    with open("library.json", "w") as file:
        json.dump(st.session_state.library, file)

def add_book(title, author, publication_year, genre, read_status, pdf_file=None):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_status,
        "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pdf_file": pdf_file.name if pdf_file else None
    }
    st.session_state.library.append(book)
    
    if pdf_file:
        with open(os.path.join("uploads", pdf_file.name), "wb") as f:
            f.write(pdf_file.getbuffer())
    
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        # Remove associated PDF if exists
        if st.session_state.library[index].get("pdf_file"):
            try:
                os.remove(os.path.join("uploads", st.session_state.library[index]["pdf_file"]))
            except:
                pass
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        time.sleep(0.5)

def create_pdf_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Library Report", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=1, align="C")
    
    for book in st.session_state.library:
        pdf.cell(200, 10, txt=f"Title: {book['title']}", ln=1)
        pdf.cell(200, 10, txt=f"Author: {book['author']}", ln=1)
        pdf.cell(200, 10, txt=f"Year: {book['publication_year']}", ln=1)
        pdf.cell(200, 10, txt=f"Genre: {book['genre']}", ln=1)
        pdf.cell(200, 10, txt=f"Status: {'Read' if book['read_status'] else 'Unread'}", ln=1)
        pdf.cell(200, 10, txt="-"*50, ln=1)
    
    return pdf.output(dest="S").encode("latin-1")

# Load the library data
load_library()

# Sidebar Navigation
st.sidebar.markdown("<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_0yfsb3a1.json")
if lottie_book:
    st_lottie(lottie_book, speed=1, height=200, key="book_animation")

nav_options = st.sidebar.radio("Choose an Option:", 
                             ["📚 View Library", "➕ Add Books", "📋 Display All Books", 
                              "📊 Library Statistics", "📤 Export Library"])

if nav_options == "📚 View Library":
    st.session_state.current_view = "library"
elif nav_options == "➕ Add Books":
    st.session_state.current_view = "add"
elif nav_options == "📋 Display All Books":
    st.session_state.current_view = "all_books"
elif nav_options == "📊 Library Statistics":
    st.session_state.current_view = "stats"
elif nav_options == "📤 Export Library":
    st.session_state.current_view = "export"

# Main Content
st.markdown("<h1 style='text-align: center;'>Personal Library Manager</h1>", unsafe_allow_html=True)

if st.session_state.current_view == "add":
    st.markdown("<h2>➕ Add a New Book</h2>", unsafe_allow_html=True)
    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", 
                                            min_value=1000, 
                                            max_value=datetime.datetime.now().year, 
                                            step=1, 
                                            value=2023)
        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Mystery", 
                                         "Science Fiction", "Fantasy", "Other"])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True) == "Read"
            pdf_file = st.file_uploader("Upload PDF (optional)", type=["pdf"])
        
        submit_button = st.form_submit_button(label='Add Book')

        
        
        if submit_button and title and author:
            add_book(title, author, publication_year, genre, read_status, pdf_file)
            if st.session_state.book_added:
                st.success("Book added successfully!")
                st.balloons()
                st.session_state.book_added = False

elif st.session_state.current_view == "library":
    st.markdown("<h2>📚 View Library</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.warning("No books in the library.")
    else:
        search_term = st.text_input("🔍 Search by title or author", max_chars=100)
        search_results = [book for book in st.session_state.library 
                        if search_term.lower() in book['title'].lower() or 
                        search_term.lower() in book['author'].lower()] if search_term else []
        
        if search_term and not search_results:
            st.error("No matching books found.")
        
        books_to_display = search_results if search_results else st.session_state.library
        
        if st.session_state.selected_book:
            book = st.session_state.selected_book
            st.markdown("---")
            st.markdown(f"""
                <h3>📖 {book['title']}</h3>
                <p><b>Author:</b> {book['author']}</p>
                <p><b>Year:</b> {book['publication_year']}</p>
                <p><b>Genre:</b> {book['genre']}</p>
                <p><b>Status:</b> {'✅ Read' if book['read_status'] else '❌ Unread'}</p>
                <p><b>Date Added:</b> {book['date_added']}</p>
            """, unsafe_allow_html=True)
            
            if book.get("pdf_file"):
                with open(os.path.join("uploads", book["pdf_file"]), "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
            
            google_books_link = f"https://books.google.com.pk/books?q={book['title'].replace(' ', '+')}+{book['author'].replace(' ', '+')}"
            st.markdown(f"[🔍 Search on Google Books]({google_books_link})", unsafe_allow_html=True)
            
            if st.button("🔙 Back to Library"):
                st.session_state.selected_book = None
                st.rerun()
        else:
            for i, book in enumerate(books_to_display):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                        <h4>{book['title']}</h4>
                        <p><i>Author:</i> {book['author']}</p>
                        <p><i>Year:</i> {book['publication_year']}</p>
                        <p><i>Genre:</i> {book['genre']}</p>
                        <p><i>Status:</i> {'✅ Read' if book['read_status'] else '❌ Unread'}</p>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button(f"👁️ View", key=f"view_{i}"):
                        st.session_state.selected_book = book
                        st.rerun()
                    if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                        remove_book(i)
                        st.rerun()
                st.markdown("---")

elif st.session_state.current_view == "all_books":
    st.markdown("<h2>📋 All Books</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.warning("No books in the library.")
    else:
        df = pd.DataFrame(st.session_state.library)
        st.dataframe(df)

elif st.session_state.current_view == "stats":
    st.markdown("<h2>📊 Library Statistics</h2>", unsafe_allow_html=True)
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    unread_books = total_books - read_books
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Books", value=total_books)
    with col2:
        st.metric(label="Read Books", value=read_books)
    with col3:
        st.metric(label="Unread Books", value=unread_books)
    
    fig = px.pie(names=["Read", "Unread"], values=[read_books, unread_books], 
                title="Reading Status", hole=0.3)
    st.plotly_chart(fig)
    
    genre_counts = pd.DataFrame(st.session_state.library)['genre'].value_counts()
    fig2 = px.bar(genre_counts, title="Books by Genre")
    st.plotly_chart(fig2)

elif st.session_state.current_view == "export":
    st.markdown("<h2>📤 Export Library</h2>", unsafe_allow_html=True)
    if st.button("Generate PDF Report"):
        pdf_data = create_pdf_report()
        st.download_button(
            label="Download PDF Report",
            data=pdf_data,
            file_name="library_report.pdf",
            mime="application/pdf"
        )
    
    if st.button("Export to JSON"):
        st.download_button(
            label="Download JSON",
            data=json.dumps(st.session_state.library, indent=4),
            file_name="library_export.json",
            mime="application/json"
        )

# PDF Management in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("<h3>📂 PDF Management</h3>", unsafe_allow_html=True)
uploaded_pdf = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_pdf:
    if uploaded_pdf.name not in [pdf.get("pdf_file") for pdf in st.session_state.library if pdf.get("pdf_file")]:
        st.session_state.uploaded_pdfs.append(uploaded_pdf.name)
        with open(os.path.join("uploads", uploaded_pdf.name), "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        st.sidebar.success("PDF uploaded successfully!")
    else:
        st.sidebar.warning("A PDF with this name already exists.")

st.sidebar.markdown("<h4>Uploaded PDFs</h4>", unsafe_allow_html=True)
for pdf in os.listdir("uploads"):
    st.sidebar.markdown(f"📄 {pdf}")

    # Footer
st.markdown("---")
st.write("📌 **All Right Received @2025 Created by Muhammad Sarim  **")
