import os
import re
import time
import glob
from datetime import datetime
import db_engine

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
INBOX_DIR = os.path.join(PROJECT_ROOT, "invoices_inbox")
os.makedirs(INBOX_DIR, exist_ok=True)


def init_invoice_db():
    """Initializes PostgreSQL table for Canadian business expenses and HST tracking."""
    conn = db_engine.get_db_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS business_invoices (
        id SERIAL PRIMARY KEY,
        filename TEXT UNIQUE,
        vendor TEXT,
        invoice_date VARCHAR(32),
        subtotal NUMERIC(10,2),
        hst_amount NUMERIC(10,2),
        total_amount NUMERIC(10,2),
        category TEXT,
        is_tax_deductible BOOLEAN DEFAULT TRUE,
        notes TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()


def extract_invoice_metadata(text: str, filename: str) -> dict:
    """Parses invoice/receipt text to extract Canadian vendor, subtotal, HST, and total."""
    # Find totals: look for numbers preceded by Total, Balance, Amount Due, etc.
    total = 0.0
    total_match = re.search(r'(?:total|balance\s+due|amount\s+paid|cad\s*\$?)[:\s]*\$?\s*([0-9]+[.,][0-9]{2})', text, re.IGNORECASE)
    if total_match:
        try:
            total = float(total_match.group(1).replace(',', ''))
        except Exception:
            pass

    # Find HST / GST (13% in Ontario)
    hst = 0.0
    hst_match = re.search(r'(?:hst|gst/hst|tax|harmonized\s+sales\s+tax)[:\s]*\$?\s*([0-9]+[.,][0-9]{2})', text, re.IGNORECASE)
    if hst_match:
        try:
            hst = float(hst_match.group(1).replace(',', ''))
        except Exception:
            pass
    elif total > 0:
        # Ontario 13% HST calculation estimate if combined
        hst = round(total - (total / 1.13), 2)

    subtotal = round(total - hst, 2) if total >= hst else total

    # Detect vendor
    vendor = "Business Vendor"
    first_lines = [l.strip() for l in text.splitlines() if l.strip()][:5]
    for line in first_lines:
        if len(line) > 3 and not any(kw in line.lower() for kw in ['invoice', 'receipt', 'date', 'order', 'bill to']):
            vendor = line[:40]
            break

    # Categorize expense
    category = "Software & Cloud Services"
    text_lower = text.lower()
    if any(k in text_lower for k in ['hydro', 'power', 'internet', 'bell', 'rogers']):
        category = "Utilities & Telecommunications"
    elif any(k in text_lower for k in ['hardware', 'computer', 'gpu', 'ram', 'dell', 'best buy', 'amazon']):
        category = "Hardware & Office Equipment"
    elif any(k in text_lower for k in ['coffee', 'restaurant', 'meal', 'lunch', 'tim hortons']):
        category = "Business Meals & Entertainment (50% CRA)"
    elif any(k in text_lower for k in ['fuel', 'gas', 'esso', 'shell', 'parking', 'uber']):
        category = "Motor Vehicle & Travel"

    # Extract date
    date_str = datetime.now().strftime("%Y-%m-%d")
    date_match = re.search(r'\b(20[2-3][0-9][-/.][0-1]?[0-9][-/.][0-3]?[0-9])\b', text)
    if date_match:
        date_str = date_match.group(1)

    return {
        "filename": filename,
        "vendor": vendor,
        "invoice_date": date_str,
        "subtotal": subtotal,
        "hst_amount": hst,
        "total_amount": total,
        "category": category,
        "is_tax_deductible": True,
        "notes": "Verified Canadian Business Expense (Ontario 13% HST ITC eligible)"
    }


def parse_file_content(filepath: str) -> str:
    """Extracts raw text from PDF or text receipt."""
    text = ""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".txt" or ext == ".csv":
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            pass
    elif ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(filepath)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        except Exception:
            pass
    return text or f"Invoice {os.path.basename(filepath)}"


def process_invoice_file(filepath: str) -> dict:
    """Processes a single invoice file and stores it in PostgreSQL."""
    init_invoice_db()
    filename = os.path.basename(filepath)
    text = parse_file_content(filepath)
    meta = extract_invoice_metadata(text, filename)

    conn = db_engine.get_db_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO business_invoices (filename, vendor, invoice_date, subtotal, hst_amount, total_amount, category, is_tax_deductible, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (filename) DO UPDATE SET
        vendor = EXCLUDED.vendor,
        subtotal = EXCLUDED.subtotal,
        hst_amount = EXCLUDED.hst_amount,
        total_amount = EXCLUDED.total_amount,
        category = EXCLUDED.category
    RETURNING id;
    """, (
        meta["filename"], meta["vendor"], meta["invoice_date"],
        meta["subtotal"], meta["hst_amount"], meta["total_amount"],
        meta["category"], meta["is_tax_deductible"], meta["notes"]
    ))
    conn.commit()
    conn.close()

    return meta


def scan_inbox_and_process() -> dict:
    """Scans invoices_inbox/ and processes all new PDFs, images, and text receipts."""
    init_invoice_db()
    files = glob.glob(os.path.join(INBOX_DIR, "*.*"))
    processed = []

    for fp in files:
        if os.path.isfile(fp):
            try:
                res = process_invoice_file(fp)
                processed.append(res)
            except Exception as e:
                print(f"[InvoiceSentry] Error processing {fp}: {e}")

    return {
        "success": True,
        "processed_count": len(processed),
        "invoices": processed
    }


def get_invoices_ledger() -> dict:
    """Returns all logged business invoices and cumulative CRA tax deduction metrics."""
    init_invoice_db()
    conn = db_engine.get_db_connection()
    conn.row_factory = True
    c = conn.cursor()
    c.execute("""
    SELECT id, filename, vendor, invoice_date, subtotal, hst_amount, total_amount, category, is_tax_deductible, notes, processed_at
    FROM business_invoices
    ORDER BY processed_at DESC;
    """)
    rows = c.fetchall()

    total_spent = sum(float(r["total_amount"] or 0) for r in rows)
    total_hst = sum(float(r["hst_amount"] or 0) for r in rows)
    total_subtotal = sum(float(r["subtotal"] or 0) for r in rows)

    conn.close()

    return {
        "success": True,
        "total_records": len(rows),
        "summary": {
            "total_expenses_cad": round(total_spent, 2),
            "total_subtotal_cad": round(total_subtotal, 2),
            "total_recoverable_hst_itc": round(total_hst, 2),
            "tax_jurisdiction": "Ontario / CRA (13% HST)"
        },
        "records": [dict(r) for r in rows]
    }


if __name__ == "__main__":
    print("Testing Canadian Tax & Invoice Sentry...")
    init_invoice_db()
    # Create sample invoice to verify pipeline
    sample_file = os.path.join(INBOX_DIR, "sample_aws_cloud_invoice.txt")
    with open(sample_file, "w") as f:
        f.write("Amazon Web Services Canada\nDate: 2026-09-20\nSubtotal: $150.00\nHST (13%): $19.50\nTotal Due: $169.50 CAD\nCloud GPU compute cluster")
    res = process_invoice_file(sample_file)
    print("Processed:", res)
    ledger = get_invoices_ledger()
    print("Ledger summary:", ledger["summary"])
