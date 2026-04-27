import fitz  # PyMuPDF
import io

def extract_text_from_pdf(file):
    """Extract text from PDF, supporting both file paths and uploaded file objects."""
    try:
        if hasattr(file, "read"):  # Streamlit UploadedFile or file-like object
            file_bytes = file.read()
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        elif isinstance(file, (str, bytes)):  # Path or bytes
            doc = fitz.open(file)
        else:
            raise ValueError("Unsupported file type for PDF extraction.")

        text = ""
        for page in doc:
            text += page.get_text()

        return text
    except Exception as e:
        return f"Error extracting text from PDF: {e}"
