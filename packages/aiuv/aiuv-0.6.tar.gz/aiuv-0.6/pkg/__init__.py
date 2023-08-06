def puzzle():
    s = """import copy  
  
# Importing the heap methods from the python  
# library for the Priority Queue  
from heapq import heappush, heappop  
  
# This particular var can be changed to transform  
# the program from 8 puzzle(n=3) into 15  
# puzzle(n=4) and so on ...  
n = 3  
  
# bottom, left, top, right  
rows = [ 1, 0, -1, 0 ]  
cols = [ 0, -1, 0, 1 ]  
  
# creating a class for the Priority Queue  
class priorityQueue:  
      
    # Constructor for initializing a  
    # Priority Queue  
    def __init__(self):  
        self.heap = []  
  
    # Inserting a new key 'key'  
    def push(self, key):  
        heappush(self.heap, key)  
  
    # funct to remove the element that is minimum,  
    # from the Priority Queue  
    def pop(self):  
        return heappop(self.heap)  
  
    # funct to check if the Queue is empty or not  
    def empty(self):  
        if not self.heap:  
            return True  
        else:  
            return False  
  
# structure of the node  
class nodes:  
      
    def __init__(self, parent, mats, empty_tile_posi,  
                costs, levels):  
                      
        # This will store the parent node to the  
        # current node And helps in tracing the  
        # path when the solution is visible  
        self.parent = parent  
  
        # Useful for Storing the matrix  
        self.mats = mats  
  
        # useful for Storing the position where the  
        # empty space tile is already existing in the matrix  
        self.empty_tile_posi = empty_tile_posi  
  
        # Store no. of misplaced tiles  
        self.costs = costs  
  
        # Store no. of moves so far  
        self.levels = levels  
  
    # This func is used in order to form the  
    # priority queue based on  
    # the costs var of objects  
    def __lt__(self, nxt):  
        return self.costs < nxt.costs  
  
# method to calc. the no. of  
# misplaced tiles, that is the no. of non-blank  
# tiles not in their final posi  
def calculateCosts(mats, final) -> int:  
      
    count = 0  
    for i in range(n):  
        for j in range(n):  
            if ((mats[i][j]) and  
                (mats[i][j] != final[i][j])):  
                count += 1  
                  
    return count  
  
def newNodes(mats, empty_tile_posi, new_empty_tile_posi,  
            levels, parent, final) -> nodes:  
                  
    # Copying data from the parent matrixes to the present matrixes  
    new_mats = copy.deepcopy(mats)  
  
    # Moving the tile by 1 position  
    x1 = empty_tile_posi[0]  
    y1 = empty_tile_posi[1]  
    x2 = new_empty_tile_posi[0]  
    y2 = new_empty_tile_posi[1]  
    new_mats[x1][y1], new_mats[x2][y2] = new_mats[x2][y2], new_mats[x1][y1]  
  
    # Setting the no. of misplaced tiles  
    costs = calculateCosts(new_mats, final)  
  
    new_nodes = nodes(parent, new_mats, new_empty_tile_posi,  
                    costs, levels)  
    return new_nodes  
  
# func to print the N by N matrix  
def printMatsrix(mats):  
      
    for i in range(n):  
        for j in range(n):  
            print("%d " % (mats[i][j]), end = " ")  
              
        print()  
  
# func to know if (x, y) is a valid or invalid  
# matrix coordinates  
def isSafe(x, y):  
      
    return x >= 0 and x < n and y >= 0 and y < n  
  
# Printing the path from the root node to the final node  
def printPath(root):  
      
    if root == None:  
        return  
      
    printPath(root.parent)  
    printMatsrix(root.mats)  
    print()  
  
# method for solving N*N - 1 puzzle algo  
# by utilizing the Branch and Bound technique. empty_tile_posi is  
# the blank tile position initially.  
def solve(initial, empty_tile_posi, final):  
      
    # Creating a priority queue for storing the live  
    # nodes of the search tree  
    pq = priorityQueue()  
  
    # Creating the root node  
    costs = calculateCosts(initial, final)  
    root = nodes(None, initial,  
                empty_tile_posi, costs, 0)  
  
    # Adding root to the list of live nodes  
    pq.push(root)  
  
    # Discovering a live node with min. costs,  
    # and adding its children to the list of live  
    # nodes and finally deleting it from  
    # the list.  
    while not pq.empty():  
  
        # Finding a live node with min. estimatsed  
        # costs and deleting it form the list of the  
        # live nodes  
        minimum = pq.pop()  
  
        # If the min. is ans node  
        if minimum.costs == 0:  
              
            # Printing the path from the root to  
            # destination;  
            printPath(minimum)  
            return  
  
        # Generating all feasible children  
        for i in range(n):  
            new_tile_posi = [  
                minimum.empty_tile_posi[0] + rows[i],  
                minimum.empty_tile_posi[1] + cols[i], ]  
                  
            if isSafe(new_tile_posi[0], new_tile_posi[1]):  
                  
                # Creating a child node  
                child = newNodes(minimum.mats,  
                                minimum.empty_tile_posi,  
                                new_tile_posi,  
                                minimum.levels + 1,  
                                minimum, final,)  
  
                # Adding the child to the list of live nodes  
                pq.push(child)  
  
# Main Code  
  
# Initial configuration  
# Value 0 is taken here as an empty space  
initial = [ [ 1, 2, 3 ],  
            [ 5, 6, 0 ],  
            [ 7, 8, 4 ] ]  
  
# Final configuration that can be solved  
# Value 0 is taken as an empty space  
final = [ [ 1, 2, 3 ],  
        [ 5, 8, 6 ],  
        [ 0, 7, 4 ] ]  
  
# Blank tile coordinates in the   
# initial configuration  
empty_tile_posi = [ 1, 2 ]  
  
# Method call for solving the puzzle  
solve(initial, empty_tile_posi, final)  
"""
    return s

