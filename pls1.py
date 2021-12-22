import random
import matplotlib.pyplot as plt

from read_file import *
from utils import *

class PLS1:
    """
    Pareto local search, naive version
    """

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
            if self.root2 is not None:
                exacte = read_exact_file(self.root2.format(k))
            
            # Define the graphs if asked
            if show is True:
                # Not possible to show in more than 2 dimensions
                show = len(instance["Objects"][1]) <= 3

                # Initializing plotting parameters
                best_distance, best_len_population, best_pop = float('inf'), [], []
                fig, axs = plt.subplots(1 if show_best is True else self.nb_tries, 2)

            # Average the results over a number of runs
            for _ in range(self.nb_tries):
                if verbose is True: print("File {}, try {}/{}".format(k, _, self.nb_tries), end='\r')

                self.times.append(-time.time())

                pareto_index = self.get_init_pop(instance)
                population_index = pareto_index[:] # Get the initial population
                len_population = [-1, len(population_index)] # History of the pareto front's length

                new_population_index = []
                visited_index = [set(p) for p in pareto_index[:]] # history of already visited solutions

                # We continue until convergence is reached
                while len(population_index) != 0:
                    for current_index in population_index:
                        # We retrieve the neighbours of the current solution
                        neighbours_index = self.get_neighbours(current_index, instance)
                        for neighbour_index in neighbours_index:
                            # We retrieve the new solution from the found neighbours
                            new_solution_index = self.get_solution_from_neighbours(current_index, neighbour_index)

                            # We do a preliminary check to see if the neighbour is not already dominated by the current solution
                            new_solution_weights, current_weights = index_to_values(instance, new_solution_index), index_to_values(instance, current_index)
                            if not is_dominated(new_solution_weights, current_weights):
                                # We update the Pareto front
                                if self.update(instance, pareto_index, new_solution_index):
                                    PLS1.update(self, instance, new_population_index, new_solution_index)

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

                # Compute the different scores
                self.times[-1] += time.time()
                pareto_coords = [get_score(index_to_values(instance, sol_index)) for sol_index in pareto_index]

                if self.root2 is not None:
                    self.proportions.append(get_proportion(exacte, pareto_coords))
                    self.distances.append(get_distance(exacte, [index_to_values(instance, y) for y in pareto_index]))

                # We add the Pareto front to the graphical output
                if show is True:
                    # We show only the best solution if asked
                    if self.root2 is not None:
                        if show_best is True:
                            if self.distances[-1] < best_distance:
                                best_distance = self.distances[-1]
                                best_len_population = len_population
                                best_pareto = pareto_coords
                        else:
                            i1 = 0 if self.nb_tries == 1 else (_, 0)
                            i2 = 1 if self.nb_tries == 1 else (_, 1)
                            
                            for x in pareto_coords:
                                plot_solution(x, ax=axs[i1])
                            
                            if self.root2 is not None:
                                plot_non_dominated(exacte, ax=axs[i1])

                            axs[i2].plot(len_population)
                           
            if verbose is True: print("File {} on {} tries:\n\t\ttime: {}\n\t\tproportion: {}\n\t\tdistance: {}"
                                        .format(k, self.nb_tries, get_avg(self.times), get_avg(self.proportions, 3), get_avg(self.distances)))      

            # We show the graphical output if asked
            if show is True:
                if show_best is True:
                    axs[0].set_title("Solutions space")
                    for x in best_pareto:  plot_solution(x, ax=axs[0])
                    if self.root2 is not None:
                        plot_non_dominated(exacte, ax=axs[0])

                    axs[1].set_title("Evolution of the population's size")
                    axs[1].plot(best_len_population)

                plt.show()
    
        return pareto_index
    
if __name__ == "__main__":
    pls1 = PLS1(nb_tries=1, nb_files=1)  
    pls1.run()
