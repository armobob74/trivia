import random
lowers = 'abcdefghijklmnopqrstuvwxyz'
uppers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
numbers = '0123456789'


def randstr(n=8,choices=lowers+numbers):
    return ''.join([random.choice(choices) for _ in range(n)])
    
