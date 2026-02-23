import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# --- Configuration ---
# Streamlit Cloud will securely inject your API key from its Secrets manager
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Initialize the model with Google Search Grounding enabled
model = genai.GenerativeModel(
    'gemini-1.5-pro',
    tools='google_search_retrieval'
)

def extract_text_from_pdf(pdf_file):
    """Extracts text from the uploaded PDF document."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page].extract_text()
    return text

def analyze_deal(text):
    """Prompts the AI to extract data and search the web."""
    prompt = f"""
    You are an expert commercial real estate analyst. Extract the following from the provided OM text. 
    If a detail is missing, write "Not provided".

    PROPERTY DETAILS FROM DOCUMENT:
    - Mobile Home Park Name & Address
    - Broker Name & Brokerage Company
    - Is this an all-age park or 55+?
    - How many total lots are in the park?
    - How many Park Owned Homes (POH)?
    - How many Tenant Owned Homes (TOH)?
    - What is the lot rent? What is the market lot rent for the area?
    - Who pays for the water, sewer, and trash?
    - Financials: Cap Rate for the park, NOI, Asking Price, Gross Rent Income, Total Park Expenses

    INTERNET SEARCH REQUIRED (Based on the property's city/state):
    - City Population and Population Growth Rate
    - Median Household Income and Median Home Price
    - Who are the major employers in the city (Healthcare, Agriculture, Manufacturing, Education, Government)?
    - Is there a Walmart in the city?

    DOCUMENT TEXT:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

# --- Streamlit UI ---
st.title("🌐 Smart MHP Deal Analyzer")
st.write("Upload an OM to extract property details and fetch live market data.")

uploaded_file = st.file_uploader("Upload PDF Document", type="pdf")

if uploaded_file is not None:
    if not API_KEY:
        st.error("API Key is missing! Please configure it in Streamlit Secrets.")
    else:
        with st.spinner("Extracting text from PDF..."):
            document_text = extract_text_from_pdf(uploaded_file)
            
        st.success("Document read! AI is analyzing the deal and searching the internet...")
        
        with st.spinner("Compiling market report..."):
            analysis_result = analyze_deal(document_text)
            
        st.subheader("Extraction & Market Results")
        st.write(analysis_result)