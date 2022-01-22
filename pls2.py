from bisect import bisect_left

from pls1 import PLS1

from utils_read_file import *
from utils_pls import *


class PLS2(PLS1):
    """
    Enhanced version of PLS for 2 objectives only, decreases computing time but doesn't change score
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.score_pareto = []

    def update(self, Pareto, x):
        """
        Pareto front is now ordered, index 0 rising (therefore 1 descending)
        Should only be called on the approximated Pareto front
        """

        # Doesn't work in more than 2 dimensions
        if len(x[0]) > 3:
            raise ValueError("PLS2 is only available with 2 objectives")
        
        if len(self.score_pareto) == 0:
            self.score_pareto = [get_score(g) for g in Pareto]

        score_x = get_score(x)

        # Get the index to insert the solution at
        i = bisect_left(self.score_pareto, score_x)

        dominated = []
        # If the following solution doesn't dominate x, it can be added
        if i != len(Pareto) and is_score_dominated(score_x, self.score_pareto[i]):
            return False

        # Only the preceding solutions can dominate x, we iterate through them to check
        for index in range(i-1, -1, -1):
            # If a solution is not dominated by x, neither are the rest, so we break
            if is_score_dominated(self.score_pareto[index], score_x):
                dominated.append(Pareto[index])
            else:
                break
        
        # We remove the dominated solutions from the Pareto front
        for sol in dominated:
            Pareto.remove(sol)
            self.score_pareto.remove(get_score(sol))

        # We insert x into the Pareto front
        Pareto[:] = Pareto[:i] + [x] + Pareto[i:]
        self.score_pareto[:] = self.score_pareto[:i] + [score_x] + self.score_pareto[i:]

        # PROBLEM WITH PARETO
        return True
    

if __name__ == "__main__":
    pls2 = PLS2(nb_files=1, nb_tries=1)
    pls2.run()
