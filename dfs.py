from search_algorithms import SearchAlgorithms


class DFS(SearchAlgorithms):
    def search(self, step_callback=None):
        visited = set()
        number_of_nodes = 1  # Count the origin node
     

        # LIFO stack for DFS
        stack = [(self.start, [self.start])]  # (current_node, path_to_current_node)

        while stack:
            current_node, path = stack.pop()

            if current_node in visited:
                continue
            
            self.frontier.remove(current_node)
            visited.add(current_node)
            
            # Check if goal is reached
            is_goal = current_node in self.goals
            
           
            # If goal is found, return immediately after showing the solution
            if is_goal:
                for node in stack:
                    if node[0] not in self.frontier:
                        self.frontier.append(node[0])

                step_callback(current_node, None, path, self.frontier, visited, is_goal)
                return [number_of_nodes, path, current_node]
            
            # Smaller valued nodes are processed first
            for neighbor, cost in reversed(self.graph['adjacency_list'][current_node]):
                if neighbor not in visited:
                    number_of_nodes += 1
                    new_path = path + [neighbor]
                    

                    
                    stack.append((neighbor, new_path))

                    for node in stack:
                        if node[0] not in self.frontier:
                          
                            self.frontier.append(node[0])

                    step_callback(current_node, neighbor, new_path, self.frontier, visited, is_goal)

        return [number_of_nodes, None, None]  # No path found
