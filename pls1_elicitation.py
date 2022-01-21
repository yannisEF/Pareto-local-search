import random
import itertools
import matplotlib.pyplot as plt

from read_file import *
from utils_pls import *

from elicitor import DecisionMaker, Elicitor
from agregation_functions import weighted_sum

import pickle



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
    def __init__(self, instance): # instance is element in population
        self.socre = get_score(instance)
        self.son = [] # full of solution
        self.length = len(self.socre)
        self.label = []
       

class Quad_tree:
    def __init__(self,solution): # instance is element in population
        self.root = solution # root is a solution type
        self.Pareto = [self.root] # full of solution
        
    def get_label(x,y):  # y is a new solution [0000] => delete x  [1111]=> delete x
        return [0 if x.socre[i] > y.socre[i] else 1 for i in range(x.length)]
    
    def remove_son(self,current_root,removed):

        if current_root.son == []:
            self.Pareto.remove(current_root)
            self.pareto_index.remove(current_root.index)
            return 1
        else:
            c = current_root.son.copy()
            for i in c:   
                removed.append(i)
                current_root.son.remove(i)
                self.remove_son(i,removed)
                
        
    def update_add_solution(self,current_root,solution,Removed_solution): # Removed_solution = []
        D = current_root.length
        solution.label = self.get_label(current_root,solution)
        if solution.label == [1 for i in range(D)]: # y dominate x, delete x
            Removed_solution = current_root.son
            self.remove_son(current_root)
            self.root = solution
            return Removed_solution
        
        elif solution.label == [0 for i in range(D)]: # x dominate y, do nothing
            return Removed_solution
        
        else:
            AddIn = True
            label_compare = compare_label(solution.label)
            for i in current_root.son:
                if i.label == label_compare[0]:
                    new_root = i
                    AddIn = False
                    
                if i.label in label_compare:
                    if self.get_label(i,solution) == [0 for k in range(D)]: # y is dominated
                        return Removed_solution
                    elif self.get_label(i,solution) == [1 for k in range(D)]: # son_x[i] is dominated
                        self.remove_son(i,Removed_solution)
                     
            if AddIn == True:
                current_root.son.append(solution)
                self.Pareto.append(solution)
                return Removed_solution
            else:
                self.update(new_root,solution,Removed_solution)
             

    def update(self,solution):
        Removed_solution = []
        self.update_add_solution(self.root,solution,Removed_solution)
        if Removed_solution != []:
            for i in Removed_solution:
                rs = []
                self.update_add_solution(self.root,i,rs)


