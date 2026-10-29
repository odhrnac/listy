"""Generating letters from a template (v2), in a background thread like the old generator."""
import os
import re

from django.db import connection

from config import OUTPUT_DIR
from generator.models import GenerationJob, GeneratedPDF
from generator.pdf_tools import encrypt_pdf
from readers import read_excel

from .models import Template
from .pdf_renderer import LetterRenderer
from .sample_data import build_context, group_by_key, link_key

# Columns that can hold the PDF file name (AttachmentName from the Jasper reports, PDF from the SK reminders)
FILENAME_COLUMNS = ('AttachmentName', 'PDF')
NUMBER_COLUMNS = ('ContractNumber', 'Contract_number')


def letter_filename(template, row, index, letter_date):
    """File name for one letter: from the Excel, or TYPE_contract_date.pdf. Never contains a path."""
    name = next((row[c] for c in FILENAME_COLUMNS if str(row.get(c, '')).strip()), None)
    if not name:
        number = next((row[c] for c in NUMBER_COLUMNS if str(row.get(c, '')).strip()), f'row_{index}')
        name = f"{template.document_type or 'LETTER'}_{number}_{letter_date.replace('.', '')}"
    name = re.sub(r'[^\w.\- ]', '_', str(name)).strip(' .') or f'letter_{index}'
    return name if name.lower().endswith('.pdf') else f'{name}.pdf'


def _unique(filename, used):
    base, ext = os.path.splitext(filename)
    candidate, n = filename, 1
    while candidate.lower() in used:
        n += 1
        candidate = f'{base}_{n}{ext}'
    used.add(candidate.lower())
    return candidate


def process_job(job_id, template_id, main_path, detail_path, letter_date, encrypt_pdfs):
    """Background thread: one PDF per row of the main Excel. The uploaded Excels are deleted afterwards.

    Playwright runs an event loop in this thread, and Django refuses database queries next to one, so
    everything is read from the database before the browser starts and saved after it has closed.
    """
    job = GenerationJob.objects.get(id=job_id)
    try:
        template = Template.objects.prefetch_related('images__image', 'fields').get(id=template_id)
        rows = read_excel(main_path)
        groups = group_by_key(read_excel(detail_path), template.detail_key) if detail_path else {}
        output_dir = os.path.join(OUTPUT_DIR, job.output_dir)
        used = set()
        pdfs = []

        with LetterRenderer() as renderer:
            for index, row in enumerate(rows, start=1):
                linked = groups.get(link_key(row.get(template.main_key, '')), []) if groups else []
                data = build_context(template, row, linked)
                data['letter_date'] = letter_date

                filename = _unique(letter_filename(template, row, index, letter_date), used)
                output_path = os.path.join(output_dir, filename)
                renderer.render(template, data, output_path)
                if encrypt_pdfs:
                    encrypt_pdf(output_path, row.get('Password', '').strip())
                pdfs.append(GeneratedPDF(job=job, filename=filename, file_path=f"outputs/{job.output_dir}/{filename}"))

        GeneratedPDF.objects.bulk_create(pdfs)
        job.status = 'success'
    except Exception as e:
        job.status = 'error'
        job.error_message = str(e)
    finally:
        job.save()
        for path in (main_path, detail_path):
            if path and os.path.exists(path):
                os.remove(path)
        connection.close()
