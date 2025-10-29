from search_algorithms import SearchAlgorithms
from collections import defaultdict
import heapq
from utils import make_heuristics
import math

class AS(SearchAlgorithms):
    def search(self, step_callback=None):
        h = make_heuristics(self.coords, self.goals)
        g_cost = defaultdict(lambda: math.inf)
        g_cost[self.start] = 0.0

        counter = 0

        # priority queue: (g(n) + h(n), h(n), node, counter, path)
        min_heap = []
        h_0 = h(self.start) 
        f_0 = g_cost[self.start] + h_0

        heapq.heappush(min_heap, (f_0, h_0, counter, self.start, [self.start]))
        number_of_nodes = 1
        visited = set()

        while min_heap:
            _f, _h, _counter, current_node, path = heapq.heappop(min_heap)

            if current_node in visited:
                continue
            visited.add(current_node)

            self.frontier.remove(current_node)

            is_goal = current_node in self.goals

            
            if is_goal:
                for node in min_heap:
                    if node[3] not in self.frontier:
                        self.frontier.append(node[3])

                step_callback(current_node, path, self.frontier, visited, is_goal)
                return [number_of_nodes, path, current_node]
            

                # return u, number_of_nodes, reconstruct(start, u)
            for neighbor, path_cost in self.graph['adjacency_list'][current_node]:
                total_cost = g_cost[current_node] + path_cost
                if total_cost < g_cost[neighbor]:
                    g_cost[neighbor] = total_cost
                    h_n = h(neighbor)
                    f_neighbor = total_cost + h_n # total cost represents g(n)
                    new_path = path + [neighbor]

                    counter += 1
                    heapq.heappush(min_heap, (f_neighbor, h_n, counter, neighbor, new_path))
                    number_of_nodes += 1

                    for node in min_heap:
                        if node[3] not in self.frontier:
                            self.frontier.append(node[3])

                        step_callback(current_node, new_path, self.frontier, visited, is_goal)
        return [number_of_nodes, None, None]