class PLS1:
    """
    Pareto local search, naive version
    """

    def __init__(self, weight ,nb_files=1, nb_tries=10 ,root="Data/100_items/2KP100-TA-{}.dat", root2="Data/100_items/2KP100-TA-{}.eff" ,instance = None):
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

        # Pareto front approximation
        self.pareto_index = []
        self.pareto_coords = []
        self.hiden_weight = weight


    def get_init_pop(self, instance):
        """
        Initialize the population with a randomly generated solution
        """

        pop_index, S = [], 0
        index_objects = list(filter(lambda i: instance["Objects"][0][i] <= instance['W'], range(instance["n"])))

        # While there is room in the backpack and that there are objects left to choose
        while S <= instance['W'] and len(index_objects) > 0:
            # Randomly choose an object
            new_index_obj = random.choice(index_objects)
            index_objects.remove(new_index_obj)

            # Add it to the population
            pop_index.append(new_index_obj)
            S += instance["Objects"][0][new_index_obj]
            
            # Filter the backpack so that only the compatible weigths remain
            index_objects = list(filter(lambda i: instance["Objects"][0][i] <= instance['W'], index_objects))

        return [pop_index]

    def get_neighbours(self, current, instance):
        """
        Get a neighbour of the current solution with a 1-1 exchange
        """
        
        other_index_list = set(range(instance["n"])) - set(current) # The other pickable objects
        S = sum([instance["Objects"][0][i] for i in current]) # The total weight of the current solution

        neighbours = [] # list of neighbours : tuple(object to take off, list of objects to add)

        # We test all the 1-1 combinations
        for obj_index in current:
            # We filter out the objects that can not get in
            filtered_index_others = set(filter(lambda i: instance["Objects"][0][i] <= instance["W"] - S + instance["Objects"][0][obj_index], other_index_list))
            for other_index in filtered_index_others:
                copy_index_others = filtered_index_others.copy()
                copy_index_others.remove(other_index)

                chosen_index_others = [other_index] # the list of objects to add
                newS =  S - instance["Objects"][0][obj_index] + instance["Objects"][0][other_index] # the new weight with the exchange

                # We update the list of pickable objects
                copy_index_others = set(filter(lambda i: instance["Objects"][0][i] <= instance['W'] - newS, copy_index_others))

                # We add the exchange to the list of neighbours
                neighbours.append(([obj_index], chosen_index_others))

                # While there is room in the backpack and that there are objects left to choose
                while newS <= instance['W'] and len(copy_index_others) > 0:
                    # Randomly choose an object
                    new_index_other = random.choice(list(copy_index_others))
                    copy_index_others.remove(new_index_other)

                    # Add it to the population
                    chosen_index_others.append(new_index_other)
                    newS += instance["Objects"][0][new_index_other]
                    
                    # Filter the backpack so that only the compatible weigths remain
                    copy_index_others = set(filter(lambda i: instance["Objects"][0][i] <= instance['W'] - newS, copy_index_others))

        return neighbours
    
    def get_solution_from_neighbours(self, current_index, neighbour_index):
        """
        Proceed with a 1-1 exchange as defined in get_neighbours method
        """

        new_solution_index = current_index[:] + neighbour_index[1]
        for index_to_remove in neighbour_index[0]:
            new_solution_index.remove(index_to_remove)

        return new_solution_index

    def update(self, instance, Pareto, x):
        """
        Naively update the list of non-dominated solutions
        """

        score_x, dominated_by_x = get_score(index_to_values(instance, x)), []

        # We iterate through the Pareto front and compare the solutions with x
        for y in Pareto:
            score_y = get_score(index_to_values(instance, y))
            if is_score_dominated(score_y, score_x):
                dominated_by_x.append(y)
            elif is_score_dominated(score_x, score_y):
                return False

        # We remove all the dominated solutions
        for y in dominated_by_x:
            Pareto.remove(y)

        # We add the solution to the Pareto front if it is not dominated
        Pareto.append(x)

        return True

    def run(self, verbose=True, verbose_progress=True, show=True, show_best=True):
        """
        Run multiple times the algorithm on the given root
        """
        
        # Iterate through the root
        for k in range(self.nb_files if self.root is not None else 1):
            # Read the file
            instance = self.instance if self.instance is not None else read_file(self.root.format(k))
            instance = read_file("2KP200-TA-0.dat")
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
                
                popu_ini = get_score(index_to_values(instance, population_index[0])) 

                Optimal = [0]*len(popu_ini)
                N_question = 0
                # We continue until convergence is reached
                while popu_ini != Optimal :
                    
                    for current_index in population_index:
                        current_values = index_to_values(instance, current_index)
                        # We retrieve the neighbours of the current solution
                        neighbours_index = self.get_neighbours(current_index, instance)
                        for neighbour_index in neighbours_index:
                            # We retrieve the new solution from the found neighbours
                            new_solution_index = self.get_solution_from_neighbours(current_index, neighbour_index)

                            # We do a preliminary check to see if the neighbour is not already dominated by the current solution
                            new_solution_values = index_to_values(instance, new_solution_index)
                            if not is_dominated(new_solution_values, current_values):
                                # We update the Pareto front
                                if self.update(instance, self.pareto_index, new_solution_index):
                                    PLS1.update(self, instance, new_population_index, new_solution_index)
                        
                        # Update the history of already visited solutions to avoid loops
                        current_index_set = set(current_index)
                        if current_index_set not in visited_index:
                            visited_index.append(current_index_set)
                    
                    # The population holds the newfound solutions that are potentially on the Pareto front
                    #population_index = [p for p in new_population_index if set(p) not in visited_index]
                    new_population_index = []
                    self.pareto_coords = [get_score(index_to_values(instance, sol_index)) for sol_index in self.pareto_index]

                    # Update the history
                    #len_population.append(len(population_index))
                    
                    root = "Data/100_items/2KP100-TA-{}.dat"
                    save_name = root.split('/')[-1][:-4].format(0) + "_obj={}_crit={}"
                    self.save_pareto(filename=save_name)
                
                    with open("Results/Pareto/2KP100-TA-0_obj={}_crit={}.pkl", "rb") as f:
                        pareto_front = pickle.load(f)
                        
                    if len(pareto_front) != 1:
                        
                        user = DecisionMaker(weighted_sum, len(pareto_front[0]), self.hiden_weight)
                        elicitor = Elicitor(pareto_front, user)
                        elicitor.query_user()

                        N_question += len(elicitor.user_preferences)
                        Optimal = elicitor.pareto_front[0]
                    
                        # find Pareto's index
                        for i in range(len(self.pareto_coords)):
                            if Optimal == self.pareto_coords[i]:
                                Optimal_index = self.pareto_index[i]
                                Optimal_index.sort()
                                break
                    
                        population_index[0].sort()
                        if Optimal_index == population_index[0]:
                            print("Final result : ", Optimal)
                            print("number of question :", N_question)
                            break
                        else:
                            population_index = [Optimal_index]
                       


                len_population = len_population[1:]
                

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
    pls1 = PLS1((0.5,0.0,0.0,0.0,0.0,0.5),nb_tries=1, nb_files=1)
    pls1.run()
    root = "Data/Other/2KP200-TA-{}.dat"
    save_name = root.split('/')[-1][:-4].format(0) + "_obj={}_crit={}"
    pls1.save_pareto(filename=save_name)
    
    