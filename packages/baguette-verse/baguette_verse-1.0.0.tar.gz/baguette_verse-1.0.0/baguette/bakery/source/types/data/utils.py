"""
This module holds some useful functions and classes for the data behavioral package.
"""

from abc import ABCMeta
from typing import Hashable, Iterator, Sequence, TypeVar

from ...utils import chrono

__all__ = ["levenshtein_similarity", "levenshtein_subset_similarity", "entropy", "printable_rate"]





S = TypeVar("S", bound=Sequence[Hashable])

@chrono
def levenshtein_similarity(s1 : S, s2 : S, threshold : float = 1.0) -> float:
    """
    Returns the normalized Levenshtein distance (float between 0 and 1) between two strings, where the weight of insertion and deletion operation is the same than the one of substitution.
    If threshold is given, it must be a float representing the minimum value of similarity required to push the calculation to the end. If similarity gets lower, 0 is returned.
    """
    from typing import Sequence
    if not isinstance(s1, Sequence):
        raise TypeError("Expected two Sequences of Hashables, got " + repr(type(s1).__name__) + " and " + repr(type(s2).__name__))
    if not isinstance(s2, type(s1)):
        raise TypeError("Expected two {}s, got {} and {}".format(type(s1).__name__, repr(type(s1).__name__), repr(type(s2).__name__)))
    if not isinstance(threshold, float):
        try:
            threshold = float(threshold)
        except:
            raise TypeError("Expected float for threshold, got " + repr(type(threshold).__name__)) from None
    if not (0 <= threshold <= 1):
        raise ValueError("Threshold must be between zero and one, got " + repr(threshold))
    if not s1 and not s2:
        return 0.0
    if hash(s1) == hash(s2) and s1 == s2:
        return 1.0
    if threshold >= 1.0:
        score_threshold = None
    else:
        score_threshold = round((1 - threshold) * max(len(s1), len(s2)))
    modifier = 1
    from Levenshtein import distance
    s = 1.0 - (distance(s1, s2, weights = (1, 1, modifier), score_cutoff = score_threshold) / max(len(s1), len(s2)))
    if s <= threshold:
        return 0.0
    return s

@chrono
def levenshtein_subset_similarity(s1 : S, s2 : S, threshold : float = 1.0) -> float:
    """
    Returns the normalized Levenshtein distance (float between 0 and 1) between two strings, where the weight of insertion and deletion operation is lower than the one of substitution.
    If threshold is given, it must be a float representing the minimum value of similarity required to push the calculation to the end. If similarity gets lower, 0 is returned.
    """
    from typing import Sequence
    if not isinstance(s1, Sequence):
        raise TypeError("Expected two Sequences of Hashables, got " + repr(type(s1).__name__) + " and " + repr(type(s2).__name__))
    if not isinstance(s2, type(s1)):
        raise TypeError("Expected two {}s, got {} and {}".format(type(s1).__name__, repr(type(s1).__name__), repr(type(s2).__name__)))
    if not isinstance(threshold, float):
        try:
            threshold = float(threshold)
        except:
            raise TypeError("Expected float for threshold, got " + repr(type(threshold).__name__)) from None
    if not (0 <= threshold <= 1):
        raise ValueError("Threshold must be between zero and one, got " + repr(threshold))
    if not s1 and not s2:
        return 0.0
    if hash(s1) == hash(s2) and s1 == s2:
        return 1.0
    if threshold >= 1.0:
        score_threshold = None
    else:
        score_threshold = round((1 - threshold) * max(len(s1), len(s2)))
    modifier = 3
    from Levenshtein import distance
    s = 1.0 - (distance(s1, s2, weights = (1, 1, modifier), score_cutoff = score_threshold) / max(len(s1), len(s2)))
    if s <= threshold:
        return 0.0
    return s

@chrono
def entropy(s : str | bytes | bytearray) -> float:
    """
    Computes the character entropy of the given string.
    """
    if not s:
        return 0.0
    from collections import Counter
    from math import log2
    probabilities = {c : nc / len(s) for c, nc in Counter(s).items()}
    return sum(-p * log2(p) for p in probabilities.values())

