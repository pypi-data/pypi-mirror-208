from AlgorithmADTs.AbstractDataTypes import *

def Prims(G: WeightedGraph):
    """ Finds the Minimal Spanning Tree of a weighted undirected graph
    OUTPUT
    tree: WeightedGraph(directed=True)
        Contains every node in the input graph and every (weighted) edge in the MST
    """
    
    if G._directed:
        raise ValueError("Prims Algorithm must be run on an undirected graph")
    N = len(G._nodes)

    tree = WeightedGraph(directed=True)
    tree.add_node(G._nodes[0])

    while len(tree._nodes) < N:
        edges = (
            (node, neighbour)
            for node in tree._nodes
            for neighbour in G.neighbours(node)
        )
        min_edge = min(
            (edge for edge in edges if not tree.has_node(edge[1])),
            key=lambda e: G.get_weight(e[0], e[1]),
        )
        tree.add_node(min_edge[1])
        tree.add_edge(*min_edge, G.get_weight(*min_edge))

    return tree

def Dijkstras(G: WeightedGraph, source: Any):
    """Finds the shortests path between source node and all others in a weighted graph with no negative edge weights

    OUTPUT
    dist: Dictionary[key: node, value: numeric]
        The distance for each node, calculated from the source
    prev: Dictionary[key: node, value: node]
        The previous node in the shortest path for each node, from the source node. 
        Used for path reconstruction
    """

    if not G.has_node(source):
        raise ValueError("Starting_node must be in G")

    dist = Dictionary()
    prev = Dictionary()
    explored = List()

    for node in G._nodes:
        dist[node] = infinity
        prev[node] = None

    dist[source] = 0

    while len(explored) < G.V:
        unexplored_nodes = (node for node in G._nodes if node not in explored)
        closest_node = min(unexplored_nodes, key=lambda node: dist[node])

        explored.append(closest_node)
        for neighbour in G.neighbours(closest_node):
            if neighbour in explored:
                continue
            alt = dist[closest_node] + G.get_weight(closest_node, neighbour)
            if alt < dist[neighbour]:
                dist[neighbour] = alt
                prev[neighbour] = closest_node
    return dist, prev

def BellmanFord(G: WeightedGraph, source: Any):
    """Finds the shortest path between source node and all others in a weighted graph. Negative weights are allowed
    Inclues error checking for negative cycles

    OUTPUT
    dist: Dictionary[key: node, value: numeric]
        The distance for each node, calculated from the source
    prev: Dictionary[key: node, value: node]
        The previous node in the shortest path for each node, from the source node. 
        Used for path reconstruction
    """
    if not G.has_node(source):
        raise ValueError("Starting_node must be in G")

    dist = Dictionary()
    prev = Dictionary()

    for node in G._nodes:
        dist[node] = infinity
        prev[node] = None

    dist[source] = 0

    for _ in range(G.V):
        for u, v, weight in G._edges:
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                prev[v] = u

    # Check for negative cycles
    for u, v, weight in G._edges:
        if dist[u] + weight < dist[v]:
            raise ValueError("Graph contains a negative cycle")

    return dist, prev

def FloydWarshall(G: WeightedGraph):
    """Finds the shortest path between all nodes in a weighted graph. Negative weights are allowed.
    No negative cycle checking

    OUTPUT
    dist: Matrix[numeric] (G.V x G.V)
        The distance between each pair of nodes, indexed according to G.nodes
        dist[i, j] is the distance from i to j
    prev: Matrix[node] (G.V x G.V)
        The previous node in the shortest path between each node
        Used for path reconstruction
        prev[i, j] is the node immediately before j
    """
    dist = Matrix(G.V, G.V)
    prev = Matrix(G.V, G.V)

    for i, node1 in enumerate(G._nodes):
        for j, node2 in enumerate(G._nodes):
            if i == j:
                dist[i][j] = 0 
                prev[i][j] = i 

            elif G.has_edge(node1, node2):
                dist[i][j] = G.get_weight(node1, node2)
                prev[i][j] = i
            
            else:
                dist[i][j] = infinity
                prev[i][j] = None

    for k in range(G.V):
        for i in range(G.V):
            for j in range(G.V):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    prev[i][j] = prev[k][j]
            
    return dist, prev

def FloydWarshalTC(G: Graph):
    """Calculates transitive closure between all nodes in an unweighted graph.

        OUTPUT
        dist: Matrix[bool] (G.V x G.V)
            Transitive closure between every pair of nodes, indexed according to G.nodes
            dist[i, j] is the boolen of whether j can be reached from i
        prev: Matrix[node] (G.V x G.V)
            The previous node in the shortest path between each node
            Used for path reconstruction
            prev[i, j] is the node immediately before j
        """

    dist = Matrix(G.V, G.V)
    prev = Matrix(G.V, G.V)
  
    for i, node1 in enumerate(G._nodes):
        for j, node2 in enumerate(G._nodes):
            if i == j:
                dist[i][j] = True
                prev[i][j] = i 

            elif G.has_edge(node1, node2):
                dist[i][j] = True
                prev[i][j] = i
            
            else:
                dist[i][j] = False
                prev[i][j] = None

    for k in range(G.V):
        for i in range(G.V):
            for j in range(G.V):
                if (not dist[i][j]) and (dist[i][k] and dist[k][j]):
                    dist[i][j] = True
                    prev[i][j] = prev[k][j]
            
    return dist, prev

def PageRank(_G: Graph, d=0.85, num_iterations = 1_000):
    """Calculates the PageRank value in an unweighted graph.
        INPUT
        d: float
            The damping factor, the probability that a surfer will continue choosing links
        num_iterations: int
            The number of times the values are updated

        OUTPUT
        Pr: Dictionary[key: node, value: float]
            The PageRank value for every node
    """
    Pr = Dictionary()

    G = Graph(directed=_G._directed) #Create a filtered copy of the graph to run the algorithm on
    for node in _G._nodes:
        G.add_node(node)

    for edge in _G._edges:
        if not edge[0] == edge[1]:#links from a page to itself are ignored
            G.add_edge(*edge)

    #Initialise values and check for sink nodes
    for node in G._nodes:
        if len(G.neighbours(node)) == 0: #redistribute sink nodes
            for other_node in G._nodes:
                if other_node != node:
                    G.add_edge(node, other_node)

        Pr.add(node, 1/G.V) 
    
    #Calculate PageRank values
    for _ in range(num_iterations): #Run for a set number of iterations
        temp = Array(G.V)
        for i, node in enumerate(G._nodes):
            incoming_links = (node2 for node2 in G._nodes if node in G.neighbours(node2))
            temp[i] = (1-d)/G.V + d*sum(Pr[node2]/len(G.neighbours(node2)) for node2 in incoming_links)

        for i, node in enumerate(G._nodes):
            Pr[node] = temp[i]

    return Pr