def vaccum():
    s = """import random

def display(room):
    print(room)

room = [
    [1, 1, 1, 1],
    [1, 1, 1, 1],
    [1, 1, 1, 1],
    [1, 1, 1, 1],
]
print("All the rooom are dirty")
display(room)

x =0
y= 0

while x < 4:
    while y < 4:
        room[x][y] = random.choice([0,1])
        y+=1
    x+=1
    y=0

print("Before cleaning the room I detect all of these random dirts")
display(room)
x =0
y= 0
z=0
while x < 4:
    while y < 4:
        if room[x][y] == 1:
            print("Vaccum in this location now,",x, y)
            room[x][y] = 0
            print("cleaned", x, y)
            z+=1
        y+=1
    x+=1
    y=0
pro= (100-((z/16)*100))
print("Room is clean now, Thanks for using : cleaner")
display(room)
print('performance=',pro,'%')
"""
    return s

def bfs_and_dfs():
    s = """graph = {
  'A' : ['B','C'],
  'B' : ['D', 'E'],
  'C' : ['F'],
  'D' : [],
  'E' : ['F'],
  'F' : []
}

visited_bfs = []
queue = []

def bfs(visited_bfs, graph, node):
  visited_bfs.append(node)
  queue.append(node)

  while queue:
    s = queue.pop(0) 
    print (s, end = " ") 

    for neighbour in graph[s]:
      if neighbour not in visited_bfs:
        visited_bfs.append(neighbour)
        queue.append(neighbour)

visited = set()

def dfs(visited, graph, node):
    if node not in visited:
        print (node, end=" ")
        visited.add(node)
        for neighbour in graph[node]:
            dfs(visited, graph, neighbour)

print("BFS:" , end =" ")
bfs(visited_bfs, graph, 'A')
print('\n')
print("DFS:" , end =" ")
dfs(visited, graph, 'A')
"""
    return s

