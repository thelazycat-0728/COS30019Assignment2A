from collections import deque, defaultdict
import heapq
import math
from utils import make_heuristics

class SearchAlgorithms:
    def __init__(self, graph):
        self.graph = graph
        self.start = graph['origin']
        self.goals = set(graph['destinations'])
        self.coords = graph['nodes']

    def bfs(self):
        visited = set()
        number_of_nodes = 1  # Count the origin node
        visited.add(self.start)

        if self.start in self.goals:
            return [number_of_nodes, [self.start], self.start]

        queue = deque([(self.start, [self.start])])  # (current_node, path_to_current_node)

        while queue:
            current_node, path = queue.popleft()

            if (current_node in self.goals):
                return [number_of_nodes, path, current_node]  # Return the path to the goal
        
            # Use adjacency list instead of edges dictionary
            for neighbor, cost in self.graph['adjacency_list'][current_node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    number_of_nodes += 1
                    
                    new_path = path + [neighbor]
                    
                    queue.append((neighbor, new_path))

        return [number_of_nodes, None, None]  # No path found
    


    def dfs(self):
        visited = set()
        number_of_nodes = 1  # Count the origin node
        visited.add(self.start)

        # LIFO stack for DFS
        stack = [(self.start, [self.start])]  # (current_node, path_to_current_node)

        while stack:
            current_node, path = stack.pop()

            if current_node in self.goals:
                return [number_of_nodes, path, current_node]  # Return the path to the goal
            
           
            # Ensure first node not entered twice
            if (number_of_nodes != 1 ):
                visited.add(current_node)

            # Smaller valued nodes are processed first
            for neighbor, cost in reversed(self.graph['adjacency_list'][current_node]):
                if neighbor not in visited:
                    number_of_nodes += 1

                    
                    new_path = path + [neighbor]
                    stack.append((neighbor, new_path))

        return [number_of_nodes, None, None]  # No path found
    

    # Need to ask whether Dijkstra just ignore path that are worse
    def dijkstra(self):
        visited = set()
        number_of_nodes = 1  # Count the origin node
        distances = defaultdict(lambda: math.inf)
        distances[self.start] = 0.0

        counter = 0 # counter is used to ensure nodes that are pushed earlier are popped earlier in case of ties
        min_heap = [(0, counter, self.start, [self.start])]  # (cost, current_node, path_to_current_node)

        while min_heap:
            cost, _counter, current_node, path = heapq.heappop(min_heap)

            if current_node in self.goals:
                visited.add(current_node)
                return [number_of_nodes, path, current_node]  # Return the path to the goal

            if current_node not in visited:
                
                visited.add(current_node)

                for neighbor, edge_cost in self.graph['adjacency_list'][current_node]:
                    if neighbor not in visited:
                        number_of_nodes += 1
                        new_cost = cost + edge_cost
                        if new_cost < distances[neighbor]:
                            new_path = path + [neighbor]
                            distances[neighbor] = new_cost
                            counter += 1
                            heapq.heappush(min_heap, (new_cost, counter, neighbor, new_path))

        return [number_of_nodes, None, None]  # No path found
    

    def gbfs(self):
        h = make_heuristics(self.coords, self.goals)
        priority_queue = []

        counter = 0
        heapq.heappush(priority_queue, (h(self.start), counter, self.start, [self.start]))
        visited = set()
        number_of_nodes = 1

        

        while priority_queue:

            _, _counter, node, path = heapq.heappop(priority_queue)
            
            visited.add(node)

            if node in self.goals:
                return [number_of_nodes, path, node]
            
            # expand neighbors in ascending id
            for neighbor, cost in self.graph['adjacency_list'][node]:
                if neighbor in visited:
                    continue

                new_path = path + [neighbor]
                counter += 1
                heapq.heappush(priority_queue, (h(neighbor), counter, neighbor, new_path))
                number_of_nodes += 1

        return [number_of_nodes, None, None]
    


    def astar(self):
        h = make_heuristics(self.coords, self.goals)
        g_cost = defaultdict(lambda: math.inf)
        g_cost[self.start] = 0.0

        counter = 0

        # priority queue: (g(n) + h(n), h(n), node, counter, path)
        priority_queue = []
        h_0 = h(self.start) 
        f_0 = g_cost[self.start] + h_0

        heapq.heappush(priority_queue, (f_0, h_0, counter, self.start, [self.start]))
        nodes_created = 1
        visited = set()

        while priority_queue:

            print(priority_queue)
            _f, _h, _counter, node, path = heapq.heappop(priority_queue)
            if node in visited: 
                continue
            visited.add(node)
            if node in self.goals:
                return [nodes_created, path, node]
                # return u, nodes_created, reconstruct(start, u)
            for neighbor, path_cost in self.graph['adjacency_list'][node]:
                total_cost = g_cost[node] + path_cost
                if total_cost < g_cost[neighbor]:
                    g_cost[neighbor] = total_cost
                    h_n = h(neighbor)
                    f_neighbor = total_cost + h_n # total cost represents g(n)
                    new_path = path + [neighbor]

                    counter += 1
                    heapq.heappush(priority_queue, (f_neighbor, h_n, counter, neighbor, new_path))
                    nodes_created += 1
        return [nodes_created, None, None]

