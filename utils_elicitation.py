import gurobipy as gp

def compute_pmr(P, x, y):
    """
    Compute the Pairwise max regret of x with respect to y given the set of observed preferences P
    """

    dim = len(x)
    model = gp.Model()
    model.setParam('OutputFlag', 0)

    # Variables
    #   All the possible weights of the agregation function
    weights = [model.addVar(vtype='C', name='w{}'.format(i)) for i in range(dim)]
    
    # Objective
    #   max f(w, x) - f(w, y)
    f = lambda a: sum(weights[i] * a[i] for i in range(dim))
    model.setObjective(f(x) - f(y), gp.GRB.MAXIMIZE)

    # Constraints
    #   All preferences have to be respected
    model.addConstrs(f(a) >= f(b) for a,b in P)
    #   Weights must sum to 1
    model.addConstr(sum(weights) == 1)
    #   Weights between 0 and 1:
    for w in weights:   model.addConstr(w <= 1)

    # Solve the model
    model.optimize()

    return model.objVal


def compute_mr(P, x_set, x):
    """
    Compute the max regret of x with respect to x_set
    """
    
    return max(compute_pmr(P, x, y) for y in x_set)


def compute_mmr(P, x_set):
    """
    Compute the Min Max Regret of x_set according to preferences P
    """

    return min(compute_mr(P, x_set, x) for x in x_set)


if __name__ == "__main__":
    X = [(4,8), (6,4), (10,2)]
    P = [((4,8), (6,4)), ((4,8), (10,2)), ((6,4), (10,2))]
    print(compute_mmr(P, X))