def best_first_search():
    s = """from queue import PriorityQueue
v = 14
graph = [[] for i in range(v)]
 
# Function For Implementing Best First Search
# Gives output path having lowest cost
 
 
def best_first_search(actual_Src, target, n):
    visited = [False] * n
    pq = PriorityQueue()
    pq.put((0, actual_Src))
    visited[actual_Src] = True
     
    while pq.empty() == False:
        u = pq.get()[1]
        # Displaying the path having lowest cost
        print(u, end=" ")
        if u == target:
            break
 
        for v, c in graph[u]:
            if visited[v] == False:
                visited[v] = True
                pq.put((c, v))
    print()
 
# Function for adding edges to graph
 
 
def addedge(x, y, cost):
    graph[x].append((y, cost))
    graph[y].append((x, cost))
 
 
# The nodes shown in above example(by alphabets) are
# implemented using integers addedge(x,y,cost);
addedge(0, 1, 3)
addedge(0, 2, 6)
addedge(0, 3, 5)
addedge(1, 4, 9)
addedge(1, 5, 8)
addedge(2, 6, 12)
addedge(2, 7, 14)
addedge(3, 8, 7)
addedge(8, 9, 5)
addedge(8, 10, 6)
addedge(9, 11, 1)
addedge(9, 12, 10)
addedge(9, 13, 2)
 
source = 0
target = 9
best_first_search(source, target, v)
"""
    return s

