from pls3 import PLS3

from Utils.utils_read_file import *
from Utils.utils_pls import *


class PLS4(PLS3):
    # NOT WORKING
    # SUPPOSED TO GET MANY NEIGHBOURS AT ONCE

    def __init__(self, *args, size_lists=10, solver=PLS3, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.size_lists = size_lists

        # Solver used to find the neighbours
        self.solver = solver

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
        worst_index_to_remove = r_sorted_index_current[:self.size_lists]
        best_index_to_add = r_sorted_index_not_current[-self.size_lists:]

        # Define a new backpack problem of reduced capacity
        new_objects_index = worst_index_to_remove + best_index_to_add
        new_instance = {"n":len(new_objects_index),
                        "W":sum(instance["Objects"][0][i] for i in set(worst_index_to_remove)),
                        "Objects":[
                            [instance["Objects"][0][i] for i in new_objects_index],
                            [[instance["Objects"][1][v][i] for i in new_objects_index] for v in range(n_dim)]
                        ],
                        "New index to old":{k:v for k, v in enumerate(new_objects_index)}}

        # Solve the new instance to find the neighbours
        solver = self.solver(nb_tries=1, root=None, root2=None, instance=new_instance, init_S=len(new_objects_index)//5)
        new_index_offset_neighbours = solver.run(verbose=False, verbose_progress=False, show=False, show_best=False)
        
        # Correct the offset due to new instance
        new_index_neighbours = [[new_instance["New index to old"][i] for i in sol] for sol in new_index_offset_neighbours]

        # Base format of pls1.run defines neighbours as tuple (to remove, to add)
        return [(set(worst_index_to_remove) - set(neigh_index), neigh_index) for neigh_index in new_index_neighbours]

   
if __name__ == "__main__":
    pls4 = PLS4(nb_files=1, nb_tries=1)
    pls4.run()