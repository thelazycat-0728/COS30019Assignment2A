from search_algorithms import SearchAlgorithms
from collections import defaultdict
import heapq
from utils import make_heuristics
import math

class AS(SearchAlgorithms):
    def search(self):
        h = make_heuristics(self.coords, self.goals)
        g_cost = defaultdict(lambda: math.inf)
        g_cost[self.start] = 0.0

        counter = 0

        # priority queue: (g(n) + h(n), h(n), node, counter, path)
        priority_queue = []
        h_0 = h(self.start) 
        f_0 = g_cost[self.start] + h_0

        heapq.heappush(priority_queue, (f_0, h_0, counter, self.start, [self.start]))
        number_of_nodes = 1
        visited = set()

        while priority_queue:
            _f, _h, _counter, node, path = heapq.heappop(priority_queue)
            if node in visited: 
                continue
            visited.add(node)
            if node in self.goals:
                return [number_of_nodes, path, node]
                # return u, number_of_nodes, reconstruct(start, u)
            for neighbor, path_cost in self.graph['adjacency_list'][node]:
                total_cost = g_cost[node] + path_cost
                if total_cost < g_cost[neighbor]:
                    g_cost[neighbor] = total_cost
                    h_n = h(neighbor)
                    f_neighbor = total_cost + h_n # total cost represents g(n)
                    new_path = path + [neighbor]

                    counter += 1
                    heapq.heappush(priority_queue, (f_neighbor, h_n, counter, neighbor, new_path))
                    number_of_nodes += 1
        return [number_of_nodes, None, None]