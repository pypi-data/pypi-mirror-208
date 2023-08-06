from pathlib import Path
from typing import List, Union


class TxtConvertor:
    @staticmethod
    def convert(path: Union[Path, str]) -> List[str]:
        with open(path, mode="r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
            pages = text.split("\f")
            return pages
