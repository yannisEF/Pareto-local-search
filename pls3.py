import random
import matplotlib.pyplot as plt

from bisect import bisect_left

from read_file import *
from utils import *

from pls1 import PLS1

class PLS3(PLS1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_S = 60 if "init_S" not in kwargs.keys() else kwargs["init_S"]

    def get_init_pop(self, instance):
        pop = []

        while len(pop) < self.init_S:
            copy_obj = instance["Objects"][:]
            q = random.random()
            S = 0
            
            indiv = []
            while S <= instance['W'] and len(copy_obj) > 0:
                r_obj = [(q * x["v1"] + (1-q) * x["v2"]) / x["w"] for x in copy_obj]
                r_obj = [r/sum(r_obj) for r in r_obj]

                new_obj = random.choices(copy_obj, weights=r_obj, k=1)[0]
                copy_obj.remove(new_obj)

                if new_obj['w'] + S <= instance['W']:   
                    indiv.append(new_obj)
                    S += new_obj['w']

            if len(indiv) == 0: raise ValueError("init_S might be to initialize the search")
            else:   pop.append(indiv)
                
        return pop
    
if __name__ == "__main__":
    pls3 = PLS3(nb_files=3)
    pls3.run()
