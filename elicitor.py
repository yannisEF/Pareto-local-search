import random

from agregation_functions import weighted_sum

from utils import get_random_weights, get_score
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

        self.pareto_front = pareto_front

        self.decision_maker = decision_maker
        self.regret_threshold = regret_threshold # Normalized threshold

        self.user_preferences = [] # P
    
    def query_user(self):
        """
        Query the user for its preferred solution amongst a given array
        """

        mmr = compute_mmr(self.user_preferences, self.pareto_front)[1] # Initial MMR with empty preferences
        initial_mmr = mmr

        # Until MMR > regret threshold
        while mmr / initial_mmr > self.regret_threshold: 
            # Make the decision maker choose between two alternatives (Current solution strategy)
            #   Update mmr
            list_index_mmr, mmr = compute_mmr(self.user_preferences, self.pareto_front)
            #   Choose xp in argminMR(x, X; P)
            xp = random.choice(list_index_mmr)
            #   Choose yp in argmaxPMR(xp, y; P)
            # maxxx
            yp = random.choice([compute_pmr(self.user_preferences, xp, y) for y in self.pareto_front])
            #   Ask the user
            choice = self.decision_maker.choose((xp, yp))
            #   Add the preference to P
            self.user_preferences.append((xp, yp) if choice == xp else (yp, xp))
        
        return compute_mmr(self.user_preferences, self.pareto_front)


if __name__ == "__main__":
    import pickle

    with open("Results/Pareto/2KP100-TA-Pareto.pkl", "rb") as f:
            pareto_front = pickle.load(f)
    
    print(pareto_front)
    user = DecisionMaker(weighted_sum, len(pareto_front[0]))
    elicitor = Elicitor(pareto_front, user)

    print(elicitor.query_user())