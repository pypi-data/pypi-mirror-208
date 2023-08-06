"""Classes relating to circular strings."""


class Circular(str):

    """A string-like object which can be circularly sliced.

    Useful for sequences that represent a bacterial genome 
    or a plasmid.

    Currently this only works if the length of the slice is 
    shorter than the sequence's total length.

    Methods
    -------
    __getitem__
        Slice string as if it were a circle.

    Examples
    --------
    >>> Circular('ATCG')[:3]
    'ATC'
    >>> Circular('ATCG')[-1:3]
    'GATC'
    >>> from streq import reverse_complement
    >>> reverse_complement(Circular('ATCg'))
    'cGAT'

    """

    def __getitem__(self, __key: slice) -> str:

        """Slice circularly.
        
        Parameters
        ----------
        __key : slice
            Python slice

        Returns
        -------
        str
            Slice from Circular object. Ordinary string.
        
        """

        if isinstance(__key, int):

            return super().__getitem__(__key)
        
        elif isinstance(__key, slice):

            start = __key.start or 0
            stop = (len(self) if __key.stop is None 
                    else __key.stop) 

            return (super().__getitem__(slice(start, None)) + self)[:(stop - start)][::__key.step]
        