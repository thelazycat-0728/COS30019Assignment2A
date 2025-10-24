from search_algorithms import SearchAlgorithms
import heapq
from utils import make_heuristics

class GBFS(SearchAlgorithms):
  def search(self):
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