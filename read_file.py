import matplotlib.pyplot as plt


def read_file(filename):  #  instance  = weight, v1, v2, W
    f = open(filename, 'r')
    lines = f.readlines()
    weight = []
    v1 = []
    v2 = []
    instance = [weight,v1,v2]
    
    for line in lines:
        tline = line.split()
        if tline[0] == 'i':
            instance[0].append(int(tline[1]))
            instance[1].append(int(tline[2]))
            instance[2].append(int(tline[3]))
        elif tline[0] == 'W':
            W = int(tline[1])
    instance.append(W)
    return instance


def read_exact_file(filename):    
    f = open(filename, 'r')
    lines = f.readlines()
    res = []
    for line in lines:
        tline = line.split()
        res.append((int(tline[0]), int(tline[1])))
    return res


def plot_solution(x, ax=None, color='blue'):
    if ax is None:  fig, ax= plt.subplots()

    ax.scatter(sum([i["v1"] for i in x]), sum([i["v2"] for i in x]), color=color)
    return ax
    
def plot_non_dominated(non_dominated, ax=None, color='red'):
    if ax is None:  fig, ax = plt.subplots()

    ax.plot([i[0] for i in non_dominated], [i[1] for i in non_dominated], color=color)
    return ax

if __name__ == '__main__':
    fig = plot_non_dominated(read_exact_file("Data/100_items/2KP100-TA-0.eff"))
    plt.show()