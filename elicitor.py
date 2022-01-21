import random

from agregation_functions import weighted_sum

from utils_pls import get_random_weights, get_score
from utils_elicitation import compute_mmr, compute_mr, compute_pmr


class User:
    """
    Class that allows the user to choose between the best solutions
    """

    def __init__(self) -> None:
        self.agregation_function = weighted_sum

    def choose(self, elligibles):
        """
        Choose a solution amongst the given array
        """

        print("Which solution do you prefer?")
        
        for i, sol in enumerate(elligibles):
            print("{} - {}".format(i + 1, sol))
        
        user_input = -1
        while user_input <= 0 or user_input > len(elligibles):
            try:
                user_input = int(input())
            except ValueError:
                pass
        
        print()
        return elligibles[user_input-1]


class DecisionMaker(User):
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
    
    def query_user(self, verbose=True):
        """
        Query the user for its preferred solution amongst a given array
        """

        mmr = compute_mmr(self.user_preferences, self.decision_maker.agregation_function, self.pareto_front)[1] # Initial MMR with empty preferences
        initial_mmr = mmr

        # Until MMR > regret threshold
        while mmr / initial_mmr > self.regret_threshold: 
            # Make the decision maker choose between two alternatives (Current solution strategy)
            #   Update mmr
            if verbose is True: print(mmr)
            list_index_mmr, mmr = compute_mmr(self.user_preferences, self.decision_maker.agregation_function, self.pareto_front)
            if mmr == 0:    return list_index_mmr, mmr
            #   Choose xp in argminMR(x, X; P)
            xp = random.choice(list_index_mmr)
            #   Choose yp in argmaxPMR(xp, y; P)
            yp = random.choice(compute_mr(self.user_preferences, self.decision_maker.agregation_function, self.pareto_front, xp)[0])
            #   Ask the user
            choice = self.decision_maker.choose((xp, yp))
            #   Add the preference to P
            self.user_preferences.append((xp, yp) if choice == xp else (yp, xp))
            if verbose is True: print(self.user_preferences[-1])
        
        return compute_mmr(self.user_preferences, self.decision_maker.agregation_function, self.pareto_front)


if __name__ == "__main__":
    import pickle

    with open("Results/Pareto/2KP100-TA-Pareto.pkl", "rb") as f:
            pareto_front = pickle.load(f)

    # user = User()
    user = DecisionMaker(weighted_sum, len(pareto_front[0]))
    elicitor = Elicitor(pareto_front, user)

    print(elicitor.query_user())