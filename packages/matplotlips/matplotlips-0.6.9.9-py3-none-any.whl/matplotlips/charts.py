def graph():
    ans = '''
    import networkx as nx

    def greedy_coloring(G):
        # Create a dictionary to store the color assigned to each node
        node_color = {}
        # Iterate over the nodes of the graph
        for node in G.nodes:
            # Initialize the set of used colors to be empty
            used_colors = set()
            # Iterate over the neighbors of the current node
            for neighbor in G.neighbors(node):
                # If the neighbor has already been colored, add its color to the set of used colors
                if neighbor in node_color:
                    used_colors.add(node_color[neighbor])
            # Find the minimum unused color
            for color in range(len(G)):
                if color not in used_colors:
                    break
            # Assign the minimum unused color to the current node
            node_color[node] = color
        # Return the dictionary of node colors
        return node_color

    # Example usage:
    G = nx.Graph()
    G.add_nodes_from([1,2,3,4,5])
    G.add_edges_from([(1,2), (1,3), (2,4), (3,5), (4,5)])

    node_color = greedy_coloring(G)
    num_colors = max(node_color.values()) + 1

    print("Minimum number of colors required:", num_colors)
    '''
    return(ans)

def banana():
    ans = '''
    dp = [[-1 for i in range(3001)] for j in range(1001)]
    def recBananaCnt(A, B, C):
        if (B <= A):
            return 0
        if (B <= C):
            return B - A
        if (A == 0):
            return B
        if (dp[A][B] != -1):
            return dp[A][B]
        maxCount = -2**32
        tripCount = ((2 * B) // C) - 1 if (B % C == 0) else ((2 * B) // C) + 1
        for i in range(1, A+1):
            curCount = recBananaCnt(A - i, B - tripCount * i, C)
            if (curCount > maxCount):
                maxCount = curCount
                dp[A][B] = maxCount
        return maxCount


    def maxBananaCnt(A, B, C):
        print("Calculating...")
        return recBananaCnt(A, B, C)


    A = 1000
    B = 3000
    C = 1000
    print(maxBananaCnt(A, B, C))
    '''
    return(ans)


def nlp():
    ans = '''
    import nltk
    nltk.download('vader_lexicon')

    from nltk.sentiment.vader import SentimentIntensityAnalyzer

    # Initialize the sentiment analyzer
    sia = SentimentIntensityAnalyzer()

    # Sample text for analysis
    text = "I really enjoyed this movie. The acting was great and the plot was engaging."

    # Calculate the sentiment score for the text
    score = sia.polarity_scores(text)

    # Print the sentiment score
    print("negative = ", score["neg"])
    print("neutral = ", score["neu"])
    print("positive = ", score["pos"])
    print("compound = ", score["compound"])
    ''' 
    return(ans)

def logistic():
    ans = '''
    from sklearn.datasets import load_breast_cancer
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression

    # Load the breast cancer dataset
    cancer = load_breast_cancer()

    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        cancer.data, cancer.target, test_size=0.2, random_state=42)

    # Create a logistic regression model
    lr_model = LogisticRegression()

    # Train the model on the training data
    lr_model.fit(X_train, y_train)

    # Predict the target values for the test data
    y_pred = lr_model.predict(X_test)

    # Calculate the accuracy of the model
    accuracy = lr_model.score(X_test, y_test)

    # Print the accuracy as a percentage
    print("Logistic Regression Accuracy: {:.2f}%".format(accuracy*100))
    ''' 
    return(ans)


