
import random
import matplotlib.pyplot as plt

from read_file import *
from utils import *
import itertools
from read_file import *
from pls1 import *



def compare_label(label):
        index_1 = [i for i in range(len(label)) if label[i] == 1]
        index_0 = [i for i in range(len(label)) if label[i] == 0]
        label_set = []
        label_set.append(label)
        liste0 = [0 for i in range(len(label))]
        for i in range(1,len(index_1)):
            p = list(itertools.combinations(index_1, i))
            for j in p:
                liste = liste0.copy()
                for k in j:
                    liste[k] = 1
                label_set.append(liste)
                    
        for i in range(1,len(index_0)):
            p = list(itertools.combinations(index_0, i))
            for j in p:
                label0 = label.copy()
                for k in j:
                    label0[k] = 1
                label_set.append(label0)
        return label_set
    
    
class solution:
    def __init__(self, instance,index): # instance is one element in population
        self.socre = get_score(index_to_values(instance, index))
        self.length = len(self.socre)
        self.label = []
        self.son = []
        self.index = index
        


class Quad_tree:
    def __init__(self,solution): # instance is element in population
        self.root = solution # root is a solution type
        self.Pareto = [self.root] # full of solution
        self.Pareto_index = [self.root.index]
        
    def get_label(self,x,y):  # y is a new solution [0000] => delete y  [1111]=> delete x
        l = []
        if max(x.socre) < max(y.socre):
            for i in range(x.length):
                if  x.socre[i] > y.socre[i]:
                    l.append(0)
                else:
                    l.append(1)
                    
      
        else:
            for i in range(x.length):
                if  x.socre[i] >= y.socre[i]:
                    l.append(0)
                else:
                    l.append(1)
        return l
    
    
    def remove_son(self,current_root,removed):
        if current_root.son == []:
            self.Pareto.remove(current_root)
            self.Pareto_index.remove(current_root.index)
            return 1
        else:
            c = current_root.son.copy()
            for i in c:
                removed.append(i)
                current_root.son.remove(i)
                self.remove_son(i,removed)
                
        
    def update_add_solution(self,current_root,solution,Removed_solution): # Removed_solution = []
        D = current_root.length
        AddIn = True
        solution.label = self.get_label(current_root,solution)
        if solution.label == [1 for i in range(D)]: # y dominate x, delete x
            self.remove_son(current_root,Removed_solution)
            self.root = solution
            self.Pareto = [self.root]
            self.Pareto_index = [self.root.index]
            return AddIn
        
        elif solution.label == [0 for i in range(D)]: # x dominate y, do nothing
           AddIn = False
           return AddIn
        
        else:
            label_compare = compare_label(solution.label)
            for i in current_root.son:
                #if i.label in label_compare:
                if self.get_label(i,solution) == [0 for k in range(D)]: # y is dominated
                    AddIn = False
                    return AddIn
                elif self.get_label(i,solution) == [1 for k in range(D)]: # i is dominated
                    self.remove_son(i,Removed_solution)
                    current_root.son.remove(i)
            
            for i in current_root.son:
                if i.label == solution.label:
                    new_root = i
                    AddIn = False
                    
            
            if AddIn == True:
                current_root.son.append(solution)
                self.Pareto.append(solution)
                self.Pareto_index.append(solution.index)
                return AddIn
            else:
                self.update_add_solution(new_root,solution,Removed_solution)

        
    def update(self,instance,new_population_index):
        solu = solution(instance,new_population_index)
        Removed_solution = []
        Add = self.update_add_solution(self.root,solu,Removed_solution)
            
        if Removed_solution != []:
            for i in Removed_solution:
                rs = []
                self.update_add_solution(self.root,i,rs)
        else:
            return Add
 
        
 

                
