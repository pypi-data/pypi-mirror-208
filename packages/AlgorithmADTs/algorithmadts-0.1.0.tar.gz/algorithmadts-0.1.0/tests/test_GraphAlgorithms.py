from AlgorithmADTs.GraphAlgorithms import *

def test_Prims():
    G = WeightedGraph()

    G.add_node("A")
    G.add_node("B")
    G.add_node("C")
    G.add_node("D")
    G.add_node("E")
    G.add_node("F")
    
    G.add_edge("A","B",8)
    G.add_edge("A","C",6)
    G.add_edge("A","F",9)

    G.add_edge("B","C",4)
    G.add_edge("B","E",7)

    G.add_edge("C","D",5)
    G.add_edge("C","F",1)

    G.add_edge("D","E",3)
    G.add_edge("D","F",2)

    G.add_edge("E","F",3)

    tree = Prims(G)
    assert sum(G.get_weight(e[0],e[1]) for e in tree.edges) == 16

def test_Dijstras():
    G = WeightedGraph(directed=True)
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)

    G.add_edge(1,2,2)
    G.add_edge(1,4,4)
    G.add_edge(2,3,3)
    G.add_edge(2,4,1)
    G.add_edge(4,3,1)

    dist, prev = Dijkstras(G, source = 1)
    assert dist[1] == 0
    assert dist[2] == 2
    assert dist[4] == 3
    assert dist[3] == 4

    assert prev[2] == 1
    assert prev[4] == 2
    assert prev[3] == 4

def test_BellmanFord():
    G = WeightedGraph(directed=True)
    G.add_node("s")
    G.add_node("A")
    G.add_node("B")
    G.add_node("C")
    G.add_node("D")
    G.add_node("t")

    G.add_edge("s","A",5)
    G.add_edge("s","C",-2)

    G.add_edge("A","B",1)
    G.add_edge("B","D",-1)
    G.add_edge("C","A",2)
    G.add_edge("C","B",4)
    G.add_edge("C","D",4)
    G.add_edge("D","t",1)
    G.add_edge("t","B",2)

    dist, prev = BellmanFord(G, source = "s")
    assert dist["A"] == 0
    assert dist["B"] == 1
    assert dist["C"] == -2
    assert dist["D"] == 0
    assert dist["t"] == 1

    assert prev["A"] == "C"
    assert prev["t"] == "D"

def test_FloydWarshall():
    G = WeightedGraph(directed=True)
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)

    G.add_edge(1,2,3)
    G.add_edge(1,4,5)
    G.add_edge(2,1,2)
    G.add_edge(2,4,4)
    G.add_edge(3,2,1)
    G.add_edge(4,3,2)

    print(G.has_edge(1,4))

    dist, prev = FloydWarshall(G)   

    M_dist = [[0, 3, 7, 5], [2, 0, 6, 4], [3, 1, 0, 5], [5, 3, 2, 0]]
    M_prev = [[0, 0, 3, 0], [1, 1, 3, 1], [1, 2, 2, 1], [1, 2, 3, 3]]


    assert M_dist == list(list(row) for row in dist)
    assert M_prev == list(list(row) for row in prev)

def test_PageRank():
    G = Graph(directed=True)
    G.add_node('A')
    G.add_node('B')
    G.add_node('C')
    G.add_node('D')
    G.add_node('E')

    G.add_edge('A','B')
    G.add_edge('B','A')
    G.add_edge('C','A')
    G.add_edge('C','E')
    G.add_edge('D','A')
    G.add_edge('D','C')
    G.add_edge('E','A')
    G.add_edge('E','D')

    Pr = PageRank(G, num_iterations = 50)

    assert round(Pr['A'],4) == 0.4397
    assert round(Pr['B'],4) == 0.4038
    assert round(Pr['C'],4) == 0.0522
    assert round(Pr['D'],4) == 0.0522
    assert round(Pr['E'],4) == 0.0522