def astar():
    s = """class Graph:
    
    # init class
    def __init__(self, graph_dict=None, directed=True):
        self.graph_dict = graph_dict or {}
        self.directed = directed
        if not directed:
            self.make_undirected()

    # create undirected graph by adding symmetric edges
    def make_undirected(self):
        for a in list(self.graph_dict.keys()):
            for (b, dist) in self.graph_dict[a].items():
                self.graph_dict.setdefault(b, {})[a] = dist

    # add link from A and B of given distance, and also add the inverse link if the graph is undirected
    def connect(self, A, B, distance=1):
        self.graph_dict.setdefault(A, {})[B] = distance
        if not self.directed:
            self.graph_dict.setdefault(B, {})[A] = distance
    # get neighbors or a neighbor
    def get(self, a, b=None):
        links = self.graph_dict.setdefault(a, {})
        if b is None:
            return links
        else:
            return links.get(b)

    # return list of nodes in the graph
    def nodes(self):
        s1 = set([k for k in self.graph_dict.keys()])
        s2 = set([k2 for v in self.graph_dict.values() for k2, v2 in v.items()])
        nodes = s1.union(s2)
        return list(nodes)
    # node class
class Node:

    # init class
    def __init__(self, name:str, parent:str):
        self.name = name
        self.parent = parent
        self.g = 0 # distance to start node
        self.h = 0 # distance to goal node
        self.f = 0 # total cost

    # compare nodes
    def __eq__(self, other):
        return self.name == other.name

    # sort nodes
    def __lt__(self, other):
         return self.f < other.f

    # print node
    def __repr__(self):
        return ('({0},{1})'.format(self.name, self.f))

# A* search
def astar_search(graph, heuristics, start, end):
    
    # lists for open nodes and closed nodes
    open = []
    closed = []

    # a start node and an goal node
    start_node = Node(start, None)
    goal_node = Node(end, None)

    # add start node
    open.append(start_node)
     # loop until the open list is empty
    while len(open) > 0:

       
        open.sort()                                 # sort open list to get the node with the lowest cost first
        current_node = open.pop(0)                  # get node with the lowest cost
        closed.append(current_node)                 # add current node to the closed list
        
        # check if we have reached the goal, return the path
        if current_node == goal_node:
            path = []
            while current_node != start_node:
                path.append(current_node.name + ': ' + str(current_node.g))
                current_node = current_node.parent
            path.append(start_node.name + ': ' + str(start_node.g))
            return path[::-1]

        
        neighbors = graph.get(current_node.name)    # get neighbours
        
        # loop neighbors
        for key, value in neighbors.items():
            neighbor = Node(key, current_node)      # create neighbor node
            if(neighbor in closed):                 # check if the neighbor is in the closed list
                continue

            # calculate full path cost
            neighbor.g = current_node.g + graph.get(current_node.name, neighbor.name)
            neighbor.h = heuristics.get(neighbor.name)
            neighbor.f = neighbor.g + neighbor.h

            # check if neighbor is in open list and if it has a lower f value
            if(add_to_open(open, neighbor) == True):
             # everything is green, add neighbor to open list
                open.append(neighbor)

    # return None, no path is found
    return None

# check if a neighbor should be added to open list
def add_to_open(open, neighbor):
    for node in open:
        if (neighbor == node and neighbor.f > node.f):
            return False
    return True

# create a graph
graph = Graph() # user-based input for edges will be updated in the upcoming days
# create graph connections (Actual distance)
graph.connect('Frankfurt', 'Wurzburg', 111)
graph.connect('Frankfurt', 'Mannheim', 85)
graph.connect('Wurzburg', 'Nurnberg', 104)
graph.connect('Wurzburg', 'Stuttgart', 140)
graph.connect('Wurzburg', 'Ulm', 183)
graph.connect('Mannheim', 'Nurnberg', 230)
graph.connect('Mannheim', 'Karlsruhe', 67)
graph.connect('Karlsruhe', 'Basel', 191)
graph.connect('Karlsruhe', 'Stuttgart', 64)
graph.connect('Nurnberg', 'Ulm', 171)
graph.connect('Nurnberg', 'Munchen', 170)
graph.connect('Nurnberg', 'Passau', 220)
graph.connect('Stuttgart', 'Ulm', 107)
graph.connect('Basel', 'Bern', 91)
graph.connect('Basel', 'Zurich', 85)
graph.connect('Bern', 'Zurich', 120)
graph.connect('Zurich', 'Memmingen', 184)
graph.connect('Memmingen', 'Ulm', 55)
graph.connect('Memmingen', 'Munchen', 115)
graph.connect('Munchen', 'Ulm', 123)
graph.connect('Munchen', 'Passau', 189)
graph.connect('Munchen', 'Rosenheim', 59)
graph.connect('Rosenheim', 'Salzburg', 81)
graph.connect('Passau', 'Linz', 102)
graph.connect('Salzburg', 'Linz', 126)
# make graph undirected, create symmetric connections
graph.make_undirected()
# create heuristics (straight-line distance, air-travel distance)
heuristics = {}
heuristics['Basel'] = 204
heuristics['Bern'] = 247
heuristics['Frankfurt'] = 215
heuristics['Karlsruhe'] = 137
heuristics['Linz'] = 318
heuristics['Mannheim'] = 164
heuristics['Munchen'] = 120
heuristics['Memmingen'] = 47
heuristics['Nurnberg'] = 132
heuristics['Passau'] = 257
heuristics['Rosenheim'] = 168
heuristics['Stuttgart'] = 75
heuristics['Salzburg'] = 236
heuristics['Wurzburg'] = 153
heuristics['Zurich'] = 157
heuristics['Ulm'] = 0
# run the search algorithm
path = astar_search(graph, heuristics, 'Frankfurt', 'Ulm')
print("Path:", path)
"""
    return s

def propositional_logic():
    s = """P1 = True  # The customer has a valid driver's license
P2 = True  # The customer is at least 25 years old
P3 = True  # The customer has a credit card with a high enough credit limit
P4 = False # The customer has outstanding traffic violations
P5 = False # The customer has a good driving record

# Define the propositional formulas
rule1 = P1 and P2
rule2 = P1 and P2 and P3 and not P4
rule3 = P1 and P2 and P3 and not P4 and P5

# Determine which types of cars the customer can rent
if rule3:
    print("The customer can rent an SUV.")
elif rule2:
    print("The customer can rent a luxury car.")
elif rule1:
    print("The customer can rent any type of car.")
else:
    print("The customer is not eligible to rent a car.")
"""
    return s