class PLS_QT(PLS1):
    def __init__(self, nb_files=1, nb_tries=10, root="Data/100_items/2KP100-TA-{}.dat", root2="Data/100_items/2KP100-TA-{}.eff", instance=None):
        self.nb_files = nb_files
        self.nb_tries = nb_tries

        # The algorithm's input
        self.root = root
        self.root2 = root2
        self.instance = instance

        # Quality testing
        self.times = []
        self.proportions = []
        self.distances = []
        

        
    def run(self, verbose=True, verbose_progress=True, show=True, show_best=True):
        """
        Run multiple times the algorithm on the given root
        """
        
        # Iterate through the root
        for k in range(self.nb_files if self.root is not None else 1):
            # Read the file
            instance = self.instance if self.instance is not None else read_file(self.root.format(k))
            if self.root2 is not None:
                exacte = read_exact_file(self.root2.format(k))
            
            # Define the graphs if asked
            if show is True:
                # Not possible to show in more than 2 dimensions
                show = len(instance["Objects"][1]) <= 3
                show_best = show_best and (self.root2 is not None)

                # Initializing plotting parameters
                best_distance, best_len_population, best_pop = float('inf'), [], []
                fig, axs = plt.subplots(1 if show_best is True else self.nb_tries, 2)

            # Average the results over a number of runs
            for _ in range(self.nb_tries):
                if verbose is True: print("File {}, try {}/{}".format(k, _, self.nb_tries), end='\r')

                self.times.append(-time.time())

                self.pareto_index = self.get_init_pop(instance)
                population_index = self.pareto_index[:] # Get the initial population
                len_population = [-1, len(population_index)] # History of the pareto front's length

                new_population_index = []
                visited_index = [set(p) for p in self.pareto_index[:]] # history of already visited solutions
                
                solu = solution(instance,population_index[0])
                Q = Quad_tree(solu)
                
                # We continue until convergence is reached
                while len(population_index) != 0:
                    for current_index in population_index:
                        current_values = index_to_values(instance, current_index)
                        # We retrieve the neighbours of the current solution
                        neighbours_index = self.get_neighbours(current_index, instance)
                        for neighbour_index in neighbours_index:
                            # We retrieve the new solution from the found neighbours
                            new_solution_index = self.get_solution_from_neighbours(current_index, neighbour_index)

                            # We do a preliminary check to see if the neighbour is not already dominated by the current solution
                            new_solution_values = index_to_values(instance, new_solution_index)
                            
                            Q.update(instance, new_solution_index)
                            
                            self.pareto_index = Q.Pareto_index
                            new_population_index = Q.Pareto_index
                        #print(len(Q.Pareto))
                            
                        # Update the history of already visited solutions to avoid loops
                        current_index_set = set(current_index)
                        if current_index_set not in visited_index:
                            visited_index.append(current_index_set)
                    
                    # The population holds the newfound solutions that are potentially on the Pareto front
                    population_index = [p for p in new_population_index if set(p) not in visited_index]
                    new_population_index = []
                    
                    if verbose_progress is True:    print(len(population_index))

                    # Update the history
                    len_population.append(len(population_index))

                len_population = len_population[1:]
                print(len(Q.Pareto_index),len(Q.Pareto))
                
                # Shows error of pls4
                # for sol in self.pareto_index:
                #     if sum(instance["Objects"][0][i] for i in sol) > instance["W"]:
                #         print("UN : \t", sum(instance["Objects"][0][i] for i in sol), instance["W"])

                # Compute the different scores
                self.times[-1] += time.time()
                self.pareto_coords = [get_score(index_to_values(instance, sol_index)) for sol_index in self.pareto_index]

                if self.root2 is not None:
                    self.proportions.append(get_proportion(exacte, self.pareto_coords))
                    self.distances.append(get_distance(exacte, [index_to_values(instance, y) for y in self.pareto_index]))

                # We add the Pareto front to the graphical output
                if show is True:
                    # We show only the best solution if asked
                    if self.root2 is not None and show_best is True:
                        if self.distances[-1] < best_distance:
                            best_distance = self.distances[-1]
                            best_len_population = len_population
                            best_pareto = self.pareto_coords
                    else:
                        i1 = 0 if self.nb_tries == 1 else (_, 0)
                        i2 = 1 if self.nb_tries == 1 else (_, 1)
                        
                        for x in self.pareto_coords:
                            plot_solution(x, ax=axs[i1])
                        
                        if self.root2 is not None:
                            plot_non_dominated(exacte, ax=axs[i1])

                        axs[i2].plot(len_population)
                           
            if verbose is True:
                show_avg_proportion, show_avg_distance = None, None
                if self.root2 is not None:
                    show_avg_proportion = get_avg(self.proportions, 3)
                    show_avg_distance = get_avg(self.distances)

                print("File {} on {} tries:\n\t\ttime: {}\n\t\tproportion: {}\n\t\tdistance: {}"
                        .format(k, self.nb_tries, get_avg(self.times), show_avg_proportion, show_avg_distance))

            # We show the graphical output if asked
            if show is True:
                if show_best is True and self.root2 is not None:
                    axs[0].set_title("Solutions space")

                    for x in best_pareto:  plot_solution(x, ax=axs[0])
                    plot_non_dominated(exacte, ax=axs[0])

                    axs[1].set_title("Evolution of the population's size")
                    axs[1].plot(best_len_population)

                plt.show()

        return self.pareto_index
    
    def save_pareto(self, directory="Results/Pareto", filename="Unnamed"):
        """
        Save the approximation of the pareto front in to the given path
        """

        with open("{}/{}.pkl".format(directory, filename), "wb") as f:
            pickle.dump(self.pareto_coords, f)

    
if __name__ == "__main__":
    pls1 = PLS_QT(nb_tries=1, nb_files=1)
    pls1.run()
        
