import random
from xml.dom import NO_DATA_ALLOWED_ERR
import matplotlib.pyplot as plt

from read_file import *
from utils import *
from nd_tree import NDTree


class PLS:
    """
    Pareto local search with NDTree implementation
    """

    def __init__(self, nb_files=1, nb_tries=1, root="Data/100_items/2KP100-TA-{}.dat", root2="Data/100_items/2KP100-TA-{}.eff", instance=None,
    init_S=20, max_size=10, nadir_ideal_update_frequency=10):
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
        self.pareto_coords = []
        # NDTree of non-dominated solutions parameters
        self.tree_params = {"max_size":max_size, "ideal_nadir_update_frequency":nadir_ideal_update_frequency}
        self.front_tree = None

        # Init population size
        self.init_S = init_S


    def get_init_pop(self, instance):
        """
        Initialize the population with a randomly generated weighted choice
        """

        n_dim = len(instance["Objects"][1])
        
        pop_index = []
        while len(pop_index) < self.init_S:
            index_objects = list(filter(lambda i: instance["Objects"][0][i] <= instance['W'], range(instance["n"])))
            
            # Randomly sample a number of weights
            q = get_random_weights(n_dim)
            S = 0
            
            indiv_index = []
            while S <= instance['W'] and len(index_objects) > 0:
                # Define the objects' weights
                r_obj = compute_performance_value_list(instance, q, index_objects)
                r_obj = normalize(r_obj)

                # Randomly choose a new object
                new_index_obj = random.choices(index_objects, weights=r_obj, k=1)[0]
                index_objects.remove(new_index_obj)
                
                # Add it to the population
                indiv_index.append(new_index_obj)
                S += instance["Objects"][0][new_index_obj]
                
                # Filter the backpack so that only the compatible weigths remain
                index_objects = list(filter(lambda i: instance["Objects"][0][i] <= instance['W'], index_objects))
                
            if len(indiv_index) == 0:
                raise ValueError("init_S might be to big to initialize the search")
            else:
                pop_index.append(indiv_index)

        return pop_index

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

    def update(self, instance, x):
        """
        Update the tree of non-dominated solutions
        """

        score_x = get_score(index_to_values(instance, x))

        return self.front_tree.update(score_x)[0]

    def run(self, verbose_progress=True, show=True, show_best=True):
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
                if verbose_progress is True: print("File {}, try {}/{}".format(k, _, self.nb_tries))

                self.times.append(-time.time())

                population_index = self.get_init_pop(instance) # Get the initial population
                len_population = [-1, len(population_index)] # History of the pareto front's length

                self.front_tree = NDTree(instance=instance, **self.tree_params)

                tree_new_population_index = NDTree(instance=instance, **self.tree_params)
                visited_index = [set(p) for p in population_index] # history of already visited solutions

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
                            if not is_dominated(new_solution_values, current_values):
                                # We update the Pareto front


                                if self.front_tree.update(new_solution_index)[0] is True:
                                    tree_new_population_index.update(new_solution_index)

                        # Update the history of already visited solutions to avoid loops
                        current_index_set = set(current_index)
                        if current_index_set not in visited_index:
                            visited_index.append(current_index_set)

                    # The population holds the newfound solutions that are potentially on the Pareto front
                    population_index = [p for p in tree_new_population_index.get_solutions() if set(p) not in visited_index]
                    tree_new_population_index.reset()
                    
                    if verbose_progress is True:    print(len(population_index))

                    # Update the history
                    len_population.append(len(population_index))

                len_population = len_population[1:]

                # Compute the different scores
                self.times[-1] += time.time()
                self.pareto_coords = [get_score(index_to_values(instance, sol_index)) for sol_index in self.front_tree.get_solutions()]

                if self.root2 is not None:
                    self.proportions.append(get_proportion(exacte, self.pareto_coords))
                    self.distances.append(get_distance(exacte, [index_to_values(instance, y) for y in self.front_tree.get_solutions()]))

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
                           
            if verbose_progress is True:
                show_avg_proportion, show_avg_distance = None, None
                if self.root2 is not None:
                    show_avg_proportion = get_avg(self.proportions, 3)
                    show_avg_distance = get_avg(self.distances)

                print("\nFile {} on {} tries:\n\t\ttime: {}\n\t\tproportion: {}\n\t\tdistance: {}"
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

        return self.front_tree.get_solutions()
    
    def save_pareto(self, directory="Results/Pareto", filename="Unnamed"):
        """
        Save the approximation of the pareto front in to the given path
        """

        with open("{}/{}.pkl".format(directory, filename), "wb") as f:
            pickle.dump(self.pareto_coords, f)

    
if __name__ == "__main__":
    pls = PLS(nb_tries=1, nb_files=1)  
    pls.run()
