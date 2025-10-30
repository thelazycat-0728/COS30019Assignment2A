from search_algorithms import SearchAlgorithms
import heapq
from utils import make_heuristics

class GBFS(SearchAlgorithms):
  def search(self, step_callback=None):
    h = make_heuristics(self.coords, self.goals)
    min_heap = []

    counter = 0
    heapq.heappush(min_heap, (h(self.start), counter, self.start, [self.start]))
    visited = set()
    number_of_nodes = 1

    

    while min_heap:

        _, _counter, current_node, path = heapq.heappop(min_heap)

        visited.add(current_node)

        self.frontier.remove(current_node)

        is_goal = current_node in self.goals

        # If goal is found, return immediately after showing the solution
        if is_goal:
            for node in min_heap:
                if node[2] not in self.frontier:
                    self.frontier.append(node[2])

            step_callback(current_node, None, path, self.frontier, visited, is_goal, None, h(current_node))
            return [number_of_nodes, path, current_node]
        
        # expand neighbors in ascending id
        for neighbor, cost in self.graph['adjacency_list'][current_node]:
            if neighbor in visited:
                continue

            new_path = path + [neighbor]

            heuristic_cost = h(neighbor)
            counter += 1
            heapq.heappush(min_heap, (heuristic_cost, counter, neighbor, new_path))
            number_of_nodes += 1

            for node in min_heap:
                if node[2] not in self.frontier:
                    self.frontier.append(node[2])

            step_callback(current_node, neighbor, new_path, self.frontier, visited, is_goal, None, heuristic_cost)

    return [number_of_nodes, None, None]