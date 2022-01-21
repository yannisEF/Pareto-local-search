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
    # f(x) = w1 * x1 + w2 * x2 + .... 
    
    # Objective
    #   max f(w, x) - f(w, y)
    f = lambda a: sum(weights[i] * a[i] for i in range(dim))
    model.setObjective(f(y) - f(x), gp.GRB.MAXIMIZE)

    # Constraints
    #   All preferences have to be respected
    model.addConstrs(f(a) >= f(b) for a,b in P)
    #   Weights must sum to 1
    model.addConstr(sum(weights) == 1)
    #   Weights between 0 and 1:
    for w in weights:
        model.addConstr(w <= 1)
        model.addConstr(w >= 0)

    # Solve the model
    model.optimize()

    return model.objVal

def compute_mr(P, x_set, x, dominated):
    """
    Compute the max regret of x with respect to x_set
    """
    list_pmr = []
    for y in x_set:
        pmr = compute_pmr(P, x, y)
        list_pmr.append(pmr)
        if pmr < 0: # If PMR(x,y;P) is strictly negative, then x is necessarily strictly preferred to y
            dominated.append(y)
    mr = max(list_pmr)
    return [x_set[i] for i in range(len(x_set)) if list_pmr[i] == mr], mr


def compute_mmr(P, x_set, dominated):

    """
    Compute the Min Max Regret of x_set according to preferences P
    """
    list_mr = [compute_mr(P, x_set, x , dominated)[1] for x in x_set]
    mmr = min(list_mr)
    return [x_set[i] for i in range(len(x_set)) if list_mr[i] == mmr], mmr


if __name__ == "__main__":
    X = [(4,8), (6,4), (10,2), (12,1), (1,9)]
    P = [((4,8), (6,4)),((4,8), (10,2))]
    dominated = []
    print(compute_mmr(P, X, dominated))
    
    
    