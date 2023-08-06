from typing import Any

infinity = float('inf')

class Array:
    @classmethod
    def create(cls, length: int):
        return cls(length)

    def __init__(self, length: int):
        self._length = length
        self._dictionary: dict[int, Any] = {i: None for i in range(self._length)}

    def get(self, index: int):
        if not (0 <= index < self._length):
            raise ValueError(f"Incorrect index value {index}")
        return self._dictionary[index]

    def set(self, index: int, element: Any):
        if not (0 <= index < self._length):
            raise ValueError(f"Incorrect index value: {index}")

        self._dictionary[index] = element
        return self

    def __getitem__(self, index: int):
        return self.get(index)

    def __setitem__(self, index: int, element: Any):
        return self.set(index, element)

    def __iter__(self):
        return self._dictionary.values().__iter__()

    def __str__(self):
        return f"Array({self.__repr__()})"

    def __repr__(self):
        return str(list(self._dictionary.values()))

    def __len__(self):
        return self._length
    
    def __eq__(self, other):
        if isinstance(other,Array):
            if len(self) == len(other) and self._dictionary == other._dictionary:
                return True
        return False

class Matrix():
    @classmethod
    def create(cls, rows: int, columns: int):
        return cls(rows, columns)

    def __init__(self, rows: int, columns: int):
        self._shape = (rows, columns)
        self._rows = rows
        self._columns = columns

        self._values = Array(rows)
        for j in range(columns):
            self._values[j] = Array(columns)

    def get(self, row: int, column: int | None = None):
        if not (0 <= row < self._rows):
            raise ValueError(f"Incorrect index value {row}")
        
        if column is None:
            return self._values[row]
        
        if not (0 <= column < self._columns):
            raise ValueError(f"Incorrect index value {row}")
        
        return self._values[row][column]

    def set(self, row: int, column: int, value: int | float | bool | None):
        if not (0 <= row < self._rows):
            raise ValueError(f"Incorrect index value {row}")
        if not (0 <= column < self._columns):
            raise ValueError(f"Incorrect index value {row}")

        self._values[row][column] = value
        return self

    def __getitem__(self, a: int | tuple):
        if isinstance(a, int):
            return self.get(a, None)
        
        if not len(a) == 2:
            raise ValueError("Too many values. Only two dimensional")
        
        return self.get(a[0], a[1])

    def __setitem__(self, a: int | tuple, value: int | float | bool | None):
        if isinstance(a, int):
            raise ValueError()
        
        if not len(a) == 2:
            raise ValueError("Too many values. Only two dimensional")
        
        return self.set(a[0], a[1], value)

    def __iter__(self):
        return self._values.__iter__()

    def __str__(self):
        return f"Matrix({self.__repr__()})"

    def __repr__(self):
        return str(self._values)
    
    def __eq__(self, other):
        if isinstance(other,Matrix):
            if self._shape == other._shape and self._values == other._values:
                return True
        return False
        
    def __add__(self, other):
        if not isinstance(other, Matrix):
            raise NotImplementedError()
        
        if other._shape != self._shape:
            raise ValueError("Matrices must have identical shapes")
        
        new = Matrix(self._shape[0], self._shape[1])
        for i in range(self._rows):
            for j in range(self._columns):
                new[i,j] = self[i][j] + other[i][j]
        return new

    def __sub__(self, other):
        if not isinstance(other, Matrix):
            raise NotImplementedError()
        
        if other._shape != self._shape:
            raise ValueError("Matrices must have identical shapes")
        
        new = Matrix(self._rows, self._columns)
        for i in range(self._rows):
            for j in range(self._columns):
                new[i,j] = self[i][j] - other[i][j]
        return new

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            new = Matrix(self._rows, self._columns)
            for i in range(self._rows):
                for j in range(self._columns):
                    new[i,j] = other * self[i,j] 

        if not isinstance(other, Matrix):
            raise NotImplementedError()
        
        if not self._columns == other._rows:
            raise ValueError("column of first matrix must equal row of second")
        
        new = Matrix(self._rows, other._columns)
        for i in range(self._rows):
            for j in range(self._columns):
                new[i,j] = sum(self[i,k]*other[k,j] for k in range(self._columns))

        return new
    

class List:
    @classmethod
    def create(cls):
        return cls()

    def __init__(self):
        self._list: list[Any] = []

    def is_empty(self):
        return len(self._list) == 0

    def get(self, index: int):
        if not (0 <= index < len(self._list)):
            raise ValueError("Incorrect index value")

        return self._list[index]

    def set(self, index: int, element: Any):
        if not (0 <= index < len(self._list)):
            raise ValueError("Incorrect index value")

        self._list[index] = element
        return self

    def append(self, element: Any):
        self._list.append(element)
        return self

    def delete(self, index: int):
        self._list.pop(index)
        return self

    def __getitem__(self, index: int):
        return self.get(index)

    def __setitem__(self, index: int, element: Any):
        return self.set(index, element)

    def __iter__(self):
        return self._list.__iter__()

    def __str__(self):
        return f"List({self.__repr__()})"

    def __repr__(self):
        return str(self._list)

    def __len__(self):
        return len(self._list)
    
    def __eq__(self, other):
        if isinstance(other, List):
            return self._list == other._list
        return False

