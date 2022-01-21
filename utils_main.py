import gurobipy as gp
import matplotlib.pyplot as plt
import numpy as np


def solve_backpack_preference(instance, nb_crit, user):
    """
    Solve the backpack problem on a given instance with LP
    Returns the optimal value according to the user's agregation function
    """

    nb_obj = instance['n']

    model = gp.Model()
    model.setParam('OutputFlag', 0)

    #   Variables
    assignement = model.addVars(nb_obj, vtype=gp.GRB.BINARY, name="x")
    
    #   Objective
    model.setObjective(user.agregation_function(user.weights, [sum(assignement[i] * instance['Objects'][1][k][i] for i in range(nb_obj)) for k in range(nb_crit)]), gp.GRB.MAXIMIZE)

    #   Constraints
    model.addConstr(sum(assignement[i] * instance['Objects'][0][i] for i in range(nb_obj)) <= instance['W'])

    #   Solve the model
    model.optimize()

    return model.objVal


def plot_bar_dict(ax, title, entry_dict, colors=["lightblue", "lightgreen"], y_label="", y_err=True):
    """
    Makes a bar plot with an error bar
    """

    ax.yaxis.grid(True)
    ax.set_xticks(range(1, len(entry_dict) + 1))
    ax.set_xticklabels(list(entry_dict.keys()))
    ax.set_title(title)


    ax.set_ylabel(y_label)

    for i, key in enumerate(entry_dict.keys()):
        plt.bar(i+1, np.mean(entry_dict[key]), yerr=np.std(entry_dict[key]) if y_err is True else 0, color=colors[i], align="center", ecolor="black")