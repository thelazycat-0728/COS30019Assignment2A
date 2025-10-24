from search_algorithms import SearchAlgorithms
from collections import deque

class BFS(SearchAlgorithms):
    def search(self):
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