import time
import math


def get_score(x):
    """
    Return sum of the weight of a solution for each objective
    """

    return tuple(sum([i[obj] for i in x]) for obj in sorted(x[0].keys() - {"w"}))


def get_proportion(Yexact, Yapprox):
    """
    Return the proportion of solutions exactly approximated
    """

    return sum([get_score(v) in Yexact for v in Yapprox]) / len(Yexact)


def d(x, y, P):
    """
    Return the weighted euclidian distance between two points
    """

    return math.sqrt(sum([P[k] * (x[k] - y[k])**2 for k in range(len(P))]))


def dprime(A, y, P):
    """
    Return the shortest distance between y and A
    """

    return min(d(x, y, P) for x in A)


def get_distance(A, B):
    """
    Return the average distance between A (exact) and B (approximated)
    """

    ideal, nadir = [], []
    for i in range(len(A[0])):
        ideal.append(max(A, key=lambda x: x[i])[i])
        nadir.append(min(A, key=lambda x: x[i])[i])

    P = [1/abs(ideal[k] - nadir[k]) for k in range(len(ideal))]
    return sum(dprime(A, get_score(y), P) for y in B) / len(A)


def get_avg(A, precision=2):
    """
    Return the average of a list with given precision
    """

    return round(sum(A) / len(A), precision)


def is_score_dominated(score_x, score_y):
    """
    Returns True if given score x is dominated by given score y
    """
    return all([score_x[k] <= score_y[k] for k in range(len(score_x))])


def is_dominated(x, y):
    """
    Return True if x is dominated by y
    """

    return is_score_dominated(get_score(x), get_score(y))
