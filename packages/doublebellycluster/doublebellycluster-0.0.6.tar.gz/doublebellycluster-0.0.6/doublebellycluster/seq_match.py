import numpy as np

def seq_match(a, b):
    ka = range(len(a))
    kb = range(len(b))
    d1 = []
    num = 2
    for num in range(2, len(a)+1):
        a1 = []
        print(ka)
        for i in ka:
            if i + num <= len(a):
                a1 += [[i, a[i:i + num]]]
        b1 = []
        print(kb)
        for i in kb:
            if i + num <= len(b):
                b1 += [[i, b[i:i + num]]]
        c1 = []
        for n, k in a1:
            for nm, m in b1:
                if k == m:
                    c1 += [[n, nm, k]]
                    d1 = [i for i in d1 if str(i[2])[1:-1] not in str(k)[1:-1]]
        d1 += c1
        ka = list(np.unique([i[0] for i in d1]))[::-1]
        kb = list(np.unique([i[1] for i in d1]))[::-1]
        print(d1)
        if len(c1) == 0:
            break
    return d1



if __name__ == '__main__':
    
    print('\n\n\n\n', seq_match([0,2,3,4,5,6], [0,3,4,0,2,3,4,12,3]))


