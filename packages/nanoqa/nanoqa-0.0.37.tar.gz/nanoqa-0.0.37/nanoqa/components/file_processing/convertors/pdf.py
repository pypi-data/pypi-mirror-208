from pathlib import Path
from typing import List, Union

import fitz


class PDFConvertor:
    @staticmethod
    def convert(path: Union[str, Path], sort_by_position: bool = False) -> List[str]:
        doc = fitz.open(path)
        page_count = int(doc.page_count)

        document = ""
        for i in range(page_count):
            page = doc[i]
            document += page.get_text("text", sort=sort_by_position, flags=0) + "\f"
        pages = document.split("\f")[:-1]
        return pages

    @staticmethod
    def convert_with_ocr(path: Union[str, Path]):
        mat = fitz.Matrix(5, 5)
        doc = fitz.open(path)
        page_count = int(doc.page_count)

        def get_tessocr(page, bbox):
            nonlocal mat
            pix = page.get_pixmap(
                colorspace=fitz.csGRAY,
                matrix=mat,
                clip=bbox,
            )
            ocrdoc = fitz.open("pdf", pix.pdfocr_tobytes())
            ocrpage = ocrdoc[0]
            tp = ocrpage.get_textpage_ocr(dpi=150, full=True)
            std_text = ocrpage.get_text(textpage=tp)
            if std_text.endswith("\n"):
                std_text = std_text[:-1]
            return std_text

        document = ""
        for i in range(page_count):
            page = doc[i]

            blocks = page.get_text("dict", flags=0)["blocks"]
            for b in blocks:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"]
                        if chr(65533) in text:
                            tmp = text.lstrip()
                            sb = " " * (len(text) - len(tmp))
                            tmp = text.rstrip()
                            sa = " " * (len(text) - len(tmp))
                            text = sb + get_tessocr(page, s["bbox"]) + sa
                        document += text
                    document += "\n"
            document += "\f"

        pages = document.split("\f")[:-1]
        return pages
