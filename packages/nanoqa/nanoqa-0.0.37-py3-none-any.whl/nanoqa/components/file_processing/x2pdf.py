import os
from pathlib import Path
from typing import List, Union

from fpdf import FPDF

from ...configs import lib_basedir
from .convertors import DocxConvertor, TxtConvertor


class X2PDF:
    def __init__(self):
        self.txt_convertor = TxtConvertor()
        self.docx_convertor = DocxConvertor()

    @staticmethod
    def path_join(paths: List[Union[str, Path]]) -> Union[Path, str]:
        """
        :param paths: list of paths to join
        :return: joined path
        """
        return Path(*paths)

    def convert(self, from_folder: str, to_folder: str) -> None:
        """
        :param from_folder: folder with files to convert
        :param to_folder: folder to output the converted files
        :return: None
        """
        for file in os.listdir(from_folder):
            if file.endswith(".txt"):
                self.txt2pdf(
                    self.path_join([from_folder, file]),
                    self.path_join([to_folder, file.replace(".txt", ".pdf")]),
                )
            elif file.endswith(".docx"):
                self.docx2pdf(
                    self.path_join([from_folder, file]),
                    self.path_join([to_folder, file.replace(".docx", ".pdf")]),
                )

    @staticmethod
    def create_pdf(content: str, target_file: str):
        pdf = FPDF()
        pdf.add_font("Roboto", "", str(lib_basedir / "static/Roboto-Regular.ttf"))
        pdf.set_font(family="Roboto", size=14)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_margin(4)
        pdf.set_text_color(0, 0, 0)
        pdf.add_page()
        pdf.write(txt=content)
        pdf.output(target_file)

    def txt2pdf(self, from_file: str, to_file: str):
        # get the content from the file first
        pages = self.txt_convertor.convert(path=Path(from_file))
        # create a pdf file from the content accordingly
        self.create_pdf("\n".join(pages), to_file)

    def docx2pdf(self, from_file: str, to_file: str):
        # get the content from the file first
        pages = self.docx_convertor.convert(path=Path(from_file))
        # create a pdf file from the content accordingly
        return self.create_pdf("\n".join(pages), to_file)
