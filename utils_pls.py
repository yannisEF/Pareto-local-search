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


def d(x, y, P=None):
    """
    Return the weighted euclidian distance between two points
    """

    if P is None:   P = [1 for k in range(len(x))]
    return math.sqrt(sum([P[k] * (x[k] - y[k])**2 for k in range(len(P))]))


def dprime(A, y, P=None):
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


def k_means(K, points, score_function, min_distance=float("-inf")):
    """
    Applies K-means algorithm to a given set of points
    """
    
    new_points = random.sample(points, len(points))
    clusters = [[score_function(new_points[-1]), [points.index(new_points.pop())]] for _ in range(K)] # (center, population)
    point_to_cluster = {ip:None for ip in range(len(points))}

    for i, cluster in enumerate(clusters):
        point_to_cluster[cluster[-1][0]] = i

    convergence = False
    while convergence is False:
        convergence = True
        for i, point in enumerate(points):
            distances = [d(score_function(point), cluster[0]) for cluster in clusters]
            best_distance = distances.index(min(distances))

            try:
                if point_to_cluster[i] is not None:
                    clusters[point_to_cluster[i]][-1].remove(i)
            except ValueError:
                pass

            convergence = convergence and ((best_distance == point_to_cluster[i]) or best_distance <= min_distance)
            point_to_cluster[i] = best_distance
            clusters[best_distance][-1].append(i)

        # Getting the new average centers according to input function
        for k in range(len(clusters)):
            if len(clusters[k][-1]) > 0:
                s = [0 for i in range(len(clusters[0][0]))]
                for ip in clusters[k][-1]:
                    new_score = score_function(points[ip])
                    for i in range(len(clusters[0][0])):
                        s[i] += new_score[i]
                
                clusters[k][0] = [p/len(clusters[k][-1]) for p in s]
    
    return tuple([points[i] for i in cluster[1]] for cluster in clusters)
