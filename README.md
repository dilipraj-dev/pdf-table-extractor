# 📄 PDF Table Extraction System

---

## 🚀 Objective

Develop a Python-based solution to extract structured table data from financial PDF documents and output them in JSON, Markdown, and HTML formats. The system supports multi-page and multi-document processing.

---

## 🐍 Python Version Requirement

Python 3.10 or 3.11 is recommended for compatibility with all dependencies.

Using newer versions (e.g., Python 3.12+) may cause installation or runtime issues with some libraries.

---

## ⚠️ Additional System Requirement

### Ghostscript (Required for Camelot)

This project uses Camelot for table extraction, which requires Ghostscript to be installed on the system.

If Ghostscript is not installed, the program may fail to extract tables.

---

### 🪟 Windows Installation

1. Download Ghostscript from:
   https://www.ghostscript.com/download/gsdnld.html

2. Install the application

3. Add Ghostscript to system PATH

   Example path:

   ```
   C:\Program Files\gs\gs10.03.0\bin
   ```

---

### 🐧 Linux Installation

```
sudo apt install ghostscript
```

---

### 🍎 Mac Installation

```
brew install ghostscript
```

---

### Verify installation

Windows:

```
gswin64c --version
```

Linux/Mac:

```
gs --version
```

---

### ✅ Important Note

Ensure Ghostscript is properly installed before running the project to avoid runtime errors with Camelot.

---

## 🏗️ High-Level Design

```
User Input (CLI)
        │
        ▼
PDF Selection (Single / Multiple)
        │
        ▼
Page Selection (Specific / All)
        │
        ▼
PDF Ingestion (PyMuPDF)
        │
        ▼
Table Extraction (Camelot)
        │
        ├──────────────► Success
        │                 │
        │                 ▼
        │          Data Cleaning
        │                 │
        │                 ▼
        │            Output (JSON/MD/HTML)
        │
        ▼
Fallback Extraction (pdfplumber)
        │
        ▼
Data Cleaning
        │
        ▼
Output (JSON/MD/HTML)
```

---

## ⚙️ Implementation Details

### 📄 PDF Processing

* **PyMuPDF (fitz)**

  * Used to read PDFs and get total number of pages
  * Efficient for handling large documents

* **Camelot**

  * Primary tool for extracting structured tables from digital PDFs
  * Works well for financial tables with defined rows and columns

* **pdfplumber**

  * Used as fallback when Camelot fails
  * Extracts raw text and converts it into table-like format

---

### 📊 Data Processing

* **pandas**

  * Used for cleaning and structuring extracted data

* **NumPy**

  * Supports internal data handling and processing

---

### 📑 Output Formatting

* **tabulate**

  * Converts tables into Markdown format

* **HTML Generation**

  * Custom Python logic used to generate HTML tables

---

### 🧠 Rationale for Tool Selection

* Camelot chosen for accurate table extraction from structured PDFs
* pdfplumber used as fallback for robustness
* PyMuPDF used for fast PDF handling
* tabulate used for clean Markdown output
* Modular functions used for better maintainability

---

## ▶️ Steps to Build and Test

### 1. Clone the Repository

```
git clone <your-repository-link>
cd pdf-table-extractor
```

---

### 2. Create Virtual Environment (Recommended)

```
python -m venv venv
```

Activate environment:

* **Windows:**

```
venv\Scripts\activate
```

* **Mac/Linux:**

```
source venv/bin/activate
```

---

### 3. Install Dependencies

```
pip install -r requirements.txt
```

---

### 4. Add Input PDFs

Place your PDF files inside:

```
input_pdfs/
```

---

### 5. Run the Project

```
python main.py
```

---

### 6. Example Execution

```
Available PDFs:

1. doc1.pdf
2. doc2.pdf
3. doc3.pdf

Enter your choice: 1,2

Processing doc1.pdf...
Enter page number: 1

Processing doc2.pdf...
Enter page number: all
```

---

### 7. Check Output

Generated files will be stored in:

```
output/
```

Example:

* doc1.json
* doc1.md
* doc1.html

---

## 📂 Project Structure

```
pdf-table-extractor/
│
├── main.py
├── requirements.txt
├── README.md
│
├── input_pdfs/
│   ├── doc1.pdf
│   ├── doc2.pdf
│   └── ...
│
├── output/
│   ├── doc1.json
│   ├── doc1.md
│   ├── doc1.html
```

---

## ⚠️ Limitations

* Works best with digital (text-based) PDFs
* Scanned PDFs are not handled without OCR
* Complex table layouts may require additional tuning

---

## 🔮 Future Improvements

* OCR integration for scanned PDFs
* Improved table detection accuracy
* Web-based interface
* Parallel processing for large datasets

---

## 🏁 Conclusion

This project provides a robust and modular system for extracting structured table data from financial PDFs, with fallback mechanisms and multiple output formats.

---

## 📜 License

This project is licensed under the Apache License 2.0.