# Monty Hall Game in Python
def montyhall():
    ans = '''
    import random

    def play_monty_hall(choice):
        # Prizes behind the door
        # initial ordering doesn't matter
        prizes = ['goat', 'car', 'goat']
        
        # Randomizing the prizes
        random.shuffle(prizes) 
        
        # Determining door without car to open
        while True:
            opening_door = random.randrange(len(prizes))
            if prizes[opening_door] != 'car' and choice-1 != opening_door:
                break
        
        opening_door = opening_door + 1
        print('We are opening the door number-%d' % (opening_door))
        
        # Determining switching door
        options = [1,2,3]
        options.remove(choice)
        options.remove(opening_door)
        switching_door = options[0]
            # Asking for switching the option
        print('Now, do you want to switch to door number-%d? (yes/no)' %(switching_door))
        answer = input()
        if answer == 'yes':
            result = switching_door - 1
        else:
            result = choice - 1
        
        # Displaying the player's prize 
        print('And your prize is ....', prizes[result].upper())
        
    # Reading initial choice
    choice = int(input('Which door do you want to choose? (1,2,3): '))

    # Playing game
    play_monty_hall(choice)
    ''' 
    return(ans)


def astar2():
    ans = '''
    from queue import PriorityQueue


    class Graph:
        def _init_(self, adjacency_list):
            self.adjacency_list = adjacency_list

        def get_neighbors(self, v):
            return self.adjacency_list[v]

        def h(self, n):
            H = {
                'A': 1,
                'B': 1,
                'C': 1,
                'D': 1
            }

            return H[n]

        def best_first_search(self, start, goal):
            explored = []
            pq = PriorityQueue()
            pq.put((0, start))
            parents = {start: None}

            while not pq.empty():
                current = pq.get()[1]

                if current == goal:
                    path = []
                    while current is not None:
                        path.append(current)
                        current = parents[current]
                    path.reverse()
                    print(f"Best-First Search path: {path}")
                    return path

                explored.append(current)

                for neighbor, weight in self.get_neighbors(current):
                    if neighbor not in explored and neighbor not in [i[1] for i in pq.queue]:
                        parents[neighbor] = current
                        pq.put((self.h(neighbor), neighbor))

            print("Path not found!")
            return None

        def a_star_algorithm(self, start_node, stop_node):
            open_list = set([start_node])
            closed_list = set([])
            g = {}

            g[start_node] = 0
            parents = {}
            parents[start_node] = start_node

            while len(open_list) > 0:
                n = None
                for v in open_list:
                    if n == None or g[v] + self.h(v) < g[n] + self.h(n):
                        n = v

                if n == None:
                    print('Path does not exist!')
                    return None
                if n == stop_node:
                    reconst_path = []

                    while parents[n] != n:
                        reconst_path.append(n)
                        n = parents[n]

                    reconst_path.append(start_node)

                    reconst_path.reverse()

                    print('A* path: {}'.format(reconst_path))
                    return reconst_path

                for (m, weight) in self.get_neighbors(n):
                    if m not in open_list and m not in closed_list:
                        open_list.add(m)
                        parents[m] = n
                        g[m] = g[n] + weight
                    else:
                        if g[m] > g[n] + weight:
                            g[m] = g[n] + weight
                            parents[m] = n

                            if m in closed_list:
                                closed_list.remove(m)
                                open_list.add(m)
                open_list.remove(n)
                closed_list.add(n)

            print('Path does not exist!')
            return None


    adjacency_list = {
        'A': [('B', 1), ('C', 3), ('D', 7)],
        'B': [('D', 5)],
        'C': [('D', 12)]
    }
    graph1 = Graph(adjacency_list)
    graph1.best_first_search('A', 'D')
    graph1.a_star_algorithm('A', 'D')
    ''' 
    return(ans)


def bfsdfs():
    ans = '''
    graph = {
        'A': ['B', 'C'],
        'B': ['D', 'E'],
        'C': ['F'],
        'D': [],
        'E': ['F'],
        'F': []
    }

    visited_bfs = []
    queue = []


    def bfs(visited_bfs, graph, node):
    visited_bfs.append(node)
    queue.append(node)

    while queue:
        s = queue.pop(0)
        print(s, end=" ")

        for neighbour in graph[s]:
        if neighbour not in visited_bfs:
            visited_bfs.append(neighbour)
            queue.append(neighbour)


    visited = set()


    def dfs(visited, graph, node):
        if node not in visited:
            print(node, end=" ")
            visited.add(node)
            for neighbour in graph[node]:
                dfs(visited, graph, neighbour)


    print("BFS:", end=" ")
    bfs(visited_bfs, graph, 'A')
    print('\n')
    print("DFS:", end=" ")
    dfs(visited, graph, 'A')
    ''' 
    return(ans)


