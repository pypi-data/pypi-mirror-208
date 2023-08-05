from enum import Enum, auto
from pathlib import Path
from deciphon.errors import FiletypeGuessError

__all__ = ["Filetype"]


class Filetype(Enum):
    JSON = auto()
    FASTA = auto()

    @staticmethod
    def guess(file: Path):
        for row in open(file, "r"):
            if row.startswith(r"["):
                return Filetype.JSON
            if row.startswith(r">"):
                return Filetype.FASTA
        raise FiletypeGuessError("Could not guess the file type.")
