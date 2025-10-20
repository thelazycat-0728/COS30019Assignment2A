from collections import deque

class SearchAlgorithms:
    def __init__(self, graph):
        self.graph = graph

    def bfs(self):
        start = self.graph['origin']
        goals = set(self.graph['destinations'])
        visited = set()
        number_of_nodes = 1  # Count the origin node
        visited.add(start)

        if start in goals:
            return [number_of_nodes, [start], start]
        
        
        queue = deque([(start, [start])])  # (current_node, path_to_current_node)

        while queue:
            current_node, path = queue.popleft()
           
        
            # Use adjacency list instead of edges dictionary
            for neighbor, cost in self.graph['adjacency_list'][current_node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    number_of_nodes += 1
                    
                    new_path = path + [neighbor]

                    if neighbor in goals:
                        return [number_of_nodes, new_path, neighbor]  # Return the path to the goal
                    
                    queue.append((neighbor, new_path))

        return [number_of_nodes, None, list(goals)]  # No path found
    

    def dfs(self):
        start = self.graph['origin']
        goals = set(self.graph['destinations'])
        visited = set()
        number_of_nodes = 1  # Count the origin node
        visited.add(start)

        stack = [(start, [start])]  # (current_node, path_to_current_node)

        while stack:
            current_node, path = stack.pop()
            
            if current_node in goals:
                return [number_of_nodes, path]  # Return the path to the goal
            
            # Use adjacency list instead of edges dictionary
            for neighbor, cost in reversed(self.graph['adjacency_list'][current_node]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    number_of_nodes += 1
                    
                    new_path = path + [neighbor]
                    stack.append((neighbor, new_path))

        return [number_of_nodes, None]  # No path found