def help():
    ans = '''
    EXP1: CAMEL BANANA PROBLEM - print(charts.banana())
    EXP2: GRAPH COLOURING - print(charts.graph())
    EXP3: crypta - print(charts.crypta())
    EXP4: DEPTH FIRST SEARCH/ BREADTH FIRST SEARCH - print(charts.bfsdfs())
    EXP5: BEST FIRST SEARCH / A* ALGORITHM - print(charts.astar())
    EXP6: MONTY HALL PROBLEM - print(charts.montyhall())
    EXP7: unification - print(charts.unification())
    EXP8: LOGISTIC REGRESSION - print(charts.logistic())
    EXP9: NLP - print(charts.nlp())
    EXP10: DL - print(charts.dl())
    ''' 
    return(ans)

def menu():
    ans = '''
    EXP1: CAMEL BANANA PROBLEM - print(charts.banana())
    EXP2: GRAPH COLOURING - print(charts.graph())
    EXP3: crypta - print(charts.crypta())
    EXP4: DEPTH FIRST SEARCH/ BREADTH FIRST SEARCH - print(charts.bfsdfs())
    EXP5: BEST FIRST SEARCH / A* ALGORITHM - print(charts.astar())
    EXP6: MONTY HALL PROBLEM - print(charts.montyhall())
    EXP7: unification - print(charts.unification())
    EXP8: LOGISTIC REGRESSION - print(charts.logistic())
    EXP9: NLP - print(charts.nlp())
    EXP10: DL - print(charts.dl())
    ''' 
    return(ans)


def all():
    ans = '''
    EXP1: CAMEL BANANA PROBLEM - print(charts.banana())
    EXP2: GRAPH COLOURING - print(charts.graph())
    EXP3: crypta - print(charts.crypta())
    EXP4: DEPTH FIRST SEARCH/ BREADTH FIRST SEARCH - print(charts.bfsdfs())
    EXP5: BEST FIRST SEARCH / A* ALGORITHM - print(charts.astar())
    EXP6: MONTY HALL PROBLEM - print(charts.montyhall())
    EXP7: unification - print(charts.unification())
    EXP8: LOGISTIC REGRESSION - print(charts.logistic())
    EXP9: NLP - print(charts.nlp())
    EXP10: DL - print(charts.dl())
    ''' 
    return(ans)


