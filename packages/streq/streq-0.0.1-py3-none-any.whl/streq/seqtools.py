"""Python utilities for working with nucleotide sequence strings.

Variety of utilities for converting, searching, and doing 
calculations on nucleotide sequences.

"""

from collections.abc import Generator, Sequence
from difflib import SequenceMatcher
import re

from .utils import (sequences, 
                    _preserve_case, 
                    _preserve_circular,
                    _normalize_case)

seqs = sequences


@_preserve_circular
def reverse(x: str) -> str:

    """Reverse a sequence.

    Parameters
    ----------
    x : str
        Sequence to convert.

    Returns
    -------
    str
        Converted sequence.

    """

    return x[::-1]


@_preserve_circular
@_preserve_case
@_normalize_case(nargs=1)
def complement(x: str) -> str:

    """Complement (but don't reverse) a sequence.

    Parameters
    ----------
    x : str
        Sequence to convert.

    Returns
    -------
    str
        Converted sequence.

    """

    return x.translate(seqs.complementer)


def reverse_complement(x: str) -> str:

    """Reverse complement a sequence.

    Parameters
    ----------
    x : str
        Sequence to convert.

    Returns
    -------
    str
        Converted sequence.

    Examples
    --------
    >>> reverse_complement('ATCG')
    'CGAT'

    """

    return complement(reverse(x))


@_preserve_circular
@_preserve_case
@_normalize_case(nargs=1)
def to_rna(x: str) -> str:

    """Convert nucleotides to RNA.

    Parameters
    ----------
    x : str
        Sequence to convert.

    Returns
    -------
    str
        Converted sequence.

    Examples
    --------
    >>> to_rna('ATCG')
    'AUCG'

    """

    return x.replace('T', 'U')


@_preserve_circular
@_preserve_case
@_normalize_case(nargs=1)
def to_dna(x: str) -> str:

    """Convert nucleotides to DNA.

    Parameters
    ----------
    x : str
        Sequence to convert.

    Returns
    -------
    str
        Converted sequence.

    Examples
    --------
    >>> to_dna('AUCG')
    'ATCG'

    """

    return x.replace('U', 'T')


@_normalize_case(nargs=2)
def find_iupac(query: str, 
               sequence: str) -> Generator[Sequence[int], str]:
    
    """Find occurrences of a query in a larger sequence.

    IUPAC codes in the query will be interpreted as ambiguities:

    A: A
    C: C
    G: G
    T: T
    U: U
    N: .
    R: "[AG]"
    Y: "[TUC]"
    W: "[ATU]"
    S: "[CG]"
    V: "[ACG]"
    B: "[TUGC]"

    Parameters
    ----------
    query : str
        Sequence to search for. Accepts IUPAC codes: N, R, Y, S, W, V, B.
    sequence : str 
        Sequence to search within.
    
    Yields
    ------
    Generator
        Generator of tuples containing the match indices and matched sequence.
    indices : tuple
        Start and stop indices of the match
    sequence : str
        matched sequence

    Examples
    --------
    >>> for (start_idx, end_idx), match in find_iupac('ARY', 'AATAGCAGTGTGAAC'):
    ...     print(f"Found ARY at {start_idx}:{end_idx}: {match}")
    ... 
    Found ARY at 0:3: AAT
    Found ARY at 3:6: AGC
    Found ARY at 6:9: AGT
    Found ARY at 12:15: AAC

    """
    
    query = query.translate(seqs.base2regex)
    query = re.compile(query) 
    
    for match in query.finditer(sequence):

        yield match.span(), match.group()


@_normalize_case(nargs=1)
def which_re_sites(x: str) -> Sequence[str]:

    """List Type IIS restriction sites in sequence.

    Currently only searches for the most commonly used
    Type IIS restriction sites for Golden Gate Cloning:

    BbsI: GAAGAC
    BsmBI: CGTCTC
    BtgZI: GCGATG
    PaqCI: CACCTGC
    SapI: GCTCTTC
    BsaI: GGTCTC

    Parameters
    ----------
    x : str
        Sequence to check.

    Returns
    -------
    tuple
        List of Type IIS restriction sites in x

    Examples
    --------
    >>> which_re_sites('AAAGAAG')
    ()
    >>> which_re_sites('AAAGAAGAC')
    ('BbsI',)
    >>> which_re_sites('AAAGAAGACACCTGC')
    ('BbsI', 'PaqCI')
    
    """

    fwd = [enz for enz, site in seqs.re_sites.items() 
           if (site in x) or 
           (reverse_complement(site) in x)]

    return tuple(fwd)


@_normalize_case(nargs=1)
def count_re_sites(x: str) -> bool:

    """Count Type IIS restriction sites in sequence.

    Currently only searches for the most commonly used
    Type IIS restriction sites for Golden Gate Cloning:

    BbsI: GAAGAC
    BsmBI: CGTCTC
    BtgZI: GCGATG
    PaqCI: CACCTGC
    SapI: GCTCTTC
    BsaI: GGTCTC

    Parameters
    ----------
    x : str
        Sequence to check.

    Returns
    -------
    int
        Number of Type IIS restriction sites in x.

    Examples
    --------
    >>> count_re_sites('AAAGAAG')
    0
    >>> count_re_sites('AAAGAAGAC')
    1
    >>> count_re_sites('AAAGAAGACACCTGC')
    2
    
    """

    return len(which_re_sites(x))
    

@_normalize_case(nargs=2)
def _x_content(x: str, y: str) -> float:

    try:
        return sum(letter in y for letter in x) / len(x)
    except ZeroDivisionError:
        return 0. 
    

def gc_content(x: str) -> float:

    """Calculate proportional GC content.

    Recognises IUPAC codes.

    Parameters
    ----------
    x : str
        Sequence.

    Returns
    -------
    float
        GC content.

    Examples
    --------
    >>> gc_content('AGGG')
    0.75

    """

    return _x_content(x, 'GCS')


def purine_content(x: str) -> float:

    """Calculate proportional purine content.

    Recognises IUPAC codes.

    Parameters
    ----------
    x : str
        Sequence.

    Returns
    -------
    float
        Purine content.

    Examples
    --------
    >>> purine_content('AUGGR')
    0.8

    """

    return _x_content(x, 'GAR')


def pyrimidine_content(x: str) -> float:

    """Calculate proportional pyrimidine content.

    Recognises IUPAC codes.

    Parameters
    ----------
    x : str
        Sequence.

    Returns
    -------
    float
        Pyrimidine content.
    
    Examples
    --------
    >>> pyrimidine_content('AUGGG')
    0.2

    """

    return _x_content(x, 'CUTY')
    