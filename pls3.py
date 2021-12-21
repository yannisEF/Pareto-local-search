from os import popen
import random
import matplotlib.pyplot as plt

from bisect import bisect_left

from read_file import *
from utils import *

from pls1 import PLS1

class PLS3(PLS1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_S = 1 if "init_S" not in kwargs.keys() else kwargs["init_S"]

    def get_init_pop(self, instance):
        """
        Initialize the population with a randomly generated weighted choice
        """

        pop_index = []
        n_dim = len(instance["Objects"][1])

        while len(pop_index) < self.init_S:
            index_objects = list(filter(lambda i: instance["Objects"][0][i] <= instance['W'], range(len(instance["Objects"][0]))))
            
            # Randomly sample a number of weights
            q = [random.random() for _ in range(n_dim)]
            q = [x / sum(q) for x in q]
            S = 0
            
            indiv_index = []
            while S <= instance['W'] and len(index_objects) > 0:
                # Define the objects' weights
                r_obj = [sum(q[i] * instance["Objects"][1][i][v] for i in range(n_dim)) / instance["Objects"][0][v] for v in index_objects]
                r_obj = [r/sum(r_obj) for r in r_obj]

                # Randomly choose a new object
                new_index_obj = random.choices(index_objects, weights=r_obj, k=1)[0]
                index_objects.remove(new_index_obj)
                
                # Add it to the population
                indiv_index.append(new_index_obj)
                S += instance["Objects"][0][new_index_obj]
                
                # Filter the backpack so that only the compatible weigths remain
                index_objects = list(filter(lambda i: instance["Objects"][0][i] <= instance['W'], index_objects))
                
            if len(indiv_index) == 0: raise ValueError("init_S might be to big to initialize the search")
            else:   pop_index.append(indiv_index)
                
        return pop_index
    
if __name__ == "__main__":
    pls3 = PLS3(nb_files=1, nb_tries=1)
    pls3.run()
