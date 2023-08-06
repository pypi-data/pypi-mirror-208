# 🧬 streq

Python utilities for working with nucleotide sequence strings.

## Installation

### The easy way

Install the pre-compiled version from PyPI:

```
pip install streq
```

### From source

Clone the repository, then `cd` into it. Then run:

```
pip install -e .
```

## Usage

Streq provides various utility functions in Python for working with nucleotide sequences. 
Sequences can be upper or lower case, and case will be preserved through transformations.

### Transformations

Reverse complement.

```
>>> import streq as sq
>>>
>>> sq.reverse_complement('ATCG')
'CGAT'
```

Convert between RNA and DNA alphabets.

```
>>> sq.to_rna('ATCG')
'AUCG'
>>> sq.to_dna('AUCG')
'ATCG'
```

Slice circular sequences such as plasmids or bacterial genomes.

```
>>> sq.Circular('ATCG')[-1:3]
'GATC'
>>> sq.reverse_complement(sq.Circular('ATCG'))[-1:3]
'CGAT'
```

Cases are preserved throughout the transformations.

```
>>> sq.reverse_complement(sq.Circular('ATCg'))
'cGAT'
```

### Calculations

Get GC and pyrimidine content.

```
>>> sq.gc_content('AGGG')
0.75
>>> sq.pyrimidine_content('AUGGG')
0.2
```

Get autocorrelation (rough indicator for secondary structure).

```
>>> sq.correlation('AACC')
0.0
>>> sq.correlation('AAATTT')
2.3
>>> sq.correlation('AAATTCT')
1.3047619047619046
>>> sq.correlation('AAACTTT')
1.9238095238095236
```

Provide a second sequence to get correlation between sequences.

```
>>> sq.correlation('AAA', 'TTT')
0.0
>>> sq.correlation('AAA', 'AAA')
3.0
```

### Distances

Calculate Levenshtein (insert, delete, mutate) distance.

```
>>> sq.levenshtein('AAATTT', 'AAATTT')
0
>>> sq.levenshtein('AAATTT', 'ACTTT')
2
>>> sq.levenshtein('AAAG', 'TCGA')
4
```

Calculate Hamming (mismatch) distance.

```
>>> sq.hamming('AAA', 'ATA')
1
>>> sq.hamming('AAA', 'ATT')
2
>>> sq.hamming('AAA', 'TTT')
3
```

### Search

Search sequences using IUPAC symbols and iterate through the results.

```
>>> for (start, end), match in sq.find_iupac('ARY', 'AATAGCAGTGTGAAC'):
...     print(f"Found ARY at {start}:{end}: {match}")
... 
Found ARY at 0:3: AAT
Found ARY at 3:6: AGC
Found ARY at 6:9: AGT
Found ARY at 12:15: AAC
```

Find common Type IIS restriction sites:

```
>>> sq.which_re_sites('AAAGAAG')
()
>>> sq.which_re_sites('AAAGAAGAC')
('BbsI',)
>>> sq.which_re_sites('AAAGAAGACACCTGC')
('BbsI', 'PaqCI')
```

## Documentation

Check the API [here](https://streq.readthedocs.io/).