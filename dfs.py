from search_algorithms import SearchAlgorithms


class DFS(SearchAlgorithms):
    def search(self):
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
