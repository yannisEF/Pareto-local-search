import random

from read_file import *
from utils import *

from pls3 import PLS3

class PLS4(PLS3):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.size_lists = 10 if "size_lists" not in kwargs.keys() else kwargs["size_lists"]

        # Solver used to find the neighbours
        self.solver = PLS3 if "solver" not in kwargs.keys() else kwargs["solver"]

    def get_neighbours(self, current, instance):
        """
        Get a neighbour of the current solution with a randomly weighted exchange
        """

        n_dim = len(instance["Objects"][1])

        # Randomly sample a number of weights
        q = get_random_weights(n_dim)

        # Compute and sort the index of instance by performance value
        self.r_instance = compute_performance_value_list(instance, q, range(instance["n"]))
        self.r_sorted_index_instance = sorted(range(instance["n"]), key=lambda i: self.r_instance[i])

        # Compute the sorted current solution in regards to the performance value
        current_set = set(current)
        r_sorted_index_current, r_sorted_index_not_current = [], []
        for i in self.r_sorted_index_instance:
            if i in current_set:    r_sorted_index_current.append(i)
            else:   r_sorted_index_not_current.append(i)

        # Get the self.size_lists-sized worsts/bests solutions
        worst_index_to_remove = r_sorted_index_current[self.size_lists:]
        best_index_to_add = r_sorted_index_not_current[-self.size_lists:]
        
        # Define a new backpack problem of reduced capacity
        current_set_removed = current_set - set(worst_index_to_remove)
        new_instance = {"n":instance["n"] - len(current_set_removed),
                        "W":instance["W"] - sum(instance["Objects"][0][i] for i in current_set_removed),
                        "Objects":[
                            [instance["Objects"][0][i] for i in worst_index_to_remove + best_index_to_add],
                            [[instance["Objects"][1][v][i] for i in worst_index_to_remove + best_index_to_add] for v in range(len(instance["Objects"][1]))]
                        ]}
        
        # Solve the new instance to find the neighbours
        new_index_offset_neighbours = self.solver(nb_tries=1, root=None, root2=None, instance=new_instance).run(verbose=False, verbose_progress=False, show=False, show_best=False)

        # Correct the offset due to new instance
        new_index_neighbours = []
        for sol in new_index_offset_neighbours:
            new_index_neighbours.append([])
            for i in sol:
                new_index_neighbours[-1].append(worst_index_to_remove[i] if i < len(worst_index_to_remove)
                                                else best_index_to_add[i - len(worst_index_to_remove)])
        
        # Base format of pls1.run considers neighbours as tuple (to remove, to add)
        return [(worst_index_to_remove, neigh_index) for neigh_index in new_index_neighbours]
        
if __name__ == "__main__":
    pls4 = PLS4(nb_files=1, nb_tries=1)
    pls4.run()
        