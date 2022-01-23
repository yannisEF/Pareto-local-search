import time

from pls3 import PLS3
from pls_ndtree import PLS_NDTREE
from pls_quadtree import PLS_QUADTREE

from elicitor import User, DecisionMaker, Elicitor
from agregation_functions import weighted_sum, OWA, choquet

from Utils.utils_main import *
from Utils.utils_read_file import *


# ------------------------- SOLVING PARAMETERS -------------------------

random_obj = True
root = "Data/Other/2KP200-TA-{}.dat"

# ------------------------- ELICITATION PARAMETERS -------------------------

manual_input = False

# ------------------------- ANALYSIS PARAMETERS -------------------------

nb_runs_1 = 20
nb_obj_to_test_1 = 20
crit_to_test_1 = [1,2,3,4,5]
crit_colors_1 = ["lightskyblue", "chartreuse", "salmon", "mediumorchid", "orange"]

# --------------------------------------------------------------------------
#       ------------------------- PART 1 -------------------------

methods = ["No data structure", "QuadTree", "NDtree"]
methods_colors = ["dodgerblue", "limegreen", "indianred"]

list_mmr_list = []
list_resolution_time_1 = []
for nb_crit_it in crit_to_test_1:

    mmr_list = []
    resolution_time_1 = {k:[] for k in methods}

    for _ in range(nb_runs_1):
        print("{} objectives\t{}/{} runs".format(nb_crit_it, _+1, nb_runs_1), end="\r")
        # loading the user
        user = User() if manual_input is True else DecisionMaker(weighted_sum, nb_crit_it)

        # Loading the problem
        instance = make_instance(root, nb_obj_to_test_1, nb_crit_it, random_obj)

        # Solving the problem
        pls3 = PLS3(root=None, root2=None, instance=instance)
        pls_quadtree = PLS_QUADTREE(root=None, root2=None, instance=instance)
        pls_ndtree = PLS_NDTREE(root=None, root2=None, instance=instance)

        # Getting the same initial population
        init_pop = pls3.get_init_pop(instance)
        
        # Comparing speed of each algorithm
        start = time.time()
        pls3.run(verbose_progress=False, show=False, show_best=False, verbose=False, init_pop=init_pop)
        resolution_time_1["No data structure"].append(time.time() - start)

        elicitor = Elicitor(pls3.pareto_coords, user)
        elicitor.query_user(verbose=False)
        mmr_list.append(elicitor.mmr_list)

        start = time.time()
        pls_quadtree.run(verbose_progress=False, show=False, show_best=False, verbose=False, init_pop=init_pop)
        resolution_time_1["QuadTree"].append(time.time() - start)

        elicitor = Elicitor(pls_quadtree.pareto_coords, user)
        elicitor.query_user(verbose=False)
        mmr_list.append(elicitor.mmr_list)

        start = time.time()
        pls_ndtree.run(verbose_progress=False, show=False, show_best=False, verbose=False, init_pop=init_pop)
        resolution_time_1["NDtree"].append(time.time() - start)

        elicitor = Elicitor(pls_ndtree.pareto_coords, user)
        elicitor.query_user(verbose=False)
        mmr_list.append(elicitor.mmr_list)
    
    # Saving results
    list_mmr_list.append(mmr_list)
    list_resolution_time_1.append(resolution_time_1)

# Plotting results
#   Plotting MMR/questions graph
plt.figure()
ax_1_regret = plt.subplot()

i, ic = iter(crit_to_test_1), iter(crit_colors_1)
for mmr_list in list_mmr_list:
    plot_avg_curve(ax=ax_1_regret, entry_list=mmr_list,
                   title="Minimax regret depending on number of questions asked for {} runs".format(3 * nb_runs_1),
                   x_label="Number of questions", y_label="Minimax regret",
                   label="{} objectives".format(next(i)),color=next(ic))


#   Plotting computing time bar graph
plt.figure()
ax_1_time = plt.subplot()

plot_bar_dict_group(ax=ax_1_time, list_entry_dict=list_resolution_time_1, group_names=["{} objectives".format(i) for i in crit_to_test_1],
                    title="Convergence time depending on PLS method for {} runs".format(nb_runs_1), 
                    colors=methods_colors, y_label="Convergence time", log_scale=True)

plt.show()
