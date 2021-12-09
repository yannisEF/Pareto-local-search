
import random
import matplotlib.pyplot as plt

from read_file import *
from utils import *

class PLS1:
    def __init__(self, nb_files=1, nb_tries=10, root="Data/100_items/2KP100-TA-{}.dat", root2="Data/100_items/2KP100-TA-{}.eff"):
        self.nb_files = nb_files
        self.nb_tries = nb_tries
        self.root = root
        self.root2 = root2
        # Quality testing
        self.times = []
        self.proportions = []
        self.distances = []

    def get_init_pop(self, instance): #population = [pop,[o1,o2]]
        weight, v1, v2, W = instance
        wt = 0
        pop = [0 for i in range(len(weight))]
        s = [i for i in range(len(weight))]
        population = [pop,[0,0]]
        r = random.choice(s)
        
        while wt + weight[r] <= W:
            wt += weight[r]
            population[1][0] += v1[r]
            population[1][1] += v2[r]
            population[0][r] = 1
            s.remove(r)
            r = random.choice(s)
        return [population]
    
    
    def get_neighbours(self, current,instance):
        weight, v1, v2, W = instance
        neighbours = []
        index_1 = [i for i in range(len(current[0])) if current[0][i] == 1]
        index_0 = [i for i in range(len(current[0])) if current[0][i] == 0]
        S = sum([weight[i] for i in range(len(weight)) if current[0][i] == 1])
        for i in index_1:
            for j in index_0:
                new = current[0].copy()
                new[i] = 0
                new[j] = 1   
                v_1 ,v_2 = current[1]
                w = S - weight[i] + weight[j] 
                if w <= W:
                    index_r = index_0.copy()
                    index_r.remove(j)
                    r =  random.choice(index_r)
                    v_1 = v_1 - v1[i] + v1[j]   
                    v_2 = v_2  - v2[i] + v2[j]    
                    while w + weight[r] <= W:
                        w += weight[r]
                        new[r] = 1
                        v_1 = v_1 + v1[r]   
                        v_2 = v_2 + v2[r]
                        index_r.remove(r)
                        r = random.choice(index_r)
                    new_ = [new,[v_1,v_2]]
                    neighbours.append(new_)
        return neighbours


    def update(self, Pareto, x): #x =[0,1,0,0...], [v1,v2]
        v1,v2 = x[1]   
        notDominated = True
        for ND in Pareto:
            if ND[1][0] >= v1 and ND[1][1] >= v2:
                notDominated = False
                break
        if notDominated:
            for ND in Pareto:
                if (v1 >=  ND[1][0] and v2 >= ND[1][1]):
                    Pareto.remove(ND)
            Pareto.append(x)
        return notDominated


    def run(self, verbose=True, show=True, show_best=True):
        
        for k in range(self.nb_files):
            instance = read_file(self.root.format(k))
            exacte = read_exact_file(self.root2.format(k))
            
            if show is True:
                best_distance, best_len_pop, best_pop = float('inf'), [], []
                fig, axs = plt.subplots(1 if show_best is True else self.nb_tries, 2)
            for _ in range(self.nb_tries):
                if verbose is True: print("File {}, try {}/{}".format(k, _, self.nb_tries), end='\r')
                self.times.append(-time.time())
                population = self.get_init_pop(instance) # une seule solution réalisable
                len_pop = len(population)
                hasAddedSolution = True # A-t-on ajouté une nouvelle solution à la population
                # On s'arrête lorsqu'on n'arrive plus à trouver de nouvelles solutions non-dominées
                add_solution = population.copy()
                while add_solution != []:
                    Potential_new_sol = []
                    for current in add_solution:  # population sont des nouvelles solutions ND
                        neighbours = self.get_neighbours(current, instance) # on calcule le voisinage
                        for n in neighbours:
                            Potential_new_sol.append(n)
                    add_solution = []
                    for i in Potential_new_sol:
                        if self.update(population, i):
                            add_solution.append(i)
                    print(len(population))
                         
                         
                self.times[-1] += time.time()
                
                population_score = [(population[i][1][0],population[i][1][1]) for i in range(len(population))]
                self.proportions.append(get_proportion(exacte,population_score))
                draw_pts(population_score,exacte)
                

                #self.distances.append(get_distance(exacte, population_score))

                if show is True:
                    if show_best is True:
                        """if self.distances[-1] < best_distance:
                            best_distance = self.distances[-1]
                            best_len_pop = len_pop
                            best_pop = population_score"""
                    else:
                        i1 = 0 if self.nb_tries == 1 else (_, 0)
                        i2 = 1 if self.nb_tries == 1 else (_, 1)
                        
                        for x in population_score:    plot_solution(x, ax=axs[i1])
                        plot_non_dominated(exacte, ax=axs[i1])

                        axs[i2].plot(len_pop)
                           
            """if verbose is True: print("File {} on {} tries:\n\t\ttime: {}\n\t\tproportion: {}\n\t\tdistance: {}"
                                        .format(k, self.nb_tries, get_avg(self.times), get_avg(self.proportions, 3)))#, get_avg(self.distances)))      
"""
            if show is True:
                if show_best is True:
                    axs[0].set_title("Espace des solutions")
                    for x in best_pop:  plot_solution(x, ax=axs[0])
                    plot_non_dominated(exacte, ax=axs[0])

                    axs[1].set_title("Evolution de la population à chaque itération")
                    axs[1].plot(best_len_pop)

                plt.show()
            print("\n \n Proportion : ",get_avg(self.proportions), " time : ", get_avg(self.times))
    
if __name__ == "__main__":
    pls1 = PLS1(nb_tries=1, nb_files=1)
    pls1.run()
