import os

from pypdf import PdfReader, PdfWriter


def encrypt_pdf(path, password):
    """Protect a PDF with a password (AES-256), replacing the file."""
    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password, algorithm="AES-256-R5")
    encrypted_path = path + ".enc"
    with open(encrypted_path, "wb") as f:
        writer.write(f)
    os.replace(encrypted_path, path)