@chrono
def printable_rate(s : bytes | bytearray) -> tuple[float, str]:
    """
    Computes the ratio of printable bytes (which can be decoded to the best endoding). Also returns the best probale encoding.
    """
    if not s:
        return 1.0, "raw"

    import codecs
    n_err = 0

    def count(err : UnicodeError) -> tuple[str, int]:
        """
        Adds one to the decoding errors counter and resume normal decoding.
        """
        nonlocal n_err
        n_err += 1
        if isinstance(err, UnicodeDecodeError | UnicodeTranslateError | UnicodeEncodeError):
            return "", err.start + 1
        else:
            raise ValueError("Unknown UnicodeError")
    
    codecs.register_error("count", count)

    best = float("inf")
    best_enc = ""

    # ("utf-8", "ascii", "utf-16", "utf-32", "gbk")

    for enc in ("ascii", ):
        n_err = 0
        codecs.decode(s, enc, "count")
        if n_err < best:
            best = n_err
            best_enc = enc
    
    return (len(s) - best) / len(s), best_enc if best == 0 else "raw"





class DiffFile:

    """
    These objects are abstract/virtual files in which you can perform IO operations at any place.
    """

    def __init__(self) -> None:
        self.__offsets : list[int] = list()
        self.__arrays : list[bytearray] = list()
        self.__last_dump : bytes | None = None
        self.__computation_index : int = 0
        self.__last_computation_index : int = -1
    
    def arrays(self) -> Iterator[tuple[int, bytes]]:
        """
        Yields all the successives entries in the DiffFile in the form (offset, buffer).
        """
        yield from zip(self.__offsets, self.__arrays)

    @chrono
    def write(self, data : bytes, offset : int):
        """
        Writes a new block of data in the virtual diff file.
        """
        if not isinstance(data, bytes | bytearray | memoryview) or not isinstance(offset, int):
            raise TypeError("Expected readable buffer and int, got " + repr(type(data).__name__) + " and " + repr(type(offset).__name__))
        # First, insert the new block in the right place
        data = bytearray(data)
        for i, (o, a) in enumerate(self.arrays()):
            if offset <= o:
                break
        else:
            i = len(self.__offsets)
        self.__offsets.insert(i, offset)
        self.__arrays.insert(i, data)
        # Second, operate all the possible merges
        end = offset + len(data)
        old_data = bytearray(len(data))
        j = i + 1
        while j < len(self.__offsets):
            o, a = self.__offsets[j], self.__arrays[j]
            if o > end:
                break
            old_data[o - offset : o - offset + len(a)] = a
            j += 1
        old_data[:len(data)] = data
        self.__arrays[i] = old_data
        # Delete useless upcoming blocks
        for k in range(i + 1, j):
            self.__offsets.pop(i + 1)
            self.__arrays.pop(i + 1)
        # Eventually merge with previous block
        if i > 0 and self.__offsets[i - 1] + len(self.__arrays[i - 1]) >= offset:
            self.__offsets.pop(i)
            self.__arrays.pop(i)
            o, a = self.__offsets[i - 1], self.__arrays[i - 1]
            a[offset - o : offset - o + len(old_data)] = old_data
        self.__computation_index += 1
    
    @chrono
    def dump(self) -> bytes:
        """
        Returns a dump of the file content. Any empty space will be represented by '[N bytes]'.
        """
        if self.__last_computation_index != self.__computation_index:
            last_end = self.__offsets[0] if self.__offsets else 0
            d = bytearray()
            for o, a in self.arrays():
                if last_end < o:
                    d.extend("[{} bytes]".format(o - (last_end + len(a))).encode("utf-8"))
                d.extend(a)
                last_end = o + len(a)
            self.__last_computation_index = self.__computation_index
            self.__last_dump = bytes(d)
            return self.__last_dump
        else:
            if self.__last_dump is None:
                raise RuntimeError("Got an empty DiffFile dump, whereas it was marked as updated")
            return self.__last_dump





class IOOperation(metaclass = ABCMeta):

    """
    This class represents a Diff vertex atomic operation in its operation log.
    """

    def __init__(self, offset : int, data : bytes) -> None:
        self.__offset = offset
        self.__data = data
    
    @property
    def start(self) -> int:
        """
        The place in the file where this buffer starts.
        """
        return self.__offset
    
    @property
    def stop(self) -> int:
        """
        The place in the file where this buffer ends.
        """
        return self.__offset + len(self.__data)
    
    @property
    def data(self) -> bytes:
        """
        The content of the buffer.
        """
        return self.__data

    



class Read(IOOperation):

    """
    This is a single read operation in a Diff Vertex log.
    """





class Write(IOOperation):

    """
    This is a single write operation in a Diff Vertex log.
    """





del ABCMeta, Hashable, Iterator, Sequence, TypeVar, chrono, S