def astar1():

    ans = '''

    import numpy as np


    class Cell:
        """
        Class cell represents a cell in the world which have the properties:
        position: represented by tuple of x and y coordinates initially set to (0,0).
        parent: Contains the parent cell object visited before we arrived at this cell.
        g, h, f: Parameters used when calling our heuristic function.
        """

        def __init__(self):
            self.position = (0, 0)
            self.parent = None
            self.g = 0
            self.h = 0
            self.f = 0

        """
        Overrides equals method because otherwise cell assign will give
        wrong results.
        """

        def __eq__(self, cell):
            return self.position == cell.position

        def showcell(self):
            print(self.position)


    class Gridworld:
        """
        Gridworld class represents the  external world here a grid M*M
        matrix.
        world_size: create a numpy array with the given world_size default is 5.
        """

        def __init__(self, world_size=(5, 5)):
            self.w = np.zeros(world_size)
            self.world_x_limit = world_size[0]
            self.world_y_limit = world_size[1]

        def show(self):
            print(self.w)

        def get_neigbours(self, cell):
            """
            Return the neighbours of cell
            """
            neughbour_cord = [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1),
            ]
            current_x = cell.position[0]
            current_y = cell.position[1]
            neighbours = []
            for n in neughbour_cord:
                x = current_x + n[0]
                y = current_y + n[1]
                if 0 <= x < self.world_x_limit and 0 <= y < self.world_y_limit:
                    c = Cell()
                    c.position = (x, y)
                    c.parent = cell
                    neighbours.append(c)
            return neighbours


    def astar(world, start, goal):
        """
        Implementation of a start algorithm.
        world : Object of the world object.
        start : Object of the cell as  start position.
        stop  : Object of the cell as goal position.

        >>> p = Gridworld()
        >>> start = Cell()
        >>> start.position = (0,0)
        >>> goal = Cell()
        >>> goal.position = (4,4)
        >>> astar(p, start, goal)
        [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
        """
        _open = []
        _closed = []
        _open.append(start)

        while _open:
            min_f = np.argmin([n.f for n in _open])
            current = _open[min_f]
            _closed.append(_open.pop(min_f))
            if current == goal:
                break
            for n in world.get_neigbours(current):
                for c in _closed:
                    if c == n:
                        continue
                n.g = current.g + 1
                x1, y1 = n.position
                x2, y2 = goal.position
                n.h = (y2 - y1) ** 2 + (x2 - x1) ** 2
                n.f = n.h + n.g

                for c in _open:
                    if c == n and c.f < n.f:
                        continue
                _open.append(n)
        path = []
        while current.parent is not None:
            path.append(current.position)
            current = current.parent
        path.append(current.position)
        return path[::-1]


    if __name__ == "__main__":
        world = Gridworld()
        # Start position and goal
        start = Cell()
        start.position = (0, 0)
        goal = Cell()
        goal.position = (4, 4)
        print(f"path from {start.position} to {goal.position}")
        s = astar(world, start, goal)
        #   Just for visual reasons.
        for i in s:
            world.w[i] = 1
        print(world.w)
    '''
    return(ans)

#resolution
def unification():

    ans = '''
    import copy
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
            inputQueries = [file.readline().strip() for _ in range(noOfQueries)]
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
        # Change the below path to the input file in your system
        inputQueries_, inputSentences_ = getInput(
            'Unification-Resolution/input.txt')
        knowledgeBase = KB(inputSentences_)
        knowledgeBase.prepareKB()
        results_ = knowledgeBase.askQueries(inputQueries_)
        print(results_)



        #unification

        def get_index_comma(string):
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


    #input text

    6
    F(Joe)
    H(John)
    ~H(Alice)
    ~H(John)
    G(Joe)
    G(Tom)
    14
    ~F(x) | G(x)
    ~G(x) | H(x)
    ~H(x) | F(x)
    ~R(x) | H(x)
    ~A(x) | H(x)
    ~D(x,y) | ~H(y)
    ~B(x,y) | ~C(x,y) | A(x)
    B(John,Alice)
    B(John,Joe)
    ~D(x,y) | ~Q(y) | C(x,y)
    D(John,Alice)
    Q(Joe)
    D(John,Joe)
    R(Tom)
    '''
    return(ans)



def crypta():
    ans = '''
    def solutions():
        # letters = ('s', 'e', 'n', 'd', 'm', 'o', 'r', 'y')
        all_solutions = list()
        for s in range(9, -1, -1):
            for e in range(9, -1, -1):
                for n in range(9, -1, -1):
                    for d in range(9, -1, -1):
                        for m in range(9, 0, -1):
                            for o in range(9, -1, -1):
                                for r in range(9, -1, -1):
                                    for y in range(9, -1, -1):
                                        if len(set([s, e, n, d, m, o, r, y])) == 8:
                                            send = 1000 * s + 100 * e + 10 * n + d
                                            more = 1000 * m + 100 * o + 10 * r + e
                                            money = 10000 * m + 1000 * o + 100 * n + 10 * e + y

                                            if send + more == money:
                                                all_solutions.append(
                                                    (send, more, money))
        return all_solutions


    print(solutions())
    '''
    return(ans)

