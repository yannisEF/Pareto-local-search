import time
import math
import random
import pickle


def index_to_values(instance, x):
    """
    Return the lists of values given an instance and a list of index
    """
    return [[instance["Objects"][1][v][i] for i in x] for v in range(len(instance["Objects"][1]))]

def get_score(x):
    """
    Return sum of the values of a solution for each objective
    """

    return tuple(sum(v) for v in x)

def get_proportion(Yexact, Yapprox):
    """
    Return the proportion of solutions exactly approximated
    """

    return len(set(Yapprox) & set(Yexact)) / len(set(Yexact))


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

def normalize(A):
    """
    Normalize a list so that it sums to 1
    """
    
    sA = sum(A)
    return [x / sA for x in A]

def get_random_weights(size):
    """
    Returns a list of randomly generated weights that sums to 1
    """

    q = [random.random() for _ in range(size)]
    return normalize(q)

def compute_performance_value(instance, weights, index):
    """
    Compute the performance value of a given object
    """

    return sum(weights[i] * instance["Objects"][1][i][index] for i in range(len(weights))) / instance["Objects"][0][index]

def compute_performance_value_list(instance, weights, index_objects):
    """
    Compute the list of performance values of a given list of objects
    """

    return [compute_performance_value(instance, weights, v) for v in index_objects]
