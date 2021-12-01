import random
import matplotlib.pyplot as plt

from bisect import bisect_left

from read_file import *
from utils import *

from pls1 import PLS1

class PLS2(PLS1):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(self, Pareto, x):
        """Pareto front is now ordered, index 0 rising and 1 descending"""
        score_pareto = [get_score(y) for y in Pareto]
        score_x = get_score(x)

        i = bisect_left(score_pareto, score_x)

        notDominated = True
        dominated = None
        if i != len(Pareto) and is_score_dominated(score_x, score_pareto[i]):   notDominated = False
        if i != 0 and not is_score_dominated(score_pareto[i-1], score_x): dominated = Pareto[i-1]

        try:
            Pareto.remove(dominated)
        except ValueError:
            pass

        if notDominated is True:
            Pareto[:] = Pareto[:i] + [x] + Pareto[i:]

        return notDominated
    
if __name__ == "__main__":
    pls2 = PLS2()
    pls2.run()