def unification():
    s = """def get_index_comma(string):
    index_list = list()
    par_count = 0

    for i in range(len(string)):
        if string[i] == ',' and par_count == 0:
            index_list.append(i)
        elif string[i] == '(':
            par_count += 1
        elif string[i] == ')':
            par_count -= 1

    return index_list


def is_variable(expr):
    for i in expr:
        if i == '(' or i == ')':
            return False

    return True


def process_expression(expr):
    expr = expr.replace(' ', '')
    index = None
    for i in range(len(expr)):
        if expr[i] == '(':
            index = i
            break
    predicate_symbol = expr[:index]
    expr = expr.replace(predicate_symbol, '')
    expr = expr[1:len(expr) - 1]
    arg_list = list()
    indices = get_index_comma(expr)

    if len(indices) == 0:
        arg_list.append(expr)
    else:
        arg_list.append(expr[:indices[0]])
        for i, j in zip(indices, indices[1:]):
            arg_list.append(expr[i + 1:j])
        arg_list.append(expr[indices[len(indices) - 1] + 1:])

    return predicate_symbol, arg_list


def get_arg_list(expr):
    _, arg_list = process_expression(expr)

    flag = True
    while flag:
        flag = False

        for i in arg_list:
            if not is_variable(i):
                flag = True
                _, tmp = process_expression(i)
                for j in tmp:
                    if j not in arg_list:
                        arg_list.append(j)
                arg_list.remove(i)

    return arg_list


def check_occurs(var, expr):
    arg_list = get_arg_list(expr)
    if var in arg_list:
        return True

    return False


def unify(expr1, expr2):

    if is_variable(expr1) and is_variable(expr2):
        if expr1 == expr2:
            return 'Null'
        else:
            return False
    elif is_variable(expr1) and not is_variable(expr2):
        if check_occurs(expr1, expr2):
            return False
        else:
            tmp = str(expr2) + '/' + str(expr1)
            return tmp
    elif not is_variable(expr1) and is_variable(expr2):
        if check_occurs(expr2, expr1):
            return False
        else:
            tmp = str(expr1) + '/' + str(expr2)
            return tmp
    else:
        predicate_symbol_1, arg_list_1 = process_expression(expr1)
        predicate_symbol_2, arg_list_2 = process_expression(expr2)

        # Step 2
        if predicate_symbol_1 != predicate_symbol_2:
            return False
        # Step 3
        elif len(arg_list_1) != len(arg_list_2):
            return False
        else:
            # Step 4: Create substitution list
            sub_list = list()

            # Step 5:
            for i in range(len(arg_list_1)):
                tmp = unify(arg_list_1[i], arg_list_2[i])

                if not tmp:
                    return False
                elif tmp == 'Null':
                    pass
                else:
                    if type(tmp) == list:
                        for j in tmp:
                            sub_list.append(j)
                    else:
                        sub_list.append(tmp)

            # Step 6
            return sub_list


if __name__ == '__main__':
    
    f1 = 'Q(a, g(x, a), f(y))'
    f2 = 'Q(a, g(f(b), a), x)'
    # f1 = input('f1 : ')
    # f2 = input('f2 : ')

    result = unify(f1, f2)
    if not result:
        print('The process of Unification failed!')
    else:
        print('The process of Unification successful!')
        print(result)
"""
    return s

def knowlwdge_rerpesentation():
    s = """lion = {
    "name": "Lion",
    "type": "Mammal",
    "habitat": "Grasslands",
    "diet": "Carnivorous"
}


monkey = {
    "name": "Monkey",
    "type": "Mammal",
    "habitat": "Forest",
    "diet": "Omnivorous"
}


penguin = {
    "name": "Penguin",
    "type": "Bird",
    "habitat": "Antarctica",
    "diet": "Carnivorous"
}
print("Name:", lion["name"])
print("Habitat:", lion["habitat"])
# Define a frame for a cat that inherits from the mammal frame
cat = {
    "name": "Cat",
    "superclass": monkey,
    "habitat": "Domestic",
    "diet": "Carnivorous",
    "has_fur": True,
    "can_climb": True
}
print("Type:", cat["superclass"]["type"])
"""
    return s

