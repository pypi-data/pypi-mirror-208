from difflib import SequenceMatcher

from .seqtools import reverse_complement
from .utils import _normalize_case

@_normalize_case(nargs=2)
def levenshtein(x: str, y: str) -> int:

	"""Calculate the Levenshtein distance between two sequences.
    
    The Levenshtein distance is the number of insertions,
    deletions, and mutations required to make two 
    sequences match.

    Parameters
    ----------
    x : str
        Sequence.
    y : str, optional
        Second sequence for correlation with x.

    Returns
    -------
    int
        Levenshtein distance.

    Examples
    --------
    >>> levenshtein('AAATTT', 'AAATTT')
    0
    >>> levenshtein('AAATTT', 'ACTTT')
    2
    >>> levenshtein('AAATTT', 'AACTTT')
    1
    >>> levenshtein('AAAG', 'TCGA')
    4

    """
    
	x_len, y_len = map(len, (x, y))

	matrix = {i: {j: 0 for j in range(y_len + 1)} 
			  for i in range(x_len + 1)}
	
	for i in range(x_len + 1):

		matrix[i][0] = i
	
	for j in range(y_len + 1):

		matrix[0][j] = j

	for i in range(1, x_len + 1):
		
		for j in range(1, y_len + 1):
			
			if x[i - 1] == y[j - 1]:
				
				matrix[i][j] = matrix[i - 1][j - 1]
			
			else:
				
				minimum = min(matrix[i - 1][j], 
							  matrix[i][j - 1], 
							  matrix[i - 1][j - 1])
				matrix[i][j] = minimum + 1

	return matrix[x_len][y_len]


@_normalize_case(nargs=2)
def hamming(x: str, y: str, 
	        wobble: bool = False) -> int:
    
    """Calculate the Hamming distance between two sequences.
    
    The Hamming distance is the number of mismatches.

    Note: the `wobble` parameter is not yet implemented.

    Parameters
    ----------
    x : str
        Sequence.
    y : str, optional
        Second sequence for correlation with x.
    wobble : bool, optional
        Whether to calulate correlations taking into account G.U wobble.
        Not yet implemented.

    Returns
    -------
    int
        Hamming distance.

    Examples
    --------
    >>> hamming('AAA', 'ATA')
    1
    >>> hamming('AAA', 'ATT')
    2
    >>> hamming('AAA', 'TTT')
    3

    """

    return sum(a != b for a, b in zip(x, y))


@_normalize_case(nargs=2)
def ratcliff_obershelp(x: str, 
					   y: str) -> int:
    
	"""Calculate the Ratcliff-Obershelp distance between two sequences.
    
    The Ratcliff-Obershelp distance is the number of grouped
	insertions, deletions, and mutations required to make two 
    sequences match.

    Parameters
    ----------
    x : str
        Sequence.
    y : str, optional
        Second sequence for correlation with x.

    Returns
    -------
    int
        Ratcliff-Obershelp distance.

    Examples
    --------
    >>> ratcliff_obershelp('AAATTT', 'AAATTT')
    0
    >>> ratcliff_obershelp('AAATTT', 'ACTTT')
    1
    >>> ratcliff_obershelp('AAATTT', 'AACTTT')
    1
    >>> ratcliff_obershelp('AAAG', 'TCGA')
    2
    
    """
    
	sm = SequenceMatcher(a=x, b=y, 
                         autojunk=False).get_opcodes()
    
	return sum(code[0] != 'equal' for code in sm)


@_normalize_case(nargs=2)
def correlation(x: str, 
                y: str = '',
                wobble: bool = False) -> float:
    
    """Get autocorrelation of a single sequence or 
    correlation between two sequences.

    If a single sequence is provided, it's autocorrelation 
    is calculated, which might be an indicator of secondary structure.

    Note: the `wobble` parameter is not yet implemented.

    Parameters
    ----------
    x : str
        Sequence.
    y : str, optional
        Second sequence for correlation with x.
    wobble : bool, optional
        Whether to calulate correlations taking into account G.U wobble.
        Not yet implemented.

    Returns
    -------
    float
        Correlation.

    Examples
    --------
    >>> correlation('AACC')
    0.0
    >>> correlation('AAATTT')
    2.3
    >>> correlation('AAATTCT')
    1.3047619047619046
    >>> correlation('AAACTTT')
    1.9238095238095236
    >>> correlation('AAA', 'TTT')
    0.0
    >>> correlation('AAA', 'AAA')
    3.0

    """
    
    x = x
    y = y or reverse_complement(x)

    max_len = min(len(x), len(y))
    
    return sum(((max_len - n) - hamming(x[n:], y, wobble)) / (max_len - n)
               for n in range(len(x)))