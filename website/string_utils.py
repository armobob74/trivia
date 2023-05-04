import random
lowers = 'abcdefghijklmnopqrstuvwxyz'
uppers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
numbers = '0123456789'


def randstr(n=8,choices=lowers+numbers):
    return ''.join([random.choice(choices) for _ in range(n)])
    
def uniquify(s, strings):
    """
    Produce a version of s that's not in strings
    >>> uniquify('cat',['dog','lizard','cat'])
    'cat 1'
    >>> uniquify('cat',['dog','lizard','cat', 'cat 1'])
    'cat 2'
    >>> uniquify('cat',['dog','lizard'])
    'cat'
    >>> uniquify('cat',[])
    'cat'
    """
    while s in strings:
        a = s.split(' ')
        if a[-1].isdigit():
            a[-1] = str(int(a[-1]) + 1)
            s = ' '.join(a)
        else:
            s = s + ' 1'
    return s

if __name__ == "__main__":  
    import doctest
    doctest.testmod()