def resolution():
    s = """import copy
import time


class Parameter:
    variable_count = 1

    def __init__(self, name=None):
        if name:
            self.type = "Constant"
            self.name = name
        else:
            self.type = "Variable"
            self.name = "v" + str(Parameter.variable_count)
            Parameter.variable_count += 1

    def isConstant(self):
        return self.type == "Constant"

    def unify(self, type_, name):
        self.type = type_
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name


class Predicate:
    def __init__(self, name, params):
        self.name = name
        self.params = params

    def __eq__(self, other):
        return self.name == other.name and all(a == b for a, b in zip(self.params, other.params))

    def __str__(self):
        return self.name + "(" + ",".join(str(x) for x in self.params) + ")"

    def getNegatedPredicate(self):
        return Predicate(negatePredicate(self.name), self.params)


class Sentence:
    sentence_count = 0

    def __init__(self, string):
        self.sentence_index = Sentence.sentence_count
        Sentence.sentence_count += 1
        self.predicates = []
        self.variable_map = {}
        local = {}

        for predicate in string.split("|"):
            name = predicate[:predicate.find("(")]
            params = []

            for param in predicate[predicate.find("(") + 1: predicate.find(")")].split(","):
                if param[0].islower():
                    if param not in local:  # Variable
                        local[param] = Parameter()
                        self.variable_map[local[param].name] = local[param]
                    new_param = local[param]
                else:
                    new_param = Parameter(param)
                    self.variable_map[param] = new_param

                params.append(new_param)

            self.predicates.append(Predicate(name, params))

    def getPredicates(self):
        return [predicate.name for predicate in self.predicates]

    def findPredicates(self, name):
        return [predicate for predicate in self.predicates if predicate.name == name]

    def removePredicate(self, predicate):
        self.predicates.remove(predicate)
        for key, val in self.variable_map.items():
            if not val:
                self.variable_map.pop(key)

    def containsVariable(self):
        return any(not param.isConstant() for param in self.variable_map.values())

    def __eq__(self, other):
        if len(self.predicates) == 1 and self.predicates[0] == other:
            return True
        return False

    def __str__(self):
        return "".join([str(predicate) for predicate in self.predicates])


class KB:
    def __init__(self, inputSentences):
        self.inputSentences = [x.replace(" ", "") for x in inputSentences]
        self.sentences = []
        self.sentence_map = {}

    def prepareKB(self):
        self.convertSentencesToCNF()
        for sentence_string in self.inputSentences:
            sentence = Sentence(sentence_string)
            for predicate in sentence.getPredicates():
                self.sentence_map[predicate] = self.sentence_map.get(
                    predicate, []) + [sentence]

    def convertSentencesToCNF(self):
        for sentenceIdx in range(len(self.inputSentences)):
            # Do negation of the Premise and add them as literal
            if "=>" in self.inputSentences[sentenceIdx]:
                self.inputSentences[sentenceIdx] = negateAntecedent(
                    self.inputSentences[sentenceIdx])

    def askQueries(self, queryList):
        results = []

        for query in queryList:
            negatedQuery = Sentence(negatePredicate(query.replace(" ", "")))
            negatedPredicate = negatedQuery.predicates[0]
            prev_sentence_map = copy.deepcopy(self.sentence_map)
            self.sentence_map[negatedPredicate.name] = self.sentence_map.get(
                negatedPredicate.name, []) + [negatedQuery]
            self.timeLimit = time.time() + 40

            try:
                result = self.resolve([negatedPredicate], [
                                      False]*(len(self.inputSentences) + 1))
            except:
                result = False

            self.sentence_map = prev_sentence_map

            if result:
                results.append("TRUE")
            else:
                results.append("FALSE")

        return results

    def resolve(self, queryStack, visited, depth=0):
        if time.time() > self.timeLimit:
            raise Exception
        if queryStack:
            query = queryStack.pop(-1)
            negatedQuery = query.getNegatedPredicate()
            queryPredicateName = negatedQuery.name
            if queryPredicateName not in self.sentence_map:
                return False
            else:
                queryPredicate = negatedQuery
                for kb_sentence in self.sentence_map[queryPredicateName]:
                    if not visited[kb_sentence.sentence_index]:
                        for kbPredicate in kb_sentence.findPredicates(queryPredicateName):

                            canUnify, substitution = performUnification(
                                copy.deepcopy(queryPredicate), copy.deepcopy(kbPredicate))

                            if canUnify:
                                newSentence = copy.deepcopy(kb_sentence)
                                newSentence.removePredicate(kbPredicate)
                                newQueryStack = copy.deepcopy(queryStack)

                                if substitution:
                                    for old, new in substitution.items():
                                        if old in newSentence.variable_map:
                                            parameter = newSentence.variable_map[old]
                                            newSentence.variable_map.pop(old)
                                            parameter.unify(
                                                "Variable" if new[0].islower() else "Constant", new)
                                            newSentence.variable_map[new] = parameter

                                    for predicate in newQueryStack:
                                        for index, param in enumerate(predicate.params):
                                            if param.name in substitution:
                                                new = substitution[param.name]
                                                predicate.params[index].unify(
                                                    "Variable" if new[0].islower() else "Constant", new)

                                for predicate in newSentence.predicates:
                                    newQueryStack.append(predicate)

                                new_visited = copy.deepcopy(visited)
                                if kb_sentence.containsVariable() and len(kb_sentence.predicates) > 1:
                                    new_visited[kb_sentence.sentence_index] = True

                                if self.resolve(newQueryStack, new_visited, depth + 1):
                                    return True
                return False
        return True


def performUnification(queryPredicate, kbPredicate):
    substitution = {}
    if queryPredicate == kbPredicate:
        return True, {}
    else:
        for query, kb in zip(queryPredicate.params, kbPredicate.params):
            if query == kb:
                continue
            if kb.isConstant():
                if not query.isConstant():
                    if query.name not in substitution:
                        substitution[query.name] = kb.name
                    elif substitution[query.name] != kb.name:
                        return False, {}
                    query.unify("Constant", kb.name)
                else:
                    return False, {}
            else:
                if not query.isConstant():
                    if kb.name not in substitution:
                        substitution[kb.name] = query.name
                    elif substitution[kb.name] != query.name:
                        return False, {}
                    kb.unify("Variable", query.name)
                else:
                    if kb.name not in substitution:
                        substitution[kb.name] = query.name
                    elif substitution[kb.name] != query.name:
                        return False, {}
    return True, substitution


def negatePredicate(predicate):
    return predicate[1:] if predicate[0] == "~" else "~" + predicate


def negateAntecedent(sentence):
    antecedent = sentence[:sentence.find("=>")]
    premise = []

    for predicate in antecedent.split("&"):
        premise.append(negatePredicate(predicate))

    premise.append(sentence[sentence.find("=>") + 2:])
    return "|".join(premise)


def getInput(filename):
    with open(filename, "r") as file:
        noOfQueries = int(file.readline().strip())
        inputQueries = [file.readline().strip() for _ in range(noOfQueries)]as
        noOfSentences = int(file.readline().strip())
        inputSentences = [file.readline().strip()
                          for _ in range(noOfSentences)]
        return inputQueries, inputSentences


def printOutput(filename, results):
    print(results)
    with open(filename, "w") as file:
        for line in results:
            file.write(line)
            file.write("\n")
    file.close()


if __name__ == '__main__':
    inputQueries_, inputSentences_ = getInput(r'C:\Users\User\Documents\input.txt')
    knowledgeBase = KB(inputSentences_)
    knowledgeBase.prepareKB()
    results_ = knowledgeBase.askQueries(inputQueries_)
    printOutput("output.txt", results_)
"""
    return s

def bayesian():
    s = """# Importing modules that are required
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.linear_model import BayesianRidge

# Loading dataset
dataset = load_boston()
X, y = dataset.data, dataset.target

# Splitting dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.15, random_state = 42)

# Creating and training model
model = BayesianRidge()
model.fit(X_train, y_train)

# Model making a prediction on test data
prediction = model.predict(X_test)

# Evaluation of r2 score of the model against the test set
print(f"r2 Score Of Test Set : {r2_score(y_test, prediction)}")
"""
    return s
