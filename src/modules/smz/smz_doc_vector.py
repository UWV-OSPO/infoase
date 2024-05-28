from typing import List
from modules.headingfwd import BaseVector


class SmzDocVector(BaseVector):
    documents: List[str] = [
        "data/proef-infoase-jan2024/82158.html",
        "data/proef-infoase-jan2024/82159.html",
        "data/proef-infoase-jan2024/Infoase - voorbereidende tekst voor de sessie op 15 februari 2024.docx",
    ]
