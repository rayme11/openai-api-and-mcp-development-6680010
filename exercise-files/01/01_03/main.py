from colorama import Fore
import streamlit as st
from pathlib import Path
import tempfile
from openai import OpenAI
import os
from dotenv import load_dotenv
from utils import speech_to_text, speech_to_translation, text_to_speech, save_file

# Load environment variables
load_dotenv()

client = OpenAI()

# Streamlit App
st.title("🔊 Audio transcriptions & Translations (Audio API)")  # Add a title

# Custom style
st.markdown(
    """
    <style>
        .stButton>button {
            background-color: transparent;
            border: 1px solid #3498db;
            float: right;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    textarea {
        color: #3498db;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# User input
with st.form("user_form", clear_on_submit=True):
    uploaded_file = st.file_uploader("Choose a file")
    submit_button = st.form_submit_button(label="Submit")

# Placeholder to allow clearing output between submissions
output_placeholder = st.empty()

# Process the uploaded file
if submit_button and uploaded_file is not None:
    output_placeholder.empty()  # Clear any previous output

    with st.spinner("Transcribing..."):
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(uploaded_file.name)[1]
        ) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name

            print(f"Temporary file created at: {temp_file_path}")
            filename = temp_file_path.split("/")[-1]
            st.success("File processed successfully!")
            original_text = speech_to_text(temp_file_path)

    with output_placeholder.container():
        st.divider()
        st.subheader("📝 Transcription")
        st.text_area("Original Text", value=original_text, height=200)

    with st.spinner("Translating..."):
        pass
