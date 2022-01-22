import gurobipy as gp
import matplotlib.pyplot as plt
import numpy as np
import random

from Utils.utils_read_file import read_file


def make_instance(root, nb_obj, nb_crit, random_obj=True):
    """
    Returns a reduced instance of the given root
    """

    init_instance = read_file(root.format(0))
    sampled_index = random.sample(range(init_instance["n"]), nb_obj) if random_obj is True \
                    else list(range(nb_obj))

    new_weights = [init_instance["Objects"][0][i] for i in sampled_index]
    new_values = [[init_instance["Objects"][1][v][i] for i in sampled_index] for v in range(nb_crit)]

    return {'n':nb_obj, 'W':int(sum(new_weights)/2), 'Objects':[new_weights, new_values]}


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


def plot_avg_curve(ax, title, entry_list, color="blue", alpha=.1, x_label="", y_label="", label=None):
    """
    Makes a curve of the average with std
    """

    ax.set_title(title)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    ax.xaxis.grid(True)
    ax.yaxis.grid(True)
    
    y_mean = []
    y2_std, y1_std = [], []
    i = 0
    while True:
        values = [l[i] for l in entry_list if len(l) > i]
        if len(values) == 0:
            break

        y_mean.append(np.mean(values))
        std = np.std(values)

        y1_std.append(y_mean[-1] - std)
        y2_std.append(y_mean[-1] + std)

        i += 1
    
    if label is None:
        ax.plot(y_mean, color=color)
    else:
        ax.plot(y_mean, color=color, label=label)
        ax.legend()

    ax.fill_between(range(len(y1_std)), y1_std, y2_std, color=color, alpha=alpha, interpolate=True)


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


def plot_bar_dict_group(ax, title, list_entry_dict, group_names=None, colors=["lightblue", "lightgreen"], y_label="", y_err=True, log_scale=True):
    """
    Makes groups of barplots with an error bar
    """

    if group_names is None:
        group_names = ["" for _ in range(list_entry_dict)]

    ax.yaxis.grid(True)
    ax.set_xticks([round(len(list_entry_dict[0])/2) + k * (len(list_entry_dict[0])+1) for k in range(len(list_entry_dict))])
    ax.set_xticklabels(group_names)
    ax.set_title(title)

    ax.set_ylabel(y_label)

    for j, entry_dict in enumerate(list_entry_dict):
        for i, key in enumerate(entry_dict.keys()):
            print(j*(len(list_entry_dict) + 1) + i+1)
            bar, = plt.bar(j*(len(list_entry_dict) + 1) + i+1, np.mean(entry_dict[key]), yerr=np.std(entry_dict[key]) if y_err is True else 0, color=colors[i], align="center", ecolor="black")

            if j == 0:
                bar.set_label(key)

    ax.legend()
    
    if log_scale is True:
        ax.set_yscale("log")
