
def weighted_sum(weights, x_vector):
    return sum(weights[i] * x_vector[i] for i in range(len(weights)))


def OWA(weights, x_vector):
    x_vector = list(x_vector)
    x_vector.sort()
    return sum(weights[i] * x_vector[i] for i in range(len(weights))) 

# Choquet
class node:
    label = set()
    N = 0
    position = 0
    def __init__(self, N_, position): # N elements capacity
        
        self.N = N_
        l = []
        for i in range(1,self.N+1):
            l.append(i)
        for i in range(1,self.N+1):
            if position == 0:
                p = position-N_+int(comb(self.N,i))
                self.label = set(list(combinations(l,i-1))[p])
                break
            if position <= N_:
                p = position-N_+int(comb(self.N,i))-1
                self.label = set(list(combinations(l,i))[p])
                break
            N_ = N_ + int(comb(self.N,i+1))
            
class capacity:
    graph = []
    N = 0
    set_label = []
    
    def __init__(self,N_):
        self.N = N_
        self.graph = []
        self.set_label = []
        for i in range(2**self.N):
            self.graph.append(node(self.N,i))
            self.set_label.append(self.graph[i].label)


def choquet(mu, x_vector):
    order = []
    x_vector  = list(x_vector)
    x = x_vector.copy()
    for i in x:
        m = min(x_vector)
        order.append(x.index(m))
        x_vector.remove(m)
        
    c = capacity(len(x))
    c = c.set_label
    c.remove(set())
    choquet_value = x[order[0]]
    l = [i+1 for i in range(len(x))]
    for i in range(len(x)-1):
        l.remove(order[i]+1)
        l = set(l)
        choquet_value += (x[order[i+1]] - x[order[i]]) * mu[c.index(l)+1]
        l = list(l)
    return choquet_value
