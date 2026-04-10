import fitz  # PyMuPDF

def load_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        return doc
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return None


def get_pages(doc, pages):
    if pages == "all":
        return list(range(len(doc)))
    
    return [int(p) - 1 for p in pages.split(",")]