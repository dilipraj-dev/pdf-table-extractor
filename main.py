import os
import camelot
import fitz
import json
import pdfplumber
from tabulate import tabulate

PDF_FOLDER = "input_pdfs"
OUTPUT_FOLDER = "output"


# ---------------- BASIC ----------------

def list_pdfs():
    return [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]


def get_total_pages(file_path):
    doc = fitz.open(file_path)
    return len(doc)


def validate_pages(page, total_pages):
    if page.lower() == "all":
        return "1-end"

    try:
        pages = [int(p) for p in page.split(",")]
        for p in pages:
            if p < 1 or p > total_pages:
                return None
        return page
    except:
        return None


# ---------------- VALIDATION ----------------

def is_valid_table(df):
    return df.shape[1] >= 2


def is_bad_extraction(tables):
    if not tables:
        return True

    for t in tables:
        if len(t["rows"]) <= 2:
            return True

        for row in t["rows"]:
            for cell in row:
                if len(str(cell)) > 120:
                    return True

    return False


# ---------------- CLEANING ----------------

def merge_multiline_rows(rows):
    merged = []
    current = None

    for row in rows:
        if row[0].strip() != "":
            if current:
                merged.append(current)
            current = row.copy()
        else:
            if current:
                for i in range(len(row)):
                    if row[i].strip():
                        current[i] += " " + row[i]

    if current:
        merged.append(current)

    return merged


def clean_financial_rows(rows):
    cleaned = []

    for row in rows:
        desc = row[0].strip()
        val = row[1].strip() if len(row) > 1 else ""

        if len(desc) < 3:
            continue

        if "cash flow statement" in desc.lower():
            continue

        if "annual report" in desc.lower():
            continue

        desc = desc.title()

        cleaned.append([desc, val])

    return cleaned


# ---------------- CAMEL0T PROCESS ----------------

def process_table(df):
    df = df.replace('', None)
    df = df.dropna(axis=1, how='all')
    df = df.dropna(how='all').reset_index(drop=True)

    if len(df) < 2:
        return None

    header_row_index = 0
    for i, row in df.iterrows():
        text = " ".join([str(cell).lower() for cell in row])
        if "date" in text or "txn" in text or "cash flow" in text:
            header_row_index = i
            break

    headers = df.iloc[header_row_index].tolist()
    headers = [str(h).replace("\n", " ").strip() for h in headers]

    # Fix Branch Code
    if header_row_index + 1 < len(df):
        next_row = df.iloc[header_row_index + 1].tolist()
        for i in range(len(headers)):
            if headers[i].lower() == "branch" and str(next_row[i]).strip().lower() == "code":
                headers[i] = "Branch Code"
                df = df.drop(header_row_index + 1).reset_index(drop=True)
                break

    data_df = df.iloc[header_row_index + 1:].reset_index(drop=True)

    clean_rows = []
    for _, row in data_df.iterrows():
        cleaned = [str(cell).strip() if str(cell).lower() != "none" else "" for cell in row]
        clean_rows.append(cleaned[:len(headers)])

    clean_rows = merge_multiline_rows(clean_rows)

    return {
        "headers": headers,
        "rows": clean_rows
    }


# ---------------- PDFPLUMBER FALLBACK ----------------

def extract_with_pdfplumber(file_path, page):
    rows = []

    with pdfplumber.open(file_path) as pdf:

        if page == "1-end":
            pages = pdf.pages
        else:
            indices = [int(p) - 1 for p in page.split(",")]
            pages = [pdf.pages[i] for i in indices]

        for p in pages:
            text = p.extract_text()
            if not text:
                continue

            lines = text.split("\n")

            for line in lines:
                line = line.strip()

                if len(line) < 5:
                    continue

                parts = line.split("  ")

                for part in parts:
                    part = part.strip()

                    if len(part) < 5:
                        continue

                    words = part.split()

                    desc = []
                    nums = []

                    for w in words:
                        if any(c.isdigit() for c in w):
                            nums.append(w)
                        else:
                            desc.append(w)

                    rows.append([
                        " ".join(desc),
                        " ".join(nums)
                    ])

    return {
        "headers": ["Description", "Value"],
        "rows": rows
    }


# ---------------- PROCESS ----------------

def process_single_pdf(selected):
    file_path = os.path.join(PDF_FOLDER, selected)

    print(f"\n📄 Processing {selected}...\n")

    total_pages = get_total_pages(file_path)
    print(f"This PDF has {total_pages} pages.")

    page_input = input(f"Enter page number (1 to {total_pages}) or 'all': ")
    page = validate_pages(page_input, total_pages)

    if not page:
        print("Invalid page input")
        return

    try:
        tables = camelot.read_pdf(
            file_path,
            pages=page,
            flavor="stream",
            row_tol=10,
            column_tol=10,
            edge_tol=500
        )
    except Exception as e:
        print(f"Error: {e}")
        return

    all_tables = []

    if tables and tables.n > 0:
        for table in tables:
            df = table.df
            if is_valid_table(df):
                processed = process_table(df)
                if processed:
                    all_tables.append(processed)

    # Fallback
    if is_bad_extraction(all_tables):
        print("⚠️ Using pdfplumber fallback...\n")

        fallback = extract_with_pdfplumber(file_path, page)

        # FINAL CLEAN
        fallback["rows"] = clean_financial_rows(fallback["rows"])

        if fallback["rows"]:
            all_tables = [fallback]

    if not all_tables:
        print("❌ No usable tables found")
        return

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    base = selected.replace(".pdf", "")

    # JSON
    with open(f"{OUTPUT_FOLDER}/{base}.json", "w", encoding="utf-8") as f:
        json.dump({"file": selected, "tables": all_tables}, f, indent=4)

    # Markdown
    with open(f"{OUTPUT_FOLDER}/{base}.md", "w") as f:
        for i, table in enumerate(all_tables):
            f.write(f"\n## Table {i+1}\n\n")
            f.write(tabulate(table["rows"], headers=table["headers"], tablefmt="pipe"))
            f.write("\n\n")

    # HTML
    with open(f"{OUTPUT_FOLDER}/{base}.html", "w") as f:
        f.write("<html><body>")

        for i, table in enumerate(all_tables):
            f.write(f"<h2>Table {i+1}</h2>")
            f.write("<table border='1'>")

            f.write("<tr>")
            for h in table["headers"]:
                f.write(f"<th>{h}</th>")
            f.write("</tr>")

            for row in table["rows"]:
                f.write("<tr>")
                for cell in row:
                    f.write(f"<td>{cell}</td>")
                f.write("</tr>")

            f.write("</table><br><br>")

        f.write("</body></html>")

    print(f"✅ Saved outputs for {selected}")


# ---------------- MAIN ----------------

def main():
    files = list_pdfs()

    if not files:
        print("No PDFs found")
        return

    print("\nAvailable PDFs:\n")
    print("0. Process ALL PDFs")

    for i, f in enumerate(files):
        print(f"{i+1}. {f}")

    choice = input("\nEnter your choice (e.g., 1 or 1,2,5 or 0): ")

    if choice.strip() == "0":
        print("\n🚀 Processing ALL PDFs...\n")
        for pdf in files:
            process_single_pdf(pdf)
        return

    try:
        selections = [int(x.strip()) for x in choice.split(",")]

        print("\n🚀 Processing selected PDFs...\n")

        for sel in selections:
            if 1 <= sel <= len(files):
                process_single_pdf(files[sel - 1])
            else:
                print(f"Invalid selection: {sel}")

    except:
        print("Invalid input format")


if __name__ == "__main__":
    main()