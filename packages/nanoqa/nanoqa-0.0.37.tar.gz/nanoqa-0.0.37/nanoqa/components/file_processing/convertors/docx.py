import re
from pathlib import Path
from typing import List, Union

from docx2python import docx2python


class DocxConvertor:
    @staticmethod
    def convert(path: Union[str, Path]) -> List[str]:
        with docx2python(path) as docx_content:
            content_of_doc = docx_content.text
            pages = content_of_doc.split("\f")
            cleaned_pages = []
            for page in pages:
                pattern = re.compile(r"<a.*?>(.*?)</a>")
                cleaned_page = re.sub(pattern, r"\1", page)
                cleaned_pages.append(cleaned_page)
            return cleaned_pages
