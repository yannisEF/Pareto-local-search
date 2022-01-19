import random

from pls import PLS
from elicitor import User, DecisionMaker, Elicitor
from agregation_functions import weighted_sum, OWA, choquet

from utils import *
from read_file import *


# ------------------------- SOLVING PARAMETERS -------------------------

random_obj = True
nb_obj = 20
nb_crit = 3

root = "Data/Other/2KP200-TA-{}.dat"
save_name = root.split('/')[-1][:-4].format(0) + "_obj={}_crit={}"

# ------------------------- ELICITATION PARAMETERS -------------------------

agr_func = weighted_sum
manual_input = False

# --------------------------------------------------------------------------


# Loading the problem
init_instance = read_file(root.format(0))

#   Creating a reduced instance
sampled_index = random.sample(range(init_instance["n"]), nb_obj) if random_obj is True \
                else list(range(nb_obj))

new_weights = [init_instance["Objects"][0][i] for i in sampled_index]
new_values = [[init_instance["Objects"][1][v][i] for i in sampled_index] for v in range(nb_crit)]

instance = {'n':nb_obj, 'W':int(sum(new_weights)/2), 'Objects':[new_weights, new_values]}

# Solving the problem
pls = PLS(root=None, root2=None, instance=instance)
pls.run(verbose_progress=False, show=False, show_best=False)
pls.save_pareto(filename=save_name)

# Starting the elicitation process
user = User() if manual_input is True else DecisionMaker(weighted_sum, len(pls.pareto_coords[0]))
elicitor = Elicitor(pls.pareto_coords, user)

print(elicitor.query_user())