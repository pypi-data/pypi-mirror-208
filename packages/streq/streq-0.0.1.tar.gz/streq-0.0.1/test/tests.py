import doctest
import streq as sq

if __name__ == '__main__':

    doctest.testmod(sq.circular)
    doctest.testmod(sq.distance)
    doctest.testmod(sq.seqtools)
    doctest.testmod(sq.utils)