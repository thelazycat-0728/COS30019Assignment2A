from search_algorithms import SearchAlgorithms
import heapq
from collections import defaultdict
import math

# Dijkstra's Algorithm Implementation
class CUS1(SearchAlgorithms):
  def search(self):
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
