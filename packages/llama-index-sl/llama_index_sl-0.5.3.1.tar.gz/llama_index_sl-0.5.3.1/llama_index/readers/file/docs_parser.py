"""Docs parser.

Contains parsers for docx, pdf files.

"""
from pathlib import Path
from typing import Dict

from llama_index.readers.file.base_parser import BaseParser
import re

class PDFParser(BaseParser):
    """PDF parser."""

    def _init_parser(self) -> Dict:
        """Init parser."""
        return {}

    def parse_file(self, file: Path, errors: str = "ignore") -> str:
        """Parse file."""
        try:
            import io
            from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
            from pdfminer.pdfpage import PDFPage
            from pdfminer.converter import TextConverter
            from pdfminer.layout import LAParams
        except ImportError:
            raise ImportError(
                "pdfminer is required to read PDF files: "
                "`pip install pdfminer`"
            )
        # Create resource manager, layout parameters and interpreter objects
        resource_manager = PDFResourceManager()
        output_string = io.StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(resource_manager, output_string, codec=codec, laparams=laparams)
        interpreter = PDFPageInterpreter(resource_manager, device)

        # Open the PDF file, loop over each page, and extract the text
        with open(file, 'rb') as fh:
            for page in PDFPage.get_pages(fh, check_extractable=True):
                interpreter.process_page(page)

            # Get the extracted text and close the converter and output_string objects
            extracted_text = output_string.getvalue()

        # replace new lines with spaces
        extracted_text=re.sub(r'[\n\r\t\f\v]', ' ', extracted_text)
        device.close()
        output_string.close()

        return extracted_text


class DocxParser(BaseParser):
    """Docx parser."""

    def _init_parser(self) -> Dict:
        """Init parser."""
        return {}

    def parse_file(self, file: Path, errors: str = "ignore") -> str:
        """Parse file."""
        try:
            import docx2txt
        except ImportError:
            raise ImportError(
                "docx2txt is required to read Microsoft Word files: "
                "`pip install docx2txt`"
            )

        text = docx2txt.process(file)

        return text
