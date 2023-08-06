"""Miscellaneous utilities used in streq."""

from collections import namedtuple
from collections.abc import Callable, Sequence
from functools import wraps
import os

import yaml

from .circular import Circular

_data_path = os.path.join(os.path.dirname(__file__), 
                          'sequences.yml')

with open(_data_path, 'r') as f:
    _sequences = yaml.safe_load(f)

sequence_dict = dict(
    complementer = str.maketrans(_sequences['complement']),
    re_sites = _sequences['type_iis_re'],
    DNA = _sequences['alphabet']['DNA'],
    RNA = _sequences['alphabet']['RNA'],
    base2regex = str.maketrans(_sequences['base2regexp']),
    PAMs = _sequences['PAMs']
)

SequenceCollection = namedtuple('SequenceCollection',
                                sequence_dict)

sequences = SequenceCollection(**sequence_dict)


def _make_lower(x: str, 
                lower: Sequence[bool]):
    
    return ''.join(str.lower(letter) if low 
                   else letter 
                   for letter, low in zip(x, lower))


def _normalize_case(nargs: int = 1) -> Callable[[Callable], Callable]:
    
    def decor(f: Callable[[str, str], 
                               str]) -> Callable[[str, str], 
                                                 str]:
        
        @wraps(f)
        def normalized(*args, **kwargs):

            args = (x.casefold().upper() 
                    for i, x in enumerate(args) if i < nargs)
            
            return f(*args, **kwargs)
        
        return normalized
    
    return decor


def _preserve_case(f: Callable[[str], 
                               str]) -> Callable[[str], 
                                                 str]:

    @wraps(f)
    def preserved(x: str, 
                  *args, **kwargs):
        
        is_lower = (letter.islower() for letter in x)

        x = f(x.casefold().upper(), *args, **kwargs)
        
        return _make_lower(x, is_lower)
    
    preserved.__doc__ = (f.__doc__ or '') + (
    """
    Note: Preserves case.

    """
    )
    
    return preserved


def _preserve_circular(f: Callable[[str], 
                                    str]) -> Callable[[str], 
                                                  str]:
    
    @wraps(f)
    def preserved(x: str, 
                  *args, **kwargs):

        is_circular = isinstance(x, Circular)

        x = f(x, *args, **kwargs)

        if is_circular:

            x = Circular(x)

        return x
    
    preserved.__doc__ = (f.__doc__ or '') + (
    """
    Note: Preserves circularity.

    """
    )
    
    return preserved