class Stack:
    @staticmethod
    def create():
        return Stack()

    def __init__(self):
        self._list: list[Any] = []

    def is_empty(self):
        return len(self._list) == 0

    def push(self, element: Any):
        self._list.append(element)
        return self

    def pop(self):
        self._list.pop()
        return self

    def head(self):
        return self._list[-1]

    def __str__(self):
        return f"Stack({self.__repr__()})"

    def __repr__(self):
        return f"Head: {self.head()}"

class Queue:
    @staticmethod
    def create():
        return Queue()

    def __init__(self):
        self._list: list[Any] = []

    def is_empty(self):
        return len(self._list) == 0

    def enqueue(self, element: Any):
        self._list.append(element)
        return self

    def dequeue(self):
        self._list.pop(0)
        return self

    def head(self):
        return self._list[0]

    def __str__(self):
        return f"Queue({self.__repr__()})"

    def __repr__(self):
        return f"Head: {self.head()}"

class PriorityQueue:
    @staticmethod
    def create():
        return PriorityQueue()

    def __init__(self):
        self._list: list[tuple[Any, int]] = []

    def is_empty(self):
        return len(self._list) == 0

    def enqueue(self, element: Any, priority: int):
        self._list.append((element, priority))
        self._list.sort(key=lambda t: t[1])
        return self

    def dequeue(self):
        self._list.pop()
        return self

    def head(self):
        return self._list[-1][0]

    def __str__(self):
        return f"PriorityQueue({self.__repr__()})"

    def __repr__(self):
        return f"Head: {self.head()}"

class Dictionary:
    @staticmethod
    def create():
        return Dictionary()

    def __init__(self):
        self._keys: list[Any] = []
        self._values: list[Any] = []

    def is_empty(self):
        return len(self._keys) == 0

    def get(self, key_element: Any):
        for key, value in zip(self._keys, self._values):
            if key == key_element:
                return value

        raise ValueError("Invalid key value")

    def set(self, key_element: Any, value_element: Any):
        for i, key in enumerate(self._keys):
            if key == key_element:
                self._values[i] = value_element
                return self

        raise ValueError("Invalid key value")

    def add(self, key_element: Any, value_element: Any):
        self._keys.append(key_element)
        self._values.append(value_element)
        return self

    def remove(self, key_element: Any):
        for i, key in enumerate(self._keys):
            if key == key_element:
                self._values.pop(i)
                self._keys.pop(i)
                return self

    def has_key(self, key_element: Any):
        return key_element in self._keys

    def __getitem__(self, key: Any):
        return self.get(key)

    def __setitem__(self, key: Any, value: Any):
        if self.has_key(key):
            return self.set(key, value)
        return self.add(key, value)

    def __iter__(self):
        return self._keys.__iter__()

    def __str__(self):
        return f"Dictionary({self.__repr__()})"

    def __repr__(self):
        return f"keys: {str(self._keys)}"
    
    def __eq__(self, other):
        if isinstance(other, Dictionary):
            return self._keys == other._keys and self._values == other._values
        return False

class Graph:
    @staticmethod
    def create(*, directed=False):
        return Graph(directed=directed)

    def __init__(self, *, directed=False):
        self._nodes: list[Any] = []
        self._edges: list[tuple[Any, Any]] = []

        self._directed = directed

    @property
    def V(self):
        return len(self._nodes)

    @property
    def E(self):
        return len(self._edges)

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    def add_node(self, node: Any):
        self._nodes.append(node)
        return self

    def add_edge(self, node1: Any, node2: Any):
        if not (node1 in self._nodes and node2 in self._nodes):
            raise ValueError("Nodes must already be in the graph")

        self._edges.append((node1, node2))
        if not self._directed:
            self._edges.append((node2, node1))

        return self

    def adjacent(self, node1: Any, node2: Any):
        return (node1, node2) in self._edges

    def neighbours(self, node: Any):
        node_neighbours = List.create()

        for edge in self._edges:
            if edge[0] == node:
                node_neighbours.append(edge[1])

        return node_neighbours

    def has_node(self, node: Any):
        return node in self._nodes

    def has_edge(self, node1: Any, node2: Any):
        for edge in self._edges:
            if edge[0] == node1 and edge[1] == node2:
                return True
        return False

class WeightedGraph(Graph):
    def __init__(self, *, directed=False):
        self._nodes: list[Any] = []
        self._edges: list[tuple[Any, Any, int]] = []

        self._directed = directed

    def add_edge(self, node1: Any, node2: Any, weight: int = 1):
        if not (node1 in self._nodes and node2 in self._nodes):
            raise ValueError("Nodes must already be in the graph")

        self._edges.append((node1, node2, weight))
        if not self._directed:
            self._edges.append((node2, node1, weight))

        return self

    def get_weight(self, node1: Any, node2: Any):
        for edge in self._edges:
            if edge[0] == node1 and edge[1] == node2:
                return edge[2]

        raise ValueError("Nodes are not adjacent")
