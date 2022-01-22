from utils_pls import *


def update_decorator(function):
    """
    Decorator to check the update frequency of the nadir and ideal points, and divide the tree if too many elements
    """

    def inner(self, *args, **kwargs):        
        res = function(self, *args, **kwargs)
        
        if self.counter_since_update > 0 and self.counter_since_update % self.ideal_nadir_update_frequency == 0:
            self.compute_ideal_nadir()
        else:
            self.counter_since_update += 1

        if len(self.children) == 0 and len(self.solutions) > self.max_size:
            self.divide_tree()
        
        return res

    return inner


class NDTree:
    """
    NDTree data structure (maximization)
    """

    def __init__(self, parent=None, solutions=[], max_size=20, ideal_nadir_update_frequency=5,
                 instance=None, get_score_function=lambda inst, x:get_score(index_to_values(inst, x))) -> None:
        # Approximation of the ideal and nadir points of the tree
        self.ideal = None
        self.nadir = None

        # Solutions in the NDTree
        self.solutions = []
        self.instance = instance
        self.max_size = max_size
        self.old_get_score_function = get_score_function
        self.get_score_function = lambda x: list(get_score_function(self.instance, x))

        # Children NDTrees
        self.parent = parent
        self.children = []
        self.add_where = [] # Containing where new solutions can be added to

        # Counter to update nadir and ideal points
        self.counter_since_update = 0
        self.ideal_nadir_update_frequency = ideal_nadir_update_frequency

        # Compute nadir and ideal points
        if len(solutions) > 0:
            first_score = self.get_score_function(solutions[0])
            self.ideal, self.nadir = first_score[:], first_score[:]
            self.solutions = [solutions[0]]

        for sol in solutions[1:]:
            self.update(sol, initialization=True)

    def reset(self):
        """
        Reset the tree
        """

        self.counter_since_update = 0
        self.ideal, self.nadir = None, None
        self.solutions, self.children = [], []

    def get_solutions(self):
        """
        Retrieve all the solutions from the children
        """

        if len(self.children) == 0:
            return self.solutions
        
        to_return = []
        for child in self.children:
            to_return += child.get_solutions()
        
        return to_return
    
    def add_to_children(self, newSolution, newScore):
        """
        Add a solution to the closest child
        """

        if len(self.children) == 0:
            self.solutions.append(newSolution)
            return
        
        distances = [(c, d(newScore, c.ideal)) for c in self.children]
        min(distances, key=lambda x: x[-1])[0].add_to_children(newSolution, newScore)
        return


    def divide_tree(self):
        """
        Divides the tree into two new ND-Trees
        The new trees are considered as children of the current Tree
        """
        
        cluster1, cluster2 = [], []

        
        # Loop prevents bad luck with empty cluster
        while len(cluster1) == 0 or len(cluster2) == 0:
            cluster1, cluster2 = k_means(2, self.solutions, self.get_score_function)

        self.solutions = []

        self.children.append(NDTree(parent=self, solutions=cluster1, max_size=self.max_size,
                                    instance=self.instance, get_score_function=self.old_get_score_function))
        self.children.append(NDTree(parent=self, solutions=cluster2, max_size=self.max_size,
                                    instance=self.instance, get_score_function=self.old_get_score_function))

    def compute_ideal_nadir(self):
        """
        Computes the Ideal and the Nadir points of the tree's solutions
        """
        
        
        
        if len(self.children) == 0:
            score_solutions = [self.get_score_function(s) for s in self.solutions]
            self.ideal = [max(sol[i] for sol in score_solutions) for i in range(len(score_solutions[0]))]
            self.nadir = [min(sol[i] for sol in score_solutions) for i in range(len(score_solutions[0]))]
        else:
            
            for child in self.children:
                child.compute_ideal_nadir()
            
            dim = len(self.children[0].ideal)
            self.ideal = [max(c.ideal[i] for c in self.children) for i in range(dim)]
            self.nadir = [min(c.nadir[i] for c in self.children) for i in range(dim)]
           

    @update_decorator
    def update(self, new_solution, new_score=None, initialization=False):
        """
        Update the tree with given solution, returns boolean tuple
        should_add, should_destroy_leaf
        """

        new_score = self.get_score_function(new_solution) if new_score is None else new_score

        # Check if the tree is not empty
        if len(self.children) == 0 and (self.parent is None or initialization is True) and len(self.solutions) == 0:
            self.solutions = [new_solution]
            self.nadir, self.ideal = new_score[:], new_score[:]
            return True, False

        # Check if the solution is obsolete
        elif is_score_dominated(new_score, self.nadir):
            return False, False

        # Check if the leaf is obsolete
        elif is_score_dominated(self.ideal, new_score):
            if self.parent is None or initialization is True:
                self.children = []
                self.solutions = [new_solution]
                self.nadir, self.ideal = new_score[:], new_score[:]
            return True, True

        # We can't say, have to check solutions one by one
        else:
            # First we always have to update the ideal, regardless of the update frequency
            for k in range(len(new_score)):
                if self.ideal[k] < new_score[k]:
                    self.ideal[k] = new_score[k]

            # We have no children to check
            if len(self.children) == 0:
                to_remove = []
                for solution in self.solutions:
                    sol_score = self.get_score_function(solution)
                    
                    # ND-Tree means if one solution dominates the candidate, the latter can be discarded
                    if is_score_dominated(new_score, sol_score):
                        return False, False
                    # List which solutions are now dominated
                    elif is_score_dominated(sol_score, new_score):
                        to_remove.append(solution)

                # Removing obsolete solutions
                for solution in to_remove:
                    self.solutions.remove(solution)
                
                if self.parent is None or initialization is True:
                    self.solutions.append(new_solution)

                return True, False

            # We have to peek into our children
            else:
                # Check the children leaves one by one
                self.add_where, destroy_where = [], []
                for child in self.children:
                    should_add, should_destroy = child.update(new_solution, new_score)

                    if should_add is True:
                        self.add_where.append(child)
                    if should_destroy is True:
                        destroy_where.append(child)
                
                # Destroy the obsolete leaves
                should_add = len(self.add_where) == len(self.children)
                for child in destroy_where:
                    self.children.remove(child)
                    try:
                        self.add_where.remove(child)
                    except ValueError:
                        pass
                
                # Only the root can add the solution
                if (self.parent is None or initialization is True) and should_add:

                    # The new solution destroyed our leaves, so we have to create a new one
                    if len(self.add_where) == 0:
                        self.children.append(NDTree(parent=self, solutions=[new_solution], max_size=self.max_size,
                                                    instance=self.instance, get_score_function=self.old_get_score_function))
                    else:
                        child = self.add_where[0]
                        while len(child.add_where) != 0:
                            child = child.add_where[0]
                        
                        if len(child.children) == 0:
                            child.solutions.append(new_solution)
                        else:
                            child.add_to_children(new_solution, new_score)

                # We absorb our child if its alone
                if len(self.children) == 1:
                    child = self.children[0]

                    self.children = child.children
                    self.solutions = child.solutions
                    self.ideal, self.nadir = child.ideal[:], child.nadir[:]

                    del child
                
                self.add_where = []
                return should_add, (len(self.children) == 0)
    
    def __str__(self):
        pref = 86 * "-" if self.parent is None else ""

        if len(self.children) == 0:
            return pref + "\n" + "Solutions: \t {}".format(self.solutions) + "\n" + pref
        
        else:
            text = "Tree with {} children\n".format(len(self.children))
            for k in range(len(self.children)):
                text += "\tChild {}: ".format(k)

                other_child = str(self.children[k]).split("\n")

                text += other_child[0] + "\n"
                for ligne in other_child[1:]:
                    text += "\t" + ligne + "\n"
            
            if self.parent is None:
                text = pref + "\n" + text[:-2] + pref 

            return text


if __name__ == "__main__":
    # sol = [(1,0),(.5,.5),(0,1)]
    # leaf = NDTree(solutions=sol, max_size=2, get_score_function=lambda inst, x:x)

    # leaf.update((.25, .8))
    # leaf.update((.5, .8))
    # leaf.update((1, .25))
    # print(leaf)
    # print(leaf.ideal, leaf.nadir)

    import pickle

    with open("Results/Pareto/2KP100-TA-Pareto.pkl", "rb") as f:
            pareto_front = pickle.load(f)

    leaf = NDTree(solutions=pareto_front, max_size=20, get_score_function=lambda inst, x:[i for i in x])
    print(leaf)
    print(len(leaf.get_solutions()))

    # leaf = NDTree(get_score_function=lambda inst, x:x, max_size=1)
    # print(leaf)

    # leaf.update((.5,.5))
    # print(leaf)

    # leaf.update((1,1))
    # leaf.update((0,9))
    # leaf.update((1.5,0.8))
    # leaf.update((-0.4,20))
    # print(leaf)

