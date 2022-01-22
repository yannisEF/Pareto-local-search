import itertools

from Utils.utils_pls import *


def compare_label(label): # label of later generation need to be compared
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
        self.score = get_score(index_to_values(instance, index))
        self.length = len(self.score)
        self.label = []
        self.children = []
        self.index = index
    

class Quad_tree:
    def __init__(self,solution):
        self.root = solution
        self.Pareto = [self.root]
        self.Pareto_index = [self.root.index]
        
    def get_label(self,x,y):
        l = [0 for i in range(len(x.score))]
        eq = []
        for i in range(len(x.score)):
            if x.score[i] < y.score[i]:
                l[i] = 1
            if x.score[i] == y.score[i]:
                eq.append(i)
                
        if max(l) == 1 :
            for i in eq:
                l[i] = 1
        return l
    
    def remove_children(self,current_root,removed):
        if current_root.children == []:
            return 1
        else:
            c = current_root.children.copy()
            for i in c:   
                removed.append(i)
                current_root.children.remove(i)
                self.remove_children(i,removed)
                
    def remove_children_P(self,removed): # delete dominated solution
        for i in removed:
            self.Pareto.remove(i)
            self.Pareto_index.remove(i.index)
            
    def need_to_compare(self,Removed_solution,solution,current_root,flag): #determine whether the new solution is dominated
        l = self.get_label(current_root,solution)
        label_compare = compare_label(l)
        c = current_root.children.copy()
        D = current_root.length
        for child in c:
            if self.get_label(current_root,child) in label_compare:
                if self.get_label(child,solution) == [0 for k in range(D)]:
                    flag.append(1)
                if self.get_label(child,solution) == [1 for k in range(D)]:
                    self.Pareto.remove(child)
                    self.Pareto_index.remove(child.index)
                    self.remove_children(child,Removed_solution)
                    current_root.children.remove(child)
                if child.children != []:
                    self.need_to_compare(Removed_solution,solution,child,flag)
       
    def update_add_solution(self,current_root,solution,Removed_solution):
        D = current_root.length
        AddIn = True
        solution.label = self.get_label(current_root,solution)
        if solution.label == [1 for i in range(D)]: # y dominate x, delete x 
            self.remove_children(current_root,Removed_solution)
            self.root = solution
            self.Pareto = [self.root]
            self.Pareto_index = [self.root.index]
            return AddIn
        
        elif solution.label == [0 for i in range(D)]: # x dominate y, do nothing
           AddIn = False
           return AddIn
        
        else:
            label_compare = compare_label(solution.label)
            flag = []
            if current_root == self.root:
                self.need_to_compare(Removed_solution,solution,current_root,flag)
            if flag != []:
                return False
            else:
                AddIn = True
            for i in current_root.children:
                if solution.label == self.get_label(current_root,i):
                    new_root = i
                    AddIn = False
            
            if AddIn == True:
                current_root.children.append(solution)
                self.Pareto.append(solution)
                self.Pareto_index.append(solution.index)
                return AddIn
            else:
                self.update_add_solution(new_root,solution,Removed_solution)
            
    def update(self,instance,new_population_index):
        solu = solution(instance,new_population_index)
        Removed_solution = []
        Add = self.update_add_solution(self.root,solu,Removed_solution)
        if len(self.Pareto) != 1 and Removed_solution != []:
            self.remove_children_P(Removed_solution)
        if Removed_solution != []:
            for i in Removed_solution:
                rs = []
                self.update_add_solution(self.root,i,rs)
        else:
            return Add
