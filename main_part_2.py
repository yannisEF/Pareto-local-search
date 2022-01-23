import time
import gurobipy as gp
model = gp.Model()

from pls3 import PLS3
from pls_elicitation import PLS_ELICITATION

from elicitor import User, DecisionMaker, Elicitor
from agregation_functions import weighted_sum, OWA, choquet

from Utils.utils_main import *
from Utils.utils_read_file import *


# ------------------------- SOLVING PARAMETERS -------------------------

random_obj = True
root = "Data/Other/2KP200-TA-{}.dat"

# ------------------------- ANALYSIS PARAMETERS -------------------------

nb_runs_2 = 20
nb_obj_to_test_2 = 20
crit_to_test_2 = [1,2,3,4,5]
crit_colors_2 = ["lightskyblue", "chartreuse", "salmon", "mediumorchid", "orange"]

nb_obj_iterate = list(range(20, 51, 10))
nb_obj_colors = ["chartreuse", "salmon", "mediumorchid", "orange"]
crit_iterate_to_test = 2

agregators_to_test = {"Weighted sum":weighted_sum}


# --------------------------------------------------------------------------
#       ------------------------- PART 2 -------------------------


methods = ["First procedure", "Second procedure"]
methods_colors = ["dodgerblue","chocolate"]

axs_2_time = []
axs_2_error = []
axs_2_question = []

for name, agregator in agregators_to_test.items():

    list_resolution_time_2 = []
    list_error_2 = []
    list_question_2 = []

    for nb_crit_it in crit_to_test_2:

        resolution_time_2 = {k:[] for k in methods}
        error_2 = {k:[] for k in methods}
        question_2 = {k:[] for k in methods}

        for _ in range(nb_runs_2):
            print("{} \t{} objectives\t{}/{} runs".format(name, nb_crit_it, _+1, nb_runs_2), end="\r")
            # loading the user
            user = DecisionMaker(agregator, nb_crit_it)

            # Loading the problem
            instance = make_instance(root, nb_obj_to_test_2, nb_crit_it, random_obj)

            # Finding the true optimal solution with linear programming
            real_val = solve_backpack_preference(instance, nb_crit_it, user)

            # Solving the problem
            pls3 = PLS3(root=None, root2=None, instance=instance)
            pls_elicitation = PLS_ELICITATION(root=None, root2=None, instance=instance,
                                            agregation_function=user.agregation_function, weights=user.weights)

            # Getting the same initial population
            init_pop = None # pls3.get_init_pop(instance)

            # Executing each procedure
            start = time.time()
            pls3.run(verbose_progress=False, show=False, show_best=False, verbose=False, init_pop=init_pop)
            elicitor = Elicitor(pls3.pareto_coords, user)
            opt_val, mmr = elicitor.query_user(verbose=False)

            resolution_time_2["First procedure"].append(time.time() - start)
            error_2["First procedure"].append(abs(user.agregation_function(user.weights, opt_val[0]) - real_val))
            question_2["First procedure"].append(len(elicitor.user_preferences))

            start = time.time()
            pls_elicitation.run(verbose_progress=False, show=False, show_best=False, verbose=False, init_pop=init_pop)

            resolution_time_2["Second procedure"].append(time.time() - start)
            error_2["Second procedure"].append(abs(user.agregation_function(user.weights, pls_elicitation.pareto_coords[0]) - real_val))
            question_2["Second procedure"].append(pls_elicitation.nb_questions)

        # Saving the results
        list_resolution_time_2.append(resolution_time_2)
        list_error_2.append(error_2)
        list_question_2.append(question_2)

    # Plotting the results
    #   Plotting computing time bar graph
    plt.figure()
    ax_2_time = plt.subplot()

    plot_bar_dict_group(ax=ax_2_time, list_entry_dict=list_resolution_time_2, group_names=["{} objectives".format(i) for i in crit_to_test_2],
                        title="Convergence time depending on PLS method for {} runs with {} agregator on {} objects".format(nb_runs_2, name, nb_obj_to_test_2), 
                        colors=methods_colors, y_label="Convergence time", log_scale=True)

    axs_2_time.append(ax_2_time)

    #   Plotting Error bar graph
    plt.figure()
    ax_2_error = plt.subplot()

    plot_bar_dict_group(ax=ax_2_error, list_entry_dict=list_error_2, group_names=["{} objectives".format(i) for i in crit_to_test_2],
                        title="Error to true optimal depending on PLS method for {} runs with {} agregator on {} objects".format(nb_runs_2, name, nb_obj_to_test_2), 
                        colors=methods_colors, y_label="Error to optimal", log_scale=False)
    
    axs_2_error.append(ax_2_error)

    #   Plotting questions bar graph
    plt.figure()
    ax_2_question = plt.subplot()

    plot_bar_dict_group(ax=ax_2_question, list_entry_dict=list_question_2, group_names=["{} objectives".format(i) for i in crit_to_test_2],
                        title="Number of queries depending on PLS method for {} runs with {} agregator on {} objects".format(nb_runs_2, name, nb_obj_to_test_2), 
                        colors=methods_colors, y_label="Number of queries", log_scale=False)
    
    axs_2_question.append(ax_2_question)

    # Plotting questions/error graph
    
    for method in methods:
        plt.figure()
        ax = plt.subplot()
        ax.xaxis.grid(True)
        ax.yaxis.grid(True)
        ax.set_title("Error depending on questions asked for {} with {} agregator on {} runs on {} objects".format(method, name, nb_runs_2, nb_obj_to_test_2))

        for i, crit_it in enumerate(crit_to_test_2):
            
            point = ax.scatter(list_question_2[i][method], list_error_2[i][method], color=crit_colors_2[i])
            
            point.set_label("{} objectives".format(crit_it))
        
        ax.legend()

