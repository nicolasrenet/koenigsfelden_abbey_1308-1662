#!/usr/bin/env python3
import itertools
import pytest

def edit_dist( x, y ):
    """
    Compute edit distance, recursively.

    Args:
        x (str): start string
        y (str): target string

    Returns:
        int: the Levenshtein edit distance, where each insertion, deletion and substitution 
            contributes for 1 to the distance.
    """
    memo = [ [-1]*(len(y)+1) for r in range(len(x)+1) ]
    def dist_rec(i, j):
        if memo[i][j]>0:
            return memo[i][j]
        if i<0 or j<0:
            return abs(i-j)
        if x[i] == y[j]:
            d = dist_rec(i-1, j-1)
        else:
            d = min(dist_rec(i-1, j), dist_rec(i, j-1), dist_rec(i-1, j-1)) + 1 
        memo[i][j]=d
        return d

    return dist_rec(len(x)-1, len(y)-1)

def edit_dist_with_mask(x, y, masks=[]):
    """
    Compute edit distance while masking one or more slice of the target string.
    The masked parts do not contribute to the resulting distance.

    Args:
        x (str): start string
        y (str): target string
        masks (List[Tuple[int,int]]): a list of tuples (offset, length)

    Returns:
        int: the Levenshtein edit distance, where each insertion, deletion and substitution 
            contributes for 1 to the distance, if it does not involve the masked parts.
    """
    jays = list( itertools.chain.from_iterable([ range(m[0], m[0]+m[1]) for m in masks ] )) if len(masks)>0 else []

    memo = [ [0]*(len(y)+1) for r in range(len(x)+1) ]
    for i in range(len(x)+1):
        memo[i][0]=i
        for j in range(1,len(y)+1):
            if i==0:
                memo[0][j]=memo[0][j-1] + (0 if j-1 in jays else 1)
            elif x[i-1]==y[j-1]:
                memo[i][j] = memo[i-1][j-1]
            else:
                memo[i][j]=min( memo[i-1][j-1], memo[i-1][j], memo[i][j-1]) + (0 if j-1 in jays else 1)
    #print( ' '*7 +'  '.join(list(y)) + '\n' + '\n'.join( [ f'{x[r-1]}  {row}' for (r,row) in enumerate(memo) ]))
    return memo[-1][-1]



@pytest.mark.parametrize("x, y, distance", [ ('', '', 0),
                                             ('La route tourne', '', 15),
                                             ('', 'Le roi court', 12),
                                             ('La route tourne', 'Le roi court', 7),
                                             ('Le roi court', 'La route tourne', 7),
                                         ])
def test_edit_dist(x, y, distance):
    assert edit_dist(x, y) == distance


@pytest.mark.parametrize("x, y, mask, distance", [ ('', '', [], 0),
                                                   ('La route tourne', '', [], 15),
                                                   ('', 'Le roi court', [], 12),
                                                   ('La route tourne', 'Le roi court', [], 7),
                                                   ('Le roi court', 'La route tourne', [], 7),
                                                   ('', 'La route tourne', [(3,3)], 12),
                                                   ('', 'La route tourne', [(1,2), (5,3)], 10),
                                                   ('La route tourne', 'Le roi court', [(3,5)], 3),
                                                   ('La route tourne', 'Le roi court', [(0,2)], 6),
                                                   ('La route tourne', 'Le roi court', [(0,2),(3,5),(8,3)], 1), ])
def test_edit_dist_with_mask(x, y, mask, distance):
    assert edit_dist_with_mask(x, y, mask) == distance



