from search_algorithms import SearchAlgorithms
import heapq
from collections import defaultdict
import math

# Dijkstra's Algorithm Implementation
class CUS1(SearchAlgorithms):
  def search(self, step_callback=None):
    visited = set()
    number_of_nodes = 1  # Count the origin node
    distances = defaultdict(lambda: math.inf)
    distances[self.start] = 0.0

    counter = 0 # counter is used to ensure nodes that are pushed earlier are popped earlier in case of ties
    min_heap = [(0, counter, self.start, [self.start])]  # (cost, current_node, path_to_current_node)

    while min_heap:
        cost, _counter, current_node, path = heapq.heappop(min_heap)

        is_goal = current_node in self.goals

        # If goal is found, return immediately after showing the solution
        if is_goal:
            for node in min_heap:
                if node[2] not in self.frontier:
                    self.frontier.append(node[2])

            step_callback(current_node, None, path, self.frontier, visited, is_goal, cost)
            return [number_of_nodes, path, current_node]

        if current_node not in visited:
            
            visited.add(current_node)
            
            self.frontier.remove(current_node)

            for neighbor, edge_cost in self.graph['adjacency_list'][current_node]:
                if neighbor not in visited:
                    
                    new_cost = cost + edge_cost
                    if new_cost < distances[neighbor]:
                        number_of_nodes += 1
                        new_path = path + [neighbor]
                        distances[neighbor] = new_cost
                        counter += 1
                        heapq.heappush(min_heap, (new_cost, counter, neighbor, new_path))

                        for node in min_heap:
                            if node[2] not in self.frontier:
                                self.frontier.append(node[2])

                        step_callback(current_node ,neighbor, new_path, self.frontier, visited, is_goal, new_cost)
                        

    return [number_of_nodes, None, None]  # No path found
