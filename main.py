import time
import random

from pls_ndtree import PLS_NDTREE

from elicitor import User, DecisionMaker, Elicitor
from agregation_functions import weighted_sum, OWA, choquet

from utils_main import *
from read_file import *


# ------------------------- SOLVING PARAMETERS -------------------------

random_obj = True
nb_obj = 20
nb_crit = 3

root = "Data/Other/2KP200-TA-{}.dat"
save_name = root.split('/')[-1][:-4].format(0) + "_obj={}_crit={}".format(nb_obj, nb_crit)

# ------------------------- ELICITATION PARAMETERS -------------------------

agr_func = OWA
manual_input = False

# ------------------------- ANALYSIS PARAMETERS -------------------------

nb_runs = 20

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------


methods = ["first_ndtree", "second"]
times = {k:[] for k in methods}
errors = {k:[] for k in methods}
questions = {k:[] for k in methods}
mmr_first = {k:[] for k in methods[:-1]}

for _ in range(nb_runs):

    print(50*" ", end='\r')
    print("{}/{}".format(_, nb_runs) + "\tLoading the problem...", end="\r")

    # loading the user
    user = User() if manual_input is True else DecisionMaker(weighted_sum, nb_crit)

    # Loading the problem
    init_instance = read_file(root.format(0))
    sampled_index = random.sample(range(init_instance["n"]), nb_obj) if random_obj is True \
                    else list(range(nb_obj))

    new_weights = [init_instance["Objects"][0][i] for i in sampled_index]
    new_values = [[init_instance["Objects"][1][v][i] for i in sampled_index] for v in range(nb_crit)]

    instance = {'n':nb_obj, 'W':int(sum(new_weights)/2), 'Objects':[new_weights, new_values]}

    print(50*" ", end='\r')
    print("{}/{}".format(_, nb_runs) + "\tFinding the true optimal solution...", end="\r")

    # Finding the true optimal solution with linear programming
    real_val = solve_backpack_preference(instance, nb_crit, user)

    print(50*" ", end='\r')
    print("{}/{}".format(_, nb_runs) + "\tSolving with PLS_NDTREE NDTree...", end="\r")

    # First procedure - NDTree
    PLS_NDTREE = PLS_NDTREE(root=None, root2=None, instance=instance)
    
    start = time.time()
    PLS_NDTREE.run(verbose_progress=False, show=False, show_best=False)
    elicitor = Elicitor(PLS_NDTREE.pareto_coords, user)
    opt_val, mmr = elicitor.query_user(verbose=False)

    times["first_ndtree"].append(time.time() - start)
    errors["first_ndtree"].append(user.agregation_function(user.weights, opt_val[0]) - real_val)
    questions["first_ndtree"].append(len(elicitor.user_preferences))
    mmr_first["first_ndtree"].append(mmr)

    # Second procedure

# Plotting the results
#   MMR en fonction du Nombre de questions

#   Bar plots
ax = plt.subplot()
plot_bar_dict(ax=ax, title="Execution time per method", entry_dict=times, y_label="Execution time")
plt.show()

ax = plt.subplot()
plot_bar_dict(ax=ax, title="Error to real optimal per method", entry_dict=errors, y_label="Error amount")
plt.show()

ax = plt.subplot()
plot_bar_dict(ax=ax, title="Number of questions per method", entry_dict=questions, y_label="Number of questions")
plt.show()