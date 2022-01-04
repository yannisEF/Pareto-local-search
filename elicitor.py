import random

from utils import get_random_weights
from utils_elicitation import compute_mmr, compute_mr, compute_pmr


class DecisionMaker:
    """
    Decision maker that holds preference and is able to choose its favourite solution from a given array of proposed solutions
    """

    def __init__(self, agregation_function, dim, weights=None):
        self.agregation_function = agregation_function
        self.weights = weights if weights is not None else get_random_weights(dim)
    
    def choose(self, elligibles):
        """
        Choose a solution amongst the given array
        """
        
        return max(elligibles, key=lambda x: self.agregation_function(self.weights, x))


class Elicitor:
    """
    Incremental elicitation procedure to make recommendations to a decision maker
    """

    def __init__(self, pareto_front, decision_maker, regret_threshold=0.1):
        """
        Pareto front is the approximation of the pareto-optimal solutions of a problem
        """

        self.pareto_front = pareto_front # coords of the pareto front

        self.decision_maker = decision_maker
        self.regret_threshold = regret_threshold # Normalized threshold

        self.user_preferences = []
    
    def query_user(self):
        """
        Query the user for its preferred solution amongst a given array
        """

        raise NotImplementedError("Need to add choice of xp and yp")

        mmr = 1.1
        # Until MMR > regret threshold
        while mmr > self.regret_threshold: 
        #   Make the decision maker choose between two alternatives (Current solution strategy)
            # Update mmr
            mmr = compute_mmr(self.user_preferences, self.pareto_front)
            # Choose xp in argminMR(x, X; P)
            xp = None
            # Choose yp in argmaxPMR(xp, y; P)
            yp = None
            # Ask the user
            choice = self.decision_maker.choose((xp, yp))
            # Add the preference to P
            self.user_preferences.append((xp, yp) if choice == xp else (yp, xp))
