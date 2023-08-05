from deciphon_core.scan import Scan as ScanCore

from deciphon.hmmfile import HMMFile
from deciphon.snapfile import NewSnapFile
from deciphon.seqfile import SeqFile

__all__ = ["Scan"]


class Scan(ScanCore):
    def __init__(self, hmm: HMMFile, seq: SeqFile, snap: NewSnapFile):
        super().__init__(hmm, seq, snap)
