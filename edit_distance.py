#!/usr/bin/env python3

def dist( x, y, mask=() ):

    memo = [ [-1]*(len(y)+1) for r in range(len(x)+1) ]
    def dist_rec(i, j, tab=''):

        #print( tab + f'dist_rec({x[:i+1]}, {y[:j+1]})')
        if memo[i][j]>0:
            return memo[i][j]
        if i<0 or j<0:
            return abs(i-j)
        # same chars: no cost
        if x[i] == y[j]:
            d = dist_rec(i-1, j-1, tab+'  ')
        # different chars: cost is 1 for insertion (from up), deletion (from left), or substitution (from upper-left)
        else:
            d = min(dist_rec(i-1, j, tab+'  '), dist_rec(i, j-1, tab+'  '), dist_rec(i-1, j-1, tab+'  ')) + 1 
        memo[i][j]=d
        return d

    def dist_rec_mask(i, j):

        if memo[i][j]>=0:
            return memo[i][j]
        if i<0:
            if len(mask) and j in jays and j >= mask[0]:
                return j-mask[0]+1
            else: 
                return j+1 - len(mask)
        if j<0:
            return i
        if x[i] == y[j]:
            d = dist_rec(i-1, j-1)
        else:
            cost = (0 if j in jays else 1)
            d = min(dist_rec_mask(i-1, j), dist_rec_mask(i, j-1), dist_rec_mask(i-1, j-1)) + cost
            print(f'{i},{j}: cost={cost}, d={d}')
        memo[i][j]=d
        return d

    #print( tab + f'dist_rec({x[:i+1]}, {y[:j+1]})')
    jays = list(range(mask[0], mask[0]+mask[1])) if len(mask)>0 else []
    print(jays, f"'{y[mask[0]:mask[0]+mask[1]]}'" if mask else '' )
    d =  dist_rec_mask( len(x)-1, len(y)-1)

    return d

#print(dist('ACDE', 'BCDC'))

# X indexé par i = prédiction
# Y indexé par j = target
# mask applied to target (not X)

#print(dist('Le roi court', 'La roue tourne'))
print(dist('La roi caur', 'Le roi court',()))
print(dist('La roi caur', 'Le roi court',(4,8))) # mask over [ourt] should negate dist.
