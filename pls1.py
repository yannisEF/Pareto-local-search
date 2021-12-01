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

    def get_init_pop(self, instance):
        objects = instance["Objects"][:]
        pop, S = [], 0

        while S <= instance['W'] and len(objects) > 0:
            new_obj = random.choice(objects)
            objects.remove(new_obj)

            if new_obj['w'] + S <= instance['W']:   
                pop.append(new_obj)
                S += new_obj['w']
        return [pop]

    def get_neighbours(self, current, instance):
        other_list = [x for x in instance["Objects"] if x not in current] # les autres objets piochables
        S = sum([x["w"] for x in current]) # poids total de la solution courante

        neighbours = [] # les solutions voisines de la solution courante : tuple(obj à retirer, liste d'objs à ajouter)
        for obj in current:
            for other in other_list:
                copy_others = other_list[:]
                copy_others.remove(other)

                chosen_others = [other] # la liste des obj à ajouter
                newS =  S - obj["w"] + other["w"]

                # On teste si la solution est réalisable
                if newS <= instance["W"]:   neighbours.append((obj, chosen_others))

                # On ajoute des objets tant que la solution est réalisable
                while newS <= instance["W"] and len(copy_others) > 0:
                    new_other = random.choice(copy_others)
                    copy_others.remove(new_other)
                    
                    newnewS = newS + new_other["w"]
                    if newnewS <= instance['W']:
                        chosen_others.append(new_other)
                        newS = newnewS
        return neighbours

    def update(self, Pareto, x):
        score_x, dominated_by_x = get_score(x), []

        notDominated = True
        for y in Pareto:
            score_y = get_score(y)
            if is_score_dominated(score_y, score_x):    dominated_by_x.append(y)
            elif is_score_dominated(score_x, score_y):
                notDominated = False
                break
                
        for y in dominated_by_x:
            Pareto.remove(y)

        if notDominated is True:    Pareto.append(x)
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
                len_pop = [-1, len(population)] # Historique des tailles de population
                hasAddedSolution = True # A-t-on ajouté une nouvelle solution à la population

                # On s'arrête lorsqu'on n'arrive plus à trouver de nouvelles solutions non-dominées
                while len_pop[-1] != len_pop[-2] or hasAddedSolution is True:
                    for current in population:
                        neighbours = self.get_neighbours(current, instance) # on calcule le voisinage

                        for neighbour in neighbours:
                            new_solution = current[:] + neighbour[1]
                            new_solution.remove(neighbour[0])

                            if new_solution not in population and not is_dominated(new_solution, current):
                                hasAddedSolution = self.update(population, new_solution) # on met à jour le front de pareto en fonction des solutions non dominées du voisinage
                    len_pop.append(len(population))
                len_pop = len_pop[1:]

                self.times[-1] += time.time()
                self.proportions.append(get_proportion(exacte, population))
                self.distances.append(get_distance(exacte, population))

                if show is True:
                    if show_best is True:
                        if self.distances[-1] < best_distance:
                            best_distance = self.distances[-1]
                            best_len_pop = len_pop
                            best_pop = population
                    else:
                        i1 = 0 if self.nb_tries == 1 else (_, 0)
                        i2 = 1 if self.nb_tries == 1 else (_, 1)
                        
                        for x in population:    plot_solution(x, ax=axs[i1])
                        plot_non_dominated(exacte, ax=axs[i1])

                        axs[i2].plot(len_pop)
                           
            if verbose is True: print("File {} on {} tries:\n\t\ttime: {}\n\t\tproportion: {}\n\t\tdistance: {}"
                                        .format(k, self.nb_tries, get_avg(self.times), get_avg(self.proportions, 3), get_avg(self.distances)))      

            if show is True:
                if show_best is True:
                    axs[0].set_title("Espace des solutions")
                    for x in best_pop:  plot_solution(x, ax=axs[0])
                    plot_non_dominated(exacte, ax=axs[0])

                    axs[1].set_title("Evolution de la population à chaque itération")
                    axs[1].plot(best_len_pop)

                plt.show()
    
if __name__ == "__main__":
    pls1 = PLS1(nb_tries=10, nb_files=2)
    pls1.run()
