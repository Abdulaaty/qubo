

import numpy        as np
import numpy.random as npr

from collections   import defaultdict
from functools     import partial


def cut_diagonal(a):
    return np.triu(a, 1)[..., 1:] + np.tril(a, 1)[..., :-1]


def generate_points(n=20, min_dist=0):
    n1, n2 = n//2, n - n//2

    # sample cluster centers
    radius = 1.5
    angle = npr.uniform(0, 2*np.pi)
    x1, y1 = radius*np.cos(angle), radius*np.sin(angle)
    x2, y2 = radius*np.cos(angle+np.pi), radius*np.sin(angle+np.pi)

    # sample standard deviation for each cluster center
    scale1, scale2 = npr.uniform(0.05, 0.15, size=2)

    # generate points
    points = np.empty((n, 2))
    while True: 
        points[:n1, :] = npr.multivariate_normal([x1, y1], np.diag([scale1, scale1]), size=n1)
        points[n1:, :] = npr.multivariate_normal([x2, y2], np.diag([scale2, scale2]), size=n2)
        dists = np.apply_along_axis(np.linalg.norm, 2, points[:,np.newaxis,:]-points)
        if np.all(dists[np.triu_indices(n, 1)] >= min_dist):
            break
            
    return points


def ising_to_qubo(I):
    Q = defaultdict(float)
    for k, v in I.items():
        if len(k) == 2:
            i, j = k
            Q[k] = 4. * v
            Q[(i,)] -= 2. * v
            Q[(j,)] -= 2. * v
            Q[()] += v
        elif len(k) == 1:
            Q[k] += 2. * v
            Q[()] -= v
        else:
            Q[()] += v
    
    return Q

def ising_to_qubo_matrix(I, n):
    m = np.zeros((n, n))
#    bias = 0
    for k, v in I.items():
        if len(k) == 2:
            i, j = k
            m[i,j] = 4. * v
            m[i,i] -= 2. * v
            m[j,j] -= 2. * v
#            bias += v
        elif len(k) == 1:
            i, = k
            m[i,i] += 2. * v
#            bias -= v
#        else:
#            bias += v
    
    return m

def binary_clustering(x, gamma=1.0):
    x = np.array(x)
    n = len(x)

    # mean adjust
    m = x.mean(axis=0)
    x = x - m

    # use Ising embedding by Bauckhage et al.
    # Gramian matrix
    G = x.dot(x.T)

    # center G
    rowMeans = np.tile(np.mean(G, axis=0), (n, 1))
    colMeans = np.tile(np.mean(G, axis=1), (n, 1)).T
    totalMean = np.mean(G)
    G = G - rowMeans - colMeans + totalMean

    # halve diagonals for reduction to triangle matrix
    G[np.diag_indices(n)] *= 0.5

    # extract parameters, skipping diagonal
    params = { (i, j): -G[i, j] for i in range(n) for j in range(i) }
    
    return ising_to_qubo_matrix(params,n)

def get_qubo_params_random():
    x = generate_points(min_dist=0.15)
    points1 = np.squeeze(np.dstack(  (x[0:10,0],x[0:10,1]) ))
    points2 = np.squeeze(np.dstack(  (x[10:,0],x[10:,1]) ))
    return binary_clustering(   np.vstack(  (points1,points2) )     ), points1,points2

def get_parameters_from_matrix(Q):
  # Extract lower (Triangualr matrix)
    Q = Q[np.tril_indices(Q.shape[0])]
    Q = Q.reshape(-1,1)   
    
    #Reverse array (get upper triangular parameters)
    result = Q[::-1]

    return result
    

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import itertools
    '''
    Q, points1,points2 = get_qubo_params_random()
    plt.plot(points1, points2, 'o')
    plt.show()
    
    # Reshape to (210,1 )
    params = get_parameters_from_matrix(-Q)
   
   
    
    n = Q.shape[0]
    Q2 = np.zeros((n,n), dtype=np.float64) 
    tri_indicies = np.triu_indices(n)
    params_iterator= 0
    for curr_index in range(0, len(tri_indicies[0])):
        Q2[tri_indicies[0][curr_index],tri_indicies[1][curr_index]] = int(params[params_iterator])
        params_iterator+=1
        
    print(Q)
    print(Q2)
    
    best_value = -np.infty
    worst_value = np.infty
    
    for x in itertools.product([0,1], repeat=n):
        value = np.dot(x, np.dot(Q2, x))
        if value > best_value:
                best_x = x
                best_value = value
        if value < worst_value:
                worst_value = value
                worst_x = x
                
    print(best_x)            
    print(best_value)
    best_x = np.array(best_x)
    print (len(best_x[best_x==1]))
    
    
    positions =   np.vstack(  (points1,points2) )    
    max_value = np.amax(positions)           # Maximum of the flattened array
    print(max_value)
    positions = 375 + positions*375/max_value
    positions = positions.astype(int)
    print(positions)
    
    
    '''
   

    x = generate_points(min_dist=0.15)
    print(x)
    plt.plot(x[:,0], x[:,1], 'o')
    plt.show()
   