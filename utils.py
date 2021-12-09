import time
import math
import matplotlib.pyplot as plt



def get_proportion(Yexact, Yapprox):# Yapprox is a dictionary with v1: v2: 
    return len(set(Yapprox) & set(Yexact))/len(set(Yexact))


def d(x, y, p1, p2):
    return math.sqrt(p1 * (x[0] - y[0])**2 + p2 * (x[1] - y[1])**2)

def dprime(A, y, p1, p2):
    return min(d(x, y, p1, p2) for x in A)

"""def get_distance(Yexact, Yapprox):
    best1, best2 = max(Yexact), max(Yexact)
    p1, p2 = 1/abs(best1[0] - best2[0]), 1/abs(best1[1] - best2[1])
    return sum(dprime(Yexact, (y), p1, p2) for y in Yapprox) / len(Yexact)
"""
def get_avg(A, precision=2):
    return round(sum(A) / len(A), precision)


def draw_pts(all_pts,exact):
    
    _x = []
    _y = []
    x_=[]
    y_=[]
    
    for x, y in all_pts:
        _x.append(x)
        _y.append(y)
    for x, y in exact:
        x_.append(x)
        y_.append(y)
        
    plt.plot(_x, _y, 'ro')
    plt.plot(x_, y_)
    plt.grid()
    plt.show()
    
    return 0