plt.show()


# Now iterating over the number of objects
methods = ["First procedure", "Second procedure"]
methods_colors = ["dodgerblue","chocolate"]

axs_2_time = []
axs_2_error = []
axs_2_question = []

for name, agregator in agregators_to_test.items():

    list_resolution_time_2 = []
    list_error_2 = []
    list_question_2 = []

    for nb_obj_it in nb_obj_iterate:

        resolution_time_2 = {k:[] for k in methods}
        error_2 = {k:[] for k in methods}
        question_2 = {k:[] for k in methods}

        for _ in range(nb_runs_2):
            print("{} \t{} objects\t{}/{} runs".format(name, nb_obj_it, _+1, nb_runs_2), end="\r")
            # loading the user
            user = DecisionMaker(agregator, crit_iterate_to_test)

            # Loading the problem
            instance = make_instance(root, nb_obj_it, crit_iterate_to_test, random_obj)

            # Finding the true optimal solution with linear programming
            real_val = solve_backpack_preference(instance, crit_iterate_to_test, user)

            # Solving the problem
            pls3 = PLS3(root=None, root2=None, instance=instance)
            pls_elicitation = PLS_ELICITATION(root=None, root2=None, instance=instance,
                                            agregation_function=user.agregation_function, weights=user.weights)

            # Getting the same initial population
            init_pop = None # pls3.get_init_pop(instance)

            # Executing each procedure
            start = time.time()
            pls3.run(verbose_progress=False, show=False, show_best=False, verbose=False, init_pop=init_pop)
            elicitor = Elicitor(pls3.pareto_coords, user)
            opt_val, mmr = elicitor.query_user(verbose=False)

            resolution_time_2["First procedure"].append(time.time() - start)
            error_2["First procedure"].append(abs(user.agregation_function(user.weights, opt_val[0]) - real_val))
            question_2["First procedure"].append(len(elicitor.user_preferences))

            start = time.time()
            pls_elicitation.run(verbose_progress=False, show=False, show_best=False, verbose=False, init_pop=init_pop)

            resolution_time_2["Second procedure"].append(time.time() - start)
            error_2["Second procedure"].append(abs(user.agregation_function(user.weights, pls_elicitation.pareto_coords[0]) - real_val))
            question_2["Second procedure"].append(pls_elicitation.nb_questions)

        # Saving the results
        list_resolution_time_2.append(resolution_time_2)
        list_error_2.append(error_2)
        list_question_2.append(question_2)

    # Plotting the results
    #   Plotting computing time bar graph
    plt.figure()
    ax_2_time = plt.subplot()

    plot_bar_dict_group(ax=ax_2_time, list_entry_dict=list_resolution_time_2, group_names=["{} objects".format(i) for i in nb_obj_iterate],
                        title="Convergence time depending on PLS method for {} runs with {} agregator".format(nb_runs_2, name), 
                        colors=methods_colors, y_label="Convergence time", log_scale=True)

    axs_2_time.append(ax_2_time)

    #   Plotting Error bar graph
    plt.figure()
    ax_2_error = plt.subplot()

    plot_bar_dict_group(ax=ax_2_error, list_entry_dict=list_error_2, group_names=["{} objects".format(i) for i in nb_obj_iterate],
                        title="Error to true optimal depending on PLS method for {} runs with {} agregator".format(nb_runs_2, name), 
                        colors=methods_colors, y_label="Error to optimal", log_scale=False)
    
    axs_2_error.append(ax_2_error)

    #   Plotting questions bar graph
    plt.figure()
    ax_2_question = plt.subplot()

    plot_bar_dict_group(ax=ax_2_question, list_entry_dict=list_question_2, group_names=["{} objects".format(i) for i in nb_obj_iterate],
                        title="Number of queries depending on PLS method for {} runs with {} agregator".format(nb_runs_2, name), 
                        colors=methods_colors, y_label="Number of queries", log_scale=False)
    
    axs_2_question.append(ax_2_question)

    # Plotting questions/error graph
    
    for method in methods:
        plt.figure()
        ax = plt.subplot()
        ax.xaxis.grid(True)
        ax.yaxis.grid(True)
        ax.set_title("Error depending on questions asked for {} with {} agregator on {} runs".format(method, name, nb_runs_2))

        for i, crit_it in enumerate(crit_to_test_2):
            
            point = ax.scatter(list_question_2[i][method], list_error_2[i][method], color=crit_colors_2[i])
            
            point.set_label("{} objects".format(crit_it))
        
        ax.legend()

plt.show()