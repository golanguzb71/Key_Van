import random
import re
from PyPDF2 import PdfReader
from docx import Document
from flask import jsonify


def find_key_by_value(redis_client, search_value):
    for key in redis_client.scan_iter():
        value = redis_client.get(key)
        if value and value.decode() == str(search_value):
            return key
    return None


def generate_code():
    return random.randint(10000, 99999)


def replace_underscore_sequences(text):
    return re.sub(r'_+', '[qazwsxedc]', text)


def process_docx(file):
    doc = Document(file)
    modified_text = ""

    for paragraph in doc.paragraphs:
        paragraph_text = paragraph.text
        modified_text += replace_underscore_sequences(paragraph_text) + "\n"

    return jsonify({'Questions': modified_text})


def process_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += replace_underscore_sequences(page_text) + "\n"

    return jsonify({'Questions': text})


def process_doc(file, file_name):
    if file_name.endswith('.docx'):
        return process_docx(file)
    elif file_name.endswith('.pdf'):
        return process_pdf(file)
    else:
        raise ValueError("Unsupported file type. Only .docx and .pdf are supported.")
