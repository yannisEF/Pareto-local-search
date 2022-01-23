
def weighted_sum(weights, x_vector):
    return sum(weights[i] * x_vector[i] for i in range(len(weights)))


def OWA(weights, x_vector):
    x_vector = list(x_vector)
    x_vector.sort()
    return sum(weights[i] * x_vector[i] for i in range(len(weights))) 


def choquet(weights, x_vector):
    raise NotImplementedError
    
