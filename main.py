from tabnanny import verbose
import time
import random

from matplotlib import colors

from pls3 import PLS3
from pls_ndtree import PLS_NDTREE
from pls_quadtree import PLS_QUADTREE

from pls_elicitation import PLS_ELICITATION
from pls_elicitation_quadtree import PLS_ELICITATION_QUADTREE

from elicitor import User, DecisionMaker, Elicitor
from agregation_functions import weighted_sum, OWA, choquet

from Utils.utils_main import *
from Utils.utils_read_file import *


# ------------------------- SOLVING PARAMETERS -------------------------

random_obj = True
nb_obj = 20
nb_crit = 3

root = "Data/Other/2KP200-TA-{}.dat"

# ------------------------- ELICITATION PARAMETERS -------------------------

agr_func = OWA
manual_input = False

# ------------------------- ANALYSIS PARAMETERS -------------------------

nb_runs_one = 20
objectives_to_test = [1,2,3,4]
objectives_colors = ["blue", "green", "red", "purple", "orange"]

nb_runs_two = 20

# --------------------------------------------------------------------------
#       ------------------------- PART 1 -------------------------


list_mmr_list = []
list_resolution_time = []
for nb_crit_it in objectives_to_test:

    mmr_list = []
    resolution_time = {k:[] for k in ["No data structure", "QuadTree", "NDtree"]}

    for _ in range(nb_runs_one):
        print("{} objectives\t{}/{} runs".format(nb_crit_it, _+1, nb_runs_one), end="\r")
        # loading the user
        user = User() if manual_input is True else DecisionMaker(weighted_sum, nb_crit_it)

        # Loading the problem
        instance = make_instance(root, nb_obj, nb_crit_it, random_obj)

        # Solving the problem
        pls3 = PLS3(root=None, root2=None, instance=instance)
        pls_quadtree = PLS_QUADTREE(root=None, root2=None, instance=instance)
        pls_ndtree = PLS_NDTREE(root=None, root2=None, instance=instance)
        
        # Comparing speed of each algorithm
        start = time.time()
        pls3.run(verbose_progress=False, show=False, show_best=False, verbose=False)
        resolution_time["No data structure"].append(time.time() - start)

        elicitor = Elicitor(pls3.pareto_coords, user)
        elicitor.query_user(verbose=False)
        mmr_list.append(elicitor.mmr_list)

        start = time.time()
        pls_quadtree.run(verbose_progress=False, show=False, show_best=False, verbose=False)
        resolution_time["QuadTree"].append(time.time() - start)

        elicitor = Elicitor(pls_quadtree.pareto_coords, user)
        elicitor.query_user(verbose=False)
        mmr_list.append(elicitor.mmr_list)

        start = time.time()
        pls_ndtree.run(verbose_progress=False, show=False, show_best=False, verbose=False)
        resolution_time["NDtree"].append(time.time() - start)

        elicitor = Elicitor(pls_ndtree.pareto_coords, user)
        elicitor.query_user(verbose=False)
        mmr_list.append(elicitor.mmr_list)
    
    # Saving results
    list_mmr_list.append(mmr_list)
    list_resolution_time.append(resolution_time)

# Plotting results
fig, axs = plt.subplots(nrows=1, ncols=2)

#   Plotting MMR/questions graph
i, ic = iter(objectives_to_test), iter(objectives_colors)
for mmr_list in list_mmr_list:
    plot_avg_curve(ax=axs[0], entry_list=mmr_list,
                   title="Minimax regret depending on number of questions asked for {} runs".format(3 * nb_runs_one),
                   x_label="Number of questions", y_label="Minimax regret",
                   label="{} objectives".format(next(i)),color=next(ic))

#   Plotting computing time bar graph
plot_bar_dict_group(ax=axs[1], list_entry_dict=list_resolution_time, group_names=["{} objectives".format(i) for i in objectives_to_test],
                    title="Convergence time depending on PLS method for {} runs".format(nb_runs_one), 
                    colors=["lightblue", "lightgreen", "pink"], y_label="Convergence time", log_scale=True)

plt.show()


# --------------------------------------------------------------------------
#       ------------------------- PART 2 -------------------------


methods = ["first", "first_ndtree", "first_quadtree", "second", "second_quadtree"]
times = {k:[] for k in methods}
errors = {k:[] for k in methods}
questions = {k:[] for k in methods}
mmr_first = {k:[] for k in methods[:-1]}


for _ in range(nb_runs_two):

    print(50*" ", end='\r')
    print("{}/{}".format(_, nb_runs_two) + "\tLoading the problem...", end="\r")

    # loading the user
    user = User() if manual_input is True else DecisionMaker(weighted_sum, nb_crit)

    # Loading the problem
    instance = make_instance(root, nb_obj, nb_crit, random_obj)

    print(50*" ", end='\r')
    print("{}/{}".format(_, nb_runs_two) + "\tFinding the true optimal solution...", end="\r")

    # Finding the true optimal solution with linear programming
    real_val = solve_backpack_preference(instance, nb_crit, user)

    print(50*" ", end='\r')
    print("{}/{}".format(_, nb_runs_two) + "\tSolving with PLS_NDTREE NDTree...", end="\r")

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