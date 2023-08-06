"""
Module for converting PDF files into text and/or images.
"""

import io

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage


def pdf_to_txt(in_pdf_file: str, out_txt_file: str) -> None:
    """
    Convert input PDF file to txt format.

    Args:
        in_pdf_file (str): Input PDF file to read from.
        out_txt_file (str): Output txt file to write to.
    """

    try:
        with open(in_pdf_file, 'rb') as in_file:
            resource_manager = PDFResourceManager()
            return_data = io.StringIO()
            text_converter = TextConverter(
                resource_manager, return_data, laparams=LAParams())
            interpreter = PDFPageInterpreter(resource_manager, text_converter)

            # process every page in pdf file
            for page in PDFPage.get_pages(in_file):
                interpreter.process_page(page)

            txt = return_data.getvalue()

            # save output data to txt file
            with open(out_txt_file, 'w')as f:
                f.write(txt)

    except FileNotFoundError:
        print("Error: File not found.")
