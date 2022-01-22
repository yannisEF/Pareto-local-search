import time
import matplotlib.pyplot as plt

from pls1 import PLS1
from pls3 import PLS3

from utils_read_file import *
from utils_pls import *

from elicitor import DecisionMaker, Elicitor
from agregation_functions import weighted_sum, OWA, choquet


class PLS_ELICITATION(PLS3):
    """
    Pareto local search mixed with elicitation
    """

    def __init__(self, *args, agregation_function=weighted_sum, weights=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.agregation_function = agregation_function
        self.hiden_weights = weights

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
                
                    new_population_index = []
                    self.pareto_coords = [get_score(index_to_values(instance, sol_index)) for sol_index in self.pareto_index]

                    # Update the history
                    len_population.append(len(population_index))
                        
                    if len(self.pareto_coords) != 1:
                        user = DecisionMaker(self.agregation_function, len(self.pareto_coords[0]), self.hiden_weights)
                        elicitor = Elicitor(self.pareto_coords, user)
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

    
if __name__ == "__main__":
    pls_el = PLS_ELICITATION(nb_tries=1, nb_files=1)
    pls_el.run()    
    