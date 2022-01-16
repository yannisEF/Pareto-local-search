from utils import *


def update_ideal_nadir(function):
    """
    Decorator to check the update frequency of the nadir and ideal points
    """

    def inner(self, *args, **kwargs):
        if self.counter_since_update % self.ideal_nadir_update_frequency == 0:
            self.compute_ideal_nadir()
        else:
            self.counter_since_update += 1
        
        return function(self, *args, **kwargs)

    return inner


class NDTree:
    """
    NDTree data structure (maximization)
    """

    def __init__(self, parent=None, solutions=[], max_size=20, ideal_nadir_update_frequency=1) -> None:
        # Approximation of the ideal and nadir points of the tree
        self.ideal = None
        self.nadir = None

        # Solutions in the NDTree
        self.solutions = solutions
        self.max_size = max_size

        self.dim = len(self.solutions[0])   

        # Children NDTrees
        self.parent = parent
        self.children = []

        # Counter to update nadir and ideal points
        self.counter_since_update = 0
        self.ideal_nadir_update_frequency = ideal_nadir_update_frequency

        # Compute nadir and ideal points
        self.compute_ideal_nadir()

        # Clamp the solutions to fit the max size of the tree
        if len(self.solutions) > self.max_size:
            self.divide_tree()

    def divide_tree(self):
        """
        Divides the tree into two new ND-Trees
        The new trees are considered as children of the current Tree
        """
        
        cluster1, cluster2 = [], []

        # Loop prevents bad luck with empty cluster
        while len(cluster1) == 0 or len(cluster2) == 0:
            cluster1, cluster2 = k_means(2, self.solutions)

        self.children.append(NDTree(parent=self, solutions=cluster1, max_size=self.max_size))
        self.children.append(NDTree(parent=self, solutions=cluster2, max_size=self.max_size))

        self.solutions = None
    
    def compute_ideal_nadir(self):
        """
        Computes the Ideal and the Nadir points of the tree's solutions
        """

        self.counter_since_update = 0

        if len(self.children) == 0:
            self.ideal = [max(s[i] for s in self.solutions) for i in range(self.dim)]
            self.nadir = [min(s[i] for s in self.solutions) for i in range(self.dim)]
        else:
            self.ideal = [max(c.ideal[i] for c in self.children) for i in range(self.dim)]
            self.nadir = [min(c.nadir[i] for c in self.children) for i in range(self.dim)]

    @update_ideal_nadir
    def update(self, new_solution):
        """
        Update the tree with given solution, returns boolean tuple
        should_be_added, should_destroy_leaf, already_added in subTree
        """

        # Check if new solution dominates one of my child
        if len(self.children) > 0:

            already_added, to_remove = False, []
            for child in self.children:
                should_add, should_remove, already_added_in_child = child.update(new_solution)
                already_added = already_added or already_added_in_child
                
                if should_add and not already_added:
                    child.solutions.append(new_solution)

                    if len(child.solutions) > self.max_size:
                        child.divide_tree()

                    already_added = True

                if should_remove is True:
                    to_remove.append(child)
            
            for child in to_remove:
                self.children.remove(child)
                del child
            
            if len(self.children) == 0:
                self.solutions = [new_solution]
            elif len(self.children) == 1:
                self.__init__(parent=self.parent, solutions=self.children[0].solutions)
            
            # Tell the parent nothing more should be done
            return True, False, True

        # Check if solution is dominated by nadir
        elif is_score_dominated(new_solution, self.nadir):
            return False, False, False

        # Check if ideal is dominated by new solution
        elif is_score_dominated(self.ideal, new_solution):
            return True, True, False
        
        # Check new if solution dominates one of the current solutions
        else:
            for solution in self.solutions:
                if is_score_dominated(new_solution, solution):
                    return False, False

            to_remove = [solution for solution in self.solutions if is_score_dominated(solution, new_solution)]
            for bad_solution in to_remove:
                self.solutions.remove(bad_solution)
                        
            return True, False, False
    
    def __str__(self):
        if len(self.children) == 0:
            return "Solutions: \t {}".format(self.solutions)
        
        else:
            text = "Tree with {} children\n".format(len(self.children))
            for k in range(len(self.children)):
                text += "\tChild {}: ".format(k)

                other_child = str(self.children[k]).split("\n")

                text += other_child[0] + "\n"
                for ligne in other_child[1:]:
                    text += "\t" + ligne + "\n"

            return text


if __name__ == "__main__":
    sol = [(1,0),(.5,.5),(0,1)]
    leaf = NDTree(solutions=sol, max_size=2)

    leaf.update((.25,.8))
    print(leaf)

    import pickle

    with open("Results/Pareto/2KP100-TA-Pareto.pkl", "rb") as f:
            pareto_front = pickle.load(f)

    leaf = NDTree(solutions=pareto_front, max_size=20)
    print(leaf)

