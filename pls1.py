import random
import matplotlib.pyplot as plt

from read_file import *
from utils import *

class PLS1:
    """
    Pareto local search, naive version
    """

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
        """
        Initialize the population with a randomly generated solution
        """

        pop, S = [], 0
        objects = list(filter(lambda x: x['w'] <= instance['W'] - S, instance["Objects"][:]))

        # While there is room in the backpack and that there are objects left to choose
        while S <= instance['W'] and len(objects) > 0:
            # Randomly choose an object
            new_obj = random.choice(objects)
            objects.remove(new_obj)

            # Add it to the population
            pop.append(new_obj)
            S += new_obj['w']
            
            # Filter the backpack so that only the compatible weigths remain
            objects = list(filter(lambda x: x['w'] <= instance['W'] - S, objects))

        return [pop]

    def get_neighbours(self, current, instance):
        """
        Get a neighbour of the current solution with a 1-1 exchange
        """

        other_list = [x for x in instance["Objects"] if x not in current] # The other pickable objects
        S = sum([x["w"] for x in current]) # The total weight of the current solution

        neighbours = [] # list of neighbours : tuple(objects to take off, list of objects to add)

        # We test all the 1-1 combinations
        for obj in current:
            # We filter out the objects that can not get in
            filtered_others = list(filter(lambda x: x["w"] <= instance["W"] - S + obj["w"], other_list))
            for other in filtered_others:
                copy_others = filtered_others[:]
                copy_others.remove(other)

                chosen_others = [other] # the list of objects to add
                newS =  S - obj["w"] + other["w"] # the new weight with the exchange

                # We update the list of pickable objects
                copy_others = list(filter(lambda x: x['w'] <= instance['W'] - newS, copy_others))

                # We add the exchange to the list of neighbours
                neighbours.append((obj, chosen_others))

                # While there is room in the backpack and that there are objects left to choose
                while newS <= instance['W'] and len(copy_others) > 0:
                    # Randomly choose an object
                    new_other = random.choice(copy_others)
                    copy_others.remove(new_other)

                    # Add it to the population
                    chosen_others.append(new_other)
                    newS += new_other['w']
                    
                    # Filter the backpack so that only the compatible weigths remain
                    copy_others = list(filter(lambda x: x['w'] <= instance['W'] - newS, copy_others))

        return neighbours

    def update(self, Pareto, x):
        """
        Naively update the list of non-dominated solutions
        """

        score_x, dominated_by_x = get_score(x), []

        # We iterate through the Pareto front and compare the solutions with x
        notDominated = True
        for y in Pareto:
            score_y = get_score(y)
            if is_score_dominated(score_y, score_x):
                dominated_by_x.append(y)
            elif is_score_dominated(score_x, score_y):
                notDominated = False
                break

        # We remove all the dominated solutions
        for y in dominated_by_x:
            Pareto.remove(y)

        # We add the solution to the Pareto front if it is not dominated
        if notDominated is True:
            Pareto.append(x)

        return notDominated

    def run(self, verbose=True, show=True, show_best=True):
        """
        Run multiple times the algorithm on the given root
        """
        
        # Iterate through the root
        for k in range(self.nb_files):
            # Read the file
            instance = read_file(self.root.format(k))
            if self.root2 is not None:
                exacte = read_exact_file(self.root2.format(k))
            
            # Define the graphs if asked
            if show is True:
                # Not possible to show in more than 2 dimensions
                show = len(instance["Objects"][0]) <= 3

                # Initializing plotting parameters
                best_distance, best_len_pop, best_pop = float('inf'), [], []
                fig, axs = plt.subplots(1 if show_best is True else self.nb_tries, 2)

            # Average the results over a number of runs
            for _ in range(self.nb_tries):
                if verbose is True: print("File {}, try {}/{}".format(k, _, self.nb_tries), end='\r')

                self.times.append(-time.time())

                population = self.get_init_pop(instance) # Get the initial population
                len_pop = [-1, len(population)] # History of the populations length over
                hasAddedSolution = True # Convergence check : have we added a solution to the front?

                # We continue until convergence is reached (population hasn't changed and we haven't added any solution)
                while len_pop[-1] != len_pop[-2] or hasAddedSolution is True:
                    for current in population:
                        # We retrieve the neighbours of the current solution
                        neighbours = self.get_neighbours(current, instance)

                        for neighbour in neighbours:
                            # We proceed with the 1-1 exchange
                            new_solution = current[:] + neighbour[1]
                            new_solution.remove(neighbour[0])
                            
                            # We do a preliminary check to see if the neighbour is not already dominated by the current solution
                            if new_solution not in population and not is_dominated(new_solution, current):
                                # We update the Pareto front
                                hasAddedSolution = self.update(population, new_solution)

                    # Update the history        
                    len_pop.append(len(population))
                len_pop = len_pop[1:]

                # Compute the different scores
                self.times[-1] += time.time()
                if self.root2 is not None:
                    self.proportions.append(get_proportion(exacte, population))
                    self.distances.append(get_distance(exacte, population))

                # We add the Pareto front to the graphical output
                if show is True:
                    # We show only the best solution if asked
                    if show_best is True:
                        if self.distances[-1] < best_distance:
                            best_distance = self.distances[-1]
                            best_len_pop = len_pop
                            best_pop = population
                    else:
                        i1 = 0 if self.nb_tries == 1 else (_, 0)
                        i2 = 1 if self.nb_tries == 1 else (_, 1)
                        
                        for x in population:    plot_solution(x, ax=axs[i1])
                        if self.root2 is not None:
                            plot_non_dominated(exacte, ax=axs[i1])

                        axs[i2].plot(len_pop)
                           
            if verbose is True: print("File {} on {} tries:\n\t\ttime: {}\n\t\tproportion: {}\n\t\tdistance: {}"
                                        .format(k, self.nb_tries, get_avg(self.times), get_avg(self.proportions, 3), get_avg(self.distances)))      

            # We show the graphical output if asked
            if show is True:
                if show_best is True:
                    axs[0].set_title("Solutions space")
                    for x in best_pop:  plot_solution(x, ax=axs[0])
                    if self.root2 is not None:
                        plot_non_dominated(exacte, ax=axs[0])

                    axs[1].set_title("Evolution of the population's size")
                    axs[1].plot(best_len_pop)

                plt.show()
    
if __name__ == "__main__":
    pls1 = PLS1(nb_tries=1, nb_files=1)
    pls1.run()
